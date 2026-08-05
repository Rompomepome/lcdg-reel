"""Verifie que la machine est prete. A lancer apres un clone, sur Windows comme sur Mac."""
import sys
# la console Windows est en cp1252 par defaut : les accents et les sparklines
# des mesures acoustiques y provoqueraient une UnicodeEncodeError.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import sys, platform
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import charte as C
from lcdg import binaires as B

ok = True
def ligne(nom, bon, detail=""):
    global ok; ok = ok and bon
    print(f"  {'OK   ' if bon else 'ABSENT'}  {nom:26} {detail}")

print(f"\nlcdg-reel — verification ({platform.system()} {platform.machine()}, Python {sys.version.split()[0]})\n")
ligne("Python >= 3.10", sys.version_info >= (3, 10))
for mod in ("PIL", "numpy", "requests", "dotenv"):
    try: __import__(mod); ligne(f"module {mod}", True)
    except ImportError: ligne(f"module {mod}", False, "pip install -r requirements.txt")
ligne("ffmpeg", bool(B.FFMPEG), B.FFMPEG or B.INSTALL)
ligne("ffprobe", bool(B.FFPROBE), B.FFPROBE or B.INSTALL)
ligne("police Montserrat", C.POLICE.exists(), str(C.POLICE.name))
ligne("logo LCDG", C.LOGO_SRC.exists(), str(C.LOGO_SRC.name))

import os
try:
    from dotenv import load_dotenv; load_dotenv(C.RACINE / ".env")
except ImportError: pass
ligne("PEXELS_API_KEY", bool(os.environ.get("PEXELS_API_KEY")), "cf .env.example")

from lcdg import audio as A
mq = A.manquants()
ligne("bibliotheque audio", not mq, "complete" if not mq else f"{len(mq)} fichier(s) a deposer")
if mq:
    print("\n  A telecharger depuis ton compte Mixkit, puis a deposer dans assets/audio/ :")
    man = A.manifeste()
    for fam in ("musiques", "effets"):
        for p in man[fam]:
            if p["fichier"] in mq:
                print(f"    - {p['fichier']:22} « {p['titre']} »  {p.get('url_page','')}")

print("\n->", "pret" if ok else "il manque des elements, voir ci-dessus")
sys.exit(0 if ok else 1)
