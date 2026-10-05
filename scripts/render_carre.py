"""
Declinaison carree 1080x1080 d'un episode, pour LinkedIn.

    python scripts/render_carre.py episodes/2026-09-18-arrets-de-travail

Reprend script.json et les B-rolls de l'episode, avec la mise en page de charte.CARRE.
Un plan compose pour le 9:16 (photo posee en bandeau au-dessus du texte) peut avoir sa
version carree dans broll_carre/, sous le meme nom : elle est prise a la place.
Sortie : reel_<slug>_carre.mp4, controlee comme le reel (code retour 2 si non conforme).
"""
import sys
# la console Windows est en cp1252 par defaut
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import json, os, shutil, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
# avant lcdg.binaires, qui lit FFMPEG_BIN et FFPROBE_BIN a l'import (cf. render.py)
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass
from config import charte as C

# avant tout import de lcdg/habillage : il fige W, H et les positions par defaut a l'import
for cle, valeur in C.CARRE.items():
    setattr(C, cle, valeur)

from lcdg import binaires as B, montage, controles, son, voix


def preparer(episode: Path, ep: dict) -> Path:
    """Dossier de travail carre/ : B-rolls de l'episode, versions carrees prioritaires."""
    travail = episode / "carre"
    (travail / "broll").mkdir(parents=True, exist_ok=True)
    for bl in ep["blocs"]:
        src = episode / "broll_carre" / bl["fichier"]
        if not src.exists():
            src = episode / "broll" / bl["fichier"]
        dst = travail / "broll" / bl["fichier"]
        dst.unlink(missing_ok=True)
        if src.exists():
            try:
                os.link(src, dst)          # pas de copie de plusieurs centaines de Mo
            except OSError:
                shutil.copy(src, dst)
    return travail


def main(dossier: str):
    B.exiger()
    episode = Path(dossier).resolve()
    ep = json.loads((episode / "script.json").read_text(encoding="utf-8"))
    travail = preparer(episode, ep)
    t0 = time.time()

    print(f"\n{ep['label']} — carre {C.LARGEUR}x{C.HAUTEUR}")
    print("1/3  normalisation des B-rolls")
    montage.verifier(ep)              # avant d'encoder le moindre plan
    # la voix off fixe la duree de chaque plan : elle passe avant la base
    piste = voix.preparer(episode, ep) if voix.active(ep) else None
    _, bornes, total = montage.base(travail, ep["blocs"])
    print(f"     {len(bornes)} plans, {total:.2f} s")
    print("2/3  rendu de l'habillage")
    muet = montage.habiller(travail, ep, bornes, total)
    audio = son.bande(episode, ep, bornes, total, piste)   # voix, musique, bruitages
    final = montage.finaliser(muet, episode / f"reel_{ep['slug']}_carre.mp4", audio)
    couv = montage.couverture(final)             # avant la coupe : l'accroche est en place
    decalage = 0.0
    if C.ACCROCHE_COUVERTURE:
        decalage = bornes[1][0]
        montage.couper_accroche(final, decalage)
    print("3/3  controles")
    # sur le fichier livre, apres la coupe ; l'accroche coupee se controle sur la couverture
    conforme = controles.rapport(final, ep, bornes, decalage, couv[0])
    print(f"\n{final}\n" + "\n".join(map(str, couv)) + f"   ({time.time()-t0:.0f} s)")
    sys.exit(0 if conforme else 2)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("usage : python scripts/render_carre.py episodes/<dossier>")
    main(sys.argv[1])
