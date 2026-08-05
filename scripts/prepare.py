"""
Etape 1 : recuperation des candidats et preparation de la validation.

    python scripts/prepare.py episodes/2026-08-05-violences-cabinet

Lit script.json, interroge Pexels pour chaque bloc, telecharge les candidats,
construit une planche contact et un extrait sonore. Ne monte rien.
"""
import sys
# la console Windows est en cp1252 par defaut : les accents et les sparklines
# des mesures acoustiques y provoqueraient une UnicodeEncodeError.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass

from lcdg import audio as A
from lcdg import binaires as B
from lcdg import pexels
from lcdg.logo import police


def planche(episode: Path, blocs: list[dict]):
    """Une vignette par bloc, avec la requete et le texte, pour valider d'un coup d'oeil."""
    cases, lg = [], police(20, "SemiBold")
    for i, bl in enumerate(blocs):
        v = episode / "broll" / bl["fichier"]
        img = episode / "broll" / f"{v.stem}.jpg"
        if v.exists() and not img.exists():
            B.run(["-ss", "1.5", "-i", str(v), "-frames:v", "1",
                   "-vf", "scale=300:-1", str(img), "-y"])
        cases.append((img if img.exists() else None, bl))

    cols = 3
    lignes = (len(cases) + cols - 1) // cols
    W, Hc = 330, 260
    sheet = Image.new("RGB", (cols * W, lignes * Hc), (245, 245, 248))
    d = ImageDraw.Draw(sheet)
    for i, (img, bl) in enumerate(cases):
        x, y = (i % cols) * W + 10, (i // cols) * Hc + 10
        if img:
            v = Image.open(img)
            v.thumbnail((300, 170))
            sheet.paste(v, (x, y))
        d.text((x, y + 176), f"[{i}] {bl['requete'][:38]}", font=lg, fill=(10, 10, 10))
        txt = (bl.get("texte") or "(intro)").replace("*", "")
        d.text((x, y + 200), txt[:44], font=lg, fill=(90, 90, 100))
        d.text((x, y + 222), txt[44:88], font=lg, fill=(90, 90, 100))
    out = episode / "planche_broll.jpg"
    sheet.save(out, quality=92)
    return out


def extrait_son(episode: Path, ep: dict):
    """25 s du lit musical choisi, normalise, pour valider a l'oreille."""
    src = A.chemin(ep["musique"])
    out = episode / f"apercu_musique_{ep['musique']}.mp3"
    B.run(["-i", str(src), "-t", "25", "-af",
           "loudnorm=I=-16:TP=-1.5,afade=t=in:st=0:d=0.8,afade=t=out:st=23.5:d=1.5",
           "-c:a", "libmp3lame", "-b:a", "192k", str(out), "-y"])
    return out


def main(dossier: str):
    B.exiger()
    episode = Path(dossier).resolve()
    fiche = episode / "script.json"
    if not fiche.exists():
        raise SystemExit(f"[!] {fiche} introuvable. Copie episodes/exemple/script.json.")
    ep = json.loads(fiche.read_text(encoding="utf-8"))
    (episode / "broll").mkdir(parents=True, exist_ok=True)

    print(f"\n{ep['label']} — {len(ep['blocs'])} plans\n")
    rapport = []
    for i, bl in enumerate(ep["blocs"]):
        bl["fichier"] = bl.get("fichier") or f"B{i}.mp4"
        cible = episode / "broll" / bl["fichier"]
        if cible.exists():
            print(f"  [{i}] deja present : {bl['fichier']}")
            continue
        cands = pexels.chercher(bl["requete"], n=4,
                                duree_min=max(6, int(bl["duree"]) + 2))
        if not cands:
            print(f"  [{i}] AUCUN resultat pour « {bl['requete']} » — reformule la requete")
            continue
        c = cands[0]
        pexels.telecharger(c, cible)
        note = pexels.qualite(c)
        rapport.append((i, bl["requete"], c, note))
        print(f"  [{i}] {bl['requete'][:34]:34} -> {c['largeur']}x{c['hauteur']}  {note}")
        alt = episode / "broll" / "alternatives.json"
        anciens = json.loads(alt.read_text(encoding="utf-8")) if alt.exists() else {}
        anciens[str(i)] = cands
        alt.write_text(json.dumps(anciens, ensure_ascii=False, indent=1), encoding="utf-8")

    fiche.write_text(json.dumps(ep, ensure_ascii=False, indent=2), encoding="utf-8")
    p = planche(episode, ep["blocs"])
    s = extrait_son(episode, ep)

    faibles = [r for r in rapport if "molle" in r[3]]
    if faibles:
        print("\n  A surveiller, ces plans seront mous apres recadrage :")
        for i, req, c, _ in faibles:
            print(f"    [{i}] {req} — {c['url_page']}")

    print(f"\nA valider :\n  {p}\n  {s}")
    print("\nPour changer un plan : prends une autre entree dans broll/alternatives.json,")
    print("ou remplace le fichier B<n>.mp4 a la main. Puis :")
    print(f"  python scripts/render.py {dossier}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("usage : python scripts/prepare.py episodes/<dossier>")
    main(sys.argv[1])
