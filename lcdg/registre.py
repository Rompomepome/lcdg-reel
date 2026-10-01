"""
Registre des plans Pexels utilises, tous episodes confondus : episodes/plans_utilises.json.

Un meme plan ne sert jamais deux fois : le public le reconnait d'un reel a l'autre.
Cle "<dossier episode>/<bloc>", valeur {"id": <id Pexels>, "url_page": <page Pexels>}.
Le fichier est versionne : il survit a la suppression des dossiers broll/.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import charte as C

FICHIER = C.EPISODES / "plans_utilises.json"


def charger() -> dict:
    return json.loads(FICHIER.read_text(encoding="utf-8")) if FICHIER.exists() else {}


def ids_utilises(sauf: str | None = None) -> dict:
    """{id Pexels: [cles qui l'utilisent]}, sans la cle `sauf` (le bloc qu'on remplace)."""
    out = {}
    for cle, plan in charger().items():
        if cle != sauf:
            out.setdefault(plan["id"], []).append(cle)
    return out


def inscrire(episode: str, bloc: int, candidat: dict):
    reg = charger()
    reg[f"{episode}/{bloc}"] = {"id": candidat["id"], "url_page": candidat["url_page"]}
    FICHIER.write_text(json.dumps(dict(sorted(reg.items())), ensure_ascii=False, indent=1),
                       encoding="utf-8")
