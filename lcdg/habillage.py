"""
Moteur d'habillage du reel LCDG, style v2 : accroche, blocs de texte animes, phrases
fortes, chiffres cles, transition en croix, carte finale.
Toutes les constantes viennent de config/charte.py — ne rien coder en dur ici.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

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
def watermark(size=C.LOGO_PX, margin=C.LOGO_MARGE):
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


def style_accroche(y):
    return dict(px=C.ACCROCHE_PX, graisse=C.ACCROCHE_GRAISSE, cle=C.ACCROCHE_GRAISSE,
                approche=C.ACCROCHE_APPROCHE, interligne=C.ACCROCHE_INTERLIGNE,
                x=C.TEXTE_X, y=y, largeur=C.TEXTE_LARGEUR)


def style_centre(texte):
    """Corps de l'accroche, centre verticalement dans la zone sure."""
    st = style_accroche(0)
    n = len(T.equilibrer(texte, T.mesureur(st), st["largeur"]))
    return style_accroche(C.ACCROCHE_CENTRE - n * C.ACCROCHE_INTERLIGNE // 2)


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

    def __init__(self, nom, texte, debut, fin, grand=False):
        self.nom, self.debut, self.fin, self.grand = nom, debut, fin, grand
        temps = [b.strip() for b in texte.split('|') if b.strip()]
        poids = [max(1, len(b.replace('*', '').split())) for b in temps]
        self.parts, t = [], debut
        for k, (b, p) in enumerate(zip(temps, poids)):
            f = fin if k == len(temps) - 1 else t + (fin - debut) * p / sum(poids)
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


class Accroche:
    """Ouverture : pastille du sujet (label) puis phrase d'accroche (sous_titre),
    centrees ensemble dans la zone sure. Le premier mot arrive des 0,2 s."""

    def __init__(self, label, accroche, debut, fin):
        self.nom, self.debut, self.fin = "accroche", debut, fin
        st = style_accroche(0)
        n = len(T.equilibrer(accroche, T.mesureur(st), st["largeur"]))
        haut = C.SURTITRE_H + C.SURTITRE_ECART + n * C.ACCROCHE_INTERLIGNE
        self.y = C.ACCROCHE_CENTRE - haut // 2
        self.texte = T.Cinetique(accroche, debut + C.PASTILLE_DUREE * 0.4, fin,
                                 style_accroche(self.y + C.SURTITRE_H + C.SURTITRE_ECART),
                                 _RUBRIQUE)
        self.label = label.upper()
        lw = T.largeur(self.label, C.SURTITRE_PX, C.SURTITRE_GRAISSE, C.SURTITRE_APPROCHE)
        pw, ph = int(lw + 2 * C.SURTITRE_PAD), C.SURTITRE_H
        self.pastille = Image.new('RGBA', (pw, ph), (0, 0, 0, 0))
        ImageDraw.Draw(self.pastille).rounded_rectangle(
            [0, 0, pw - 1, ph - 1], radius=C.RADIUS, fill=tuple(_RUBRIQUE) + (255,))
        _, gl, m = T.sprite(self.label, C.SURTITRE_PX, C.SURTITRE_GRAISSE, C.SURTITRE_APPROCHE)
        f = T._police(C.SURTITRE_PX, C.SURTITRE_GRAISSE)
        haut_cap = f.getbbox("H")
        dy = (ph - (haut_cap[3] - haut_cap[1])) // 2 - haut_cap[1]
        self.pastille.alpha_composite(gl, (C.SURTITRE_PAD - m, dy - m))

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
            else:
                a = allume
            T.coller(lay, sp, (x - m, y - m + dy_s), a * a_s)

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
            out.append(Texte(f"bloc {k}", bl["texte"], a, b, grand=bl.get("type") == "phrase"))
    return out


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
