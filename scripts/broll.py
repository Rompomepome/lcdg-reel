"""
Revue des B-rolls d'un episode : chercher des candidats, choisir un plan, controler.

    python scripts/broll.py chercher episodes/<dossier> <bloc> "<requete>" ["<requete>" ...]
    python scripts/broll.py choisir  episodes/<dossier> <bloc> C<n>
    python scripts/broll.py revue    episodes/<dossier>
    python scripts/broll.py doublons

chercher : planche des candidats Pexels de toutes les requetes (broll/candidats/<bloc>.jpg),
           recadres comme au montage ; un plan deja utilise ailleurs est marque en rouge.
choisir  : telecharge le candidat n en broll/B<bloc>.mp4 et l'inscrit au registre
           (episodes/plans_utilises.json). Refuse un plan deja pris dans un autre bloc.
revue    : planche de controle revue_plans.jpg : debut, milieu et fin de la portion
           utilisee de chaque plan, recadres comme au montage, avec le texte du bloc.
           C'est elle qu'on regarde avant de lancer render : une vignette Pexels ment
           souvent sur ce que montre le plan deux secondes plus tard.
doublons : plans utilises par plusieurs blocs, tous episodes confondus.
"""
import sys
# la console Windows est en cp1252 par defaut : les accents y provoqueraient une
# UnicodeEncodeError.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import io
import json
import subprocess
from pathlib import Path

import requests
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass
from config import charte as C
from lcdg import binaires as B, pexels, registre
from lcdg.logo import police

TW, TH = 180, 320          # vignettes au format 9:16


def _ep(dossier):
    episode = Path(dossier).resolve()
    return episode, json.loads((episode / "script.json").read_text(encoding="utf-8"))


def _texte(ep, bl):
    return (bl.get("texte") or bl.get("legende") or ep.get("sous_titre") or "").replace(
        "*", "").replace("|", "/")


def recadrer(im: Image.Image) -> Image.Image:
    """Meme logique que le montage : remplir le cadre puis couper au centre."""
    r = max(TW / im.width, TH / im.height)
    im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1))
    x, y = (im.width - TW) // 2, (im.height - TH) // 2
    return im.crop((x, y, x + TW, y + TH))


def apercu(url: str) -> Image.Image | None:
    try:
        return recadrer(Image.open(io.BytesIO(requests.get(url, timeout=30).content)).convert("RGB"))
    except Exception:
        return None


def image_video(src: Path, t: float) -> Image.Image | None:
    vf = (f"scale={C.LARGEUR}:{C.HAUTEUR}:force_original_aspect_ratio=increase,"
          f"crop={C.LARGEUR}:{C.HAUTEUR},scale={TW}:{TH}")
    r = subprocess.run([B.FFMPEG, "-v", "error", "-ss", f"{t:.2f}", "-i", str(src),
                        "-frames:v", "1", "-vf", vf, "-f", "image2pipe", "-vcodec", "png", "-"],
                       capture_output=True)
    return Image.open(io.BytesIO(r.stdout)).convert("RGB") if r.stdout else None


def chercher(dossier, bloc, requetes):
    episode, ep = _ep(dossier)
    bl = ep["blocs"][bloc]
    vus, cands = set(), []
    for q in requetes:
        for c in pexels.chercher(q, n=8, duree_min=max(6, int(bl["duree"]) + 2)):
            if c["id"] not in vus:
                vus.add(c["id"]); c["requete"] = q; cands.append(c)
    dest = episode / "broll" / "candidats"
    dest.mkdir(parents=True, exist_ok=True)
    (dest / f"{bloc}.json").write_text(json.dumps(cands, ensure_ascii=False, indent=1),
                                       encoding="utf-8")
    pris = registre.ids_utilises(sauf=f"{episode.name}/{bloc}")
    cols, f, fs = 6, police(18, "SemiBold"), police(15, "Medium")
    lignes = (len(cands) + cols - 1) // cols
    feuille = Image.new("RGB", (cols * (TW + 6) + 10, lignes * (TH + 50) + 50), (240, 240, 244))
    d = ImageDraw.Draw(feuille)
    d.text((10, 10), f"[{bloc}] " + _texte(ep, bl)[:95], font=f, fill=(0, 0, 0))
    for k, c in enumerate(cands):
        x, y = 10 + (k % cols) * (TW + 6), 45 + (k // cols) * (TH + 50)
        im = apercu(c["apercu"]) if c.get("apercu") else None
        if im:
            feuille.paste(im, (x, y))
        deja = " DEJA PRIS" if c["id"] in pris else ""
        paysage = "" if c["vertical"] else " paysage"
        d.text((x, y + TH + 2), f"C{k + 1} {c['duree']}s{paysage}{deja}", font=f,
               fill=(200, 30, 30) if deja else (0, 0, 0))
        d.text((x, y + TH + 22), c["requete"][:22], font=fs, fill=(90, 90, 90))
    sortie = dest / f"{bloc}.jpg"
    feuille.save(sortie, quality=88)
    print(sortie)


def choisir(dossier, bloc, code):
    episode, ep = _ep(dossier)
    if not code.upper().startswith("C"):
        raise SystemExit("[!] code attendu : C<n>, tel qu'affiche sur la planche des candidats")
    cands = json.loads((episode / "broll" / "candidats" / f"{bloc}.json").read_text(encoding="utf-8"))
    c = cands[int(code[1:]) - 1]
    cle = f"{episode.name}/{bloc}"
    autres = registre.ids_utilises(sauf=cle).get(c["id"])
    if autres:
        raise SystemExit(f"[!] plan {c['id']} deja utilise : {autres}")
    bl = ep["blocs"][bloc]
    cible = episode / "broll" / bl["fichier"]
    cible.unlink(missing_ok=True)
    (episode / "broll" / f"{cible.stem}.jpg").unlink(missing_ok=True)
    pexels.telecharger(c, cible)
    registre.inscrire(episode.name, bloc, c)
    if c.get("requete"):
        bl["requete"] = c["requete"]
        (episode / "script.json").write_text(json.dumps(ep, ensure_ascii=False, indent=2),
                                             encoding="utf-8")
    print(f"[{bloc}] <- {c['id']} {c['largeur']}x{c['hauteur']} {pexels.qualite(c)}")


def revue(dossier):
    episode, ep = _ep(dossier)
    blocs, cols = ep["blocs"], 3
    f, fs = police(20, "SemiBold"), police(17, "Medium")
    largeur_bloc = 3 * (TW + 4) + 24
    feuille = Image.new("RGB", (cols * largeur_bloc + 10,
                                ((len(blocs) + cols - 1) // cols) * (TH + 80) + 10),
                        (240, 240, 244))
    d = ImageDraw.Draw(feuille)
    for i, bl in enumerate(blocs):
        x0, y0 = 10 + (i % cols) * largeur_bloc, 10 + (i // cols) * (TH + 80)
        txt = _texte(ep, bl)
        d.text((x0, y0), f"[{i}] {bl['duree']}s  {bl.get('type', '')}", font=f, fill=(0, 0, 0))
        d.text((x0, y0 + 24), txt[:62], font=fs, fill=(60, 60, 90))
        d.text((x0, y0 + 44), txt[62:124], font=fs, fill=(60, 60, 90))
        src = episode / "broll" / bl["fichier"]
        if not src.exists():
            d.text((x0, y0 + 80), "plan manquant", font=f, fill=(200, 30, 30))
            continue
        dur = bl["duree"]
        for k, t in enumerate([C.BROLL_MARGE_S + 0.2, C.BROLL_MARGE_S + dur / 2,
                               C.BROLL_MARGE_S + dur - 0.2]):
            im = image_video(src, t)
            if im:
                feuille.paste(im, (x0 + k * (TW + 4), y0 + 68))
    sortie = episode / "revue_plans.jpg"
    feuille.save(sortie, quality=88)
    print(sortie)


def doublons():
    n = 0
    for vid, cles in registre.ids_utilises().items():
        if len(cles) > 1:
            print(vid, cles); n += 1
    print(f"{n} plan(s) en double")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    B.exiger()
    cmd = sys.argv[1]
    if cmd == "chercher" and len(sys.argv) >= 5:
        chercher(sys.argv[2], int(sys.argv[3]), sys.argv[4:])
    elif cmd == "choisir" and len(sys.argv) == 5:
        choisir(sys.argv[2], int(sys.argv[3]), sys.argv[4])
    elif cmd == "revue" and len(sys.argv) == 3:
        revue(sys.argv[2])
    elif cmd == "doublons":
        doublons()
    else:
        raise SystemExit(__doc__)
