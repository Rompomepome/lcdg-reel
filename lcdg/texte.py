"""
Texte anime du style v2 : les mots se posent un par un, le segment cle se surligne
de gauche a droite, puis le texte sort vers le haut.
Toutes les constantes viennent de config/charte.py — ne rien coder en dur ici.
"""
import sys
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import charte as C
from lcdg.logo import police

BLANC = C.BLANC
# Montserrat n'a pas de glyphe pour l'espace fine insecable : elle sortirait en carre vide
REMPLACEMENTS = {"\u202f": "\u00a0"}


def normaliser(texte: str) -> str:
    """Remplace les caracteres que Montserrat ne sait pas dessiner."""
    for a, b in REMPLACEMENTS.items():
        texte = texte.replace(a, b)
    return texte


def lisse(x: float) -> float:
    """Sortie cubique : rapide au debut, posee a la fin."""
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def rebond(x: float) -> float:
    """Comme lisse(), mais depasse legerement la cible avant de s'y poser (rebond)."""
    x = max(0.0, min(1.0, x))
    c = C.REBOND
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


@lru_cache(maxsize=64)
def _police(px: int, graisse: str):
    return police(px, graisse)


def largeur(mot: str, px: int, graisse: str, approche: float) -> float:
    """Largeur d'un mot avec son interlettrage (approche en fraction du corps)."""
    return _police(px, graisse).getlength(mot) + max(0, len(mot) - 1) * approche * px


@lru_cache(maxsize=4096)
def sprite(mot: str, px: int, graisse: str, approche: float, couleur=BLANC):
    """(ombre, glyphes, marge) d'un mot, gardes en cache : un mot sert sur des
    dizaines d'images."""
    return _sprite(mot, px, graisse, approche, couleur)


@lru_cache(maxsize=48)
def sprite_chiffre(mot: str, px: int, graisse: str, approche: float, couleur=BLANC):
    """Meme chose pour le grand chiffre : chaque valeur du compteur ne sert qu'une
    image ou deux, inutile de garder toutes ces grandes couches en memoire."""
    return _sprite(mot, px, graisse, approche, couleur)


def _sprite(mot: str, px: int, graisse: str, approche: float, couleur=BLANC):
    """(ombre, glyphes, marge) : le mot en deux couches, ombre douce comprise.

    L'ombre remplace le contour du style v1 : un halo large qui assourdit le fond,
    plus une ombre portee courte qui detache la lettre."""
    f = _police(px, graisse)
    m = C.HALO_FLOU * 2
    w = int(largeur(mot, px, graisse, approche)) + 2 * m + 6
    h = int(px * 1.4) + 2 * m
    glyphes = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(glyphes)
    for k, ch in enumerate(mot):
        d.text((m + f.getlength(mot[:k]) + k * approche * px, m), ch, font=f,
               fill=tuple(couleur) + (255,))
    a = glyphes.getchannel("A")
    halo = a.filter(ImageFilter.GaussianBlur(C.HALO_FLOU)).point(
        lambda p: p * C.HALO_ALPHA // 255)
    portee = Image.new("L", (w, h), 0)
    portee.paste(a.filter(ImageFilter.GaussianBlur(C.OMBRE_FLOU)).point(
        lambda p: p * C.OMBRE_ALPHA // 255), (0, C.OMBRE_DECALAGE))
    noir = Image.new("L", (w, h), 0)
    ombre = Image.merge("RGBA", (noir, noir, noir, ImageChops.lighter(halo, portee)))
    return ombre, glyphes, m


def coller(fond: Image.Image, im: Image.Image, xy, alpha: float = 1.0):
    """Compose `im` sur `fond` en (x, y), opacite multipliee par alpha."""
    if alpha <= 0.003:
        return
    if alpha < 0.997:
        im = im.copy()
        im.putalpha(im.getchannel("A").point(lambda p: int(p * alpha)))
    fond.alpha_composite(im, (int(round(xy[0])), int(round(xy[1]))))


# ---------------------------------------------------------------- mise en page
def atomes(texte):
    """Transforme '*mot* suivant' en atomes (texte, surligne), espaces compris.
    La ponctuation collee reste collee, et un surlignage multi-mots reste continu."""
    texte = normaliser(texte)
    runs, surl = [], False
    for part in texte.split("*"):
        if part:
            runs.append((part, surl))
        surl = not surl
    out = []
    for txt, hl in runs:
        buf = ""
        for ch in txt:
            if ch == " ":
                if buf:
                    out.append((buf, hl)); buf = ""
                out.append((" ", hl))
            else:
                buf += ch
        if buf:
            out.append((buf, hl))
    # un espace n'est surligne que s'il est encadre de deux atomes surlignes
    for i, (t, hl) in enumerate(out):
        if t == " " and hl:
            g = out[i - 1][1] if i > 0 else False
            dr = out[i + 1][1] if i + 1 < len(out) else False
            out[i] = (" ", g and dr)
    # espace au bord d'un surlignage : elle s'elargit de son debord, sinon le mot
    # voisin touche le surlignage (troisieme element a True)
    for i, (t, hl) in enumerate(out):
        if t == " " and not hl:
            g = out[i - 1][1] if i > 0 else False
            dr = out[i + 1][1] if i + 1 < len(out) else False
            if g or dr:
                out[i] = (" ", False, True)
    return out


def lignes(texte, mesure, maxw):
    """Retour a la ligne impose a chaque fin de phrase (. ? !), puis habillage a la largeur.
    On ne coupe que sur une espace ordinaire : des atomes sans espace entre eux (mot
    surligne et sa ponctuation, apostrophe devant un surlignage) changent de ligne ensemble.
    `mesure(atome)` donne la largeur d'un atome, selon sa graisse."""
    res = []
    for fin in ".?!":
        texte = texte.replace(fin + " ", fin + "\n")
    for ph in (p.strip() for p in texte.split("\n")):
        if not ph:
            continue
        cur, larg = [], 0
        for at in atomes(ph):
            w = mesure(at)
            if larg + w > maxw and cur and at[0] != " ":
                report = []
                # atome colle au precedent (pas d'espace entre eux) : ils partent ensemble
                while cur and cur[-1][0] != " ":
                    report.insert(0, cur.pop())
                # ne jamais couper au milieu d'un surlignage : on reporte le segment entier
                if (report or [at])[0][1]:
                    while cur and cur[-1][1]:
                        report.insert(0, cur.pop())
                    while report and report[0][0] == " ":
                        report.pop(0)
                while cur and cur[-1][0] == " ":
                    cur.pop()
                if cur:
                    res.append(cur)
                cur = report
                larg = sum(mesure(a) for a in cur)
            if not (not cur and at[0] == " "):
                cur.append(at); larg += w
        while cur and cur[-1][0] == " ":
            cur.pop()
        if cur:
            res.append(cur)
    return res


def mesureur(style):
    """Largeur d'un atome selon le style : le segment cle a sa propre graisse, et
    l'espace porte l'interlettrage qui suit la derniere lettre du mot precedent."""
    px, ap = style["px"], style["approche"]

    def mesure(at):
        if at[0] == " ":
            bord = C.SURLIGNE_MARGE if len(at) > 2 else 0
            return largeur(" ", px, style["graisse"], 0) + ap * px + bord
        return largeur(at[0], px, style["cle"] if at[1] else style["graisse"], ap)
    return mesure


def equilibrer(texte, mesure, maxw):
    """Comme lignes(), mais a nombre de lignes egal, la colonne la plus etroite
    possible : les lignes s'equilibrent, comme les titres du site (text-wrap: balance)."""
    ref = lignes(texte, mesure, maxw)
    lo, hi = maxw * 0.45, float(maxw)
    for _ in range(14):
        mid = (lo + hi) / 2
        if len(lignes(texte, mesure, mid)) <= len(ref):
            hi = mid
        else:
            lo = mid
    return lignes(texte, mesure, hi)


class Cinetique:
    """Un texte anime entre `debut` et `fin` (secondes).

    style : px, graisse, cle (graisse du segment surligne), approche, interligne,
    x, y (haut de la premiere ligne), largeur (colonne), centre (bool)."""

    def __init__(self, texte, debut, fin, style, couleur_cle):
        self.debut, self.fin, self.couleur = debut, fin, couleur_cle
        s = self.style = style
        px = s["px"]

        def graisse(hl):
            return s["cle"] if hl else s["graisse"]

        mesure = mesureur(s)
        self.mots, self.marques = [], []
        f = _police(px, s["graisse"])
        asc, _ = f.getmetrics()
        cap = f.getbbox("H")[1]               # haut des capitales sous l'origine du texte
        t = debut + C.ENTREE_DELAI
        for i, ligne in enumerate(equilibrer(texte, mesure, s["largeur"])):
            yy = s["y"] + i * s["interligne"]
            total = sum(mesure(a) for a in ligne)
            x = s["x"] + ((s["largeur"] - total) / 2 if s.get("centre") else 0)
            seg = None                        # [x debut, x fin, instant du premier mot]
            for at in ligne:
                w = mesure(at)
                if at[0] != " ":
                    self.mots.append((at[0], graisse(at[1]), x, yy, t))
                if at[1]:
                    if seg is None:
                        seg = [x, x + w, t]
                    else:
                        seg[1] = x + w
                elif seg is not None and at[0] != " ":
                    self._marque(seg, yy, cap, asc, px); seg = None
                if at[0] != " ":
                    t += C.MOT_DECALAGE
                x += w
            if seg is not None:
                self._marque(seg, yy, cap, asc, px)
        # le dernier mot doit etre pose avant la sortie : sinon on accelere tout
        dispo = (fin - C.SORTIE_DUREE - C.TENUE_MIN) - (debut + C.ENTREE_DELAI)
        pose = t - (debut + C.ENTREE_DELAI)
        if pose > dispo > 0:
            k = dispo / pose
            t0 = debut + C.ENTREE_DELAI
            self.mots = [(m, g, x, y, t0 + (tm - t0) * k) for m, g, x, y, tm in self.mots]
            self.marques = [(a, b, y0, y1, t0 + (tm - t0) * k) for a, b, y0, y1, tm in self.marques]

    def _marque(self, seg, yy, cap, asc, px):
        x0, x1, t_premier = seg
        y0 = yy + cap - int(px * C.SURLIGNE_HAUT)
        y1 = yy + asc + int(px * C.SURLIGNE_BAS)
        # le trait suit les mots du segment pendant qu'ils se posent, comme un feutre
        self.marques.append((x0 - C.SURLIGNE_MARGE, x1 + C.SURLIGNE_MARGE, y0, y1,
                             t_premier + C.SURLIGNE_RETARD))

    def _sortie(self, t):
        if t <= self.fin - C.SORTIE_DUREE:
            return 0.0
        return lisse((t - (self.fin - C.SORTIE_DUREE)) / C.SORTIE_DUREE)

    def dessiner(self, lay, t, final=False):
        s = self.style
        px, ap = s["px"], s["approche"]
        so = 0.0 if final else self._sortie(t)
        if so >= 1:
            return
        a_s, dy_s = 1 - so, -C.SORTIE_MONTEE * so
        etats = []
        for mot, g, x, y, tm in self.mots:
            e = 1.0 if final else lisse((t - tm) / C.MOT_DUREE)
            if e > 0:
                etats.append((mot, g, x, y + C.MOT_MONTEE * (1 - e) + dy_s, e * a_s))
        # 1) ombres de tous les mots, 2) surlignages, 3) lettres : le surlignage reste net
        for mot, g, x, y, a in etats:
            ombre, _, m = sprite(mot, px, g, ap)
            coller(lay, ombre, (x - m, y - m), a)
        for x0, x1, y0, y1, tm in self.marques:
            p = 1.0 if final else lisse((t - tm) / C.SURLIGNE_DUREE)
            if p <= 0:
                continue
            w = max(2, int((x1 - x0) * p))
            barre = Image.new("RGBA", (w, int(y1 - y0)), (0, 0, 0, 0))
            ImageDraw.Draw(barre).rounded_rectangle(
                [0, 0, w - 1, int(y1 - y0) - 1], radius=C.SURLIGNE_RAYON,
                fill=tuple(self.couleur) + (255,))
            coller(lay, barre, (x0, y0 + dy_s), a_s)
        for mot, g, x, y, a in etats:
            _, glyphes, m = sprite(mot, px, g, ap)
            coller(lay, glyphes, (x - m, y - m), a)
