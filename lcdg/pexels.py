"""Client de l'API Pexels Video. Documentation : https://www.pexels.com/api/documentation/"""
import os
from pathlib import Path

import requests

API = "https://api.pexels.com/videos/search"


def _cle() -> str:
    cle = os.environ.get("PEXELS_API_KEY", "").strip()
    if not cle:
        raise SystemExit(
            "[!] PEXELS_API_KEY absente.\n"
            "    Copie .env.example en .env et renseigne ta cle "
            "(https://www.pexels.com/api/)."
        )
    return cle


def chercher(requete: str, n: int = 6, duree_min: int = 6):
    """Retourne les meilleurs candidats verticaux pour une requete."""
    r = requests.get(API, headers={"Authorization": _cle()},
                     params={"query": requete, "orientation": "portrait",
                             "size": "large", "per_page": 20, "locale": "en-US"},
                     timeout=30)
    r.raise_for_status()
    out = []
    for v in r.json().get("videos", []):
        if v.get("duration", 0) < duree_min:
            continue
        # on prend le fichier le plus defini, en privilegiant le portrait
        fichiers = sorted(v.get("video_files", []),
                          key=lambda f: (f.get("height", 0) >= f.get("width", 0),
                                         f.get("height", 0)), reverse=True)
        if not fichiers:
            continue
        f = fichiers[0]
        out.append({
            "id": v["id"], "duree": v["duration"], "url_page": v["url"],
            "auteur": v.get("user", {}).get("name", ""),
            "largeur": f.get("width"), "hauteur": f.get("height"),
            "vertical": f.get("height", 0) >= f.get("width", 0),
            "lien": f["link"], "apercu": v.get("image"),
        })
    # vertical d'abord, puis la plus grande definition
    out.sort(key=lambda c: (c["vertical"], c["hauteur"] or 0), reverse=True)
    return out[:n]


def telecharger(candidat: dict, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        return destination
    with requests.get(candidat["lien"], stream=True, timeout=120) as r:
        r.raise_for_status()
        with open(destination, "wb") as fh:
            for bloc in r.iter_content(1 << 20):
                fh.write(bloc)
    return destination


def qualite(candidat: dict) -> str:
    """Avertit quand un plan devra etre recadre depuis un format paysage."""
    if candidat["vertical"]:
        return "vertical, ideal"
    if (candidat["hauteur"] or 0) >= 2160:
        return "paysage 4K, recadrage sans perte"
    return "paysage sous 4K, l'image sera molle apres recadrage"
