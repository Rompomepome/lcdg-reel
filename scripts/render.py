"""
Etape 2 : montage.

    python scripts/render.py episodes/2026-08-05-violences-cabinet

Normalise les B-rolls, rend l'habillage, puis controle le fichier de sortie par
mesure de pixels. Le reel sort sans piste audio : la musique est posee ensuite, a part.
"""
import sys
# la console Windows est en cp1252 par defaut : les accents y provoqueraient une
# UnicodeEncodeError.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import json, shutil, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass
from config import charte as C
from lcdg import binaires as B, montage, controles, son, voix


def main(dossier: str):
    B.exiger()
    episode = Path(dossier).resolve()
    ep = json.loads((episode / "script.json").read_text(encoding="utf-8"))
    t0 = time.time()

    print("\n1/3  normalisation des B-rolls")
    montage.verifier(ep)              # avant d'encoder le moindre plan
    # la voix off fixe la duree de chaque plan : elle passe avant la base
    piste = voix.preparer(episode, ep) if voix.active(ep) else None
    _, bornes, total = montage.base(episode, ep["blocs"])
    print(f"     {len(bornes)} plans, {total:.2f} s")

    print("2/3  rendu de l'habillage")
    muet = montage.habiller(episode, ep, bornes, total)
    audio = son.bande(episode, ep, bornes, total, piste)   # voix, musique, bruitages
    sortie = montage.finaliser(muet, episode / f"reel_{ep['slug']}.mp4", audio)
    if piste:                         # voix seule, pour le montage final en musique
        shutil.copy(piste, episode / piste.name)

    couv = montage.couverture(sortie)            # avant la coupe : l'accroche est en place
    decalage = 0.0
    if C.ACCROCHE_COUVERTURE:
        decalage = bornes[1][0]
        montage.couper_accroche(sortie, decalage)

    print("3/3  controles")
    # sur le fichier livre, apres la coupe ; l'accroche coupee se controle sur la couverture
    conforme = controles.rapport(sortie, ep, bornes, decalage, couv[0])

    print(f"\n{sortie}\n" + "\n".join(map(str, couv)) + f"   ({time.time()-t0:.0f} s)")
    sys.exit(0 if conforme else 2)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("usage : python scripts/render.py episodes/<dossier>")
    main(sys.argv[1])
