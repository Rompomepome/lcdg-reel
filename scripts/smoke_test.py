"""
Test de fumee : monte un episode de 3 plans a partir de mires generees,
puis verifie que les controles passent.

    python scripts/smoke_test.py

Ne demande ni cle Pexels, ni B-roll. Ne teste que les fichiers audio, qui doivent
etre presents. A lancer apres un clone, apres une mise a jour de la charte, ou
avant de pousser une modification de lcdg/.
"""
import json
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from config import charte as C
from lcdg import audio as A
from lcdg import binaires as B
from lcdg import controles, montage

EPISODE = {
    "slug": "smoke", "rubrique": "pro",
    "label": "Test de fumée",
    "sous_titre": "Vérification de la chaîne de montage",
    "musique": None,
    "blocs": [
        {"duree": 3.8, "texte": None, "fichier": "B0.mp4"},
        {"duree": 5.0, "texte": "Premier bloc avec un *segment surligné* et une virgule, "
                                "puis une seconde phrase.", "fichier": "B1.mp4"},
        {"duree": 5.0, "texte": "Second bloc, *plus court*.", "fichier": "B2.mp4"},
    ],
}


def mire(dest: Path, secondes: float, teinte: int):
    B.run(["-f", "lavfi", "-i",
           f"gradients=s={C.LARGEUR}x{C.HAUTEUR}:c0=0x{teinte:02x}2233:"
           f"c1=0x{teinte:02x}8899:d={secondes + 4}",
           "-t", str(secondes + 4), "-r", str(C.FPS),
           "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
           "-pix_fmt", "yuv420p", str(dest), "-y"])


def main():
    B.exiger()
    manquants = A.manquants()
    musiques = [m["cle"] for m in A.manifeste()["musiques"]
                if m["fichier"] not in manquants]
    if not musiques or manquants:
        raise SystemExit(
            "[!] Bibliotheque audio incomplete, le test ne peut pas tourner.\n"
            "    Lance d'abord : python scripts/doctor.py")
    ep = {**EPISODE, "musique": musiques[0]}

    with tempfile.TemporaryDirectory() as tmp:
        dossier = Path(tmp) / "smoke"
        (dossier / "broll").mkdir(parents=True)
        (dossier / "script.json").write_text(
            json.dumps(ep, ensure_ascii=False), encoding="utf-8")
        for i, bl in enumerate(ep["blocs"]):
            mire(dossier / "broll" / bl["fichier"], bl["duree"], 0x20 + i * 0x30)

        print("\n1/4  normalisation")
        _, bornes, total = montage.base(dossier, ep["blocs"])
        print(f"     {len(bornes)} plans, {total:.2f} s")
        print("2/4  habillage")
        montage.habiller(dossier, ep, bornes, total)
        print("3/4  mixage")
        sortie = montage.mixer(dossier, ep, bornes, total)
        print("4/4  controles")
        conforme = controles.rapport(sortie)

        garde = Path(__file__).resolve().parent.parent / "smoke_test.mp4"
        shutil.copy(sortie, garde)
        print(f"\nSortie conservee : {garde}")

    if not conforme:
        raise SystemExit("[!] Le test de fumee a echoue : ne pas pousser en l'etat.")
    print("[OK] chaine de montage conforme")


if __name__ == "__main__":
    main()
