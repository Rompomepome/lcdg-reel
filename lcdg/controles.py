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
from lcdg import habillage as hb
from lcdg import son


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
    """Nombre de pistes audio du fichier livre : une avec la voix off, aucune sinon."""
    sortie = B.probe(video, "stream=codec_type")
    return sum(1 for ligne in sortie.splitlines() if ligne.strip() == "audio")


def mesurer_voix(video: Path) -> dict:
    """Loudness integree et true peak de la piste audio (la voix seule)."""
    r = subprocess.run([B.FFMPEG, "-hide_banner", "-i", str(video), "-af",
                        f"loudnorm=I={C.VOIX_LUFS}:TP={C.VOIX_TP_CIBLE}:print_format=summary",
                        "-f", "null", "-"], capture_output=True, text=True)
    out = {}
    for ligne in r.stderr.splitlines():
        if "Input Integrated" in ligne:
            out["lufs"] = float(ligne.split(":")[1].replace("LUFS", "").strip())
        if "Input True Peak" in ligne:
            out["tp"] = float(ligne.split(":")[1].replace("dBTP", "").strip())
    return out


def _temps_surlignes(ep: dict, bornes: list) -> list:
    """[(nom, texte anime, bande de l'image)] des temps de texte qui portent un surlignage :
    l'accroche, chaque temps d'un bloc, la legende d'un chiffre. Instants et positions
    viennent des scenes de l'habillage : le controle suit ce qui a ete dessine."""
    hb.rubrique(ep.get("rubrique"))
    blocs = ep["blocs"]
    croix = bornes[-1][0] + blocs[-1]["duree"]
    bande_bloc = slice(C.BLOC_Y, C.BLOC_Y + 4 * C.BLOC_INTERLIGNE)
    demi = 2 * C.ACCROCHE_INTERLIGNE
    bande_phrase = slice(C.ACCROCHE_CENTRE - demi, C.ACCROCHE_CENTRE + demi)
    out = []
    for k, sc in enumerate(hb.scenes(ep, bornes, croix)):
        if isinstance(sc, hb.Accroche):
            st, n = hb.style_ajuste(ep["sous_titre"])
            haut = sc.y + C.SURTITRE_H + C.SURTITRE_ECART
            out.append(("accroche", sc.texte,
                        slice(haut, haut + n * st["interligne"] + C.SURLIGNE_MARGE)))
        elif isinstance(sc, hb.Chiffre):
            out.append((f"bloc {k}", sc.legende, bande_bloc))
        else:
            for i, part in enumerate(sc.parts):
                nom = f"bloc {k}" + (f" (temps {i + 1})" if len(sc.parts) > 1 else "")
                out.append((nom, part, bande_phrase if sc.grand else bande_bloc))
    return [(nom, cine, bande) for nom, cine, bande in out if cine.marques]


def _proches(im: Image.Image, bande: slice, couleur) -> int:
    """Pixels de la couleur du surlignage dans la bande, colonne de texte comprise."""
    colonne = slice(max(0, C.TEXTE_X - C.SURLIGNE_MARGE),
                    C.TEXTE_X + C.TEXTE_LARGEUR + C.SURLIGNE_MARGE)
    a = np.array(im.convert("RGB")).astype(int)[bande, colonne]
    return int((np.abs(a - couleur).sum(axis=2) < C.SURLIGNE_CONTROLE_ECART).sum())


def mesurer_surlignages(video: Path, ep: dict, bornes: list, decalage: float = 0.0,
                        couverture: Path | None = None) -> tuple[int, list]:
    """(temps controles, temps ou le surlignage manque).

    Le controle du texte sur le fichier livre : pour chaque temps qui porte un surlignage,
    on cherche la couleur de la rubrique dans la bande ou ce texte est pose, juste avant sa
    sortie. Un texte decale, mal colore ou absent fait echouer le temps. decalage : debut
    du fichier livre dans le montage (l'accroche coupee) ; ce qui le precede se controle
    sur l'image de couverture."""
    couleur = np.array(C.RUBRIQUES.get(ep.get("rubrique") or "pro", C.PRIMARY))
    n, manques = 0, []
    for nom, cine, bande in _temps_surlignes(ep, bornes):
        t = max(cine.debut, cine.fin - C.SORTIE_DUREE - 0.1)
        if t < decalage:
            if not (couverture and Path(couverture).exists()):
                continue
            im = Image.open(couverture)
        else:
            im = _frame(video, t - decalage)
        if im is None:
            continue
        n += 1
        proches = _proches(im, bande, couleur)
        if proches < C.SURLIGNE_CONTROLE_MIN:
            manques.append(f"{nom} ({proches} px)")
    return n, manques


def rapport(video: Path, ep: dict | None = None, bornes: list | None = None,
            decalage: float = 0.0, couverture: Path | None = None) -> bool:
    """Affiche le bilan et retourne True si tout est conforme. Avec le script et les
    bornes des plans, controle aussi la duree et le texte (surlignages) du fichier livre.
    decalage : debut du fichier livre dans le montage, quand l'accroche a ete coupee ; elle
    se controle alors sur la couverture."""
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
    avec_voix = ep is not None and any((bl.get("voix") or "").strip() for bl in ep["blocs"])
    avec_fond = ep is not None and son.musique(ep) is not None
    check("pistes audio", pa, 1 if (avec_voix or avec_fond) else 0, 0)
    if avec_voix or avec_fond:
        # voix seule : -16 LUFS ; avec la musique et les bruitages, le mixage vise -14
        cible, plafond = (C.SON_LUFS, C.SON_TP_PLAFOND) if avec_fond else (C.VOIX_LUFS, C.VOIX_TP_PLAFOND)
        mv = mesurer_voix(video)
        check("son (loudness)", mv.get("lufs", 0), cible, C.VOIX_LUFS_TOLERANCE, " LUFS")
        tp = mv.get("tp", 0)
        bon = tp <= plafond
        ok = ok and bon
        lignes.append(f"  {'OK ' if bon else 'ECHEC'}  {'son (true peak)':22} {tp} dBTP "
                      f"(plafond {plafond} dBTP)")
    if ep is not None and bornes:
        check("duree", round(B.duree(video), 2), round(bornes[-1][1] - decalage, 2), 0.1, " s")
        n, manques = mesurer_surlignages(video, ep, bornes, decalage, couverture)
        bon = not manques
        ok = ok and bon
        lignes.append(f"  {'OK ' if bon else 'ECHEC'}  {'surlignages':22} {n - len(manques)}/{n}"
                      + (f" — absents : {', '.join(manques)}" if manques else ""))

    print("\nControles sur le fichier livre :")
    print("\n".join(lignes))
    print("  ->", "conforme" if ok else "NON CONFORME, ne pas publier en l'etat")
    return ok
