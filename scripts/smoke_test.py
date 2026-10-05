"""
Test de fumee : monte un episode de 5 plans a partir de mires generees,
puis verifie que les controles passent.

    python scripts/smoke_test.py

Ne demande ni cle Pexels, ni B-roll. Couvre tous les types de scene : accroche,
texte en deux temps (separes par "|"), chiffre cle avec valeur barree, chiffre a
pictogrammes (fond flou) et phrase forte, plus la voix off : une fausse narration
(tonalite generee localement) remplace ElevenLabs, sans cle ni credit ; musique et
bruitages de assets/ s'ils sont presents. A lancer
apres un clone, apres une mise a jour de la charte, ou avant de pousser une
modification de lcdg/.
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
from lcdg import binaires as B
from lcdg import controles, montage, son, voix

PAS = 0.06          # duree d'un caractere dans la fausse narration


def fausse_synthese(texte, voice_id, dossier, modele=None, reglages=None):
    """Tonalite de la duree du texte, horodatage lineaire : teste le calage et le mixage."""
    dossier.mkdir(parents=True, exist_ok=True)
    mp3 = dossier / "fausse_voix.mp3"
    B.run(["-f", "lavfi", "-i", f"sine=frequency=220:duration={len(texte) * PAS:.2f}",
           "-ac", "2", str(mp3), "-y"])
    return mp3, {"characters": list(texte),
                 "character_start_times_seconds": [i * PAS for i in range(len(texte))],
                 "character_end_times_seconds": [(i + 1) * PAS for i in range(len(texte))]}

EPISODE = {
    "slug": "smoke", "rubrique": "pro",
    "label": "Test de fumée",
    "badge": "Test · ouverture",
    "sous_titre": "Vérification de la chaîne de *montage*.",
    "appel": "Le test, en détail :",
    "blocs": [
        {"duree": 3.8, "texte": None, "fichier": "B0.mp4", "cadrage": "largeur",
         "credit": "Images : source test"},                 # accroche : couverture, sans voix
        {"duree": 5.0, "texte": "Premier bloc avec un *segment surligné* et une virgule. "
                                "| Puis un second temps.",
         "voix": "Premier bloc, avec un segment surligne. | Puis un second temps.",
         "fichier": "B1.mp4",
         "insert": {"type": "choix", "lignes": [{"label": "Oui", "ok": True},
                                                {"label": "Non", "ok": False, "temps": 1}]}},
        {"duree": 5.0, "type": "chiffre", "valeur": 140, "depuis": 100, "suffixe": " €",
         "legende": "de reste à charge *par an*",
         "voix": "Cent quarante euros par an.", "fichier": "B2.mp4"},
        {"duree": 5.0, "type": "chiffre", "valeur": 70, "suffixe": " boîtes", "pictos": True,
         "legende": "par an, *six par mois*",
         "voix": "Soixante-dix boites par an.", "fichier": "B3.mp4"},
        {"duree": 5.0, "type": "phrase", "texte": "Une phrase forte, *centrée*.",
         "voix": "Une phrase forte, centree.", "fichier": "B4.mp4"},
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
    ep = EPISODE
    with tempfile.TemporaryDirectory() as tmp:
        dossier = Path(tmp) / "smoke"
        (dossier / "broll").mkdir(parents=True)
        (dossier / "script.json").write_text(
            json.dumps(ep, ensure_ascii=False), encoding="utf-8")
        for i, bl in enumerate(ep["blocs"]):
            mire(dossier / "broll" / bl["fichier"], bl["duree"], 0x20 + i * 0x30)

        print("\n1/3  normalisation")
        montage.verifier(ep)              # avant d'encoder le moindre plan
        voix.synthese = fausse_synthese
        piste = voix.preparer(dossier, ep)
        _, bornes, total = montage.base(dossier, ep["blocs"])
        print(f"     {len(bornes)} plans, {total:.2f} s")
        print("2/3  habillage")
        muet = montage.habiller(dossier, ep, bornes, total)
        audio = son.bande(dossier, ep, bornes, total, piste)
        sortie = montage.finaliser(muet, dossier / f"reel_{ep['slug']}.mp4", audio)
        couv = montage.couverture(sortie)
        avant = B.duree(sortie)
        montage.couper_accroche(sortie, bornes[1][0])
        if len(couv) != 2:
            raise SystemExit("[!] couvertures incorrectes")
        print("3/3  controles")
        conforme = controles.rapport(sortie, ep, bornes, bornes[1][0], couv[0])
        print(f"     accroche coupee : {avant:.2f} s -> {B.duree(sortie):.2f} s, "
              f"{len(couv)} couvertures")

        garde = Path(__file__).resolve().parent.parent / "smoke_test.mp4"
        shutil.copy(sortie, garde)
        print(f"\nSortie conservee : {garde}")

    if not conforme:
        raise SystemExit("[!] Le test de fumee a echoue : ne pas pousser en l'etat.")
    print("[OK] chaine de montage conforme")


if __name__ == "__main__":
    main()
