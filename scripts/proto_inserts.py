"""Banc d'essai des inserts : dessine un insert seul, à plusieurs instants, sur une image de fond,
sans rendre de reel (quelques secondes au lieu de cinq minutes).

    python scripts/proto_inserts.py <spec.json> <sortie.png> [--temps 0,2.5] [--bas 980] [--fond image.jpg]
        [--instants 0.3,0.8,1.5,3,6]

spec.json : un insert (objet) ou plusieurs (liste, comme le champ "insert" d'un bloc).
--temps : début de chaque temps du bloc, en secondes (0 = début du bloc)."""
import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

R = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(R))
from config import charte as C
from lcdg import inserts as I
from lcdg import texte as T

a = argparse.ArgumentParser()
a.add_argument("spec"), a.add_argument("sortie")
a.add_argument("--temps", default="0,3")
a.add_argument("--bas", type=float, default=990)
a.add_argument("--fond")
a.add_argument("--instants", default="0.3,0.7,1.2,2,3,3.6,4.5,7")
args = a.parse_args()


class Part:
    def __init__(self, debut):
        self.debut = debut

    def _sortie(self, t):
        return 0.0


class Scene:
    def __init__(self, temps):
        self.debut, self.fin = temps[0], temps[-1] + 10
        self.parts = [Part(x) for x in temps]


specs = json.loads(Path(args.spec).read_text(encoding="utf-8"))
specs = [specs] if isinstance(specs, dict) else specs
scene = Scene([float(x) for x in args.temps.split(",")])
objs, premier = [], None
for sp in specs:
    o = I.TYPES[sp["type"]]("essai", sp, scene, args.bas - C.INSERT_ECART)
    if sp.get("sur") and premier is not None:
        o.x = premier.x + (premier.w - o.w) / 2
        o.y = premier.y + (premier.h - o.h) / 2
    premier = premier or o
    objs.append(o)
print("échelles :", [round(o.s, 2) for o in objs], "tailles :", [(o.w, o.h) for o in objs])
fond = Image.open(args.fond).convert("RGBA").resize((C.LARGEUR, C.HAUTEUR)) if args.fond else \
    Image.new("RGBA", (C.LARGEUR, C.HAUTEUR), (70, 80, 96, 255))
haut = int(min(o.y for o in objs) - 60)
bas = int(args.bas + 140)
vignettes = []
for t in [float(x) for x in args.instants.split(",")] + ["final"]:
    im = fond.copy()
    for o in objs:
        o.dessiner(im, 0 if t == "final" else t, final=t == "final")
    im = im.crop((0, max(0, haut), C.LARGEUR, min(C.HAUTEUR, bas)))
    d = ImageDraw.Draw(im)
    d.text((16, 10), f"t = {t}", fill=(255, 255, 0, 255), font=T._police(34, "SemiBold"))
    vignettes.append(im.resize((im.width // 2, im.height // 2), Image.LANCZOS))
cols = 3
w, h = vignettes[0].size
planche = Image.new("RGB", (cols * w + (cols + 1) * 6, ((len(vignettes) + cols - 1) // cols) * (h + 6) + 6), (230, 230, 236))
for i, v in enumerate(vignettes):
    planche.paste(v, (6 + (i % cols) * (w + 6), 6 + (i // cols) * (h + 6)))
planche.save(args.sortie)
print(args.sortie, planche.size)
print("sons :", [(round(x, 2), s) for o in objs for x, s in o.sons()])
