"""
Controle d'un script sans rien rendre (quelques secondes), a lancer apres chaque modification du texte :

    python scripts/verifier.py episodes/<dossier> [...]

1. Nombre de lignes de chaque temps de texte, coupe comme le moteur le coupe : trois au plus (regle du
   CLAUDE.md ; montage.verifier ne controle que la zone sure, pas ce nombre).
2. Mise en page complete (textes, surlignages, inserts, pastille, bandeau) en 9:16 ET en carre : la charte
   CARRE s'applique avant l'import de lcdg (comme render_carre.py), d'ou un sous-processus par format.
"""
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import json
import subprocess
from pathlib import Path

R = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(R))
from lcdg import habillage as hb
from lcdg import texte as T

LIGNES_MAX = 3
VERIF = r'''
import json, sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, sys.argv[1])
from config import charte as C
if sys.argv[3] == "1":
    for cle, valeur in C.CARRE.items():
        setattr(C, cle, valeur)
from lcdg import montage
montage.verifier(json.loads(open(sys.argv[2], encoding="utf-8").read()))
print("mise en page conforme")
'''


def lignes(ep):
    trop = 0
    for k, b in enumerate(ep["blocs"]):
        if not b.get("texte") or b.get("type") == "chiffre":
            continue
        for i, temps in enumerate(b["texte"].split("|")):
            temps = temps.strip()
            if b.get("type") == "phrase":
                _, n = hb.style_ajuste(temps)
            else:
                st = hb.style_bloc()
                n = len(T.equilibrer(temps, T.mesureur(st), st["largeur"]))
            if n > LIGNES_MAX:
                trop += 1
                print(f"  [!] B{k}.{i} : {n} lignes (3 au plus) : {temps}")
    return trop


if len(sys.argv) < 2:
    raise SystemExit(__doc__)
ok = True
for d in sys.argv[1:]:
    script = (R / d / "script.json").resolve()
    ep = json.loads(script.read_text(encoding="utf-8"))
    print(f"== {Path(d).name}")
    ok &= lignes(ep) == 0
    for nom, carre in (("9:16", "0"), ("carre", "1")):
        r = subprocess.run([sys.executable, "-c", VERIF, str(R), str(script), carre], capture_output=True,
                           text=True, encoding="utf-8", errors="replace", cwd=R)
        sortie = (r.stdout + r.stderr).strip().splitlines()
        print(f"  {nom:6} " + ("\n    ".join(sortie[-6:]) if r.returncode else (sortie[-1] if sortie else "?")))
        ok &= r.returncode == 0
sys.exit(0 if ok else 1)
