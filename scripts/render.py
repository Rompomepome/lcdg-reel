"""
Etape 2 : montage.

    python scripts/render.py episodes/2026-08-05-violences-cabinet

Normalise les B-rolls, rend l'habillage, mixe, masterise, puis controle
le fichier de sortie par mesure de pixels et de niveaux.
"""
import sys
# la console Windows est en cp1252 par defaut : les accents et les sparklines
# des mesures acoustiques y provoqueraient une UnicodeEncodeError.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass
from lcdg import binaires as B, montage, controles


def main(dossier: str):
    B.exiger()
    episode = Path(dossier).resolve()
    ep = json.loads((episode / "script.json").read_text(encoding="utf-8"))
    t0 = time.time()

    print("\n1/4  normalisation des B-rolls")
    _, bornes, total = montage.base(episode, ep["blocs"])
    print(f"     {len(bornes)} plans, {total:.2f} s")

    print("2/4  rendu de l'habillage")
    montage.habiller(episode, ep, bornes, total)

    print("3/4  mixage et mastering")
    sortie = montage.mixer(episode, ep, bornes, total)

    print("4/4  controles")
    conforme = controles.rapport(sortie)

    print(f"\n{sortie}   ({time.time()-t0:.0f} s)")
    sys.exit(0 if conforme else 2)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("usage : python scripts/render.py episodes/<dossier>")
    main(sys.argv[1])
