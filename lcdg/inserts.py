"""
Inserts animes : de petites illustrations posees au-dessus du texte d'un bloc, pour faire
comprendre l'information d'un coup d'oeil (Romain, 05/10/2026 : « les inserts et les
illustrations en plus, ca aide a la comprehension »).

Champ "insert" d'un bloc de texte (pas d'une phrase forte ni d'un chiffre cle) :

  {"type": "verrou", "n": 3}
      les recommandations de l'article, en cartes fermees d'un cadenas (dernier bloc)
  {"type": "calendrier", "annee": 2026, "mois": 10, "du": 12, "au": 18, "legende": "mi-octobre"}
      le mois, la periode surlignee (sur une meme semaine), une etiquette
  {"type": "barres", "unite": "×", "lignes": [{"label": "Sans désogestrel", "valeur": 1}, ...]}
      des barres qui poussent ; une valeur de 1 en tete sert de reference (grise). "unite"
      se place avant le nombre (×1,7), "suffixe" apres (50 €) ; "reference": true grise une
      ligne
  {"type": "choix", "lignes": [{"label": "En pharmacie", "ok": true}, ...]}
      une liste coche / croix
  {"type": "tampon", "texte": "Export interdit"}
      un tampon qui claque

Un element (ligne, barre, tampon) peut porter "temps" : il arrive avec le temps du texte
de ce numero (0 = debut du bloc, 1 = apres le premier "|"...). L'insert se cale en bas sur
le haut du texte (et de la pastille d'ouverture), en haut sur INSERT_HAUT_MIN, a gauche sur
la colonne de texte ; il retrecit s'il le faut. Il sort avec le texte du bloc.
Toutes les valeurs viennent de config/charte.py — ne rien coder en dur ici.
"""
import calendar
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import charte as C
from lcdg import habillage as hb
from lcdg import texte as T

MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre",
        "octobre", "novembre", "décembre"]
JOURS = "LMMJVSD"


def _ecrire(d, xy, texte, px, graisse, couleur, ancre="la"):
    d.text(xy, T.normaliser(texte), font=T._police(px, graisse), fill=couleur, anchor=ancre)


def _ombre(im, s):
    flou, alpha, dy = C.INSERT_OMBRE
    return hb.shadow(im, blur=max(2, int(flou * s)), alpha=alpha, offset=(0, max(1, int(dy * s))))


def _cadre(w, h, s, couleur=C.BLANC, marge=0):
    """Carte arrondie (avec une marge transparente pour l'ombre)."""
    im = Image.new("RGBA", (w + 2 * marge, h + 2 * marge), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle([marge, marge, marge + w - 1, marge + h - 1],
                                         radius=max(4, int(C.INSERT_RAYON * s)),
                                         fill=tuple(couleur) + (255,))
    return im


def _poser(fond, im, cx, cy, k=1.0, alpha=1.0, angle=0.0):
    """Colle im centre en (cx, cy), a l'echelle k, tourne de angle degres."""
    if alpha <= 0.003 or k <= 0.01:
        return
    if abs(k - 1) > 0.01:
        im = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.BICUBIC)
    if abs(angle) > 0.05:
        im = im.rotate(angle, resample=Image.BICUBIC, expand=True)
    T.coller(fond, im, (cx - im.width / 2, cy - im.height / 2), min(1.0, alpha))


def _nombre(v, dec):
    return f"{v:.{dec}f}".replace(".", ",")


class _Insert:
    """Placement, entree commune et sortie avec le texte du bloc."""

    def __init__(self, nom, spec, scene, bas):
        self.nom, self.spec, self.scene = nom, spec, scene
        self.debut, self.fin = scene.debut, scene.fin
        self.instants = [scene.debut] + [p.debut for p in scene.parts[1:]]
        w0, h0 = self.taille_nominale()
        dispo = bas - C.INSERT_HAUT_MIN
        self.s = min(1.0, dispo / h0, C.TEXTE_LARGEUR / w0)
        if self.s < C.INSERT_ECHELLE_MIN:
            raise SystemExit(f"[!] {nom} : pas la place pour l'insert « {spec['type']} » au-dessus "
                             f"du texte ({dispo:.0f} px pour {h0} px). Raccourcis le texte du bloc "
                             "ou retire l'insert.")
        self.w, self.h = int(w0 * self.s), int(h0 * self.s)
        self.m = int(C.INSERT_OMBRE[0] * C.INSERT_MARGE_OMBRE * self.s) + 4   # ombres
        self.x, self.y = C.TEXTE_X, bas - self.h
        self.rubrique = tuple(hb._RUBRIQUE)

    def px(self, v):
        return max(1, int(round(v * self.s)))

    def t0(self, k=0):
        return self.instants[min(max(0, k), len(self.instants) - 1)] + C.INSERT_DELAI

    def taille_nominale(self):
        raise NotImplementedError

    def image(self, t, final):
        raise NotImplementedError

    def sons(self):
        return []

    def dessiner(self, lay, t, final=False):
        so = 0.0 if final else self.scene.parts[-1]._sortie(t)
        if so >= 1:
            return
        im = self.image(t, final)
        if im is not None:
            T.coller(lay, im, (self.x - self.m, self.y - self.m - C.SORTIE_MONTEE * so), 1 - so)

    def couche(self):
        lay = hb._vide(); self.dessiner(lay, 0, final=True)
        return lay


# ----------------------------------------------------------------- verrou
class Verrou(_Insert):
    """Les recommandations gardees pour le site : une carte fermee par recommandation."""

    def taille_nominale(self):
        return C.TEXTE_LARGEUR, C.VERROU_CARTE_H

    def __init__(self, *a):
        super().__init__(*a)
        self.n = int(self.spec["n"])
        g = self.px(C.INSERT_ECART_ELEMENTS)
        self.cw = (self.w - (self.n - 1) * g) // self.n
        self.pas = self.cw + g
        self.cartes = [self._carte(i + 1) for i in range(self.n)]
        self.cadenas = self._cadenas()

    def _carte(self, numero):
        cw, ch, s, m = self.cw, self.h, self.s, self.m
        im = _cadre(cw, ch, s, marge=m)
        d = ImageDraw.Draw(im)
        g = C.VERROU_GEO
        r = self.px(g["rond"])
        cx, cy = m + self.px(g["rond_marge"]) + r, m + self.px(g["rond_marge"]) + r
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=self.rubrique + (255,))
        _ecrire(d, (cx, cy), str(numero), self.px(g["numero_px"]), C.INSERT_GRAISSE_FORTE,
                C.BLANC + (255,), "mm")
        pad = self.px(g["pad"])
        for k, frac in enumerate(C.VERROU_LIGNES):
            y = m + self.px(g["ligne_y"]) + k * self.px(g["ligne_pas"])
            d.rounded_rectangle([m + pad, y, m + pad + int((cw - 2 * pad) * frac), y + self.px(g["ligne_h"])],
                                radius=self.px(g["ligne_h"] / 2), fill=C.INSERT_GRIS + (255,))
        return _ombre(im, s)

    def _cadenas(self):
        s = self.s
        g = C.VERROU_GEO
        r = self.px(g["pastille"])                       # pastille blanche sous le cadenas
        im = Image.new("RGBA", (2 * r + 8, 2 * r + 8), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        c = r + 4
        d.ellipse([c - r, c - r, c + r, c + r], fill=C.BLANC + (255,))
        bw, bh = self.px(g["corps"][0]), self.px(g["corps"][1])
        x0, y0 = c - bw / 2, c - bh / 2 + self.px(g["corps_bas"])
        anse, trait = self.px(g["anse"]), self.px(g["trait"])
        haut_anse = y0 - anse * 0.15                     # centre de l'arc de l'anse
        d.arc([c - anse / 2, haut_anse - anse * 0.7, c + anse / 2, haut_anse + anse * 0.7],
              180, 360, fill=C.NAVY + (255,), width=trait)
        for xa in (c - anse / 2 + trait / 2, c + anse / 2 - trait / 2):   # les branches
            d.line([(xa, haut_anse), (xa, y0 + 2)], fill=C.NAVY + (255,), width=trait)
        d.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], radius=self.px(g["corps_rayon"]),
                            fill=C.NAVY + (255,))
        k = self.px(g["trou"])
        d.ellipse([c - k, y0 + bh * 0.36 - k, c + k, y0 + bh * 0.36 + k], fill=C.BLANC + (255,))
        d.rectangle([c - k / 3, y0 + bh * 0.36, c + k / 3, y0 + bh * 0.72], fill=C.BLANC + (255,))
        return _ombre(im, s)

    def _t(self, i):
        return self.t0() + i * C.INSERT_DECALAGE

    def image(self, t, final):
        out = Image.new("RGBA", (self.w + 2 * self.m, self.h + 2 * self.m), (0, 0, 0, 0))
        for i, carte in enumerate(self.cartes):
            u = 1.0 if final else (t - self._t(i)) / C.INSERT_ENTREE
            if u <= 0:
                continue
            k = C.INSERT_ECHELLE + (1 - C.INSERT_ECHELLE) * (1.0 if final else T.rebond(u))
            dy = 0 if final else C.INSERT_MONTEE * self.s * (1 - T.lisse(u))
            cx = self.m + i * self.pas + self.cw / 2
            cy = self.m + self.h / 2 + dy
            _poser(out, carte, cx, cy, k, 1.0 if final else T.lisse(u * C.INSERT_FONDU))
            # le cadenas tremble une fois, quand la carte est posee
            v = 1.0 if final else (t - self._t(i) - C.VERROU_SECOUSSE[1]) / C.VERROU_SECOUSSE[2]
            angle = 0.0 if (final or not 0 < v < 1) else \
                C.VERROU_SECOUSSE[0] * math.sin(2 * math.pi * 3 * v) * (1 - v)
            _poser(out, self.cadenas, cx, cy + self.h * C.VERROU_GEO["cadenas_y"] * k, k,
                   1.0 if final else T.lisse(u * C.INSERT_FONDU), angle)
        return out

    def sons(self):
        return [(self._t(i), "clic") for i in range(self.n)]


# ------------------------------------------------------------- calendrier
class Calendrier(_Insert):
    """Le mois en carte, la periode qui compte surlignee, une etiquette a cote."""

    def taille_nominale(self):
        lg = T.largeur(T.normaliser(self.spec.get("legende", "")), C.CAL_ETIQUETTE_PX,
                       C.INSERT_GRAISSE_FORTE, 0)
        self.etiquette_w0 = int(lg + 2 * C.CAL_ETIQUETTE_PAD) if self.spec.get("legende") else 0
        w = C.CAL_W + (C.INSERT_ECART_ELEMENTS + self.etiquette_w0 if self.etiquette_w0 else 0)
        return w, C.CAL_H

    def __init__(self, *a):
        super().__init__(*a)
        sp = self.spec
        self.cw = self.px(C.CAL_W)
        semaines = calendar.Calendar(0).monthdayscalendar(sp["annee"], sp["mois"])
        g = C.CAL_GEO
        pad, tete = self.px(g["pad"]), self.px(C.CAL_TETE)
        jours_y = tete + self.px(g["jours_y"])
        grille_y = jours_y + self.px(g["grille_y"])
        cel_w = (self.cw - 2 * pad) / 7
        cel_h = (self.h - grille_y - pad) / len(semaines)
        self.cellules = {}
        for li, sem in enumerate(semaines):
            for co, jour in enumerate(sem):
                if jour:
                    self.cellules[jour] = (pad + co * cel_w, grille_y + li * cel_h, cel_w, cel_h)
        m = self.m
        fond = _cadre(self.cw, self.h, self.s, marge=m)
        d = ImageDraw.Draw(fond)
        d.rounded_rectangle([m, m, m + self.cw - 1, m + tete], radius=max(4, int(C.INSERT_RAYON * self.s)),
                            fill=self.rubrique + (255,))
        d.rectangle([m, m + tete // 2, m + self.cw - 1, m + tete], fill=self.rubrique + (255,))
        titre = f"{MOIS[sp['mois'] - 1]} {sp['annee']}".upper()
        _ecrire(d, (m + self.cw / 2, m + tete / 2), titre, self.px(g["titre_px"]),
                C.INSERT_GRAISSE_FORTE, C.BLANC + (255,), "mm")
        for co, j in enumerate(JOURS):
            _ecrire(d, (m + pad + (co + 0.5) * cel_w, m + jours_y), j, self.px(g["jour_px"]),
                    C.INSERT_GRAISSE_TEXTE, C.INSERT_GRIS_TEXTE + (255,), "mm")
        self.chiffres_blancs = Image.new("RGBA", fond.size, (0, 0, 0, 0))
        db = ImageDraw.Draw(self.chiffres_blancs)
        for jour, (x, y, w, h) in self.cellules.items():
            xy = (m + x + w / 2, m + y + h / 2)
            _ecrire(d, xy, str(jour), self.px(g["numero_px"]), C.INSERT_GRAISSE_CHIFFRE,
                    C.NAVY + (255,), "mm")
            if sp["du"] <= jour <= sp["au"]:
                _ecrire(db, xy, str(jour), self.px(g["numero_px"]), C.INSERT_GRAISSE_FORTE,
                        C.BLANC + (255,), "mm")
        self.fond = _ombre(fond, self.s)
        x0, y0, _, h0 = self.cellules[sp["du"]]
        x1, _, w1, _ = self.cellules[sp["au"]]
        r = self.px(g["bande_retrait"])
        self.bande = (m + x0 + r, m + y0 + r, m + x1 + w1 - r, m + y0 + h0 - r)
        self.etiquette = None
        if self.etiquette_w0:
            ew, eh = self.px(self.etiquette_w0), self.px(C.CAL_ETIQUETTE_H)
            et = Image.new("RGBA", (ew, eh), (0, 0, 0, 0))
            de = ImageDraw.Draw(et)
            de.rounded_rectangle([0, 0, ew - 1, eh - 1], radius=eh // 2, fill=self.rubrique + (255,))
            _ecrire(de, (ew / 2, eh / 2), sp["legende"], self.px(C.CAL_ETIQUETTE_PX),
                    C.INSERT_GRAISSE_FORTE, C.BLANC + (255,), "mm")
            self.etiquette = _ombre(et, self.s)
            self.etiquette_c = (m + self.cw + self.px(C.INSERT_ECART_ELEMENTS) + ew / 2,
                                (self.bande[1] + self.bande[3]) / 2)

    def _temps(self):
        t0 = self.t0()
        balai = t0 + C.CAL_BALAYAGE_DELAI
        return t0, balai, balai + C.INSERT_POUSSE

    def image(self, t, final):
        t0, balai, fin_balai = self._temps()
        u = 1.0 if final else (t - t0) / C.INSERT_ENTREE
        if u <= 0:
            return None
        carte = self.fond.copy()
        p = 1.0 if final else T.lisse((t - balai) / C.INSERT_POUSSE)
        if p > 0:
            x0, y0, x1, y1 = self.bande
            xe = x0 + (x1 - x0) * p
            ImageDraw.Draw(carte).rounded_rectangle([x0, y0, xe, y1],
                                                    radius=self.px(C.CAL_GEO["bande_rayon"]),
                                                    fill=self.rubrique + (255,))
            masque = Image.new("L", carte.size, 0)
            ImageDraw.Draw(masque).rectangle([x0, y0, xe, y1], fill=255)
            # les jours de la periode passent en blanc, au rythme du balayage
            blancs = self.chiffres_blancs.copy()
            blancs.putalpha(Image.composite(blancs.getchannel("A"), masque, masque))
            carte.alpha_composite(blancs)
        out = Image.new("RGBA", (self.w + 2 * self.m, self.h + 2 * self.m), (0, 0, 0, 0))
        k = C.INSERT_ECHELLE + (1 - C.INSERT_ECHELLE) * (1.0 if final else T.rebond(u))
        _poser(out, carte, carte.width / 2, carte.height / 2, k,
               1.0 if final else T.lisse(u * C.INSERT_FONDU))
        if self.etiquette is not None:
            v = 1.0 if final else (t - fin_balai) / C.INSERT_ENTREE
            if v > 0:
                ke = C.INSERT_ECHELLE + (1 - C.INSERT_ECHELLE) * (1.0 if final else T.rebond(v))
                _poser(out, self.etiquette, *self.etiquette_c, ke,
                       1.0 if final else T.lisse(v * C.INSERT_FONDU))
        return out

    def sons(self):
        t0, balai, fin_balai = self._temps()
        out = [(t0, "souffle"), (balai, "clic")]
        if self.etiquette is not None:
            out.append((fin_balai, "clic"))
        return out


# ----------------------------------------------------------------- barres
class Barres(_Insert):
    """Des barres horizontales qui poussent, la valeur qui defile au bout."""

    def taille_nominale(self):
        n = len(self.spec["lignes"])
        return C.TEXTE_LARGEUR, 2 * C.BARRES_PAD + n * C.BARRES_LIGNE_H

    def __init__(self, *a):
        super().__init__(*a)
        sp = self.spec
        self.unite = T.normaliser(sp.get("unite", ""))
        # suffixe colle au nombre par une espace insecable : « 50 € »
        self.suffixe = T.normaliser(sp.get("suffixe", "")).replace(" ", "\u00a0")
        self.lignes = sp["lignes"]
        self.vmax = max(l["valeur"] for l in self.lignes)
        self.dec = max((len(str(l["valeur"]).split(".")[1]) if "." in str(l["valeur"]) else 0)
                       for l in self.lignes)
        self.depart = 1.0 if self.unite in ("×", "x") else 0.0
        pad = self.px(C.BARRES_PAD)
        val_w = T.largeur(f"{self.unite}{_nombre(self.vmax, self.dec)}{self.suffixe}",
                          self.px(C.BARRES_VALEUR_PX), C.INSERT_GRAISSE_FORTE, 0)
        self.barre_max = self.w - 2 * pad - val_w - self.px(C.BARRES_GEO["valeur_marge"])
        self.pad = pad
        self._fonds = {}

    def _fond(self, hc):
        """Carte de hauteur hc (elle grandit a chaque nouvelle barre), gardee en cache."""
        if hc not in self._fonds:
            self._fonds[hc] = _ombre(_cadre(self.w, hc, self.s, marge=self.m), self.s)
        return self._fonds[hc]

    def _hauteur(self, t, final):
        lh = self.px(C.BARRES_LIGNE_H)
        if final:
            return self.h
        n = sum(T.lisse((t - self._t(i)) / C.BARRES_OUVERTURE) for i in range(len(self.lignes)))
        return min(self.h, int(2 * self.pad + n * lh))

    def _t(self, i):
        precedentes = [j for j in range(i) if self.lignes[j].get("temps", 0) == self.lignes[i].get("temps", 0)]
        return self.t0(self.lignes[i].get("temps", 0)) + C.BARRES_DELAI + len(precedentes) * C.BARRES_DECALAGE

    def image(self, t, final):
        u = 1.0 if final else (t - self.t0()) / C.INSERT_ENTREE
        if u <= 0:
            return None
        # la carte est calee en bas, sur le texte : elle grandit vers le haut, et les barres
        # deja posees montent avec elle
        hc = self._hauteur(t, final)
        carte = Image.new("RGBA", (self.w + 2 * self.m, self.h + 2 * self.m), (0, 0, 0, 0))
        haut = self.h - hc
        carte.alpha_composite(self._fond(hc), (0, haut))
        d = ImageDraw.Draw(carte)
        m, pad = self.m, self.pad
        for i, l in enumerate(self.lignes):
            v_ = 1.0 if final else (t - self._t(i)) / C.INSERT_POUSSE
            if v_ <= 0:
                continue
            p = 1.0 if final else T.lisse(v_)
            y = m + haut + pad + i * self.px(C.BARRES_LIGNE_H)
            if y + self.px(C.BARRES_LIGNE_H) > m + haut + hc + self.px(C.BARRES_GEO["tolerance"]):
                continue                                 # pas encore de place pour cette ligne
            a = int(255 * min(1.0, 1.0 if final else v_ * C.BARRES_GEO["fondu_ligne"]))
            _ecrire(d, (m + pad, y), l["label"], self.px(C.BARRES_LABEL_PX), C.INSERT_GRAISSE_TEXTE,
                    C.NAVY + (a,))
            yb = y + self.px(C.BARRES_LABEL_PX + C.BARRES_GEO["label_ecart"])
            hb_ = self.px(C.BARRES_EPAISSEUR)
            # une premiere ligne a x1 (multiplicateur) est la reference : grise
            reference = l.get("reference", i == 0 and self.depart == 1.0 and l["valeur"] == 1)
            couleur = C.INSERT_GRIS if reference else self.rubrique
            longueur = max(hb_, self.barre_max * l["valeur"] / self.vmax * p)
            d.rounded_rectangle([m + pad, yb, m + pad + longueur, yb + hb_], radius=hb_ // 2,
                                fill=tuple(couleur) + (a,))
            v = self.depart + (l["valeur"] - self.depart) * p
            # des que l'arrondi atteint la cible, la valeur s'affiche telle quelle (« ×2 »,
            # pas « ×2,0 » quelques images avant)
            if p >= 1 or round(v, self.dec) == round(l["valeur"], self.dec):
                v, dec = l["valeur"], (0 if float(l["valeur"]).is_integer() else self.dec)
            else:
                dec = self.dec
            texte = f"{self.unite}{_nombre(v, dec)}{self.suffixe}"
            _ecrire(d, (m + pad + longueur + self.px(C.BARRES_GEO["valeur_ecart"]), yb + hb_ / 2),
                    texte, self.px(C.BARRES_VALEUR_PX), C.INSERT_GRAISSE_FORTE,
                    (C.INSERT_GRIS_TEXTE if reference else C.NAVY) + (a,), "lm")
        out = Image.new("RGBA", (self.w + 2 * self.m, self.h + 2 * self.m), (0, 0, 0, 0))
        k = C.INSERT_ECHELLE + (1 - C.INSERT_ECHELLE) * (1.0 if final else T.rebond(u))
        _poser(out, carte, carte.width / 2, carte.height / 2, k,
               1.0 if final else T.lisse(u * C.INSERT_FONDU))
        return out

    def sons(self):
        return [(self._t(i), "clic") for i in range(len(self.lignes))]


# ------------------------------------------------------------------ choix
class Choix(_Insert):
    """Une liste ou chaque ligne recoit une coche verte ou une croix rouge."""

    def taille_nominale(self):
        n = len(self.spec["lignes"])
        larg = max(T.largeur(T.normaliser(l["label"]), C.CHOIX_PX, C.INSERT_GRAISSE_TEXTE, 0)
                   for l in self.spec["lignes"])
        w = int(C.CHOIX_PAD * 3 + C.CHOIX_ICONE + larg + C.CHOIX_PAD)
        return max(w, C.CHOIX_LARGEUR_MIN), n * C.CHOIX_LIGNE_H + (n - 1) * C.CHOIX_ECART

    def __init__(self, *a):
        super().__init__(*a)
        self.lignes = self.spec["lignes"]
        self.lh = self.px(C.CHOIX_LIGNE_H)
        self.pas = self.lh + self.px(C.CHOIX_ECART)
        self.cartes = [self._ligne(l) for l in self.lignes]
        self.icones = [self._icone(l["ok"]) for l in self.lignes]

    def _ligne(self, l):
        m = self.m
        im = _cadre(self.w, self.lh, self.s, marge=m)
        d = ImageDraw.Draw(im)
        x = m + self.px(C.CHOIX_PAD) * 2 + self.px(C.CHOIX_ICONE)
        _ecrire(d, (x, m + self.lh / 2), l["label"], self.px(C.CHOIX_PX), C.INSERT_GRAISSE_TEXTE,
                C.NAVY + (255,), "lm")
        return _ombre(im, self.s)

    def _icone(self, ok):
        r = self.px(C.CHOIX_ICONE) / 2
        n = int(2 * r) + 4
        im = Image.new("RGBA", (n, n), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        c = n / 2
        d.ellipse([c - r, c - r, c + r, c + r], fill=(C.INSERT_VERT if ok else C.INSERT_ROUGE) + (255,))
        e = self.px(C.CHOIX_GEO["trait"])
        if ok:
            d.line([(c - r * 0.45, c + r * 0.02), (c - r * 0.1, c + r * 0.36), (c + r * 0.48, c - r * 0.3)],
                   fill=C.BLANC + (255,), width=e, joint="curve")
        else:
            k = r * 0.38
            d.line([(c - k, c - k), (c + k, c + k)], fill=C.BLANC + (255,), width=e)
            d.line([(c - k, c + k), (c + k, c - k)], fill=C.BLANC + (255,), width=e)
        return im

    def _t(self, i):
        l = self.lignes[i]
        precedentes = [j for j in range(i) if self.lignes[j].get("temps", 0) == l.get("temps", 0)]
        return self.t0(l.get("temps", 0)) + len(precedentes) * C.CHOIX_DECALAGE

    def image(self, t, final):
        out = Image.new("RGBA", (self.w + 2 * self.m, self.h + 2 * self.m), (0, 0, 0, 0))
        for i, (carte, icone) in enumerate(zip(self.cartes, self.icones)):
            u = 1.0 if final else (t - self._t(i)) / C.INSERT_ENTREE
            if u <= 0:
                continue
            dx = 0 if final else -C.INSERT_MONTEE * self.s * (1 - T.lisse(u))
            cy = self.m + i * self.pas + self.lh / 2
            _poser(out, carte, carte.width / 2 + dx, cy, 1.0,
                   1.0 if final else T.lisse(u * C.INSERT_FONDU))
            v = 1.0 if final else (t - self._t(i) - C.CHOIX_ICONE_DELAI) / C.INSERT_ENTREE
            if v > 0:
                k0 = C.CHOIX_GEO["icone_depart"]
                k = k0 + (1 - k0) * (1.0 if final else T.rebond(v))
                cx = self.m + self.px(C.CHOIX_PAD) + self.px(C.CHOIX_ICONE) / 2 + dx
                _poser(out, icone, cx, cy, k, 1.0 if final else T.lisse(v * C.CHOIX_GEO["fondu_icone"]))
        return out

    def sons(self):
        return [(self._t(i) + C.CHOIX_ICONE_DELAI, "clic") for i in range(len(self.lignes))]


# ----------------------------------------------------------------- tampon
class Tampon(_Insert):
    """Un tampon qui claque sur l'image (« Export interdit »)."""

    def _sprite(self, s):
        texte = T.normaliser(self.spec["texte"]).upper()
        px = max(8, int(C.TAMPON_PX * s))
        f = T._police(px, C.INSERT_GRAISSE_FORTE)
        b = f.getbbox(texte)
        tw, th = b[2] - b[0], b[3] - b[1]
        g = C.TAMPON_GEO
        padx, pady = int(C.TAMPON_PAD[0] * s), int(C.TAMPON_PAD[1] * s)
        trait = max(2, int(g["trait"] * s))
        w, h = tw + 2 * padx, th + 2 * pady
        im = Image.new("RGBA", (w + 8, h + 8), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        rouge = C.INSERT_ROUGE + (255,)
        d.rounded_rectangle([4, 4, 4 + w, 4 + h], radius=max(4, int(g["rayon"] * s)),
                            fill=C.BLANC + (C.TAMPON_FOND,), outline=rouge, width=trait)
        i = trait + max(2, int(g["filet_retrait"] * s))
        d.rounded_rectangle([4 + i, 4 + i, 4 + w - i, 4 + h - i], radius=max(3, int(g["filet_rayon"] * s)),
                            outline=rouge, width=max(1, trait // 3))
        d.text((4 + padx - b[0], 4 + pady - b[1]), texte, font=f, fill=rouge)
        return im.rotate(C.TAMPON_ANGLE, resample=Image.BICUBIC, expand=True)

    def taille_nominale(self):
        im = self._sprite(1.0)
        return im.width, im.height

    def __init__(self, *a):
        super().__init__(*a)
        self.sprite = _ombre(self._sprite(self.s), self.s)

    def _t(self):
        return self.t0(self.spec.get("temps", 0))

    def dessiner(self, lay, t, final=False):
        """Colle le tampon directement sur le cadre : agrandi au moment de la frappe, il
        deborde de sa boite."""
        so = 0.0 if final else self.scene.parts[-1]._sortie(t)
        u = 1.0 if final else (t - self._t()) / C.TAMPON_FRAPPE
        if so >= 1 or u <= 0:
            return
        k = 1.0 if final or u >= 1 else C.TAMPON_ECHELLE - (C.TAMPON_ECHELLE - 1) * u * u
        dx = 0.0
        if not final and u > 1:
            v = (t - self._t() - C.TAMPON_FRAPPE) / C.TAMPON_SECOUSSE[1]
            if v < 1:
                dx = C.TAMPON_SECOUSSE[0] * self.s * math.sin(2 * math.pi * 4 * v) * (1 - v)
        alpha = (1.0 if final else min(1.0, u * C.TAMPON_GEO["fondu"])) * (1 - so)
        _poser(lay, self.sprite, self.x + self.w / 2 + dx,
               self.y + self.h / 2 - C.SORTIE_MONTEE * so, k, alpha)

    def sons(self):
        return [(self._t() + C.TAMPON_FRAPPE, "impact")]


TYPES = {"verrou": Verrou, "calendrier": Calendrier, "barres": Barres, "choix": Choix,
         "tampon": Tampon}


def inserts(ep, scenes, ouverture=None):
    """Les inserts du reel, un par bloc qui en porte un (scenes : habillage.scenes)."""
    out = []
    for k, bl in enumerate(ep["blocs"]):
        spec = bl.get("insert")
        if not spec:
            continue
        if bl.get("type") in ("phrase", "chiffre") or k == 0:
            raise SystemExit(f"[!] bloc {k} : un insert se pose sur un bloc de texte (pas sur "
                             "l'accroche, une phrase forte ou un chiffre cle).")
        if spec.get("type") not in TYPES:
            raise SystemExit(f"[!] bloc {k} : insert inconnu « {spec.get('type')} ». "
                             f"Types : {', '.join(TYPES)}.")
        scene = scenes[k]
        hauts = [b[1] for b in (hb._bbox(lay) for _, lay, _ in scene.couches()) if b]
        bas = min(hauts) if hauts else C.BLOC_Y
        if ouverture is not None and ouverture.scene is scene:
            bas = ouverture.pos[1]
        out.append(TYPES[spec["type"]](f"insert bloc {k}", spec, scene, bas - C.INSERT_ECART))
    return out
