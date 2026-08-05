"""Detourage du logo LCDG et composition du lockup en Montserrat."""
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))
from config import charte as C

GRIS = (117, 111, 143)


def police(taille, graisse):
    f = ImageFont.truetype(str(C.POLICE), taille)
    f.set_variation_by_name(graisse)
    return f


@lru_cache(maxsize=1)
def _marque_source() -> Image.Image:
    """Alpha = pixels bleus. Les deux mains restent evidees."""
    im = Image.open(C.LOGO_SRC).convert("RGBA")
    a = np.array(im).astype(float)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    score = np.clip((b - r - 12) / 45.0, 0, 1)
    score *= np.clip(((r + g + b) / 3.0 - 55) / 40.0, 0, 1)
    score = np.where(a[..., 3] < 20, 0, score)
    rgb = np.array(im.convert("RGB"))
    mk = Image.fromarray(np.dstack([rgb, score * 255]).astype(np.uint8), "RGBA")
    return mk.crop(mk.split()[3].point(lambda p: 255 if p > 12 else 0).getbbox())


def marque(taille, blanc=False):
    m = _marque_source().resize((taille, taille), Image.LANCZOS)
    if not blanc:
        return m
    w = Image.new("RGBA", m.size, (255, 255, 255, 0))
    w.putalpha(m.split()[3])
    return w


@lru_cache(maxsize=8)
def lockup(hauteur, blanc=True):
    """Croix + 'Le Cercle / des Generalistes'."""
    m = marque(hauteur, blanc=blanc)
    f1 = police(int(hauteur * 0.40), "Bold")
    f2 = police(int(hauteur * 0.255), "Medium")
    gap = int(hauteur * 0.13)
    d0 = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    tw = max(d0.textbbox((0, 0), "Le Cercle", font=f1)[2],
             d0.textbbox((0, 0), "des Généralistes", font=f2)[2])

    img = Image.new("RGBA", (hauteur + gap + tw, int(hauteur * 1.02)), (0, 0, 0, 0))
    img.paste(m, (0, (img.height - hauteur) // 2), m)
    d = ImageDraw.Draw(img)
    x, y = hauteur + gap, img.height // 2 - int(hauteur * 0.355)
    coul = C.BLANC if blanc else C.NAVY
    sous = C.BLANC if blanc else GRIS
    d.text((x, y), "Le Cercle", font=f1, fill=coul + (255,))
    d.text((x, y + int(hauteur * 0.40)), "des Généralistes", font=f2, fill=sous + (255,))
    return img
