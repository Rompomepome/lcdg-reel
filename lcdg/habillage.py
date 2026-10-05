"""
Moteur d'habillage du reel LCDG, style v2 : accroche, blocs de texte animes, phrases
fortes, chiffres cles, transition en croix, carte finale.
Toutes les constantes viennent de config/charte.py — ne rien coder en dur ici.
"""
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import charte as C
from lcdg import texte as T
from lcdg.logo import lockup

W, H = C.LARGEUR, C.HAUTEUR
NAVY, WHITE = C.NAVY, C.BLANC

_RUBRIQUE = C.PRIMARY


def rubrique(nom: str | None):
    """Fixe la couleur d'accent selon la categorie de l'article (cf. charte.RUBRIQUES)."""
    global _RUBRIQUE
    _RUBRIQUE = C.RUBRIQUES.get(nom or "pro", C.PRIMARY)
    return _RUBRIQUE


# droite autorisee pour les textes (marge du surlignage, +1 car getbbox donne un bord
# droit exclusif) : un surlignage ne se coupe jamais, trop long il deborderait
COLONNE = C.TEXTE_X + C.TEXTE_LARGEUR + C.SURLIGNE_MARGE + 1


def shadow(layer, blur=16, alpha=150, offset=(0, 5)):
    a = layer.split()[3].filter(ImageFilter.GaussianBlur(blur))
    sh = Image.new('RGBA', layer.size, (0, 0, 0, 0))
    sh.putalpha(a.point(lambda p: int(p * alpha / 255)))
    out = Image.new('RGBA', layer.size, (0, 0, 0, 0))
    out.paste(sh, offset, sh)
    out.alpha_composite(layer)
    return out


def hors_zone(layer, droite=W):
    """(haut, bas, droite) des pixels opaques si la couche sort de la zone sure 4:5
    ou depasse `droite`, sinon None."""
    bbox = layer.split()[3].point(lambda p: 255 if p > 128 else 0).getbbox()
    if bbox and (bbox[1] < C.ZONE_SURE_HAUT or bbox[3] > C.ZONE_SURE_BAS or bbox[2] > droite):
        return bbox[1], bbox[3], bbox[2]
    return None


def cross_mask(size, cx=W // 2, cy=H // 2, canvas=(W, H)):
    """Masque en croix medicale, aux proportions du logo."""
    m = Image.new('L', canvas, 0)
    if size <= 2: return m
    d = ImageDraw.Draw(m)
    a, r = size * 0.335, max(2, size * 0.055)
    d.rounded_rectangle([cx - a / 2, cy - size / 2, cx + a / 2, cy + size / 2], radius=r, fill=255)
    d.rounded_rectangle([cx - size / 2, cy - a / 2, cx + size / 2, cy + a / 2], radius=r, fill=255)
    return m


# ---------- couches fixes ----------
_WM = {}
def watermark(size=C.LOGO_PX, margin=C.LOGO_MARGE_X):
    if size not in _WM:
        logo = lockup(size)
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        lay.paste(logo, (W - logo.width - margin, C.LOGO_Y), logo)
        _WM[size] = shadow(lay, blur=12, alpha=140, offset=(0, 4))
    return _WM[size]


def scrim():
    g = Image.new('L', (1, H))
    bas = C.SCRIM_BAS_DEBUT
    for i in range(H):
        t = i / H
        v = int(C.SCRIM_BAS_ALPHA * ((t - bas) / (1 - bas)) ** 1.25) if t > bas else 0
        haut = 1 - (i - C.ZONE_SURE_HAUT) / C.SCRIM_HAUT_PX
        if haut > 0: v = max(v, int(C.SCRIM_HAUT_ALPHA * min(1.0, haut)))
        g.putpixel((0, i), min(v, C.SCRIM_MAX))
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    lay.putalpha(g.resize((W, H)))
    return lay


# ---------- styles de texte ----------
def style_bloc():
    return dict(px=C.BLOC_PX, graisse=C.BLOC_GRAISSE, cle=C.CLE_GRAISSE,
                approche=C.BLOC_APPROCHE, interligne=C.BLOC_INTERLIGNE,
                x=C.TEXTE_X, y=C.BLOC_Y, largeur=C.TEXTE_LARGEUR)


def style_accroche(y, px=None):
    px = px or C.ACCROCHE_PX
    return dict(px=px, graisse=C.ACCROCHE_GRAISSE, cle=C.ACCROCHE_GRAISSE,
                approche=C.ACCROCHE_APPROCHE,
                interligne=round(C.ACCROCHE_INTERLIGNE * px / C.ACCROCHE_PX),
                x=C.TEXTE_X, y=y, largeur=C.TEXTE_LARGEUR)


def style_ajuste(texte):
    """(style au corps de l'accroche, nombre de lignes). Au-dela de ACCROCHE_LIGNES_MAX
    lignes, le corps diminue : une phrase precise ne se raccourcit pas pour tenir."""
    px = C.ACCROCHE_PX
    while True:
        st = style_accroche(0, px)
        n = len(T.equilibrer(texte, T.mesureur(st), st["largeur"]))
        if n <= C.ACCROCHE_LIGNES_MAX or px <= C.ACCROCHE_PX_MIN:
            return st, n
        px -= 4


def style_centre(texte):
    """Corps de l'accroche (ajuste), centre verticalement dans la zone sure."""
    st, n = style_ajuste(texte)
    return style_accroche(C.ACCROCHE_CENTRE - n * st["interligne"] // 2, st["px"])


def _vide():
    return Image.new('RGBA', (W, H), (0, 0, 0, 0))


def voile(lay, opacite):
    """Assombrit tout le cadre (opacite 0 a 1). Pas de cache : une couche pleine par
    valeur d'opacite, pendant les fondus, ferait des centaines de Mo."""
    if opacite <= 0.003:
        return
    lay.alpha_composite(Image.new('RGBA', (W, H), (0, 0, 0, int(255 * opacite))))


_PICTO = {}
def picto(taille):
    """Boite de medicament : carre arrondi blanc frappe d'une croix de la rubrique."""
    cle = (taille, tuple(_RUBRIQUE))
    if cle not in _PICTO:
        m = max(6, taille // 5)                       # marge pour l'ombre
        im = Image.new('RGBA', (taille + 2 * m, taille + 2 * m), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([m, m, m + taille - 1, m + taille - 1],
                            radius=max(4, int(taille * C.PICTO_RAYON)),
                            fill=WHITE + (C.PICTO_OPACITE,))
        longueur, epaisseur = C.PICTO_CROIX
        c, b, l = m + taille / 2, taille * longueur, max(2, taille * epaisseur)
        d.rectangle([c - l / 2, c - b / 2, c + l / 2, c + b / 2], fill=tuple(_RUBRIQUE) + (255,))
        d.rectangle([c - b / 2, c - l / 2, c + b / 2, c + l / 2], fill=tuple(_RUBRIQUE) + (255,))
        _PICTO[cle] = (shadow(im, blur=max(3, taille // 10), alpha=C.PICTO_OMBRE,
                              offset=(0, 2)), m)
    return _PICTO[cle]


# ---------- scenes ----------
class Texte:
    """Bloc de texte. Un '|' le decoupe en temps successifs sur le meme plan.
    grand=True : phrase forte, au corps de l'accroche, centree, sur fond voile."""

    def __init__(self, nom, texte, debut, fin, grand=False, instants=None, retard=0.0):
        """instants : debut de chaque temps apres le premier, relatif au debut du bloc
        (donnes par la voix off) ; sinon les temps se partagent le bloc au prorata des mots.
        retard : le premier temps arrive plus tard (entree du reel, cf. Ouverture)."""
        self.nom, self.debut, self.fin, self.grand = nom, debut, fin, grand
        temps = [b.strip() for b in texte.split('|') if b.strip()]
        poids = [max(1, len(b.replace('*', '').split())) for b in temps]
        cales = instants is not None and len(instants) == len(temps) - 1
        self.parts, t = [], debut + retard
        for k, (b, p) in enumerate(zip(temps, poids)):
            if k == len(temps) - 1:
                f = fin
            elif cales:
                f = min(fin, debut + instants[k])
            else:
                f = t + (fin - debut) * p / sum(poids)
            st = style_centre(b) if grand else style_bloc()
            self.parts.append(T.Cinetique(b, t, f, st, _RUBRIQUE))
            t = f

    def dessiner(self, lay, t):
        for c in self.parts:
            if c.debut <= t < c.fin:
                c.dessiner(lay, t)

    def voiler(self, lay, t):
        if self.grand:
            voile(lay, C.VOILE_PHRASE * T.lisse((t - self.debut) / C.VOILE_DUREE)
                  * (1 - self.parts[-1]._sortie(t)))

    def couches(self):
        out = []
        for k, c in enumerate(self.parts):
            lay = _vide(); c.dessiner(lay, 0, final=True)
            out.append((self.nom + (f" (temps {k + 1})" if len(self.parts) > 1 else ""),
                        lay, COLONNE))
        return out


def pastille(texte):
    """Pastille du sujet : capitales blanches sur la couleur de la rubrique."""
    label = texte.upper()
    lw = T.largeur(label, C.SURTITRE_PX, C.SURTITRE_GRAISSE, C.SURTITRE_APPROCHE)
    pw, ph = int(lw + 2 * C.SURTITRE_PAD), C.SURTITRE_H
    im = Image.new('RGBA', (pw, ph), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle([0, 0, pw - 1, ph - 1], radius=C.RADIUS,
                                         fill=tuple(_RUBRIQUE) + (255,))
    _, gl, m = T.sprite(label, C.SURTITRE_PX, C.SURTITRE_GRAISSE, C.SURTITRE_APPROCHE)
    f = T._police(C.SURTITRE_PX, C.SURTITRE_GRAISSE)
    cap = f.getbbox("H")
    dy = (ph - (cap[3] - cap[1])) // 2 - cap[1]
    im.alpha_composite(gl, (C.SURTITRE_PAD - m, dy - m))
    return im


class Accroche:
    """Ouverture : pastille du sujet (label) puis phrase d'accroche (sous_titre),
    centrees ensemble dans la zone sure. Le premier mot arrive des 0,2 s."""

    def __init__(self, label, accroche, debut, fin):
        self.nom, self.debut, self.fin = "accroche", debut, fin
        st, n = style_ajuste(accroche)
        haut = C.SURTITRE_H + C.SURTITRE_ECART + n * st["interligne"]
        self.y = C.ACCROCHE_CENTRE - haut // 2
        self.texte = T.Cinetique(accroche, debut + C.PASTILLE_DUREE * 0.4, fin,
                                 style_accroche(self.y + C.SURTITRE_H + C.SURTITRE_ECART,
                                                st["px"]),
                                 _RUBRIQUE)
        self.pastille = pastille(label)

    def dessiner(self, lay, t, final=False):
        so = 0.0 if final else self.texte._sortie(t)
        if so >= 1:
            return
        p = 1.0 if final else T.lisse((t - self.debut) / C.PASTILLE_DUREE)
        if p > 0:
            w = max(1, int(self.pastille.width * p))
            T.coller(lay, self.pastille.crop((0, 0, w, self.pastille.height)),
                     (C.TEXTE_X, self.y - C.SORTIE_MONTEE * so), 1 - so)
        self.texte.dessiner(lay, t, final)

    def voiler(self, lay, t):
        voile(lay, C.VOILE_ACCROCHE * T.lisse((t - self.debut) / C.VOILE_DUREE)
              * (1 - self.texte._sortie(t)))

    def couches(self):
        lay = _vide(); self.dessiner(lay, 0, final=True)
        return [(self.nom, lay, COLONNE)]


class Chiffre:
    """Chiffre cle : la valeur defile jusqu'a sa cible, l'ancienne valeur est barree,
    la legende se pose dessous a la place habituelle du texte. Avec "pictos", une boite
    par unite s'allume (ou s'eteint) au rythme du compteur, au-dessus du chiffre.

    Champs du bloc : valeur, depuis (optionnel), prefixe, suffixe, decimales,
    compte (defaut vrai), pictos (defaut faux), legende."""

    def __init__(self, nom, bl, debut, fin):
        self.nom, self.debut, self.fin = nom, debut, fin
        self.valeur = bl["valeur"]
        self.depuis = bl.get("depuis")
        self.compte = bl.get("compte", True)
        self.dec = bl.get("decimales", 0)
        suf = bl.get("suffixe", "")
        # une unite en toutes lettres ("boites") passe en petit, sur la ligne de base du
        # chiffre ; un symbole (EUR, %) garde le corps du chiffre, avec une espace fine :
        # une espace pleine ouvrirait un trou a ce corps
        self.suf_mot = sum(ch.isalpha() for ch in suf) >= 3
        suf, pre = T.normaliser(suf), T.normaliser(bl.get("prefixe", ""))
        self.suf = suf if self.suf_mot else suf.replace(" ", "\u2009")
        self.pre = pre.replace(" ", "\u2009")
        self.legende = T.Cinetique(bl.get("legende", ""),
                                   debut + C.COMPTE_DELAI + C.COMPTE_DUREE * 0.5,
                                   fin, style_bloc(), _RUBRIQUE)
        # le compteur affiche aussi la valeur de depart : le corps se regle sur la plus large
        valeurs = [self.valeur] + ([self.depuis] if self.compte and self.depuis is not None else [])
        px = C.CHIFFRE_PX
        while px > C.ANCIEN_PX and max(self._largeur(v, px) for v in valeurs) > C.TEXTE_LARGEUR:
            px -= 4
        self.px = px
        self.px_suf = int(px * C.UNITE_ECHELLE) if self.suf_mot else px
        f = T._police(px, C.CHIFFRE_GRAISSE)
        self.asc, _ = f.getmetrics()
        self.y = C.BLOC_Y - C.CHIFFRE_ECART - self.asc       # origine du trace du chiffre
        haut = self.y + f.getbbox("0")[1]                    # haut visible des chiffres
        if self.depuis is not None:
            fa = T._police(C.ANCIEN_PX, C.ANCIEN_GRAISSE)
            asc_a, _ = fa.getmetrics()
            self.y_ancien = haut - C.ANCIEN_ECART - asc_a
            b = fa.getbbox("0")
            self.y_barre = self.y_ancien + (b[1] + b[3]) // 2
            self.w_ancien = T.largeur(self.texte(self.depuis), C.ANCIEN_PX, C.ANCIEN_GRAISSE, 0)
            haut = self.y_ancien + b[1]
        self.pictos = self._pictos(haut) if bl.get("pictos") else None

    # -- texte du chiffre
    def nombre(self, v):
        return f"{v:,.{self.dec}f}".replace(",", "\u2009").replace(".", ",")

    def texte(self, v):
        return self.pre + self.nombre(v) + self.suf

    def _largeur(self, v, px):
        g, ap = C.CHIFFRE_GRAISSE, C.CHIFFRE_APPROCHE
        w = T.largeur(self.pre + self.nombre(v), px, g, ap)
        if self.suf_mot:
            return w + T.largeur(self.suf, int(px * C.UNITE_ECHELLE), g, 0)
        return w + T.largeur(self.suf, px, g, ap)

    def _valeur(self, lay, v, y, alpha):
        """Prefixe et unite dans la couleur de la rubrique, chiffre en blanc."""
        g, ap = C.CHIFFRE_GRAISSE, C.CHIFFRE_APPROCHE
        x = C.TEXTE_X
        for morceau, couleur in ((self.pre, _RUBRIQUE), (self.nombre(v), WHITE)):
            if not morceau:
                continue
            om, gl, m = T.sprite_chiffre(morceau, self.px, g, ap, tuple(couleur))
            T.coller(lay, om, (x - m, y - m), alpha)
            T.coller(lay, gl, (x - m, y - m), alpha)
            x += T.largeur(morceau, self.px, g, ap) + ap * self.px
        if self.suf:
            asc_s, _ = T._police(self.px_suf, g).getmetrics()
            ys = y + self.asc - asc_s                        # meme ligne de base
            om, gl, m = T.sprite(self.suf, self.px_suf, g, 0 if self.suf_mot else ap,
                                 tuple(_RUBRIQUE))
            T.coller(lay, om, (x - m, ys - m), alpha)
            T.coller(lay, gl, (x - m, ys - m), alpha)

    # -- pictogrammes
    def _pictos(self, bas):
        n = int(round(max(self.valeur, self.depuis or 0)))
        if n < 1 or n > C.PICTO_MAX:
            return None
        if n <= C.PICTO_GRAND_MAX:
            s, g, cols = C.PICTO_GRAND, C.PICTO_GRAND_ECART, n
            # une ligne de grandes boites tient dans la colonne : au-dela de 7 boites
            # (9:16), elles retrecissent
            k = min(1.0, (C.TEXTE_LARGEUR + g) / (n * (s + g)))
            s, g = int(s * k), int(g * k)
        else:
            s, g, cols = C.PICTO_PX, C.PICTO_ECART, C.PICTO_COLONNES
        lignes = -(-n // cols)
        haut = bas - C.PICTO_MARGE - lignes * (s + g) + g
        return s, [(C.TEXTE_X + (i % cols) * (s + g), haut + (i // cols) * (s + g))
                   for i in range(n)]

    def _dessiner_pictos(self, lay, v, t, a_s, dy_s, final):
        s, pos = self.pictos
        sp, m = picto(s)
        v0 = self.depuis if self.depuis is not None else 0
        t0 = self.debut + C.ENTREE_DELAI
        for i, (x, y) in enumerate(pos):
            allume = min(1.0, max(0.0, v - i))
            if i < v0:
                # deja la au depart : apparait avec le chiffre, s'eteint si le compte descend
                e = 1.0 if final else T.lisse((t - t0 - i * C.PICTO_DECALAGE) / C.MOT_DUREE)
                a = e * (C.PICTO_ETEINT + (1 - C.PICTO_ETEINT) * allume)
                k = 1.0
            else:
                # une boite qui s'allume rebondit : elle part petite et se pose a sa taille
                a = allume
                k = C.PICTO_ECHELLE + (1 - C.PICTO_ECHELLE) * T.rebond(allume)
            im = sp if abs(k - 1) < 0.01 else sp.resize(
                (max(1, int(sp.width * k)), max(1, int(sp.height * k))), Image.BICUBIC)
            cx, cy = x - m + sp.width / 2, y - m + sp.height / 2 + dy_s
            T.coller(lay, im, (cx - im.width / 2, cy - im.height / 2), min(1.0, a * a_s))

    def dessiner(self, lay, t, final=False):
        so = 0.0 if final else self.legende._sortie(t)
        if so >= 1:
            return
        a_s, dy_s = 1 - so, -C.SORTIE_MONTEE * so
        t0 = self.debut + C.ENTREE_DELAI
        v0 = self.depuis if self.depuis is not None else 0
        k = 1.0 if (final or not self.compte) else T.lisse(
            (t - (self.debut + C.COMPTE_DELAI)) / C.COMPTE_DUREE)
        v_continu = v0 + (self.valeur - v0) * k if self.compte else self.valeur
        if self.pictos:
            self._dessiner_pictos(lay, v_continu, t, a_s, dy_s, final)
        if self.depuis is not None:
            e = 1.0 if final else T.lisse((t - t0) / C.MOT_DUREE)
            om, gl, m = T.sprite(self.texte(self.depuis), C.ANCIEN_PX, C.ANCIEN_GRAISSE, 0)
            y = self.y_ancien + C.MOT_MONTEE * (1 - e) + dy_s
            T.coller(lay, om, (C.TEXTE_X - m, y - m), e * a_s)
            T.coller(lay, gl, (C.TEXTE_X - m, y - m), e * a_s * C.ANCIEN_ALPHA)
            p = 1.0 if final else T.lisse((t - (t0 + C.BARRE_DELAI)) / C.BARRE_DUREE)
            if p > 0:
                largeur_barre = self.w_ancien + 2 * C.BARRE_DEBORD
                barre = Image.new('RGBA', (max(1, int(largeur_barre * p)), C.BARRE_PX),
                                  tuple(_RUBRIQUE) + (255,))
                T.coller(lay, barre, (C.TEXTE_X - C.BARRE_DEBORD,
                                      self.y_barre - C.BARRE_PX // 2 + dy_s), a_s)
        e = 1.0 if final else T.lisse((t - (t0 + C.CHIFFRE_DELAI)) / C.MOT_DUREE)
        if e > 0:
            v = round(v_continu, self.dec) if self.dec else int(round(v_continu))
            self._valeur(lay, v, self.y + C.MOT_MONTEE * (1 - e) + dy_s, e * a_s)
        self.legende.dessiner(lay, t, final)

    def voiler(self, lay, t):
        voile(lay, C.VOILE_CHIFFRE * T.lisse((t - self.debut) / C.VOILE_DUREE)
              * (1 - self.legende._sortie(t)))

    def couches(self):
        lay = _vide(); self.dessiner(lay, 0, final=True)
        out = [(self.nom, lay, COLONNE)]
        if self.compte and self.depuis is not None:
            # le compteur part de l'ancienne valeur : elle doit tenir dans la colonne aussi
            depart = _vide(); self._valeur(depart, self.depuis, self.y, 1.0)
            out.append((self.nom + " (depart du compteur)", depart, COLONNE))
        return out


def _bbox(lay, marge=0):
    """Boite englobante des pixels nettement visibles d'une couche (ombres legeres
    exclues), elargie de marge ; None si la couche est vide."""
    b = lay.getchannel("A").point(lambda v: 255 if v > 24 else 0).getbbox()
    return None if b is None else (b[0] - marge, b[1] - marge, b[2] + marge, b[3] + marge)


def _croise(a, b):
    return (a is not None and b is not None
            and a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3])


class Bandeau:
    """Invitation a commenter, en haut a gauche, en blanc sans fond : la raison en petit
    corps, l'appel (la ligne qui porte le mot cle) en plus grand, pour qu'on le voie. Le mot
    cle (entre asterisques) dans un encadre de la couleur de la rubrique, en blanc,
    legerement penche. Un "|" passe a la ligne. Visible du premier bloc a la croix : les
    lignes glissent depuis la gauche, l'encadre s'ouvre avec un rebond, puis le tout
    repart vers la gauche. Il fait de meme pour laisser la place a un bloc qui entrerait
    dans sa zone (scenes), et revient apres lui."""

    def __init__(self, texte, debut, fin, scenes=()):
        self.debut, self.fin = debut, fin
        g = C.BANDEAU_GRAISSE
        self.marge = m = C.HALO_FLOU * 2
        self.lignes = []           # par ligne : mots (ombre, glyphes, x, y) et encadres (image, centre)
        y = C.BANDEAU_Y
        for ligne in (l.strip() for l in texte.split('|') if l.strip()):
            atomes = T.atomes(ligne)
            px = self._corps_appel(atomes) if any(at[1] for at in atomes) else C.BANDEAU_PX
            cap = T._police(px, g).getbbox("H")
            x = 0.0
            mots, boites = [], []
            for at in atomes:
                mot, cle = at[0], at[1]
                if mot == " ":
                    x += T.largeur(" ", px, g, 0)
                elif cle:
                    boite, bw = self._boite(mot, px)
                    boites.append((boite, (C.TEXTE_X + x + bw / 2, y + (cap[1] + cap[3]) / 2)))
                    x += bw
                else:
                    om, gl, _ = T.sprite(mot, px, g, 0)
                    mots.append((om, gl, C.TEXTE_X + x - m, y - m))
                    x += T.largeur(mot, px, g, 0)
            self.lignes.append((mots, boites))
            y += round(px * C.BANDEAU_INTERLIGNE)
        self.segments = self._segments(scenes)

    def _segments(self, scenes):
        """Intervalles (debut, fin) ou le bandeau est visible."""
        zone = _bbox(self.couche(), C.BANDEAU_ECART_BLOC)
        pauses = sorted((sc.debut, sc.fin) for sc in scenes
                        if any(_croise(zone, _bbox(lay)) for _, lay, _ in sc.couches()))
        segs, a = [], self.debut
        for p0, p1 in pauses:
            if p1 <= a or p0 >= self.fin:
                continue
            if p0 - a >= C.BANDEAU_SEGMENT_MIN:
                segs.append((a, p0))
            a = max(a, p1)
        if self.fin - a >= C.BANDEAU_SEGMENT_MIN:
            segs.append((a, self.fin))
        return segs

    @staticmethod
    def _corps_appel(atomes):
        """Corps de la ligne du mot cle : BANDEAU_ACTION_PX, moins si la ligne ne tient pas
        entre la marge et le logo (ombres comprises), jamais sous BANDEAU_ACTION_PX_MIN."""
        g = C.BANDEAU_GRAISSE
        dispo = (watermark().getchannel("A").getbbox()[0] - C.BANDEAU_ECART_LOGO - C.TEXTE_X
                 - 4)                                     # ombre de l'encadre

        def largeur(px):
            total = 0.0
            for at in atomes:
                mot, cle = at[0], at[1]
                if mot == " ":
                    total += T.largeur(" ", px, g, 0)
                elif cle:
                    total += T.largeur(mot, px, C.CLE_GRAISSE, 0) + 2 * round(px * C.BANDEAU_BOITE_PAD[0])
                else:
                    total += T.largeur(mot, px, g, 0)
            return total

        px = C.BANDEAU_ACTION_PX
        while px > C.BANDEAU_ACTION_PX_MIN and largeur(px) > dispo:
            px -= 1
        return px

    @staticmethod
    def _boite(mot, px):
        """(encadre penche, largeur avant rotation) du mot cle, au corps de sa ligne."""
        g = C.CLE_GRAISSE
        f = T._police(px, g)
        cap = f.getbbox("H")
        pad_x, pad_y = (round(px * r) for r in C.BANDEAU_BOITE_PAD)
        bw = int(T.largeur(mot, px, g, 0) + 2 * pad_x)
        bh = int(cap[3] - cap[1] + 2 * pad_y)
        im = Image.new('RGBA', (bw, bh), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([0, 0, bw - 1, bh - 1], radius=round(px * C.BANDEAU_BOITE_RAYON),
                            fill=tuple(_RUBRIQUE) + (255,))
        d.text((pad_x, pad_y - cap[1]), mot, font=f, fill=WHITE + (255,))
        im = im.rotate(C.BANDEAU_INCLINAISON, resample=Image.BICUBIC, expand=True)
        return shadow(im, blur=5, alpha=110, offset=(0, 2)), bw

    def dessiner(self, lay, t, final=False):
        debut = fin = 0.0
        if not final:
            seg = next(((a, b) for a, b in self.segments if a <= t < b), None)
            if seg is None:
                return
            debut, fin = seg
        sortie = 0.0 if final else T.lisse((t - (fin - C.BANDEAU_FONDU)) / C.BANDEAU_FONDU)
        for i, (mots, boites) in enumerate(self.lignes):
            t0 = debut + i * C.BANDEAU_DECALAGE
            e = 1.0 if final else T.lisse((t - t0) / C.BANDEAU_ENTREE)
            alpha = e * (1 - sortie) * C.BANDEAU_ALPHA
            if alpha <= 0.003:
                continue
            dx = -C.BANDEAU_GLISSEMENT * ((1 - e) + sortie)
            for om, gl, x, y in mots:
                T.coller(lay, om, (x + dx, y), alpha)
                T.coller(lay, gl, (x + dx, y), alpha)
            p = 1.0 if final else T.rebond((t - t0 - C.BANDEAU_BOITE_RETARD) / C.BANDEAU_BOITE_POP)
            if p <= 0:
                continue
            k = C.BANDEAU_BOITE_ECHELLE + (1 - C.BANDEAU_BOITE_ECHELLE) * p
            for boite, (cx, cy) in boites:
                im = boite if abs(k - 1) < 0.01 else boite.resize(
                    (max(1, int(boite.width * k)), max(1, int(boite.height * k))), Image.BICUBIC)
                T.coller(lay, im, (cx + dx - im.width / 2, cy - im.height / 2),
                         min(1.0, (1 - sortie) * C.BANDEAU_ALPHA * min(1.0, p * 2)))

    def couche(self):
        lay = _vide(); self.dessiner(lay, 0, final=True)
        return lay


class Credit:
    """Source d'un plan (champ "credit" du bloc), en petit sous le logo, alignee sur sa
    droite, le temps du plan."""

    def __init__(self, texte, debut, fin):
        self.debut, self.fin = debut, fin
        px, g = C.CREDIT_PX, C.CREDIT_GRAISSE
        m = C.HALO_FLOU * 2
        self.ombre, self.glyphes, _ = T.sprite(texte, px, g, 0)
        x = W - C.LOGO_MARGE_X - T.largeur(texte, px, g, 0)
        y = C.LOGO_Y + lockup(C.LOGO_PX).height + C.CREDIT_ECART
        self.pos = (x - m, y - m)

    def dessiner(self, lay, t, final=False):
        a = 1.0 if final else min(T.lisse((t - self.debut) / C.CREDIT_FONDU),
                                  T.lisse((self.fin - t) / C.CREDIT_FONDU))
        if a <= 0.003:
            return
        T.coller(lay, self.ombre, self.pos, a * C.CREDIT_ALPHA)
        T.coller(lay, self.glyphes, self.pos, a * C.CREDIT_ALPHA)

    def couche(self):
        lay = _vide(); self.dessiner(lay, 0, final=True)
        return lay


def credits(ep, bornes):
    return [Credit(bl["credit"], a, b) for (a, b), bl in zip(bornes, ep["blocs"])
            if bl.get("credit")]


# types de bloc dont l'arriere-plan passe en flou de profondeur (cf. montage.base)
TYPES_FLOUS = ("chiffre",)


def scenes(ep, bornes, croix):
    """Les scenes du reel, dans l'ordre : accroche sur le premier plan, puis un bloc par plan."""
    out = [Accroche(ep["label"], ep["sous_titre"], 0.0, bornes[0][1])]
    blocs = ep["blocs"]
    for k in range(1, len(blocs)):
        a, b = bornes[k]
        if k == len(blocs) - 1:
            b = croix + C.BLOC_RESIDU
        bl = blocs[k]
        if bl.get("type") == "chiffre":
            out.append(Chiffre(f"bloc {k}", bl, a, b))
        else:
            entree = C.ACCROCHE_COUVERTURE and k == 1
            out.append(Texte(f"bloc {k}", bl["texte"], a, b, grand=bl.get("type") == "phrase",
                             instants=bl.get("temps"),
                             retard=C.OUVERTURE_TEXTE_DELAI if entree else 0.0))
    return out


class Ouverture:
    """Entree du reel livre, quand l'accroche ne sert que de couverture : un eclair blanc
    tres bref, puis la pastille du sujet s'ouvre au-dessus du premier texte et un reflet la
    traverse ; elle sort avec le texte du bloc. L'image, elle, arrive en zoom et floue
    (montage.base). Aucun bruitage (Romain, 02/10/2026)."""

    def __init__(self, texte, scene):
        self.scene, self.debut, self.fin = scene, scene.debut, scene.fin
        self.pastille = pastille(texte)
        hauts = [b[1] for b in (_bbox(lay) for _, lay, _ in scene.couches()) if b]
        haut = min(hauts) if hauts else C.BLOC_Y
        self.pos = (C.TEXTE_X, haut - C.SURTITRE_ECART - self.pastille.height)

    def _sortie(self, t):
        cine = self.scene.parts[-1] if isinstance(self.scene, Texte) else self.scene.legende
        return cine._sortie(t)

    @staticmethod
    def _reflet(im, q):
        """Bande de lumiere inclinee qui traverse la pastille (q de 0 a 1)."""
        w, h = im.size
        bande = Image.new('L', (w, h), 0)
        large = h * 0.8
        x = -large + (w + 2 * large) * q
        ImageDraw.Draw(bande).polygon([(x, 0), (x + large * 0.55, 0),
                                       (x + large * 0.55 - h * 0.45, h), (x - h * 0.45, h)],
                                      fill=C.OUVERTURE_REFLET_ALPHA)
        lumiere = Image.new('RGBA', (w, h), (255, 255, 255, 0))
        lumiere.putalpha(ImageChops.multiply(bande, im.getchannel('A')))
        out = im.copy()
        out.alpha_composite(lumiere)
        return out

    def dessiner(self, lay, t, final=False):
        if not final:
            e = (t - self.debut) / C.OUVERTURE_ECLAIR_DUREE
            if 0 <= e < 1:
                a = int(255 * C.OUVERTURE_ECLAIR * (1 - T.lisse(e)))
                if a > 1:
                    lay.alpha_composite(Image.new('RGBA', (W, H), (255, 255, 255, a)))
        so = 0.0 if final else self._sortie(t)
        if so >= 1:
            return
        p = 1.0 if final else T.lisse((t - self.debut - C.OUVERTURE_BADGE_DELAI) / C.PASTILLE_DUREE)
        if p <= 0:
            return
        im = self.pastille.crop((0, 0, max(1, int(self.pastille.width * p)), self.pastille.height))
        if not final:
            r0, rd = C.OUVERTURE_REFLET
            q = (t - self.debut - r0) / rd
            if 0 < q < 1:
                im = self._reflet(im, q)
        T.coller(lay, im, (self.pos[0], self.pos[1] - C.SORTIE_MONTEE * so), 1 - so)

    def couche(self):
        lay = _vide(); self.dessiner(lay, 0, final=True)
        return lay


def ouverture(ep, scenes):
    """L'entree animee du reel livre, si l'accroche ne sert que de couverture."""
    if not (C.ACCROCHE_COUVERTURE and len(scenes) > 1):
        return None
    return Ouverture(ep.get("badge") or ep["label"], scenes[1])


class CarteFinale:
    """Carte navy apres la croix : logo, appel a l'action (celui du script, sinon celui
    de la charte), lien, rappel de l'endroit ou cliquer, mention."""

    def __init__(self, debut, appel=None):
        self.debut = debut
        self.logo = lockup(200)
        self.texte_appel = appel or C.APPEL
        st = dict(px=C.APPEL_PX, graisse=C.APPEL_GRAISSE, cle=C.APPEL_GRAISSE,
                  approche=0, interligne=int(C.APPEL_PX * 1.25),
                  x=0, y=C.OUTRO_APPEL_Y, largeur=W, centre=True)
        # l'appel tient sur une ligne : une deuxieme passerait sous le lien
        self.lignes_appel = len(T.equilibrer(self.texte_appel, T.mesureur(st), C.TEXTE_LARGEUR))
        self.appel = T.Cinetique(self.texte_appel, debut + C.OUTRO_FONDU * 0.6, float("inf"),
                                 st, _RUBRIQUE)
        self.t_lien = self.appel.mots[-1][4] + C.MOT_DUREE * 0.6
        st_rappel = dict(px=C.RAPPEL_PX, graisse=C.RAPPEL_GRAISSE, cle=C.RAPPEL_GRAISSE,
                         approche=0, interligne=int(C.RAPPEL_PX * 1.25),
                         x=0, y=C.OUTRO_RAPPEL_Y, largeur=W, centre=True)
        self.rappel = T.Cinetique(C.APPEL_RAPPEL, self.t_lien + C.SURLIGNE_DUREE,
                                  float("inf"), st_rappel, _RUBRIQUE)
        lw = T.largeur(C.LIEN, C.LIEN_PX, C.LIEN_GRAISSE, 0)
        bw, bh = int(lw + 64), C.LIEN_H
        self.pilule = Image.new('RGBA', (bw, bh), (0, 0, 0, 0))
        ImageDraw.Draw(self.pilule).rounded_rectangle(
            [0, 0, bw - 1, bh - 1], radius=C.RADIUS, fill=tuple(_RUBRIQUE) + (255,))
        _, gl, m = T.sprite(C.LIEN, C.LIEN_PX, C.LIEN_GRAISSE, 0)
        f = T._police(C.LIEN_PX, C.LIEN_GRAISSE)
        b = f.getbbox("Hd")
        self.pilule.alpha_composite(gl, (32 - m, (bh - (b[3] - b[1])) // 2 - b[1] - m))
        self.mention = Image.new('RGBA', (W, 60), (0, 0, 0, 0))
        ImageDraw.Draw(self.mention).text((W // 2, 30), C.MENTION,
                                          font=T._police(30, "Medium"),
                                          fill=(150, 146, 175, 255), anchor='mm')

    def dessiner(self, lay, t, final=False):
        e = 1.0 if final else T.lisse((t - self.debut) / C.OUTRO_FONDU)
        if e <= 0:
            return
        T.coller(lay, self.logo, ((W - self.logo.width) // 2,
                                  C.OUTRO_LOGO_Y + C.MOT_MONTEE * (1 - e)), e)
        self.appel.dessiner(lay, t, final)
        p = 1.0 if final else T.lisse((t - self.t_lien) / C.SURLIGNE_DUREE)
        if p > 0:
            bw = self.pilule.width
            w = max(2, int(bw * p))
            x0 = (bw - w) // 2
            T.coller(lay, self.pilule.crop((x0, 0, x0 + w, self.pilule.height)),
                     ((W - bw) // 2 + x0, C.OUTRO_LIEN_Y))
        self.rappel.dessiner(lay, t, final)
        T.coller(lay, self.mention, (0, C.OUTRO_MENTION_Y - 30), e)

    def couche(self):
        lay = _vide(); self.dessiner(lay, 0, final=True)
        return lay


def cross_wipe(p):
    """Transition finale : la croix medicale s'ouvre et remplit le cadre en navy.
    p 0->1. Phase 1 : la croix grandit et se lit. Phase 2 : elle envahit tout."""
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    if p <= 0: return lay
    if p < 0.42:
        e = (p / 0.42) ** 0.55
        size = 620 * e
    else:
        e = ((p - 0.42) / 0.58) ** 2.1
        size = 620 + (3400 - 620) * e
    fill = Image.new('RGBA', (W, H), NAVY + (255,))
    lay.paste(fill, (0, 0), cross_mask(size))
    return lay


def evenements(ep, bornes, croix):
    """Instants des animations qui portent un bruitage, en (secondes, nom de son). Calcules
    sur les memes scenes que l'image : un bruitage ne peut pas se decaler du motion."""
    from lcdg import inserts as ins          # inserts importe habillage : import ici
    out = []        # aucun bruitage a l'ouverture du reel (Romain, 02/10/2026)
    les_scenes = scenes(ep, bornes, croix)
    for i in ins.inserts(ep, les_scenes, ouverture(ep, les_scenes)):
        out += i.sons()
    for sc in les_scenes:
        if isinstance(sc, Accroche):
            out += [(m[4], "clic") for m in sc.texte.marques]
        elif isinstance(sc, Chiffre):
            out.append((sc.debut, "souffle"))
            if sc.compte:
                out.append((sc.debut + C.COMPTE_DELAI, "compteur"))
                out.append((sc.debut + C.COMPTE_DELAI + C.COMPTE_DUREE * C.IMPACT_COMPTE, "impact"))
            out += [(m[4], "clic") for m in sc.legende.marques]
        else:
            out.append((sc.debut, "impact" if sc.grand else "souffle"))
            for c in sc.parts:
                out += [(m[4], "clic") for m in c.marques]
    out.append((croix, "transition"))
    out.append((CarteFinale(croix + C.CROIX_DUREE, ep.get("appel")).t_lien, "carillon"))
    # rien avant le debut du reel livre, ni dans ses premiers instants (Romain, 02/10/2026)
    debut = bornes[1][0] if C.ACCROCHE_COUVERTURE and len(bornes) > 1 else 0.0
    return sorted((t, nom) for t, nom in out if t >= debut + C.DEBUT_SANS_BRUITAGE)
