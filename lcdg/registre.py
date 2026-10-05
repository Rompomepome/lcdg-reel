"""
Registre des plans Pexels utilises, tous episodes confondus : episodes/plans_utilises.json.

Un meme plan ne sert jamais deux fois : le public le reconnait d'un reel a l'autre. Un
plan du meme tournage non plus : memes acteurs, meme decor (Romain, 02/10/2026). Sur
Pexels, les plans d'un tournage ont le meme auteur et des numeros proches.
Cle "<dossier episode>/<bloc>", valeur {"id", "url_page", "auteur_id", "auteur"}.
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


def _ecrire(reg: dict):
    FICHIER.write_text(json.dumps(dict(sorted(reg.items())), ensure_ascii=False, indent=1),
                       encoding="utf-8")


def inscrire(episode: str, bloc: int, candidat: dict):
    reg = charger()
    reg[f"{episode}/{bloc}"] = {"id": candidat["id"], "url_page": candidat["url_page"],
                               "auteur_id": candidat.get("auteur_id"),
                               "auteur": candidat.get("auteur", "")}
    _ecrire(reg)


def completer() -> int:
    """Ajoute l'auteur Pexels aux plans inscrits avant le 02/10/2026. Un appel par plan."""
    from lcdg import pexels
    reg, n = charger(), 0
    for plan in reg.values():
        if plan.get("auteur_id") is None and isinstance(plan["id"], int):
            u = pexels.video(plan["id"]).get("user", {})
            plan["auteur_id"], plan["auteur"] = u.get("id"), u.get("name", "")
            n += 1
    if n:
        _ecrire(reg)
    return n


def meme_tournage(candidat: dict, episode: str) -> list:
    """Cles des plans d'autres episodes tournes avec ce candidat (meme auteur, numeros
    a moins de charte.TOURNAGE_ECART). Vide si l'auteur du candidat est inconnu."""
    auteur = candidat.get("auteur_id")
    if auteur is None:
        return []

    def proche(plan):
        # un plan hors Pexels (id texte : reportage, plan fourni) est son propre tournage
        if isinstance(plan["id"], int) and isinstance(candidat["id"], int):
            return abs(plan["id"] - candidat["id"]) <= C.TOURNAGE_ECART
        return True

    return [cle for cle, plan in charger().items()
            if not cle.startswith(episode + "/") and plan.get("auteur_id") == auteur
            and proche(plan)]
