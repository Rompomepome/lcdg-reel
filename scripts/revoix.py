"""
Corriger une phrase d'un reel deja valide sans relire toute la narration.

    python scripts/revoix.py episodes/<dossier> [--avant <revision git>] [--essai]

voix.py genere la narration entiere d'un seul appel : changer une phrase la regenere toute,
consomme le quota pour l'ensemble et remplace une lecture deja validee. Ici, chaque groupe
de blocs dont le texte lu a change est relu seul, encadre de la phrase qui le precede et de
celle qui le suit pour que l'intonation s'enchaine. Seule sa partie neuve est gardee : elle
est collee dans l'ancienne narration, au silence entre deux phrases, au niveau sonore de
l'ancienne lecture (mesure sur les phrases d'encadrement, lues dans les deux prises). Le
resultat entre dans le cache de voix.py sous la cle du nouveau texte : render.py et
render_carre.py le reprennent comme une narration ordinaire.

L'ancienne narration est celle du script.json de la revision --avant (HEAD par defaut) ;
elle doit se trouver dans le cache. Les prises partielles sont gardees dans
episodes/<dossier>/voix/raccords/ : relancer ne les repaie pas. --essai affiche ce qui
serait relu et le quota consomme, sans appeler ElevenLabs. A lancer apres avoir modifie le
champ "voix" des blocs, avant de rendre le reel.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

# la console Windows est en cp1252 par defaut : les accents y provoqueraient une
# UnicodeEncodeError.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

R = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(R))
try:
    from dotenv import load_dotenv
    load_dotenv(R / ".env")
except ImportError:
    pass
from config import charte as C
from lcdg import binaires as B, voix

TAUX = 44100                      # Hz : frequence de travail (celle des mp3 d'ElevenLabs)
INDICATION = re.compile(r"\[[^\]]*\]")   # indication de jeu v3, non prononcee


def _ancien(episode: Path, rev: str) -> dict:
    """Le script.json de l'episode a la revision git rev."""
    try:
        rel = (episode / "script.json").relative_to(R).as_posix()
    except ValueError:
        raise SystemExit(f"[!] {episode} n'est pas dans le depot {R}.")
    r = subprocess.run(["git", "show", f"{rev}:{rel}"], cwd=R, capture_output=True)
    if r.returncode:
        raise SystemExit(f"[!] git show {rev}:{rel} : {r.stderr.decode('utf-8', 'replace').strip()}")
    return json.loads(r.stdout.decode("utf-8"))


def _pcm(fichier: Path) -> np.ndarray:
    """Le son du fichier, mono, en flottants a TAUX."""
    B.exiger()
    r = subprocess.run([B.FFMPEG, "-v", "error", "-i", str(fichier), "-f", "f32le", "-ac", "1",
                        "-ar", str(TAUX), "-"], capture_output=True)
    if r.returncode:
        raise RuntimeError(f"ffmpeg n'a pas pu lire {fichier} :\n"
                           f"{r.stderr.decode('utf-8', 'replace')[-600:]}")
    return np.frombuffer(r.stdout, dtype="<f4").copy()


def _ecrire_mp3(son: np.ndarray, sortie: Path):
    B.exiger()
    r = subprocess.run([B.FFMPEG, "-v", "error", "-f", "f32le", "-ar", str(TAUX), "-ac", "1",
                        "-i", "-", "-c:a", "libmp3lame", "-b:a", "192k", "-f", "mp3",
                        str(sortie), "-y"],
                       input=son.astype("<f4").tobytes(), capture_output=True)
    if r.returncode:
        raise RuntimeError(f"ffmpeg n'a pas pu ecrire {sortie} :\n"
                           f"{r.stderr.decode('utf-8', 'replace')[-600:]}")


def _positions(lus: list[str]) -> list[int]:
    """Debut de chaque texte dans la narration (les textes y sont joints par une espace)."""
    pos, debuts = 0, []
    for t in lus:
        debuts.append(pos)
        pos += len(t) + 1
    return debuts


def _prononces(texte: str) -> list[int]:
    """Indices des caracteres prononces : ni espace, ni indication de jeu entre crochets."""
    muets = set()
    for m in INDICATION.finditer(texte):
        muets.update(range(m.start(), m.end()))
    return [i for i, c in enumerate(texte) if i not in muets and not c.isspace()]


def _parole(al: dict, debut: int, texte: str) -> tuple[float, float]:
    """(debut, fin) de la parole d'un bloc, en secondes dans sa prise."""
    idx = _prononces(texte)
    if not idx:
        raise SystemExit(f"[!] texte lu sans parole : « {texte} »")
    return (al["character_start_times_seconds"][debut + idx[0]],
            al["character_end_times_seconds"][debut + idx[-1]])


def _raccord(son: np.ndarray, fin_a: float, debut_b: float) -> float:
    """Instant du raccord entre deux phrases : le point le plus calme du blanc qui les separe."""
    a, b = fin_a + C.VOIX_RACCORD_GARDE, debut_b - C.VOIX_RACCORD_GARDE
    n = max(1, int(C.VOIX_RACCORD_PAS * TAUX))
    i0, i1 = int(a * TAUX), min(int(b * TAUX), len(son))
    if i1 - i0 < 2 * n:
        print(f"[!] pas de vrai blanc entre {fin_a:.2f} s et {debut_b:.2f} s : raccord au milieu, "
              "a reecouter.")
        return (fin_a + debut_b) / 2
    fenetres = son[i0:i1 - (i1 - i0) % n].reshape(-1, n)
    k = int(np.argmin((fenetres ** 2).mean(axis=1)))
    return (i0 + k * n + n // 2) / TAUX


def _niveau(son: np.ndarray, t0: float, t1: float) -> float:
    """Niveau moyen (dB) d'un passage."""
    morceau = son[int(t0 * TAUX):int(t1 * TAUX)]
    return 10 * np.log10(float(np.mean(morceau ** 2)) + 1e-12)


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("episode", help="episodes/<dossier>")
    ap.add_argument("--avant", default="HEAD", help="revision git du texte deja lu (HEAD)")
    ap.add_argument("--essai", action="store_true",
                    help="affiche ce qui serait relu, sans appeler ElevenLabs")
    args = ap.parse_args()

    episode = Path(args.episode).resolve()
    neuf = json.loads((episode / "script.json").read_text(encoding="utf-8"))
    vieux = _ancien(episode, args.avant)
    muet_n, morceaux_n = voix.textes(neuf)
    muet_v, morceaux_v = voix.textes(vieux)
    v = voix.choix(neuf)
    if v != voix.choix(vieux):
        raise SystemExit("[!] La voix (voix_off) a change : toute la narration est a relire "
                         "(render.py la regenere).")
    if muet_n != muet_v or len(morceaux_n) != len(morceaux_v):
        raise SystemExit("[!] Les blocs lus ne sont plus les memes (ajout, retrait, voix du "
                         "bloc 0) : toute la narration est a relire (render.py la regenere).")
    tn = [t for t, _ in morceaux_n]
    tv = [t for t, _ in morceaux_v]
    if not all(tn):
        raise SystemExit("[!] Bloc(s) sans texte lu : "
                         + ", ".join(str(k + muet_n) for k, t in enumerate(tn) if not t))
    nb = len(tn)
    modifies = [k for k in range(nb) if tn[k] != tv[k]]
    if not modifies:
        print("[i] Aucun texte lu n'a change depuis " + args.avant + " : rien a relire.")
        return

    vid, modele, reglages = v.get("id") or C.VOIX_ID, v.get("modele"), v.get("reglages")
    dossier = episode / "voix"
    mp3_n, js_n = voix.chemins(" ".join(tn), vid, dossier, modele, reglages)
    if mp3_n.exists() and js_n.exists():
        print("[i] Cette narration est deja dans le cache : rien a relire.")
        return
    mp3_v, js_v = voix.chemins(" ".join(tv), vid, dossier, modele, reglages)
    if not (mp3_v.exists() and js_v.exists()):
        raise SystemExit(f"[!] L'ancienne narration (texte de {args.avant}) n'est pas dans le "
                         f"cache {dossier} : rien a quoi raccorder. render.py relira tout.")

    # blocs modifies consecutifs : relus ensemble
    groupes: list[list[int]] = []
    for k in modifies:
        if groupes and k == groupes[-1][-1] + 1:
            groupes[-1].append(k)
        else:
            groupes.append([k])
    relectures = []
    for g in groupes:
        i, j = g[0], g[-1]
        avant = [tv[i - 1]] if i > 0 else []          # voisins inchanges : tv == tn
        apres = [tv[j + 1]] if j + 1 < nb else []
        relectures.append((i, j, avant, tn[i:j + 1], apres))
    quota = sum(len(" ".join(a + m + p)) for _, _, a, m, p in relectures)
    blocs = ", ".join(str(k + muet_n) for k in modifies)
    print(f"[i] Blocs a relire : {blocs} ({len(relectures)} appel(s), {quota} caracteres du quota)")
    if args.essai:
        for i, j, a, m, p in relectures:
            print("    « " + " ".join(a + m + p) + " »")
        return

    al_v = json.loads(js_v.read_text(encoding="utf-8"))
    if "".join(al_v["characters"]) != " ".join(tv):
        raise SystemExit(f"[!] {js_v.name} ne correspond pas au texte de {args.avant}.")
    son_v = _pcm(mp3_v)
    pos_v = _positions(tv)
    parole_v = [_parole(al_v, pos_v[k], tv[k]) for k in range(nb)]

    def coupe_v(k):                   # raccord entre les anciens blocs k-1 et k
        return _raccord(son_v, parole_v[k - 1][1], parole_v[k][0])

    # morceaux de la nouvelle narration, dans l'ordre : (son, debut, fin, gain dB,
    # [(bloc, alignement de la prise, position du texte du bloc dans la prise)])
    morceaux, t, dernier = [], 0.0, -1
    for i, j, avant, lus, apres in relectures:
        if i > 0:
            morceaux.append((son_v, t, coupe_v(i), 0.0,
                             [(k, al_v, pos_v[k]) for k in range(dernier + 1, i)]))
        prise = avant + lus + apres
        mp3_g, al_g = voix.synthese(" ".join(prise), vid, dossier / "raccords", modele, reglages)
        son_g = _pcm(mp3_g)
        pos_g = _positions(prise)
        parole_g = [_parole(al_g, pos_g[m], prise[m]) for m in range(len(prise))]
        d, f = len(avant), len(avant) + j - i          # premier et dernier bloc neufs
        debut = _raccord(son_g, parole_g[d - 1][1], parole_g[d][0]) if avant else 0.0
        fin = _raccord(son_g, parole_g[f][1], parole_g[f + 1][0]) if apres else len(son_g) / TAUX
        ecarts = []
        if avant:
            ecarts.append(_niveau(son_v, *parole_v[i - 1]) - _niveau(son_g, *parole_g[0]))
        if apres:
            ecarts.append(_niveau(son_v, *parole_v[j + 1]) - _niveau(son_g, *parole_g[f + 1]))
        gain = float(np.mean(ecarts)) if ecarts else 0.0
        if abs(gain) > C.VOIX_RACCORD_ECART_MAX:
            raise SystemExit(f"[!] Blocs {i + muet_n}-{j + muet_n} : la nouvelle prise est a "
                             f"{gain:+.1f} dB de l'ancienne. Les deux lectures sont trop "
                             f"differentes pour etre raccordees. Pour une autre prise, supprime "
                             f"{mp3_g} et {mp3_g.with_suffix('.json')} puis relance ; sinon, "
                             "laisse render.py relire toute la narration.")
        print(f"    blocs {i + muet_n}-{j + muet_n} : {fin - debut:.2f} s de nouvelle lecture, "
              f"niveau ajuste de {gain:+.1f} dB")
        morceaux.append((son_g, debut, fin, gain,
                         [(k, al_g, pos_g[d + k - i]) for k in range(i, j + 1)]))
        t, dernier = (coupe_v(j + 1) if j + 1 < nb else len(son_v) / TAUX), j
    if dernier + 1 < nb:
        morceaux.append((son_v, t, len(son_v) / TAUX, 0.0,
                         [(k, al_v, pos_v[k]) for k in range(dernier + 1, nb)]))

    # assemblage, a l'echantillon pres ; l'horodatage de chaque bloc suit son morceau
    fondu = int(C.VOIX_RACCORD_FONDU * TAUX)
    sons, n, temps = [], 0, {}
    for m, (son, t0, t1, gain, contenus) in enumerate(morceaux):
        i0, i1 = int(round(t0 * TAUX)), int(round(t1 * TAUX))
        morceau = son[i0:i1] * np.float32(10 ** (gain / 20))
        if m > 0:
            morceau[:fondu] *= np.linspace(0, 1, min(fondu, len(morceau)), dtype=np.float32)
        if m < len(morceaux) - 1:
            morceau[-fondu:] *= np.linspace(1, 0, min(fondu, len(morceau)), dtype=np.float32)
        decalage = (n - i0) / TAUX
        # seuls les raccords bornent la parole : aux deux bouts de la narration, l'horodatage
        # d'ElevenLabs peut deborder du son de quelques millisecondes
        borne0 = n / TAUX if m > 0 else -np.inf
        borne1 = (n + len(morceau)) / TAUX if m < len(morceaux) - 1 else np.inf
        for k, al, pos in contenus:
            plage = range(pos, pos + len(tn[k]))
            temps[k] = ([al["character_start_times_seconds"][q] + decalage for q in plage],
                        [al["character_end_times_seconds"][q] + decalage for q in plage])
            p0, p1 = (temps[k][0][_prononces(tn[k])[0]], temps[k][1][_prononces(tn[k])[-1]])
            if p0 < borne0 or p1 > borne1:
                raise SystemExit(f"[!] Bloc {k + muet_n} : sa parole deborde de son morceau "
                                 f"({p0:.2f}-{p1:.2f} s) : raccord mal place, rien n'est ecrit.")
        sons.append(morceau)
        n += len(morceau)

    caracteres, debuts, fins = [], [], []
    for k in range(nb):
        st, en = temps[k]
        caracteres += list(tn[k])
        debuts += st
        fins += en
        if k < nb - 1:                # l'espace entre deux blocs : le blanc qui les separe
            caracteres.append(" ")
            debuts.append(en[-1])
            fins.append(max(en[-1], temps[k + 1][0][0]))
    if "".join(caracteres) != " ".join(tn):
        raise SystemExit("[!] Horodatage reconstitue incoherent : rien n'est ecrit.")

    # ecriture atomique : voix.synthese ne lit le cache que si les deux fichiers existent
    provisoire_mp3 = mp3_n.with_name(mp3_n.stem + ".tmp.mp3")
    provisoire_js = js_n.with_name(js_n.stem + ".tmp.json")
    _ecrire_mp3(np.concatenate(sons), provisoire_mp3)
    provisoire_js.write_text(json.dumps({
        "characters": caracteres,
        "character_start_times_seconds": [round(x, 4) for x in debuts],
        "character_end_times_seconds": [round(x, 4) for x in fins],
    }, ensure_ascii=False), encoding="utf-8")
    os.replace(provisoire_mp3, mp3_n)
    os.replace(provisoire_js, js_n)
    print(f"[i] Narration : {len(son_v) / TAUX:.2f} s -> {n / TAUX:.2f} s, en cache sous "
          f"{mp3_n.stem}.\n    Rends ensuite le reel : python scripts/render.py {args.episode}"
          f" puis python scripts/render_carre.py {args.episode}")


if __name__ == "__main__":
    main()
