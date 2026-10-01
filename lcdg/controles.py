"""
Controles automatiques sur le fichier de sortie.

Ils existent a cause d'un bug reel : une valeur codee en dur dans le script de rendu
ecrasait la taille du logo definie dans la charte. L'apercu montrait la bonne taille,
la video non, et l'erreur a survecu a quatre corrections. On ne verifie donc plus
sur un apercu, mais par mesure de pixels sur le fichier livre.
"""
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

    On evite l'accroche et l'outro (fond navy), et surtout on cale sur la duree
    reelle : des instants codes en dur cassent sur une video courte.
    """
    d = B.duree(video)
    debut = min(4.6, d * 0.30)   # apres l'accroche
    fin = max(debut + 0.5, d - (C.CROIX_DUREE + C.OUTRO_DUREE + 1.0))
    if fin <= debut:
        debut, fin = d * 0.25, d * 0.75
    pas = (fin - debut) / max(1, n - 1)
    return [round(debut + i * pas, 2) for i in range(n)]


def mesurer_logo(video: Path, instants=None) -> tuple[int, int, int]:
    """Intersection des zones claires sur plusieurs plans.

    Mesurer sur une seule image est piegeux : un ciel ou une blouse dans le coin
    superieur droit se fait compter comme du logo. Le logo, lui, est le seul element
    clair present au meme endroit sur TOUS les plans.

    Retourne (hauteur, largeur, ordonnee du haut) en pixels de l'image.
    """
    haut = max(0, C.LOGO_Y - 34)
    commun = None
    for t in (instants or _instants(video, 4)):
        im = _frame(video, t)
        if im is None:
            continue
        g = np.array(im.convert("L")).astype(float)
        masque = g[haut:C.LOGO_Y + C.LOGO_PX + 116, C.LARGEUR // 2:] > 200
        commun = masque if commun is None else (commun & masque)
    if commun is None:
        return (0, 0, 0)
    ys, xs = np.where(commun)
    if not len(ys):
        return (0, 0, 0)
    return int(ys.max() - ys.min() + 1), int(xs.max() - xs.min() + 1), haut + int(ys.min())


def mesurer_hors_zone(video: Path) -> int:
    """Pixels clairs hors de la zone sure 4:5 sur la carte finale.

    La carte est un aplat navy : au-dessus et en dessous de la zone sure, tout pixel
    clair est un element (logo, slogan, mention) qui serait coupe dans le fil.
    """
    im = _frame(video, max(0.0, B.duree(video) - 0.2))
    if im is None:
        return -1
    g = np.array(im.convert("L"))
    dehors = np.concatenate([g[:C.ZONE_SURE_HAUT].ravel(), g[C.ZONE_SURE_BAS:].ravel()])
    return int((dehors > 90).sum())


def pistes_audio(video: Path) -> int:
    """Nombre de pistes audio du fichier livre : il doit sortir muet."""
    sortie = B.probe(video, "stream=codec_type")
    return sum(1 for ligne in sortie.splitlines() if ligne.strip() == "audio")


def mesurer_surlignages(video: Path, ep: dict, bornes: list) -> tuple[int, list]:
    """(blocs controles, blocs ou le surlignage manque).

    Remplace la mesure du filet du style v1 : c'est le controle du texte sur le fichier
    livre. Pour chaque bloc dont le dernier temps porte un surlignage, on cherche la
    couleur de la rubrique dans la bande ou ce texte doit etre pose, juste avant sa
    sortie. Un texte decale, mal colore ou absent fait echouer le bloc."""
    couleur = np.array(C.RUBRIQUES.get(ep.get("rubrique") or "pro", C.PRIMARY))
    blocs = ep["blocs"]
    croix = bornes[-1][0] + blocs[-1]["duree"]
    colonne = slice(max(0, C.TEXTE_X - C.SURLIGNE_MARGE),
                    C.TEXTE_X + C.TEXTE_LARGEUR + C.SURLIGNE_MARGE)
    n, manques = 0, []
    for k in range(1, len(blocs)):
        bl = blocs[k]
        texte = (bl.get("legende") if bl.get("type") == "chiffre" else bl.get("texte")) or ""
        if "*" not in texte.split("|")[-1]:
            continue
        fin = croix + C.BLOC_RESIDU if k == len(blocs) - 1 else bornes[k][1]
        im = _frame(video, max(bornes[k][0], fin - C.SORTIE_DUREE - 0.1))
        if im is None:
            continue
        if bl.get("type") == "phrase":
            demi = 2 * C.ACCROCHE_INTERLIGNE
            bande = slice(C.ACCROCHE_CENTRE - demi, C.ACCROCHE_CENTRE + demi)
        else:
            bande = slice(C.BLOC_Y, C.BLOC_Y + 4 * C.BLOC_INTERLIGNE)
        a = np.array(im.convert("RGB")).astype(int)[bande, colonne]
        proches = int((np.abs(a - couleur).sum(axis=2) < C.SURLIGNE_CONTROLE_ECART).sum())
        n += 1
        if proches < C.SURLIGNE_CONTROLE_MIN:
            manques.append(f"bloc {k} ({proches} px)")
    return n, manques


def rapport(video: Path, ep: dict | None = None, bornes: list | None = None) -> bool:
    """Affiche le bilan et retourne True si tout est conforme. Avec le script et les
    bornes des plans, controle aussi le texte (surlignages) sur le fichier livre."""
    lh, _, ly = mesurer_logo(video)
    hz = mesurer_hors_zone(video)
    pa = pistes_audio(video)
    lignes, ok = [], True

    def check(nom, valeur, attendu, tol, unite=""):
        nonlocal ok
        bon = abs(valeur - attendu) <= tol
        ok = ok and bon
        lignes.append(f"  {'OK ' if bon else 'ECHEC'}  {nom:22} {valeur}{unite} "
                      f"(attendu {attendu}{unite} ±{tol})")

    check("logo (hauteur)", lh, C.LOGO_PX, 8, " px")
    check("logo (position)", ly, C.LOGO_Y, 8, " px")
    check("hors zone 4:5 (fin)", hz, 0, 0, " px")
    check("pistes audio", pa, 0, 0)
    if ep is not None and bornes:
        n, manques = mesurer_surlignages(video, ep, bornes)
        bon = not manques
        ok = ok and bon
        lignes.append(f"  {'OK ' if bon else 'ECHEC'}  {'surlignages':22} {n - len(manques)}/{n}"
                      + (f" — absents : {', '.join(manques)}" if manques else ""))

    print("\nControles sur le fichier livre :")
    print("\n".join(lignes))
    print("  ->", "conforme" if ok else "NON CONFORME, ne pas publier en l'etat")
    return ok
