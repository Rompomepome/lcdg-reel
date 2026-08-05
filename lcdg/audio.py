"""
Bibliotheque audio locale.

Mixkit n'expose aucune API : on ne va pas gratter leur HTML a chaque episode.
Les pistes sont telechargees une fois depuis le compte, rangees dans assets/audio/,
et decrites dans config/audio_manifest.json avec leurs mesures acoustiques.
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import charte as C
from lcdg import binaires as B

MANIFEST = C.RACINE / "config" / "audio_manifest.json"


def manifeste() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def chemin(cle: str) -> Path:
    m = manifeste()
    for famille in ("musiques", "effets"):
        for p in m[famille]:
            if p["cle"] == cle:
                f = C.AUDIO / p["fichier"]
                if not f.exists():
                    raise SystemExit(
                        f"[!] Fichier audio manquant : {f.name}\n"
                        f"    Telecharge-le depuis {p.get('url_page', 'Mixkit')} "
                        f"et depose-le dans assets/audio/ sous ce nom exact.\n"
                        f"    Lance 'python scripts/doctor.py' pour la liste complete."
                    )
                return f
    raise KeyError(f"cle audio inconnue : {cle}")


def manquants() -> list[str]:
    m = manifeste()
    return [p["fichier"] for f in ("musiques", "effets") for p in m[f]
            if not (C.AUDIO / p["fichier"]).exists()]


# --------------------------------------------------------------- analyse
def profil(fichier, secondes=55):
    """Mesure ce qui compte pour un lit sous texte : stabilite, brillance, rythme."""
    x = B.pcm(fichier, sr=22050, duree_s=secondes)
    if x.size < 22050 * 20:
        return None
    f = 22050
    w = f * 5
    niveaux = [20 * np.log10(max(np.sqrt((x[i:i + w] ** 2).mean()), 1e-6))
               for i in range(0, len(x) - w, w)][:11]

    n, hop = 512, 256
    nf = (len(x) - n) // hop
    S = np.abs(np.fft.rfft(
        np.lib.stride_tricks.sliding_window_view(x, n)[::hop][:nf] * np.hanning(n), axis=1))
    fr = np.fft.rfftfreq(n, 1 / f)
    flux = np.maximum(0, np.diff(S, axis=0)).sum(axis=1)
    flux = (flux - flux.mean()) / max(flux.std(), 1e-9)
    return {
        "amplitude_db": round(max(niveaux) - min(niveaux), 1),
        "centroide_hz": int((S * fr).sum() / max(S.sum(), 1e-9)),
        "attaques_par_s": round(float((flux > 1.6).sum() / (nf * hop / f)), 2),
        "profil": "".join("▁▂▃▄▅▆▇█"[min(7, max(0, int((v + 45) / 4)))] for v in niveaux),
    }


def brillance(fichier) -> dict:
    """Pour les effets : un son qui pique a beaucoup d'energie au-dessus de 6 kHz."""
    x = B.pcm(fichier, sr=44100)
    n = 2048
    nf = len(x) // n
    if nf < 2:
        return {}
    S = np.abs(np.fft.rfft(x[:nf * n].reshape(nf, n) * np.hanning(n), axis=1))
    fr = np.fft.rfftfreq(n, 1 / 44100)
    return {
        "centroide_hz": int((S * fr).sum() / max(S.sum(), 1e-9)),
        "aigus_pct": round(float(S[:, fr > 6000].sum() / max(S.sum(), 1e-9) * 100), 1),
        "crete": round(float(np.abs(x).max()), 2),
    }


def suggerer(registre: str = "sobre") -> list[dict]:
    """Classe les lits disponibles selon le registre vise."""
    cibles = {
        # nappe qui avance, facon lit d'actualite moderne
        "news": {"attaques": (1.5, 4.5), "centroide": (1000, 2900)},
        # plus grave et plus distant, pour les sujets lourds
        "sobre": {"attaques": (0.4, 2.5), "centroide": (500, 1600)},
    }[registre]
    res = []
    for p in manifeste()["musiques"]:
        f = C.AUDIO / p["fichier"]
        if not f.exists():
            continue
        m = p.get("mesures") or profil(f)
        if not m:
            continue
        s = max(0, 6 - m["amplitude_db"])
        s += 4 if cibles["attaques"][0] <= m["attaques_par_s"] <= cibles["attaques"][1] else 0
        s += 4 if cibles["centroide"][0] <= m["centroide_hz"] <= cibles["centroide"][1] else 0
        res.append({**p, "mesures": m, "score": round(s, 1)})
    return sorted(res, key=lambda x: -x["score"])
