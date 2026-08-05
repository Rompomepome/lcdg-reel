"""
Controles automatiques sur le fichier de sortie.

Ils existent a cause d'un bug reel : une valeur codee en dur dans le script de rendu
ecrasait la taille du logo definie dans la charte. L'apercu montrait la bonne taille,
la video non, et l'erreur a survecu a quatre corrections. On ne verifie donc plus
sur un apercu, mais par mesure de pixels sur le fichier livre.
"""
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import charte as C
from lcdg import binaires as B


def _frame(video: Path, t: float) -> Image.Image | None:
    tmp = video.parent / f"_ctrl_{int(t*100)}.png"
    B.run(["-ss", str(t), "-i", str(video), "-frames:v", "1", str(tmp), "-y"])
    if not tmp.exists():
        return None
    im = Image.open(tmp).copy()
    tmp.unlink(missing_ok=True)
    return im


def _instants(video: Path, n: int = 4) -> list[float]:
    """Points de mesure repartis dans la zone qui porte du texte.

    On evite l'intro (bandeau centre) et l'outro (fond navy), et surtout on cale
    sur la duree reelle : des instants codes en dur cassent sur une video courte.
    """
    d = B.duree(video)
    debut = min(4.6, d * 0.30)   # apres l'intro, qui n'a pas de filet
    fin = max(debut + 0.5, d - (C.CROIX_DUREE + C.OUTRO_DUREE + 1.0))
    if fin <= debut:
        debut, fin = d * 0.25, d * 0.75
    pas = (fin - debut) / max(1, n - 1)
    return [round(debut + i * pas, 2) for i in range(n)]


def mesurer_logo(video: Path, instants=None) -> tuple[int, int]:
    """Intersection des zones claires sur plusieurs plans.

    Mesurer sur une seule image est piegeux : un ciel ou une blouse dans le coin
    superieur droit se fait compter comme du logo. Le logo, lui, est le seul element
    clair present au meme endroit sur TOUS les plans.
    """
    commun = None
    for t in (instants or _instants(video, 4)):
        im = _frame(video, t)
        if im is None:
            continue
        g = np.array(im.convert("L")).astype(float)
        masque = g[10:C.LOGO_PX + 160, C.LARGEUR // 2:] > 200
        commun = masque if commun is None else (commun & masque)
    if commun is None:
        return (0, 0)
    ys, xs = np.where(commun)
    if not len(ys):
        return (0, 0)
    return int(ys.max() - ys.min() + 1), int(xs.max() - xs.min() + 1)


def mesurer_filet(video: Path, instants=None) -> int:
    """Mediane sur plusieurs plans : un fond clair fausserait une mesure isolee."""
    largeurs = []
    for t in (instants or _instants(video, 3)):
        im = _frame(video, t)
        if im is None:
            continue
        a = np.array(im.convert("RGB")).astype(int)
        # fenetre calee sur les deux premieres lignes : un bloc court a un filet court
        bande = a[C.BLOC_Y + 10:C.BLOC_Y + 70, 60:200]
        plein = [(bande[:, i].min(axis=1) > 215).mean() > 0.9
                 for i in range(bande.shape[1])]
        # plus longue suite de colonnes pleines
        run = best = 0
        for p in plein:
            run = run + 1 if p else 0
            best = max(best, run)
        # un fond blanc donnerait une suite bien plus large que le filet attendu
        if best <= C.FILET_PX * 3:
            largeurs.append(best)
    return max(largeurs) if largeurs else 0


def mesurer_audio(video: Path) -> dict:
    r = subprocess.run([B.FFMPEG, "-hide_banner", "-i", str(video), "-af",
                        f"loudnorm=I={C.LUFS_CIBLE}:TP=-1.5:print_format=summary",
                        "-f", "null", "-"], capture_output=True, text=True)
    out = {}
    for ligne in r.stderr.splitlines():
        if "Input Integrated" in ligne:
            out["lufs"] = float(ligne.split(":")[1].replace("LUFS", "").strip())
        if "Input True Peak" in ligne:
            out["true_peak"] = float(ligne.split(":")[1].replace("dBTP", "").strip())
    x = B.pcm(video, sr=48000)
    out["crete"] = round(float(np.abs(x).max()), 3)
    return out


def rapport(video: Path) -> bool:
    """Affiche le bilan et retourne True si tout est conforme."""
    lh, _ = mesurer_logo(video)
    fi = mesurer_filet(video)
    au = mesurer_audio(video)
    lignes, ok = [], True

    def check(nom, valeur, attendu, tol, unite=""):
        nonlocal ok
        bon = abs(valeur - attendu) <= tol
        ok = ok and bon
        lignes.append(f"  {'OK ' if bon else 'ECHEC'}  {nom:22} {valeur}{unite} "
                      f"(attendu {attendu}{unite} ±{tol})")

    check("logo (hauteur)", lh, C.LOGO_PX, 8, " px")
    check("filet (largeur)", fi, C.FILET_PX, 3, " px")
    check("loudness", au.get("lufs", 0), C.LUFS_CIBLE, 1.5, " LUFS")
    check("true peak", au.get("true_peak", 0), -2.0, 1.5, " dBTP")

    ecr = au["crete"] >= 1.0
    ok = ok and not ecr
    lignes.append(f"  {'ECHEC' if ecr else 'OK '}  {'ecretage':22} "
                  f"crete {au['crete']}")

    print("\nControles sur le fichier livre :")
    print("\n".join(lignes))
    print("  ->", "conforme" if ok else "NON CONFORME, ne pas publier en l'etat")
    return ok
