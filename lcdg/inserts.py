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
      une liste coche / croix ; sans "ok", un « ? » : une question encore ouverte
  {"type": "tampon", "texte": "Export interdit"}
      un tampon qui claque
  {"type": "circuit", "lignes": [{"titre": "Dose injectée", "etapes": ["−11,75 €", "+11,75 €"],
                                  "fin": "remboursée", "ok": true}, ...]}
      un flux par ligne : des pilules reliees par des fleches qui se tracent, une issue
      verte (ok) ou rouge ; une etape qui commence par « − » s'ecrit en rouge, « + » en vert
  {"type": "duel", "cartes": [{"date": "14 oct.", "texte": "Contrôler 650 médecins", "ok": false},
                              {"date": "20 oct.", "texte": "Les aider : SOS IJ", "ok": true}]}
      deux cartes datees face a face, puis un « ≠ » qui claque entre elles ; sans "ok", une
      carte prend la couleur de la rubrique (deux options : « Accepter » / « Refuser »)
  {"type": "frise", "etapes": [{"label": "Vos chiffres notifiés"}, ..., {"label": "...", "alerte": true}]}
      une procedure, de haut en bas : le trait descend de noeud en noeud ; une etape
      "alerte" en rouge

Illustrations (Romain, 23/10/2026 : « ça doit être interactif et ultra ludique ») :

  {"type": "frigo", "mode": "remplir", "doses": 6, "prix": 1, "etiquette": ["Payées d'abord", "par vous"]}
      les boites de vaccin tombent dans le refrigerateur ; au temps "prix", une piece « € » se
      pose sur chacune et l'etiquette claque sur la porte
  {"type": "frigo", "mode": "releve", "titre": "Température enregistrée"}
      le refrigerateur plein et la courbe de temperature qui s'enregistre entre +2 et +8 °C
      (conservation des vaccins grippe) ; l'ecran affiche la valeur du moment
  {"type": "ticket", "titre": "Votre facturation", "lignes": [{"label": "Injection",
                                                               "valeur": "pas à part", "ok": false}, ...]}
      un ticket qui s'imprime ligne par ligne, coche ou croix a gauche, valeur a droite
  {"type": "appel", "etapes": [{"icone": "telephone", "label": "Appel de votre CPAM", "note": "en principe"},
                               {"icone": "courrier", "label": "Puis le courrier"}]}
      un telephone qui sonne, une fleche, puis le courrier qui arrive en vol
  {"type": "loupe", "site": "ameli.fr", "recherche": "mise sous objectifs", "vide": "Aucun résultat"}
      la recherche se tape, la loupe balaie la page, rien ne sort
  {"type": "calcul", "titre": "...", "temps_question": 1,
   "parts": [{"label": "...", "valeur": 0.68}, {"label": "...", "valeur": 0.32, "question": true}]}
      une barre qui se remplit ; la part "question" se detache, un « ? » au-dessus. Les parts
      sont une illustration : aucun chiffre ne s'affiche. "ton": "rouge", "vert" ou "bleu"
      colore une part et son libelle (trois regimes selon l'age, par exemple)

  {"type": "ages", "titre": "...", "ordre": [2, 1, 0], "zones": [{"label": "Avant l'âge légal",
                                                                "bulle": "Réduite dès le 1er €", "ton": "rouge"}, ...]}
      une regle en zones colorees ; un curseur va de zone en zone, une bulle dit ce qui s'y passe
  {"type": "vases", "titre": "1 € gagné, 1 € de pension en moins", "gauche": "...", "droite": "...",
   "ajout": {"label": "IJ", "temps": 1}}
      deux bocaux communicants : l'un monte, l'autre baisse d'autant ; une piece tombe ensuite
  {"type": "pieces", "titre": "Au-delà du seuil", "gauche": "...", "droite": "...", "temps": 1}
      deux piles de pieces : deux s'empilent a gauche, une s'envole a droite, compteurs
  {"type": "part", "pastille": "...", "part": 20, "centre": "au plus", "legende_part": "...",
   "legende_reste": "...", "temps_part": 1}
      un anneau d'activite qui se remplit, la part plafonnee se detache, son pourcentage au centre
  {"type": "bascule", "avant": {"haut": "Sept. 2026", "jour": "30", "bas": "..."}, "apres": {...},
   "legende_avant": "...", "legende_apres": "...", "pilule": "Nouvelles règles", "temps": 1}
      un ephemeride dont la page se plie pour montrer la suivante ; une pilule claque
  {"type": "icones", "cartes": [{"icone": "repere" | "lune" | "casque" | "poubelle" | "bon" | "enfant",
                                 "label": "...", "temps": 1}, ...]}
      des cartes a icone dessinee, un « ? » qui se balance au coin de chacune
  {"type": "prix", "boites": [{"nom": "Vaxigrip", "prix": "11,75 €"}, {..., "ton": "rouge"}],
   "pastille": "plus du double"}
      des boites de vaccin dessinees, une etiquette de prix tombe sur chacune, une pastille claque

Reels docteurs juniors et acces direct aux IPA (28/10/2026) :

  {"type": "carte", "titulaire": "Docteur junior", "ok": true, "temps": 1}
      une carte CPS au nom du titulaire glisse dans le lecteur ; l'ecran repond coche ou croix
      (refusee, la carte tremble)
  {"type": "compteur", "titre": "Cartes CPS délivrées", "date": "au 28 octobre", "pilule": "...", "temps": 1}
      des rouleaux de chiffres qui defilent puis s'arretent sur « ? » ; aucun nombre ne reste
  {"type": "bouclier", "temps": 1, "pilules": [{"texte": "...", "ton": "rouge", "temps": 1}, ...]}
      un bouclier sur une silhouette, dont le contour passe en pointilles avec un « ? » ; les
      pilules du texte a droite
  {"type": "departements", "liste": [{"numero": "34", "nom": "Hérault"}, ...]}
      des tuiles de departement qui se retournent l'une apres l'autre
  {"type": "ordonnance", "titre": "Ordonnance", "marque": "IPA", "lignes": [{"label": "...", "note": "...",
   "temps": 1}], "pied": "...", "temps_pied": 2}
      une ordonnance qui s'ecrit au stylo, ligne par ligne, une pilule rouge au pied
  {"type": "sablier", "pilules": [...]}
      un sablier qui coule et se retourne sans fin, un « ? » ; les pilules du texte a droite
  {"type": "pilule", "texte": "Aucune rémunération prévue", "temps": 1}
      une pilule seule qui claque, sous un dessin : elle ne cache pas ses libelles
  "appel" accepte aussi l'icone "infirmier", et un "temps" par etape ; "icones" accepte les icones
  "compte_rendu", "concertation", "patient", et par carte "question": false (une tache, pas une
  question ouverte) ou "temps_question"

Le champ "insert" peut aussi etre une liste : les elements s'empilent dans l'ordre, et
"sur": true centre un element sur le premier (un tampon qui claque sur un dessin).

Un element (ligne, barre, tampon) peut porter "temps" : il arrive avec le temps du texte
de ce numero (0 = debut du bloc, 1 = apres le premier "|"...). "carre": false dans l'insert
le retire de la version carree, quand il n'y tient pas (bloc 1, sous la pastille d'ouverture). L'insert se cale en bas sur
le haut du texte (et de la pastille d'ouverture), en haut sur INSERT_HAUT_MIN, a gauche sur
la colonne de texte ; il retrecit s'il le faut. Il sort avec le texte du bloc.
Toutes les valeurs viennent de config/charte.py — ne rien coder en dur ici.
"""
import calendar
import math
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import charte as C
from lcdg import habillage as hb
from lcdg import texte as T

MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre",
        "octobre", "novembre", "décembre"]
JOURS = "LMMJVSD"
NBSP = " "


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
    # meme ecriture que les chiffres cles (habillage.Chiffre.nombre) : milliers separes par
    # une espace fine, virgule decimale (« 3 400 », « 49,6 »)
    return f"{v:,.{dec}f}".replace(",", " ").replace(".", ",")


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
        self.icones = [self._icone(l.get("ok")) for l in self.lignes]

    def _ligne(self, l):
        m = self.m
        im = _cadre(self.w, self.lh, self.s, marge=m)
        d = ImageDraw.Draw(im)
        x = m + self.px(C.CHOIX_PAD) * 2 + self.px(C.CHOIX_ICONE)
        _ecrire(d, (x, m + self.lh / 2), l["label"], self.px(C.CHOIX_PX), C.INSERT_GRAISSE_TEXTE,
                C.NAVY + (255,), "lm")
        return _ombre(im, self.s)

    def _icone(self, ok):
        return _icone_choix(ok, self.px(C.CHOIX_ICONE), self.px(C.CHOIX_GEO["trait"]), self.rubrique)

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
                # une question ouverte ne tient pas en place : son « ? » se balance
                angle = 0.0
                if not final and self.lignes[i].get("ok") is None and v > 1:
                    amp, freq = C.CHOIX_GEO["balance"]
                    angle = amp * math.sin(2 * math.pi * freq * (t - self._t(i)))
                _poser(out, icone, cx, cy, k, 1.0 if final else T.lisse(v * C.CHOIX_GEO["fondu_icone"]), angle)
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


def _couper(texte, px, graisse, largeur):
    """Decoupe un libelle en lignes qui tiennent dans largeur (mots entiers)."""
    lignes, cur = [], ""
    for mot in T.normaliser(texte).split(" "):
        essai = f"{cur} {mot}".strip()
        if cur and T.largeur(essai, px, graisse, 0) > largeur:
            lignes.append(cur)
            cur = mot
        else:
            cur = essai
    return lignes + ([cur] if cur else [])


def _pilule(texte, px, h, pad, fond, couleur):
    w = int(T.largeur(T.normaliser(texte), px, C.INSERT_GRAISSE_FORTE, 0) + 2 * pad)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=h // 2, fill=tuple(fond) + (255,))
    _ecrire(d, (w / 2, h / 2), texte, px, C.INSERT_GRAISSE_FORTE, tuple(couleur) + (255,), "mm")
    return im


def _fleche(d, x0, x1, y, p, trait, tete, couleur):
    """Fleche horizontale de x0 a x1, tracee sur la fraction p (la pointe suit le trait)."""
    if p <= 0:
        return
    xe = x0 + (x1 - x0) * min(1.0, p)
    d.line([(x0, y), (max(x0, xe - tete * 0.6), y)], fill=couleur, width=trait)
    d.polygon([(xe, y), (xe - tete, y - tete * 0.7), (xe - tete, y + tete * 0.7)], fill=couleur)


# ---------------------------------------------------------------- circuit
class Circuit(_Insert):
    """Ce que devient l'argent, ligne par ligne : pilules reliees par des fleches, issue."""

    def _elements(self, l, s):
        g = C.CIRCUIT_GEO
        px, h, pad = max(8, int(C.CIRCUIT_PILULE_PX * s)), max(8, int(C.CIRCUIT_PILULE_H * s)), int(g["pilule_pad"] * s)
        out = []
        for e in l["etapes"]:
            couleur = C.INSERT_ROUGE if e.startswith(("−", "-")) else C.INSERT_VERT if e.startswith("+") else C.NAVY
            out.append(_pilule(e, px, h, pad, C.INSERT_GRIS, couleur))
        if l.get("fin"):
            fond = C.INSERT_VERT if l.get("ok") else C.INSERT_ROUGE
            out.append(_pilule(l["fin"], max(8, int(C.CIRCUIT_FIN_PX * s)), h, pad, fond, C.BLANC))
        return out

    def taille_nominale(self):
        lignes = self.spec["lignes"]
        larg = max(2 * C.CIRCUIT_PAD + sum(e.width for e in self._elements(l, 1.0))
                   + (len(self._elements(l, 1.0)) - 1) * C.CIRCUIT_FLECHE for l in lignes)
        n = len(lignes)
        return max(C.TEXTE_LARGEUR, larg), n * C.CIRCUIT_LIGNE_H + (n - 1) * C.CIRCUIT_ECART

    def __init__(self, *a):
        super().__init__(*a)
        self.lignes = self.spec["lignes"]
        self.lh = self.px(C.CIRCUIT_LIGNE_H)
        self.pas = self.lh + self.px(C.CIRCUIT_ECART)
        self.elements = [self._elements(l, self.s) for l in self.lignes]
        self.cartes = []
        for l in self.lignes:
            im = _cadre(self.w, self.lh, self.s, marge=self.m)
            _ecrire(ImageDraw.Draw(im), (self.m + self.px(C.CIRCUIT_PAD), self.m + self.px(C.CIRCUIT_GEO["titre_y"])),
                    l.get("titre", ""), self.px(C.CIRCUIT_TITRE_PX), C.INSERT_GRAISSE_TEXTE,
                    C.INSERT_GRIS_TEXTE + (255,))
            self.cartes.append(_ombre(im, self.s))

    def _t(self, i):
        l = self.lignes[i]
        precedentes = [j for j in range(i) if self.lignes[j].get("temps", 0) == l.get("temps", 0)]
        return self.t0(l.get("temps", 0)) + len(precedentes) * C.INSERT_DECALAGE * 3

    def image(self, t, final):
        out = Image.new("RGBA", (self.w + 2 * self.m, self.h + 2 * self.m), (0, 0, 0, 0))
        g = C.CIRCUIT_GEO
        trait, tete, marge = self.px(g["trait"]), self.px(g["tete"]), self.px(g["fleche_marge"])
        for i, (carte, elements) in enumerate(zip(self.cartes, self.elements)):
            u = 1.0 if final else (t - self._t(i)) / C.INSERT_ENTREE
            if u <= 0:
                continue
            dx = 0 if final else -C.INSERT_MONTEE * self.s * (1 - T.lisse(u))
            top = self.m + i * self.pas
            _poser(out, carte, carte.width / 2 + dx, top + self.lh / 2, 1.0,
                   1.0 if final else T.lisse(u * C.INSERT_FONDU))
            cy = top + self.px(g["rangee_y"]) + (self.lh - self.px(g["rangee_y"])) / 2
            x = self.m + self.px(C.CIRCUIT_PAD) + dx
            d = ImageDraw.Draw(out)
            for k, e in enumerate(elements):
                tk = self._t(i) + C.INSERT_ENTREE * 0.5 + k * C.CIRCUIT_DECALAGE
                v = 1.0 if final else (t - tk) / C.INSERT_ENTREE
                if k > 0:                                # la fleche qui mene a cet element
                    p = 1.0 if final else (t - (tk - C.CIRCUIT_DECALAGE * 0.75)) / (C.CIRCUIT_DECALAGE * 0.7)
                    _fleche(d, x - self.px(C.CIRCUIT_FLECHE) + marge, x - marge, cy, p, trait, tete,
                            C.INSERT_GRIS_TEXTE + (255,))
                if v > 0:
                    kk = C.INSERT_ECHELLE + (1 - C.INSERT_ECHELLE) * (1.0 if final else T.rebond(v))
                    _poser(out, e, x + e.width / 2, cy, kk, 1.0 if final else T.lisse(v * C.INSERT_FONDU))
                x += e.width + self.px(C.CIRCUIT_FLECHE)
        return out

    def sons(self):
        return [(self._t(i) + C.INSERT_ENTREE * 0.5 + k * C.CIRCUIT_DECALAGE, "clic")
                for i, el in enumerate(self.elements) for k in range(len(el))]


# ------------------------------------------------------------------- duel
class Duel(_Insert):
    """Deux cartes datees face a face (une decision, puis son contraire), un « ≠ » entre."""

    def taille_nominale(self):
        return C.TEXTE_LARGEUR, C.DUEL_H

    def __init__(self, *a):
        super().__init__(*a)
        g = C.DUEL_GEO
        self.cartes_spec = self.spec["cartes"][:2]
        self.ecart = self.px(g["ecart"])
        self.cw = (self.w - self.ecart) // 2
        self.cartes = [self._carte(c) for c in self.cartes_spec]
        r = self.px(C.DUEL_SIGNE) // 2
        im = Image.new("RGBA", (2 * r + 8, 2 * r + 8), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.ellipse([4, 4, 4 + 2 * r, 4 + 2 * r], fill=C.NAVY + (255,))
        _ecrire(d, (4 + r, 4 + r), "≠", self.px(g["signe_px"]), C.INSERT_GRAISSE_FORTE, C.BLANC + (255,), "mm")
        self.signe = _ombre(im, self.s)

    def _carte(self, c):
        g, m = C.DUEL_GEO, self.m
        im = _cadre(self.cw, self.h, self.s, marge=m)
        d = ImageDraw.Draw(im)
        tete = self.px(C.DUEL_TETE)
        # "ok" absent : une option neutre, a la couleur de la rubrique
        couleur = (self.rubrique if "ok" not in c else C.INSERT_VERT if c["ok"] else C.INSERT_ROUGE) + (255,)
        rayon = max(4, int(C.INSERT_RAYON * self.s))
        d.rounded_rectangle([m, m, m + self.cw - 1, m + tete], radius=rayon, fill=couleur)
        d.rectangle([m, m + tete // 2, m + self.cw - 1, m + tete], fill=couleur)
        _ecrire(d, (m + self.cw / 2, m + tete / 2), c["date"], self.px(C.DUEL_DATE_PX),
                C.INSERT_GRAISSE_FORTE, C.BLANC + (255,), "mm")
        px = self.px(C.DUEL_TEXTE_PX)
        lignes = _couper(c["texte"], px, C.INSERT_GRAISSE_FORTE, self.cw - 2 * self.px(g["pad"]))
        lh = px * g["interligne"]
        y0 = m + tete + (self.h - tete - lh * len(lignes)) / 2 + lh / 2
        for k, ligne in enumerate(lignes):
            _ecrire(d, (m + self.cw / 2, y0 + k * lh), ligne, px, C.INSERT_GRAISSE_FORTE, C.NAVY + (255,), "mm")
        return _ombre(im, self.s)

    def _t(self, i):
        c = self.cartes_spec[i]
        precedentes = [j for j in range(i) if self.cartes_spec[j].get("temps", 0) == c.get("temps", 0)]
        return self.t0(c.get("temps", 0)) + len(precedentes) * C.DUEL_DECALAGE

    def _t_signe(self):
        return max(self._t(i) for i in range(len(self.cartes))) + C.DUEL_SIGNE_DELAI

    def image(self, t, final):
        out = Image.new("RGBA", (self.w + 2 * self.m, self.h + 2 * self.m), (0, 0, 0, 0))
        for i, carte in enumerate(self.cartes):
            u = 1.0 if final else (t - self._t(i)) / C.INSERT_ENTREE
            if u <= 0:
                continue
            sens = -1 if i == 0 else 1
            dx = 0 if final else sens * C.INSERT_MONTEE * self.s * (1 - T.lisse(u))
            k = C.INSERT_ECHELLE + (1 - C.INSERT_ECHELLE) * (1.0 if final else T.rebond(u))
            cx = self.m + i * (self.cw + self.ecart) + self.cw / 2 + dx
            _poser(out, carte, cx, self.m + self.h / 2, k, 1.0 if final else T.lisse(u * C.INSERT_FONDU))
        v = 1.0 if final else (t - self._t_signe()) / C.INSERT_ENTREE
        if v > 0 and len(self.cartes) == 2:
            k = 0.3 + 0.7 * (1.0 if final else T.rebond(v))
            angle = 0.0 if (final or v >= 1) else 12 * math.sin(2 * math.pi * 2 * v) * (1 - v)
            _poser(out, self.signe, self.m + self.w / 2, self.m + self.h / 2, k,
                   1.0 if final else T.lisse(v * C.INSERT_FONDU), angle)
        return out

    def sons(self):
        return [(self._t(i), "clic") for i in range(len(self.cartes))] + [(self._t_signe(), "impact")]


# ------------------------------------------------------------------ frise
class Frise(_Insert):
    """Une procedure en etapes, de haut en bas : le trait descend de noeud en noeud, chaque
    libelle se pose a droite de son noeud ; une etape "alerte" en rouge."""

    def _largeur_libelle(self, e, s):
        graisse = C.INSERT_GRAISSE_FORTE if e.get("alerte") else C.INSERT_GRAISSE_TEXTE
        return T.largeur(T.normaliser(e["label"]), max(8, int(C.FRISE_LABEL_PX * s)), graisse, 0)

    def taille_nominale(self):
        g = C.FRISE_GEO
        n = len(self.spec["etapes"])
        larg = 2 * C.FRISE_PAD + 2 * C.FRISE_NOEUD + g["label_x"] + max(
            self._largeur_libelle(e, 1.0) for e in self.spec["etapes"])
        return max(int(larg), C.CHOIX_LARGEUR_MIN), 2 * C.FRISE_PAD + n * C.FRISE_LIGNE_H

    def __init__(self, *a):
        super().__init__(*a)
        self.etapes = self.spec["etapes"]
        self.pad = self.px(C.FRISE_PAD)
        self.r = self.px(C.FRISE_NOEUD)
        self.lh = self.px(C.FRISE_LIGNE_H)
        self.xn = self.m + self.pad + self.r
        self.ys = [self.m + self.pad + self.lh * (i + 0.5) for i in range(len(self.etapes))]
        self.fond = _ombre(_cadre(self.w, self.h, self.s, marge=self.m), self.s)
        self.noeuds = []
        for i, e in enumerate(self.etapes):
            couleur = (C.INSERT_ROUGE if e.get("alerte") else self.rubrique) + (255,)
            im = Image.new("RGBA", (2 * self.r + 4, 2 * self.r + 4), (0, 0, 0, 0))
            d = ImageDraw.Draw(im)
            d.ellipse([2, 2, 2 + 2 * self.r, 2 + 2 * self.r], fill=couleur)
            _ecrire(d, (2 + self.r, 2 + self.r), "!" if e.get("alerte") else str(i + 1),
                    self.px(C.FRISE_GEO["numero_px"]), C.INSERT_GRAISSE_FORTE, C.BLANC + (255,), "mm")
            self.noeuds.append(im)

    def _t(self, i):
        e = self.etapes[i]
        precedentes = [j for j in range(i) if self.etapes[j].get("temps", 0) == e.get("temps", 0)]
        return self.t0(e.get("temps", 0)) + C.INSERT_ENTREE * 0.6 + len(precedentes) * C.FRISE_DECALAGE

    def image(self, t, final):
        u = 1.0 if final else (t - self.t0()) / C.INSERT_ENTREE
        if u <= 0:
            return None
        carte = self.fond.copy()
        d = ImageDraw.Draw(carte)
        g = C.FRISE_GEO
        trait = self.px(g["trait"])
        d.line([(self.xn, self.ys[0]), (self.xn, self.ys[-1])], fill=C.INSERT_GRIS + (255,), width=trait)
        for i in range(1, len(self.ys)):         # le trait colore descend jusqu'au noeud i
            p = 1.0 if final else (t - (self._t(i) - C.FRISE_TRACE)) / C.FRISE_TRACE
            if p > 0:
                y1 = self.ys[i - 1] + (self.ys[i] - self.ys[i - 1]) * min(1.0, p)
                couleur = (C.INSERT_ROUGE if self.etapes[i].get("alerte") else self.rubrique) + (255,)
                d.line([(self.xn, self.ys[i - 1]), (self.xn, y1)], fill=couleur, width=trait)
        px = self.px(C.FRISE_LABEL_PX)
        for i, e in enumerate(self.etapes):
            v = 1.0 if final else (t - self._t(i)) / C.INSERT_ENTREE
            if v <= 0:
                continue
            k = 0.3 + 0.7 * (1.0 if final else T.rebond(v))
            _poser(carte, self.noeuds[i], self.xn, self.ys[i], k, 1.0 if final else T.lisse(v * C.INSERT_FONDU))
            a = int(255 * (1.0 if final else T.lisse(v * C.INSERT_FONDU)))
            dx = 0 if final else -self.px(g["glisse"]) * (1 - T.lisse(v))
            couleur = (C.INSERT_ROUGE if e.get("alerte") else C.NAVY) + (a,)
            graisse = C.INSERT_GRAISSE_FORTE if e.get("alerte") else C.INSERT_GRAISSE_TEXTE
            _ecrire(d, (self.xn + self.r + self.px(g["label_x"]) + dx, self.ys[i]), e["label"], px, graisse,
                    couleur, "lm")
        out = Image.new("RGBA", (self.w + 2 * self.m, self.h + 2 * self.m), (0, 0, 0, 0))
        k = C.INSERT_ECHELLE + (1 - C.INSERT_ECHELLE) * (1.0 if final else T.rebond(u))
        _poser(out, carte, carte.width / 2, carte.height / 2, k, 1.0 if final else T.lisse(u * C.INSERT_FONDU))
        return out

    def sons(self):
        return [(self._t(i), "impact" if e.get("alerte") else "clic") for i, e in enumerate(self.etapes)]


# ---------------------------------------------------- illustrations : outils
def _net(w, h, dessiner):
    """Forme sans escalier : tracee a INSERT_SURECHANTILLON fois sa taille, puis reduite.
    dessiner(d, k) recoit le pinceau et le facteur k, a appliquer a toutes les longueurs."""
    k = C.INSERT_SURECHANTILLON
    w, h = max(1, int(round(w))), max(1, int(round(h)))
    grand = Image.new("RGBA", (w * k, h * k), (0, 0, 0, 0))
    dessiner(ImageDraw.Draw(grand), k)
    return grand.resize((w, h), Image.LANCZOS)


def _teinte(couleur, p):
    """La couleur eclaircie vers le blanc (p = 1 : blanc)."""
    return tuple(int(round(c + (255 - c) * p)) for c in couleur)


def _ombre_marge(im, s):
    """im entoure de la marge que demande son ombre, puis ombre (le centre ne bouge pas)."""
    m = int(C.INSERT_OMBRE[0] * C.INSERT_MARGE_OMBRE * s) + 4
    out = Image.new("RGBA", (im.width + 2 * m, im.height + 2 * m), (0, 0, 0, 0))
    out.alpha_composite(im, (m, m))
    return _ombre(out, s)


def _icone_choix(ok, diametre, trait, rubrique):
    """Rond a coche (ok), a croix (non), ou « ? » a la couleur de la rubrique (ok absent : une
    question encore ouverte)."""
    r = diametre / 2
    n = int(2 * r) + 4
    im = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = n / 2
    fond = rubrique if ok is None else C.INSERT_VERT if ok else C.INSERT_ROUGE
    d.ellipse([c - r, c - r, c + r, c + r], fill=tuple(fond) + (255,))
    if ok is None:
        _ecrire(d, (c, c), "?", int(r * C.CHOIX_GEO["question"]), C.INSERT_GRAISSE_FORTE, C.BLANC + (255,), "mm")
    elif ok:
        d.line([(c - r * 0.45, c + r * 0.02), (c - r * 0.1, c + r * 0.36), (c + r * 0.48, c - r * 0.3)],
               fill=C.BLANC + (255,), width=trait, joint="curve")
    else:
        k = r * 0.38
        d.line([(c - k, c - k), (c + k, c + k)], fill=C.BLANC + (255,), width=trait)
        d.line([(c - k, c + k), (c + k, c - k)], fill=C.BLANC + (255,), width=trait)
    return im


def _pointilles(im, periode, plein):
    """Garde un trait sur deux le long de diagonales : un contour devient pointille."""
    masque = Image.new("L", im.size, 0)
    d = ImageDraw.Draw(masque)
    for x in range(-im.height, im.width, periode):
        d.polygon([(x, 0), (x + plein, 0), (x + plein + im.height, im.height), (x + im.height, im.height)], fill=255)
    out = im.copy()
    out.putalpha(ImageChops.multiply(im.getchannel("A"), masque))
    return out


def _etiquette(lignes, px, padx, pady, couleur=C.INSERT_ROUGE):
    """Etiquette de prix (pointe et trou a gauche), texte blanc ; ni rotation ni ombre."""
    lignes = [T.normaliser(l) for l in lignes]
    lh = px * 1.18
    h = len(lignes) * lh + 2 * pady
    pointe = h * 0.42
    w = max(T.largeur(l, px, C.INSERT_GRAISSE_FORTE, 0) for l in lignes) + 2 * padx + pointe

    def dessin(d, k):
        W, H, P = w * k, h * k, pointe * k
        fond = tuple(couleur) + (255,)
        d.rounded_rectangle([P * 0.6, 0, W, H], radius=H * 0.16, fill=fond)
        d.polygon([(P + 1, 0), (0, H / 2), (P + 1, H)], fill=fond)
        r = H * 0.085
        d.ellipse([P * 0.5 - r, H / 2 - r, P * 0.5 + r, H / 2 + r], fill=(0, 0, 0, 0))
    im = _net(w, h, dessin)
    d = ImageDraw.Draw(im)
    for i, l in enumerate(lignes):
        _ecrire(d, (pointe + (w - pointe) / 2, pady + lh * (i + 0.5)), l, px, C.INSERT_GRAISSE_FORTE,
                C.BLANC + (255,), "mm")
    return im


# -------------------------------------------------------------- frigo
class Frigo(_Insert):
    """L'enceinte refrigeree du cabinet.
    Mode "remplir" : les boites de vaccin tombent sur les etageres ; au temps "prix", une piece
    « € » se pose sur chacune, puis une etiquette claque sur la porte (« Payées d'abord »).
    Mode "releve" : le refrigerateur plein et, a cote, la courbe de temperature qui s'enregistre
    dans la plage de conservation ; l'ecran du refrigerateur affiche la valeur du moment."""

    def _releve(self):
        return self.spec.get("mode") == "releve"

    def _hauteur_frigo(self):
        return C.FRIGO_RELEVE_H if self._releve() else C.FRIGO_H

    def _etiquette(self, s):
        """L'etiquette de prix, deja tournee (sans ombre)."""
        g = C.FRIGO_GEO
        im = _etiquette(self.spec.get("etiquette", []), max(8, int(round(g["etiquette_px"] * s))),
                        g["etiquette_pad"][0] * s, g["etiquette_pad"][1] * s)
        return im.rotate(-g["etiquette_angle"], resample=Image.BICUBIC, expand=True)

    def taille_nominale(self):
        fh = self._hauteur_frigo()
        fw = C.FRIGO_W * fh / C.FRIGO_H
        if self._releve():
            return C.TEXTE_LARGEUR, fh
        ew = self._etiquette(1.0).width if self.spec.get("etiquette") else 0
        return int(fw + max(0, ew - C.FRIGO_GEO["chevauche"])), fh

    def __init__(self, *a):
        super().__init__(*a)
        g = C.FRIGO_GEO
        self.f = self.s * self._hauteur_frigo() / C.FRIGO_H        # echelle de la geometrie FRIGO_GEO
        self.fh = int(round(self._hauteur_frigo() * self.s))
        self.fw = int(round(C.FRIGO_W * self.f))
        q = self.f
        pan, vm, pied = g["panneau"] * q, g["vitre_marge"] * q, g["pied"][1] * q
        self.vitre = (vm, pan + vm, self.fw - 2 * vm - g["poignee"][0] * q, self.fh - pied - vm)
        x0, y0, x1, y1 = self.vitre
        bw, bh = g["boite"][0] * q, g["boite"][1] * q
        ecart = g["boite_ecart"] * q
        rang = (y1 - y0) / 2
        self.places = []                                         # coin haut-gauche de chaque boite
        for r in range(2):
            base = y0 + rang * (r + 1) - g["etagere"] * q
            larg = 3 * bw + 2 * ecart
            for c in range(3):
                self.places.append((x0 + (x1 - x0 - larg) / 2 + c * (bw + ecart), base - bh))
        self.n = min(len(self.places), int(self.spec.get("doses", len(self.places))))
        self.boite = self._boite(bw, bh)
        self.mf = int(C.INSERT_OMBRE[0] * C.INSERT_MARGE_OMBRE * self.s) + 4     # marge d'ombre
        corps = self._corps(plein=self._releve())
        self.fond_frigo = _ombre_marge(corps, self.s)
        self.masque_vitre = Image.new("L", corps.size, 0)
        ImageDraw.Draw(self.masque_vitre).rounded_rectangle([x0, y0, x1, y1], radius=g["rayon"] * q * 0.5,
                                                             fill=255)
        if self._releve():
            self._init_courbe()
        else:
            p = max(8, int(round(g["piece"] * q)))
            self.piece = _net(p, p, lambda d, k: d.ellipse([0, 0, p * k - 1, p * k - 1],
                                                           fill=C.INSERT_ROUGE + (255,)))
            _ecrire(ImageDraw.Draw(self.piece), (p / 2, p / 2), "€", max(6, int(round(g["piece_px"] * q))),
                    C.INSERT_GRAISSE_FORTE, C.BLANC + (255,), "mm")
            self.etiquette = _ombre_marge(self._etiquette(self.s), self.s) if self.spec.get("etiquette") else None

    # -- dessin du refrigerateur
    def _boite(self, bw, bh):
        q = self.f

        def dessin(d, k):
            W, H = bw * k, bh * k
            d.rounded_rectangle([0, 0, W - 1, H - 1], radius=6 * q * k, fill=C.BLANC + (255,),
                                outline=C.INSERT_GRIS + (255,), width=max(1, int(2 * q * k)))
            d.rounded_rectangle([0, 0, W - 1, H * 0.3], radius=6 * q * k, fill=tuple(self.rubrique) + (255,))
            d.rectangle([0, H * 0.18, W - 1, H * 0.3], fill=tuple(self.rubrique) + (255,))
            for i, frac in enumerate((0.7, 0.45)):
                y = H * (0.48 + i * 0.16)
                d.rounded_rectangle([W * 0.16, y, W * (0.16 + frac * 0.7), y + H * 0.07], radius=H * 0.035,
                                    fill=C.INSERT_GRIS + (255,))
        return _net(bw, bh, dessin)

    def _corps(self, plein):
        g, q = C.FRIGO_GEO, self.f
        w, h = self.fw, self.fh
        x0, y0, x1, y1 = self.vitre

        def dessin(d, k):
            W, H, Q = w * k, h * k, q * k
            pw, ph = g["pied"][0] * Q, g["pied"][1] * Q
            for x in (W * 0.2, W * 0.8):
                d.rounded_rectangle([x - pw / 2, H - ph - 8 * Q, x + pw / 2, H - 1], radius=4 * Q,
                                    fill=C.INSERT_GRIS_TEXTE + (255,))
            r = g["rayon"] * Q
            d.rounded_rectangle([0, 0, W - 1, H - ph], radius=r, fill=C.BLANC + (255,))
            pan = g["panneau"] * Q
            d.rounded_rectangle([0, 0, W - 1, pan + r], radius=r, fill=C.NAVY + (255,))
            d.rectangle([0, pan, W - 1, pan + r], fill=C.BLANC + (255,))
            ew, eh = g["ecran"][0] * Q, g["ecran"][1] * Q
            d.rounded_rectangle([(W - ew) / 2, (pan - eh) / 2, (W + ew) / 2, (pan + eh) / 2], radius=eh * 0.25,
                                fill=(8, 5, 26, 255))
            led = 5 * Q
            d.ellipse([r * 0.7 - led, pan / 2 - led, r * 0.7 + led, pan / 2 + led], fill=C.INSERT_VERT + (255,))
            d.ellipse([W - r * 0.7 - led, pan / 2 - led, W - r * 0.7 + led, pan / 2 + led],
                      fill=_teinte(C.NAVY, 0.45) + (255,))
            vx0, vy0, vx1, vy1 = x0 * k, y0 * k, x1 * k, y1 * k
            d.rounded_rectangle([vx0, vy0, vx1, vy1], radius=r * 0.5, fill=_teinte(self.rubrique, 0.86) + (255,))
            lw = vx1 - vx0
            d.polygon([(vx0 + lw * 0.58, vy0), (vx0 + lw * 0.78, vy0), (vx0 + lw * 0.38, vy1), (vx0 + lw * 0.18, vy1)],
                      fill=_teinte(self.rubrique, 0.93) + (255,))
            rang = (vy1 - vy0) / 2
            for i in range(2):
                y = vy0 + rang * (i + 1) - g["etagere"] * Q
                d.rectangle([vx0, y, vx1, y + g["etagere"] * Q], fill=_teinte(self.rubrique, 0.6) + (255,))
            gw, gh = g["poignee"][0] * Q, g["poignee"][1] * Q
            gx = vx1 + (W - vx1 - gw) / 2
            d.rounded_rectangle([gx, H * 0.36, gx + gw, H * 0.36 + gh], radius=gw / 2,
                                fill=C.INSERT_GRIS + (255,))
        im = _net(w, h, dessin)
        if plein:
            for i in range(self.n):
                im.alpha_composite(self.boite, (int(round(self.places[i][0])), int(round(self.places[i][1]))))
        if not self._releve():
            self._ecran(im, self.spec.get("ecran", "+5 °C"))
        return im

    def _ecran(self, im, texte):
        g, q = C.FRIGO_GEO, self.f
        _ecrire(ImageDraw.Draw(im), (self.fw / 2, g["panneau"] * q / 2), texte, max(6, int(round(g["ecran_px"] * q))),
                C.INSERT_GRAISSE_FORTE, _teinte(C.INSERT_VERT, 0.35) + (255,), "mm")

    # -- mode « remplir »
    def _t_boite(self, i):
        return self.t0(self.spec.get("temps", 0)) + C.INSERT_ENTREE * 0.6 + i * C.FRIGO_DECALAGE

    def _t_piece(self, i):
        return self.t0(self.spec.get("prix", 1)) + i * C.FRIGO_PIECE_DECALAGE

    def _t_etiquette(self):
        return self._t_piece(self.n - 1) + C.INSERT_ENTREE * 0.6

    def _remplir(self, frigo, t, final):
        g, q = C.FRIGO_GEO, self.f
        couche = Image.new("RGBA", self.masque_vitre.size, (0, 0, 0, 0))
        for i in range(self.n):
            v = 1.0 if final else (t - self._t_boite(i)) / C.INSERT_ENTREE
            if v <= 0:
                continue
            x, y = self.places[i]
            if v < 1:                                   # la boite tombe, en accelerant
                y -= g["chute"] * q * (1 - v * v)
            else:                                       # puis rebondit a peine sur l'etagere
                w2 = 1.0 if final else (t - self._t_boite(i) - C.INSERT_ENTREE) / C.INSERT_ENTREE
                if w2 < 1:
                    y -= 6 * q * math.sin(math.pi * w2) * (1 - w2)
            T.coller(couche, self.boite, (x, y), min(1.0, v * 4))
        couche.putalpha(ImageChops.multiply(couche.getchannel("A"), self.masque_vitre))
        frigo.alpha_composite(couche, (self.mf, self.mf))
        for i in range(self.n):
            v = 1.0 if final else (t - self._t_piece(i)) / C.INSERT_ENTREE
            if v <= 0:
                continue
            x, y = self.places[i]
            kk = 0.3 + 0.7 * (1.0 if final else T.rebond(v))
            _poser(frigo, self.piece, self.mf + x + self.boite.width * 0.82, self.mf + y + self.boite.height * 0.12,
                   kk, 1.0 if final else T.lisse(v * C.INSERT_FONDU))

    # -- mode « releve »
    @staticmethod
    def _temperature(x):
        """Courbe de demonstration, toujours dans la plage (3,4 a 6,6 °C)."""
        return (5.0 + 0.9 * math.sin(2 * math.pi * (1.3 * x + 0.1)) + 0.45 * math.sin(2 * math.pi * (3.7 * x + 0.3))
                + 0.2 * math.sin(2 * math.pi * 7.1 * x))

    def _init_courbe(self):
        g = C.FRIGO_COURBE
        self.cx0 = self.fw + self.px(g["ecart"])                 # gauche de la carte, dans la boite
        cw, ch = self.w - self.cx0, self.h
        pad = self.px(g["pad"])
        carte = _cadre(cw, ch, self.s, marge=self.m)
        d = ImageDraw.Draw(carte)
        m = self.m
        _ecrire(d, (m + pad, m + pad), self.spec.get("titre", "Température enregistrée"), self.px(g["titre_px"]),
                C.INSERT_GRAISSE_FORTE, C.NAVY + (255,))
        axe = self.px(g["axe_px"])
        lab_w = T.largeur("+8 °C", axe, C.INSERT_GRAISSE_TEXTE, 0) + pad * 0.6
        self.zone = (m + pad + lab_w, m + pad + self.px(g["titre_px"]) * 1.9, m + cw - pad, m + ch - pad)
        zx0, zy0, zx1, zy1 = self.zone
        lo, hi = g["plage"]
        ya, yb = self._y(hi), self._y(lo)
        d.rectangle([zx0, ya, zx1, yb], fill=_teinte(C.INSERT_VERT, 0.85) + (255,))
        for y, v in ((ya, hi), (yb, lo)):
            for x in range(int(zx0), int(zx1), self.px(14)):
                d.line([(x, y), (min(zx1, x + self.px(8)), y)], fill=C.INSERT_VERT + (255,), width=max(1, self.px(3)))
            _ecrire(d, (zx0 - pad * 0.4, y), f"+{v}{NBSP}°C", axe, C.INSERT_GRAISSE_TEXTE, C.INSERT_VERT + (255,), "rm")
        self.carte_courbe = _ombre(carte, self.s)
        self.rec_px = self.px(g["rec_px"])
        self.rec_xy = (m + cw - pad, m + pad + self.px(g["titre_px"]) * 0.55)

    def _y(self, v):
        zx0, zy0, zx1, zy1 = self.zone
        e0, e1 = C.FRIGO_COURBE["echelle"]
        return zy1 - (v - e0) / (e1 - e0) * (zy1 - zy0)

    def _t_courbe(self):
        return self.t0(self.spec.get("temps", 0)) + C.INSERT_ENTREE * 1.2

    def _courbe(self, t, final):
        """La carte de la courbe, tracee jusqu'a p ; et la temperature du moment."""
        g = C.FRIGO_COURBE
        p = 1.0 if final else max(0.0, min(1.0, (t - self._t_courbe()) / g["duree"]))
        carte = self.carte_courbe.copy()
        zx0, zy0, zx1, zy1 = self.zone
        if p > 0:
            n = max(2, int(120 * p))
            pts = [(zx0 + (zx1 - zx0) * p * i / (n - 1), self._y(self._temperature(p * i / (n - 1))))
                   for i in range(n)]

            def dessin(d, k):
                d.line([(x * k, y * k) for x, y in pts], fill=tuple(self.rubrique) + (255,),
                       width=max(2, int(self.px(g["trait"]) * k)), joint="curve")
                r = self.px(g["tete"]) * k
                x, y = pts[-1][0] * k, pts[-1][1] * k
                d.ellipse([x - r, y - r, x + r, y + r], fill=C.BLANC + (255,), outline=tuple(self.rubrique) + (255,),
                          width=max(2, int(self.px(4) * k)))
            carte.alpha_composite(_net(carte.width, carte.height, dessin))
        # pastille rouge qui clignote : l'enregistrement ne s'arrete pas
        d = ImageDraw.Draw(carte)
        allume = final or (t * 2) % 2 < 1.3
        x, y = self.rec_xy
        r = self.rec_px * 0.36
        d.ellipse([x - 2 * r, y - r, x, y + r], fill=C.INSERT_ROUGE + (255 if allume else 60,))
        return carte, self._temperature(p)

    def image(self, t, final):
        u = 1.0 if final else (t - self.t0(self.spec.get("temps", 0))) / C.INSERT_ENTREE
        if u <= 0:
            return None
        out = Image.new("RGBA", (self.w + 2 * self.m, self.h + 2 * self.m), (0, 0, 0, 0))
        frigo = self.fond_frigo.copy()
        if self._releve():
            carte, temp = self._courbe(t, final)
            v = 1.0 if final else (t - self.t0(self.spec.get("temps", 0)) - C.INSERT_ENTREE * 0.5) / C.INSERT_ENTREE
            if v > 0:
                dx = 0 if final else C.INSERT_MONTEE * self.s * (1 - T.lisse(v))
                _poser(out, carte, self.cx0 + carte.width / 2 + dx, self.m + self.h / 2,
                       1.0, 1.0 if final else T.lisse(v * C.INSERT_FONDU))
            ecran = Image.new("RGBA", frigo.size, (0, 0, 0, 0))
            self._ecran_sur(ecran, f"+{temp:.1f}{NBSP}°C".replace(".", ","))
            frigo.alpha_composite(ecran)
        else:
            self._remplir(frigo, t, final)
        k = C.INSERT_ECHELLE + (1 - C.INSERT_ECHELLE) * (1.0 if final else T.rebond(u))
        _poser(out, frigo, self.m + self.fw / 2, self.m + self.h - self.fh / 2, k,
               1.0 if final else T.lisse(u * C.INSERT_FONDU))
        if not self._releve() and self.etiquette is not None:
            v = 1.0 if final else (t - self._t_etiquette()) / C.TAMPON_FRAPPE
            if v > 0:
                kk = 1.0 if final or v >= 1 else C.TAMPON_ECHELLE - (C.TAMPON_ECHELLE - 1) * v * v
                dx = 0.0
                if not final and v > 1:
                    w2 = (t - self._t_etiquette() - C.TAMPON_FRAPPE) / C.TAMPON_SECOUSSE[1]
                    if w2 < 1:
                        dx = C.TAMPON_SECOUSSE[0] * self.s * math.sin(2 * math.pi * 4 * w2) * (1 - w2)
                g = C.FRIGO_GEO
                cx = self.m + self.fw - g["chevauche"] * self.s + (self.etiquette.width - 2 * self.mf) / 2 + dx
                cy = self.m + self.h - self.fh + self.fh * g["etiquette_y"]
                _poser(out, self.etiquette, cx, cy, kk, 1.0 if final else min(1.0, v * C.TAMPON_GEO["fondu"]))
        return out

    def _ecran_sur(self, im, texte):
        g, q = C.FRIGO_GEO, self.f
        _ecrire(ImageDraw.Draw(im), (self.mf + self.fw / 2, self.mf + g["panneau"] * q / 2), texte,
                max(6, int(round(g["ecran_px"] * q))), C.INSERT_GRAISSE_FORTE, _teinte(C.INSERT_VERT, 0.35) + (255,), "mm")

    def sons(self):
        t0 = self.t0(self.spec.get("temps", 0))
        if self._releve():
            return [(t0, "clic"), (self._t_courbe(), "compteur")]
        out = [(self._t_boite(0), "compteur"), (self._t_piece(0), "compteur")]
        if self.etiquette is not None:
            out.append((self._t_etiquette() + C.TAMPON_FRAPPE, "impact"))
        return out


# ------------------------------------------------------------- ticket
class Ticket(_Insert):
    """Un ticket de facturation qui s'imprime ligne par ligne ; chaque ligne recoit une coche ou
    une croix, et sa valeur a droite (« remboursée », « pas à part »)."""

    def taille_nominale(self):
        g = C.TICKET_GEO
        n = len(self.spec["lignes"])
        return C.TICKET_W + 2 * g["fente_deborde"], g["fente_h"] + g["tete"] + n * g["ligne_h"] + g["pad"] + g["dents"]

    def __init__(self, *a):
        super().__init__(*a)
        g = C.TICKET_GEO
        self.lignes = self.spec["lignes"]
        self.pw = self.px(C.TICKET_W)
        self.fente = (self.px(g["fente_h"]), self.px(g["fente_deborde"]))
        self.tete, self.lh, self.pad = self.px(g["tete"]), self.px(g["ligne_h"]), self.px(g["pad"])
        self.dents = self.px(g["dents"])
        ph = self.tete + len(self.lignes) * self.lh + self.pad
        papier = Image.new("RGBA", (self.pw, ph), C.BLANC + (255,))
        d = ImageDraw.Draw(papier)
        _ecrire(d, (self.pw / 2, self.tete * 0.55), T.normaliser(self.spec.get("titre", "")).upper(),
                self.px(g["titre_px"]), C.INSERT_GRAISSE_FORTE, C.INSERT_GRIS_TEXTE + (255,), "mm")
        self.icone_x = self.pad + self.px(g["icone"]) / 2
        for i, l in enumerate(self.lignes):
            y = self.tete + i * self.lh
            for x in range(self.pad, self.pw - self.pad, self.px(16)):     # pointilles d'imprimante
                d.line([(x, y), (x + self.px(8), y)], fill=C.INSERT_GRIS + (255,), width=max(1, self.px(3)))
            cy = y + self.lh / 2
            # le libelle se resserre plutot que de toucher la valeur, alignee a droite
            x_label = self.pad + self.px(g["icone"]) + self.px(18)
            place = (self.pw - self.pad - x_label - self.px(g["ecart_valeur"])
                     - T.largeur(T.normaliser(l.get("valeur", "")), self.px(g["valeur_px"]), C.INSERT_GRAISSE_FORTE, 0))
            px = self.px(g["label_px"])
            while px > self.px(g["label_px_min"]) and \
                    T.largeur(T.normaliser(l["label"]), px, C.INSERT_GRAISSE_TEXTE, 0) > place:
                px -= 1
            _ecrire(d, (x_label, cy), l["label"], px, C.INSERT_GRAISSE_TEXTE, C.NAVY + (255,), "lm")
            couleur = C.INSERT_VERT if l.get("ok") else C.INSERT_ROUGE
            _ecrire(d, (self.pw - self.pad, cy), l.get("valeur", ""), self.px(g["valeur_px"]), C.INSERT_GRAISSE_FORTE,
                    couleur + (255,), "rm")
        self.papier = papier
        self.icones = [_icone_choix(l.get("ok"), self.px(g["icone"]), self.px(g["trait_icone"]), self.rubrique)
                       for l in self.lignes]
        fw, fh = self.pw + 2 * self.fente[1], self.fente[0]

        def dessin(d, k):
            d.rounded_rectangle([0, 0, fw * k - 1, fh * k - 1], radius=fh * k / 2, fill=C.NAVY + (255,))
            d.rounded_rectangle([fh * k * 0.6, fh * k * 0.42, (fw - fh * 0.6) * k, fh * k * 0.62], radius=fh * k * 0.1,
                                fill=(8, 5, 26, 255))
        self.imprimante = _ombre_marge(_net(fw, fh, dessin), self.s)

    def _t_ligne(self, i):
        l = self.lignes[i]
        precedentes = [j for j in range(i) if self.lignes[j].get("temps", 0) == l.get("temps", 0)]
        return self.t0(l.get("temps", 0)) + C.INSERT_ENTREE + len(precedentes) * C.TICKET_GEO["avance"] * 1.3

    def _longueur(self, t, final):
        if final:
            return self.papier.height
        a = C.TICKET_GEO["avance"]
        L = self.tete * T.lisse((t - self.t0() - C.INSERT_ENTREE * 0.4) / a)
        for i in range(len(self.lignes)):
            L += self.lh * T.lisse((t - self._t_ligne(i)) / a)
        if len(self.lignes):
            L += self.pad * T.lisse((t - self._t_ligne(len(self.lignes) - 1) - a) / a)
        return int(round(L))

    def image(self, t, final):
        u = 1.0 if final else (t - self.t0()) / C.INSERT_ENTREE
        if u <= 0:
            return None
        out = Image.new("RGBA", (self.w + 2 * self.m, self.h + 2 * self.m), (0, 0, 0, 0))
        L = self._longueur(t, final)
        x0 = self.m + self.fente[1]
        y0 = self.m + self.fente[0] / 2
        if L > 0:
            dents = self.dents
            bande = Image.new("RGBA", (self.pw, L + dents), (0, 0, 0, 0))
            bande.alpha_composite(self.papier.crop((0, 0, self.pw, L)))
            n = max(2, self.pw // max(4, dents))

            def dessin(d, k):
                pas = self.pw * k / n
                pts = [(0, 0)]
                for i in range(n):
                    pts += [(pas * (i + 0.5), dents * k * 0.95), (pas * (i + 1), 0)]
                d.polygon(pts, fill=C.BLANC + (255,))
            bande.alpha_composite(_net(self.pw, dents, dessin), (0, L))
            for i, l in enumerate(self.lignes):              # l'icone tombe quand sa ligne est sortie
                v = 1.0 if final else (t - self._t_ligne(i) - C.TICKET_GEO["avance"] * 0.8) / C.INSERT_ENTREE
                cy = self.tete + (i + 0.5) * self.lh
                if v > 0 and cy < L:
                    kk = C.CHOIX_GEO["icone_depart"] + (1 - C.CHOIX_GEO["icone_depart"]) * (1.0 if final else T.rebond(v))
                    _poser(bande, self.icones[i], self.icone_x, cy, kk, 1.0 if final else T.lisse(v * C.INSERT_FONDU))
            _poser(out, _ombre_marge(bande, self.s), x0 + self.pw / 2, y0 + (L + dents) / 2)
        k = C.INSERT_ECHELLE + (1 - C.INSERT_ECHELLE) * (1.0 if final else T.rebond(u))
        _poser(out, self.imprimante, self.m + self.w / 2, self.m + self.fente[0] / 2, k,
               1.0 if final else T.lisse(u * C.INSERT_FONDU))
        return out

    def sons(self):
        return [(self.t0() + C.INSERT_ENTREE * 0.4, "souffle")] + [(self._t_ligne(i), "clic")
                                                                    for i in range(len(self.lignes))]


# -------------------------------------------------------------- appel
class Appel(_Insert):
    """Ce qui arrive d'abord : un telephone qui sonne dans sa carte, une fleche, puis le
    courrier qui vole jusqu'a la sienne."""

    def taille_nominale(self):
        return C.TEXTE_LARGEUR, C.APPEL_H

    def __init__(self, *a):
        super().__init__(*a)
        g = C.APPEL_GEO
        self.etapes = self.spec["etapes"][:2]
        self.ecart = self.px(g["ecart"])
        self.cw = (self.w - self.ecart) // 2
        self.cartes = [self._carte(e) for e in self.etapes]
        self.icones = [self._icone(e.get("icone")) for e in self.etapes]
        self.ondes = self._ondes()

    def _icone(self, nom):
        return {"telephone": self._telephone, "infirmier": self._infirmier}.get(nom, self._enveloppe)()

    def _infirmier(self):
        """Un soignant en buste, la croix du soin sur la poitrine (l'infirmier en pratique avancee)."""
        g = C.APPEL_GEO
        w, h = self.px(g["infirmier"][0]), self.px(g["infirmier"][1])
        rub = tuple(self.rubrique) + (255,)

        def dessin(d, k):
            W, H = w * k, h * k
            r = W * 0.2
            d.ellipse([W / 2 - r, 0, W / 2 + r, 2 * r], fill=C.NAVY + (255,))
            d.rounded_rectangle([W * 0.08, H * 0.42, W * 0.92, H - 1], radius=W * 0.3, fill=rub)
            c, l, e = (W / 2, H * 0.7), W * 0.26, W * 0.08
            d.rectangle([c[0] - l / 2, c[1] - e / 2, c[0] + l / 2, c[1] + e / 2], fill=C.BLANC + (255,))
            d.rectangle([c[0] - e / 2, c[1] - l / 2, c[0] + e / 2, c[1] + l / 2], fill=C.BLANC + (255,))
        return _net(w, h, dessin)

    def _carte(self, e):
        g, m = C.APPEL_GEO, self.m
        im = _cadre(self.cw, self.h, self.s, marge=m)
        d = ImageDraw.Draw(im)
        pad = self.px(g["pad"])
        px, pn = self.px(g["label_px"]), self.px(g["note_px"])
        lignes = _couper(e["label"], px, C.INSERT_GRAISSE_FORTE, self.cw - 2 * pad)
        note = e.get("note")
        bas = m + self.h - pad - (pn * 1.3 if note else 0)
        for i, l in enumerate(reversed(lignes)):
            _ecrire(d, (m + self.cw / 2, bas - i * px * 1.18), l, px, C.INSERT_GRAISSE_FORTE, C.NAVY + (255,), "ms")
        if note:
            _ecrire(d, (m + self.cw / 2, m + self.h - pad), note, pn, C.INSERT_GRAISSE_TEXTE,
                    C.INSERT_GRIS_TEXTE + (255,), "ms")
        return _ombre(im, self.s)

    def _telephone(self):
        g = C.APPEL_GEO
        w, h = self.px(g["telephone"][0]), self.px(g["telephone"][1])

        def dessin(d, k):
            W, H = w * k, h * k
            d.rounded_rectangle([0, 0, W - 1, H - 1], radius=W * 0.2, fill=C.NAVY + (255,))
            b = W * 0.08
            d.rounded_rectangle([b, b * 1.6, W - b, H - b * 1.6], radius=W * 0.12, fill=tuple(self.rubrique) + (255,))
            r = W * 0.17
            d.ellipse([W / 2 - r, H * 0.3 - r, W / 2 + r, H * 0.3 + r], fill=_teinte(self.rubrique, 0.75) + (255,))
            rb = W * 0.11
            for x, c in ((W * 0.3, C.INSERT_ROUGE), (W * 0.7, C.INSERT_VERT)):
                d.ellipse([x - rb, H * 0.76 - rb, x + rb, H * 0.76 + rb], fill=c + (255,))
            d.rounded_rectangle([W * 0.38, b * 0.55, W * 0.62, b * 1.05], radius=b * 0.25, fill=(8, 5, 26, 255))
        return _net(w, h, dessin)

    def _enveloppe(self):
        g = C.APPEL_GEO
        w, h = self.px(g["enveloppe"][0]), self.px(g["enveloppe"][1])
        tr = self.px(g["trait"])

        def dessin(d, k):
            W, H, e = w * k, h * k, tr * k
            d.rounded_rectangle([e / 2, e / 2, W - e / 2, H - e / 2], radius=W * 0.06, fill=C.BLANC + (255,),
                                outline=C.NAVY + (255,), width=int(e))
            d.line([(e, e), (W / 2, H * 0.58), (W - e, e)], fill=C.NAVY + (255,), width=int(e), joint="curve")
            r = H * 0.14
            d.ellipse([W - r * 1.6 - r, -0, W - r * 1.6 + r, 2 * r], fill=C.INSERT_ROUGE + (255,))
        return _net(w, h, dessin)

    def _ondes(self):
        """Les ondes de la sonnerie, de part et d'autre du telephone."""
        g = C.APPEL_GEO
        tw, th = self.px(g["telephone"][0]), self.px(g["telephone"][1])
        w, h = tw * 2.2, th * 0.8
        tr = self.px(g["trait"])

        def dessin(d, k):
            W, H = w * k, h * k
            for i in range(g["ondes"]):
                r = (tw * 0.62 + i * tr * 2.6) * k
                box = [W / 2 - r, H / 2 - r, W / 2 + r, H / 2 + r]
                for a0 in (-35, 145):
                    d.arc(box, a0, a0 + 70, fill=tuple(self.rubrique) + (255,), width=int(tr * k))
        return _net(w, h, dessin)

    def _t(self, i):
        if "temps" in self.etapes[i]:                    # une etape peut attendre son temps du texte
            return self.t0(self.etapes[i]["temps"])
        t = self.t0(self.spec.get("temps", 0))
        return t if i == 0 else t + C.APPEL_GEO["courrier"]

    def image(self, t, final):
        g = C.APPEL_GEO
        out = Image.new("RGBA", (self.w + 2 * self.m, self.h + 2 * self.m), (0, 0, 0, 0))
        for i, carte in enumerate(self.cartes):
            u = 1.0 if final else (t - self._t(i)) / C.INSERT_ENTREE
            if u <= 0:
                continue
            k = C.INSERT_ECHELLE + (1 - C.INSERT_ECHELLE) * (1.0 if final else T.rebond(u))
            dx = 0 if final or i == 0 else C.INSERT_MONTEE * self.s * (1 - T.lisse(u))
            cx = self.m + i * (self.cw + self.ecart) + self.cw / 2
            _poser(out, carte, cx + dx, self.m + self.h / 2, k, 1.0 if final else T.lisse(u * C.INSERT_FONDU))
            iy = self.m + self.px(g["icone_y"])
            icone, angle, ix = self.icones[i], 0.0, cx + dx
            if self.etapes[i].get("icone") == "telephone":
                tau = 0.0 if final else t - self._t(i) - C.INSERT_ENTREE * 0.4
                sonne = not final and 0 < tau < g["sonnerie"] and (tau % 0.65) < 0.45
                if sonne:
                    angle = g["secousse"] * math.sin(2 * math.pi * 14 * tau)
                    _poser(out, self.ondes, ix, iy, 1.0, 0.55 + 0.45 * math.sin(2 * math.pi * 3 * tau) ** 2)
            elif self.etapes[i].get("icone") != "infirmier":   # le courrier arrive en vol, de la droite
                v = 1.0 if final else (t - self._t(i) - C.INSERT_ENTREE * 0.3) / (C.INSERT_ENTREE * 1.4)
                if v <= 0:
                    continue
                p = 1.0 if final else T.rebond(v)
                ix += (1 - p) * self.px(260)
                iy -= (1 - p) * self.px(90)
                angle = -22 * (1 - p)
            _poser(out, icone, ix, iy, k, 1.0 if final else T.lisse(u * C.INSERT_FONDU), angle)
        if len(self.cartes) == 2:                         # la fleche se trace d'une carte a l'autre
            p = 1.0 if final else (t - (self._t(1) - C.INSERT_ENTREE * 0.6)) / (C.INSERT_ENTREE * 0.6)
            x0 = self.m + self.cw + self.ecart * 0.2
            x1 = self.m + self.cw + self.ecart * 0.8
            fl = Image.new("RGBA", out.size, (0, 0, 0, 0))
            _fleche(ImageDraw.Draw(fl), x0, x1, self.m + self.h / 2, p, self.px(C.CIRCUIT_GEO["trait"]),
                    self.px(C.CIRCUIT_GEO["tete"]), C.BLANC + (255,))
            out.alpha_composite(_ombre(fl, self.s))
        return out

    def sons(self):
        return [(self._t(0), "clic")] + ([(self._t(1), "souffle")] if len(self.cartes) == 2 else [])


# -------------------------------------------------------------- loupe
class Loupe(_Insert):
    """Une page qu'on fouille : la recherche se tape, la loupe balaie la page, rien ne sort."""

    def taille_nominale(self):
        return C.TEXTE_LARGEUR, C.LOUPE_H

    def __init__(self, *a):
        super().__init__(*a)
        g = C.LOUPE_GEO
        m = self.m
        carte = _cadre(self.w, self.h, self.s, marge=m)
        d = ImageDraw.Draw(carte)
        barre = self.px(g["barre"])
        rayon = max(4, int(C.INSERT_RAYON * self.s))
        gris = _teinte(C.INSERT_GRIS_TEXTE, 0.82)
        d.rounded_rectangle([m, m, m + self.w - 1, m + barre], radius=rayon, fill=gris + (255,))
        d.rectangle([m, m + barre - rayon, m + self.w - 1, m + barre], fill=gris + (255,))
        r = self.px(g["point"])
        for i in range(3):
            x = m + self.px(28) + i * r * 3
            d.ellipse([x - r, m + barre / 2 - r, x + r, m + barre / 2 + r], fill=C.BLANC + (255,))
        upx = self.px(g["url_px"])
        url = T.normaliser(self.spec.get("site", ""))
        uw = T.largeur(url, upx, C.INSERT_GRAISSE_TEXTE, 0) + 2 * self.px(g["url_pad"])
        ux = m + self.px(28) + r * 9
        d.rounded_rectangle([ux, m + barre * 0.2, ux + uw, m + barre * 0.8], radius=barre * 0.3, fill=C.BLANC + (255,))
        _ecrire(d, (ux + uw / 2, m + barre / 2), url, upx, C.INSERT_GRAISSE_TEXTE, C.INSERT_GRIS_TEXTE + (255,), "mm")
        pad = self.px(28)
        ch = self.px(g["champ_h"])
        self.champ = (m + pad, m + barre + self.px(g["champ_y"]), m + self.w - pad, m + barre + self.px(g["champ_y"]) + ch)
        x0, y0, x1, y1 = self.champ
        d.rounded_rectangle([x0, y0, x1, y1], radius=ch / 2, outline=C.INSERT_GRIS + (255,), width=max(2, self.px(4)))
        self.fond = _ombre(carte, self.s)
        self.petite = self._loupe(ch * 0.18, max(2, self.px(4)), C.INSERT_GRIS_TEXTE)
        self.grande = self._loupe(self.px(g["loupe"]), self.px(g["trait"]), C.NAVY, vitre=True)
        self.zone = (x0, y1, x1, m + self.h)                       # sous le champ : la page

    def _loupe(self, r, trait, couleur, vitre=False):
        taille = r * 3.3

        def dessin(d, k):
            R, e, c = r * k, trait * k, taille * k * 0.38
            if vitre:
                d.ellipse([c - R, c - R, c + R, c + R], fill=_teinte(self.rubrique, 0.82) + (150,))
            d.ellipse([c - R, c - R, c + R, c + R], outline=tuple(couleur) + (255,), width=int(e))
            a = c + R * 0.72
            d.line([(a, a), (taille * k * 0.92, taille * k * 0.92)], fill=tuple(couleur) + (255,), width=int(e * 1.5))
        return _net(taille, taille, dessin)

    def _temps(self):
        g = C.LOUPE_GEO
        t0 = self.t0(self.spec.get("temps", 0)) + C.INSERT_ENTREE * 0.5
        return t0, t0 + g["frappe"], t0 + g["frappe"] + g["balayage"]

    def image(self, t, final):
        g = C.LOUPE_GEO
        u = 1.0 if final else (t - self.t0(self.spec.get("temps", 0))) / C.INSERT_ENTREE
        if u <= 0:
            return None
        carte = self.fond.copy()
        d = ImageDraw.Draw(carte)
        frappe, balai, fin = self._temps()
        x0, y0, x1, y1 = self.champ
        ch = y1 - y0
        _poser(carte, self.petite, x0 + ch * 0.62, (y0 + y1) / 2 + ch * 0.04)
        texte = T.normaliser(self.spec.get("recherche", ""))
        n = len(texte) if final else int(len(texte) * max(0.0, min(1.0, (t - frappe) / g["frappe"])))
        px = self.px(g["champ_px"])
        tx = x0 + ch * 1.15
        _ecrire(d, (tx, (y0 + y1) / 2), texte[:n], px, C.INSERT_GRAISSE_TEXTE, C.NAVY + (255,), "lm")
        if not final and t < fin and (t % g["curseur"]) < g["curseur"] * 0.55:
            xc = tx + T.largeur(texte[:n], px, C.INSERT_GRAISSE_TEXTE, 0) + self.px(4)
            d.line([(xc, (y0 + y1) / 2 - px * 0.6), (xc, (y0 + y1) / 2 + px * 0.6)], fill=tuple(self.rubrique) + (255,),
                   width=max(2, self.px(4)))
        zx0, zy0, zx1, zy1 = self.zone
        cx, cy = (zx0 + zx1) / 2, (zy0 + zy1) / 2
        if not final and balai < t < fin + C.INSERT_ENTREE:      # la loupe cherche, en huit
            tau = (t - balai) / g["balayage"]
            a = min(1.0, (t - balai) / C.INSERT_ENTREE) * min(1.0, max(0.0, (fin + C.INSERT_ENTREE - t) / C.INSERT_ENTREE))
            lx = cx + (zx1 - zx0) * 0.3 * math.sin(2 * math.pi * tau)
            ly = cy + (zy1 - zy0) * 0.16 * math.sin(4 * math.pi * tau)
            _poser(carte, self.grande, lx + self.grande.width * 0.12, ly + self.grande.height * 0.12, 1.0, a)
        v = 1.0 if final else (t - fin) / C.INSERT_ENTREE
        if v > 0:
            _ecrire(d, (cx, zy0 + (zy1 - zy0) * g["vide_y"]), self.spec.get("vide", ""), self.px(g["vide_px"]),
                    C.INSERT_GRAISSE_FORTE,
                    C.INSERT_GRIS_TEXTE + (int(255 * min(1.0, v)),), "mm")
        out = Image.new("RGBA", (self.w + 2 * self.m, self.h + 2 * self.m), (0, 0, 0, 0))
        k = C.INSERT_ECHELLE + (1 - C.INSERT_ECHELLE) * (1.0 if final else T.rebond(u))
        _poser(out, carte, carte.width / 2, carte.height / 2, k, 1.0 if final else T.lisse(u * C.INSERT_FONDU))
        return out

    def sons(self):
        frappe, balai, _ = self._temps()
        return [(frappe, "compteur"), (balai, "souffle")]


# ------------------------------------------------------------- calcul
class Calcul(_Insert):
    """Le calcul qui cible les medecins : la barre se remplit ; au temps "temps_question", la part
    marquee "question" se detache vers le haut, son empreinte en pointille, un « ? » au-dessus."""

    def taille_nominale(self):
        return C.TEXTE_LARGEUR, C.CALCUL_H

    def __init__(self, *a):
        super().__init__(*a)
        g = C.CALCUL_GEO
        m, pad = self.m, self.px(g["pad"])
        self.parts = self.spec["parts"]
        total = sum(p["valeur"] for p in self.parts)
        self.bx0, self.bx1 = m + pad, m + self.w - pad
        self.by, self.bh = m + self.px(g["barre_y"]), self.px(g["barre_h"])
        bw = self.bx1 - self.bx0
        bornes, x = [], 0.0
        for p in self.parts:
            bornes.append((x, x + bw * p["valeur"] / total))
            x = bornes[-1][1]
        self.bornes = bornes
        carte = _cadre(self.w, self.h, self.s, marge=m)
        d = ImageDraw.Draw(carte)
        _ecrire(d, (m + pad, m + pad), self.spec.get("titre", ""), self.px(g["titre_px"]), C.INSERT_GRAISSE_FORTE,
                C.NAVY + (255,))
        d.rounded_rectangle([self.bx0, self.by, self.bx1, self.by + self.bh], radius=self.bh / 2,
                            fill=C.INSERT_GRIS + (255,))
        self.fond = carte
        self.segments = [self._segment(i) for i in range(len(self.parts))]
        self.labels = self._labels()
        b = self.px(g["badge"])
        badge = _net(2 * b, 2 * b, lambda dd, k: dd.ellipse([0, 0, 2 * b * k - 1, 2 * b * k - 1], fill=C.NAVY + (255,)))
        _ecrire(ImageDraw.Draw(badge), (b, b), "?", int(b * 1.25), C.INSERT_GRAISSE_FORTE, C.BLANC + (255,), "mm")
        self.badge = _ombre_marge(badge, self.s)
        self.question = next((i for i, p in enumerate(self.parts) if p.get("question")), None)
        if self.question is not None:
            a, b2 = self.bornes[self.question]
            empreinte = _net(b2 - a, self.bh, lambda dd, k: dd.rounded_rectangle(
                [0, 0, (b2 - a) * k - 1, self.bh * k - 1], radius=self.bh * k / 2 if self.question == len(self.parts) - 1 else 0,
                outline=C.INSERT_GRIS_TEXTE + (255,), width=int(self.px(4) * k)))
            self.empreinte = _pointilles(empreinte, *[self.px(v) for v in g["pointille"]])

    def _ton(self, p):
        """Couleur d'une part : "ton" rouge ou vert (une regle defavorable ou favorable) ; "bleu",
        ou pas de ton, la rubrique. Un libelle ne prend la couleur de sa part que si elle porte un
        ton."""
        return {"rouge": C.INSERT_ROUGE, "vert": C.INSERT_VERT}.get(p.get("ton"), tuple(self.rubrique))

    def _segment(self, i):
        """Le segment i, arrondi a ses bouts exterieurs ; raye s'il porte la question."""
        g = C.CALCUL_GEO
        a, b = self.bornes[i]
        w, h = b - a, self.bh
        premier, dernier = i == 0, i == len(self.parts) - 1
        question = self.parts[i].get("question")

        def dessin(d, k):
            W, H = w * k, h * k
            couleur = _teinte(self.rubrique, 0.45) if question else self._ton(self.parts[i])
            gauche = 0 if premier else -H
            droite = W if dernier else W + H
            d.rounded_rectangle([gauche, 0, droite - 1, H - 1], radius=H / 2, fill=couleur + (255,))
            if question:
                pas = self.px(g["rayures"]) * k
                x = -H
                while x < W:
                    d.line([(x, H), (x + H, 0)], fill=_teinte(self.rubrique, 0.68) + (255,), width=int(pas * 0.4))
                    x += pas
        return _net(w, h, dessin)

    def _labels(self):
        g = C.CALCUL_GEO
        px = self.px(g["label_px"])
        y = self.by + self.bh + self.px(g["accolade_y"])
        out = []
        for i, p in enumerate(self.parts):
            a, b = self.bornes[i]
            dernier = i == len(self.parts) - 1
            im = Image.new("RGBA", self.fond.size, (0, 0, 0, 0))
            d = ImageDraw.Draw(im)
            couleur = (self._ton(p) if p.get("ton") else C.NAVY if p.get("question") else C.INSERT_GRIS_TEXTE) + (255,)
            tr = max(2, self.px(3))
            d.line([(self.bx0 + a + tr, y), (self.bx0 + b - tr, y)], fill=couleur, width=tr)
            for x in (self.bx0 + a + tr, self.bx0 + b - tr):
                d.line([(x, y - self.px(10)), (x, y)], fill=couleur, width=tr)
            ancre, x = ("rt", self.bx0 + b) if dernier else ("lt", self.bx0 + a)
            _ecrire(d, (x, y + self.px(10)), p["label"], px,
                    C.INSERT_GRAISSE_FORTE if p.get("question") else C.INSERT_GRAISSE_TEXTE, couleur, ancre)
            out.append(im)
        return out

    def _t_question(self):
        return self.t0(self.spec.get("temps_question", 1)) + C.INSERT_DELAI

    def image(self, t, final):
        g = C.CALCUL_GEO
        u = 1.0 if final else (t - self.t0()) / C.INSERT_ENTREE
        if u <= 0:
            return None
        carte = self.fond.copy()
        p = 1.0 if final else T.lisse((t - self.t0() - C.INSERT_ENTREE * 0.5) / g["remplissage"])
        bw = self.bx1 - self.bx0
        rempli = bw * p
        v = 0.0 if self.question is None else (1.0 if final else T.lisse((t - self._t_question()) / C.INSERT_ENTREE))
        for i, seg in enumerate(self.segments):
            a, b = self.bornes[i]
            if rempli <= a:
                continue
            vis = seg.crop((0, 0, max(1, int(round(min(b, rempli) - a))), seg.height))
            if i == self.question and v > 0:
                carte.alpha_composite(self.empreinte, (int(round(self.bx0 + a)), int(round(self.by))))
                dy = -self.px(g["levee"]) * v
                flotte = 0.0 if final else self.px(g["flotte"]) * math.sin(2 * math.pi * 0.8 * (t - self._t_question())) * v
                cx = self.bx0 + (a + b) / 2
                cy = self.by + self.bh / 2 + dy + flotte
                _poser(carte, _ombre_marge(vis, self.s), cx, cy, 1.0, 1.0, g["angle"] * v)
                w2 = 1.0 if final else (t - self._t_question() - C.INSERT_ENTREE * 0.5) / C.INSERT_ENTREE
                if w2 > 0:
                    kk = 0.3 + 0.7 * (1.0 if final else T.rebond(w2))
                    _poser(carte, self.badge, self.bx0 + b - self.px(g["badge"]) * 0.6,
                           cy - self.bh / 2 - self.px(g["badge"]) * 0.7, kk, 1.0 if final else T.lisse(w2 * C.INSERT_FONDU))
            else:
                carte.alpha_composite(vis, (int(round(self.bx0 + a)), int(round(self.by))))
        for i, lab in enumerate(self.labels):
            w2 = 1.0 if final else (t - self.t0() - C.INSERT_ENTREE * 0.5 - g["remplissage"] * (i + 1) / len(self.labels)) \
                / C.INSERT_ENTREE
            if w2 > 0:
                T.coller(carte, lab, (0, 0), min(1.0, w2))
        carte = _ombre(carte, self.s)
        out = Image.new("RGBA", (self.w + 2 * self.m, self.h + 2 * self.m), (0, 0, 0, 0))
        k = C.INSERT_ECHELLE + (1 - C.INSERT_ECHELLE) * (1.0 if final else T.rebond(u))
        _poser(out, carte, carte.width / 2, carte.height / 2, k, 1.0 if final else T.lisse(u * C.INSERT_FONDU))
        return out

    def sons(self):
        out = [(self.t0() + C.INSERT_ENTREE * 0.5, "souffle")]
        if self.question is not None:
            out += [(self._t_question(), "clic"), (self._t_question() + C.INSERT_ENTREE * 0.5, "impact")]
        return out


def _ton(spec, rubrique):
    """Couleur d'un element : "ton" rouge, vert, ou la rubrique."""
    return {"rouge": C.INSERT_ROUGE, "vert": C.INSERT_VERT}.get(spec.get("ton"), tuple(rubrique))


def _bulle(texte, px, h, pad, couleur, queue=True):
    """Pilule de couleur, texte blanc, avec une pointe dessous (une bulle qui designe)."""
    w = int(T.largeur(T.normaliser(texte), px, C.INSERT_GRAISSE_FORTE, 0) + 2 * pad)
    q = h * 0.32 if queue else 0

    def dessin(d, k):
        d.rounded_rectangle([0, 0, w * k - 1, h * k - 1], radius=h * k / 2, fill=tuple(couleur) + (255,))
        if queue:
            d.polygon([(w * k / 2 - q * k, h * k - 2), (w * k / 2 + q * k, h * k - 2), (w * k / 2, (h + q) * k)],
                      fill=tuple(couleur) + (255,))
    im = _net(w, h + q, dessin)
    _ecrire(ImageDraw.Draw(im), (w / 2, h / 2), texte, px, C.INSERT_GRAISSE_FORTE, C.BLANC + (255,), "mm")
    return im


def _entree(t, t0, final):
    """(echelle, opacite) d'un element qui arrive en rebond a t0."""
    u = 1.0 if final else (t - t0) / C.INSERT_ENTREE
    if u <= 0:
        return 0.0, 0.0
    return (C.INSERT_ECHELLE + (1 - C.INSERT_ECHELLE) * (1.0 if final else T.rebond(u)),
            1.0 if final else T.lisse(u * C.INSERT_FONDU))


# --------------------------------------------------------------- ages
class Ages(_Insert):
    """La regle des ages : trois zones colorees, un curseur « vous » qui va de zone en zone (dans
    l'ordre de "ordre") ; a chaque arret, une bulle dit ce que devient la pension dans cette zone."""

    def taille_nominale(self):
        return C.TEXTE_LARGEUR, C.AGES_H

    def __init__(self, *a):
        super().__init__(*a)
        g, m = C.AGES_GEO, self.m
        pad = self.px(g["pad"])
        self.zones = self.spec["zones"]
        n = len(self.zones)
        self.x0, self.x1 = m + pad, m + self.w - pad
        self.ry = m + self.px(g["regle_y"])
        rh, ecart = self.px(g["regle_h"]), self.px(g["ecart"])
        larg = (self.x1 - self.x0 - (n - 1) * ecart) / n
        self.bornes = [(self.x0 + i * (larg + ecart), self.x0 + i * (larg + ecart) + larg) for i in range(n)]
        carte = _cadre(self.w, self.h, self.s, marge=m)
        d = ImageDraw.Draw(carte)
        _ecrire(d, (m + pad, m + pad), self.spec.get("titre", ""), self.px(g["titre_px"]), C.INSERT_GRAISSE_FORTE,
                C.NAVY + (255,))
        regle = Image.new("RGBA", carte.size, (0, 0, 0, 0))

        def dessin(dd, k):
            for i, (a, b) in enumerate(self.bornes):
                r = rh * k / 2 if i in (0, n - 1) else rh * k * 0.2
                dd.rounded_rectangle([a * k, (self.ry - rh / 2) * k, b * k, (self.ry + rh / 2) * k], radius=r,
                                     fill=_ton(self.zones[i], self.rubrique) + (255,))
        regle.alpha_composite(_net(carte.width, carte.height, dessin))
        carte.alpha_composite(regle)
        for i, (a, b) in enumerate(self.bornes):
            _ecrire(d, ((a + b) / 2, self.ry + rh / 2 + self.px(g["label_ecart"])), self.zones[i]["label"], self.px(g["label_px"]),
                    C.INSERT_GRAISSE_FORTE, _ton(self.zones[i], self.rubrique) + (255,), "mt")
        self.fond = _ombre(carte, self.s)
        self.bulles = [_ombre_marge(_bulle(z["bulle"], self.px(g["bulle_px"]), self.px(g["bulle_h"]),
                                           self.px(g["bulle_pad"]), _ton(z, self.rubrique)), self.s) for z in self.zones]
        r = self.px(g["curseur"])
        curseur = _net(2 * r + 4, 2 * r + 4, lambda dd, k: (
            dd.ellipse([2 * k, 2 * k, (2 * r + 2) * k, (2 * r + 2) * k], fill=C.BLANC + (255,)),
            dd.ellipse([2 * k + r * 0.28 * k, 2 * k + r * 0.28 * k, (2 * r + 2) * k - r * 0.28 * k,
                        (2 * r + 2) * k - r * 0.28 * k], fill=C.NAVY + (255,))))
        self.curseur = _ombre_marge(curseur, self.s)
        self.ordre = self.spec.get("ordre", list(range(n)))

    def _etapes(self):
        """[(zone, arrivee, depart)] : le curseur arrive au centre de chaque zone, s'y arrete."""
        g = C.AGES_GEO
        t = self.t0(self.spec.get("temps", 0)) + C.INSERT_ENTREE * 0.8
        out = []
        for k, z in enumerate(self.ordre):
            arrivee = t if k == 0 else t + g["deplacement"]
            depart = arrivee + g["pause"]
            out.append((z, arrivee, depart))
            t = depart
        return out

    def _x(self, z):
        a, b = self.bornes[z]
        return (a + b) / 2

    def image(self, t, final):
        g = C.AGES_GEO
        k, a = _entree(t, self.t0(self.spec.get("temps", 0)), final)
        if a <= 0:
            return None
        carte = self.fond.copy()
        etapes = self._etapes()
        if final:
            z, x, bulle = etapes[-1][0], self._x(etapes[-1][0]), (etapes[-1][0], 1.0)
        else:
            x, bulle = self._x(etapes[0][0]), None
            for i, (z, arr, dep) in enumerate(etapes):
                if t >= arr:
                    x = self._x(z)
                    bulle = (z, (t - arr) / C.INSERT_ENTREE)
                if i + 1 < len(etapes) and dep <= t < etapes[i + 1][1]:      # en chemin vers la suivante
                    p = T.lisse((t - dep) / g["deplacement"])
                    x = self._x(z) + (self._x(etapes[i + 1][0]) - self._x(z)) * p
                    bulle = None
            if t < etapes[0][1]:
                bulle = None
        _poser(carte, self.curseur, x, self.ry)
        if bulle:
            z, u = bulle
            kk = C.INSERT_ECHELLE + (1 - C.INSERT_ECHELLE) * (1.0 if final else T.rebond(u))
            b = self.bulles[z]
            bx = min(max(x, self.m + b.width / 2), self.m + self.w - b.width / 2)
            _poser(carte, b, bx, self.ry - self.px(g["curseur"]) - self.px(g["bulle_ecart"]) - (b.height - 2 * self.m) / 2
                   - self.m + self.m, kk, 1.0 if final else T.lisse(u * C.INSERT_FONDU))
        out = Image.new("RGBA", (self.w + 2 * self.m, self.h + 2 * self.m), (0, 0, 0, 0))
        _poser(out, carte, carte.width / 2, carte.height / 2, k, a)
        return out

    def sons(self):
        e = self._etapes()
        return [(e[0][1] - C.INSERT_ENTREE * 0.4, "souffle")] + [(arr, "clic") for _, arr, _ in e]


# --------------------------------------------------------------- vases
class Vases(_Insert):
    """Deux bocaux communicants : vos revenus montent, votre pension baisse d'autant, des « +1 € »
    et « −1 € » s'envolent ; au temps "ajout", une piece (« IJ ») tombe dans les revenus et la
    pension baisse encore."""

    def taille_nominale(self):
        return C.TEXTE_LARGEUR, C.VASES_H

    def __init__(self, *a):
        super().__init__(*a)
        g, m = C.VASES_GEO, self.m
        carte = _cadre(self.w, self.h, self.s, marge=m)
        d = ImageDraw.Draw(carte)
        _ecrire(d, (m + self.w / 2, m + self.px(g["pad"])), self.spec.get("titre", ""), self.px(g["titre_px"]),
                C.INSERT_GRAISSE_FORTE, C.NAVY + (255,), "mt")
        self.vw, self.vh = self.px(g["vase"][0]), self.px(g["vase"][1])
        self.fond_y = m + self.px(g["fond_y"])                              # bas des bocaux
        self.cx = [m + self.w * c for c in g["col"]]
        for cx, lab in zip(self.cx, (self.spec.get("gauche", ""), self.spec.get("droite", ""))):
            _ecrire(d, (cx, self.fond_y + self.px(10)), lab, self.px(g["label_px"]), C.INSERT_GRAISSE_FORTE,
                    C.NAVY + (255,), "mt")
        self.fond = carte
        tr = self.px(g["trait"])
        self.bocal = _net(self.vw, self.vh, lambda dd, k: dd.rounded_rectangle(
            [tr * k / 2, tr * k / 2, (self.vw - tr / 2) * k, (self.vh - tr / 2) * k], radius=self.vw * k * 0.16,
            outline=C.INSERT_GRIS + (255,), width=int(tr * k)))
        self.masque = _net(self.vw, self.vh, lambda dd, k: dd.rounded_rectangle(
            [tr * k, tr * k, (self.vw - tr) * k, (self.vh - tr) * k], radius=self.vw * k * 0.13,
            fill=(255, 255, 255, 255))).getchannel("A")
        j = self.px(g["jeton"])
        jeton = _net(j, j, lambda dd, k: dd.ellipse([0, 0, j * k - 1, j * k - 1], fill=C.INSERT_VERT + (255,)))
        _ecrire(ImageDraw.Draw(jeton), (j / 2, j / 2), self.spec.get("ajout", {}).get("label", ""),
                self.px(g["jeton_px"]), C.INSERT_GRAISSE_FORTE, C.BLANC + (255,), "mm")
        self.jeton = _ombre_marge(jeton, self.s)

    def _t(self):
        return self.t0(self.spec.get("temps", 0)) + C.INSERT_ENTREE * 0.8

    def _t_ajout(self):
        return self.t0(self.spec.get("ajout", {}).get("temps", 1)) + C.INSERT_DELAI

    def _niveaux(self, t, final):
        g = C.VASES_GEO
        p = 1.0 if final else T.lisse((t - self._t()) / g["remplissage"])
        rev = g["revenus"][0] + (g["revenus"][1] - g["revenus"][0]) * p
        pen = g["pension"][0] + (g["pension"][1] - g["pension"][0]) * p
        if self.spec.get("ajout"):
            q = 1.0 if final else T.lisse((t - self._t_ajout() - g["chute"]) / C.INSERT_ENTREE)
            rev += g["ij"] * q
            pen -= g["ij"] * q
        return rev, pen

    def _contenu(self, niveau, couleur, t):
        """Le bocal rempli jusqu'a niveau (0 a 1), surface ondulee."""
        g = C.VASES_GEO
        tr = self.px(g["trait"])
        haut = tr + (self.vh - 2 * tr) * (1 - niveau)
        amp = self.px(g["vague"])

        def dessin(dd, k):
            pts = [(x * k, (haut + amp * math.sin(2 * math.pi * (x / self.vw * g["onde"][0] + t * g["onde"][1]))) * k)
                   for x in range(0, self.vw + 1, max(1, self.vw // 24))]
            dd.polygon(pts + [(self.vw * k, self.vh * k), (0, self.vh * k)], fill=tuple(couleur) + (255,))
        im = _net(self.vw, self.vh, dessin)
        im.putalpha(ImageChops.multiply(im.getchannel("A"), self.masque))
        im.alpha_composite(self.bocal)
        return im

    def image(self, t, final):
        g = C.VASES_GEO
        k, a = _entree(t, self.t0(self.spec.get("temps", 0)), final)
        if a <= 0:
            return None
        carte = self.fond.copy()
        rev, pen = self._niveaux(t, final)
        for cx, niveau, couleur in ((self.cx[0], rev, C.INSERT_VERT), (self.cx[1], pen, self.rubrique)):
            v = self._contenu(niveau, couleur, 0 if final else t)
            carte.alpha_composite(v, (int(round(cx - self.vw / 2)), int(round(self.fond_y - self.vh))))
        d = ImageDraw.Draw(carte)
        if not final:                                    # les « +1 € » et « −1 € » s'envolent
            n = int(g["remplissage"] / g["envol_pas"])
            for i in range(n):
                ti = self._t() + i * g["envol_pas"]
                w2 = (t - ti) / g["envol"]
                if 0 < w2 < 1:
                    al = int(255 * min(1.0, w2 * 4) * (1 - w2))
                    dy = self.px(g["envol_dy"]) * T.lisse(w2)
                    y = self.fond_y - self.vh * 0.35 - dy
                    ecart = self.vw / 2 + self.px(g["envol_ecart"])
                    _ecrire(d, (self.cx[0] - ecart, y), f"+1{NBSP}€", self.px(g["envol_px"]), C.INSERT_GRAISSE_FORTE,
                            C.INSERT_VERT + (al,), "rs")
                    _ecrire(d, (self.cx[1] + ecart, y), f"−1{NBSP}€", self.px(g["envol_px"]), C.INSERT_GRAISSE_FORTE,
                            C.INSERT_ROUGE + (al,), "ls")
        _ecrire(d, ((self.cx[0] + self.cx[1]) / 2, self.fond_y - self.vh * g["egal_y"]), "=", self.px(g["egal_px"]),
                C.INSERT_GRAISSE_FORTE, C.INSERT_GRIS_TEXTE + (255,), "mm")
        if self.spec.get("ajout") and not final:         # le jeton tombe dans le bocal des revenus
            w2 = (t - self._t_ajout()) / g["chute"]
            if 0 < w2 < g["jeton_vie"]:
                y0 = self.fond_y - self.vh - self.px(g["jeton_haut"])
                y1 = self.fond_y - self.vh * (rev + 0.1)
                y = y0 + (y1 - y0) * min(1.0, w2) ** 2
                _poser(carte, self.jeton, self.cx[0], y, 1.0, min(1.0, (g["jeton_vie"] - w2) * 3))
        carte = _ombre(carte, self.s)
        out = Image.new("RGBA", (self.w + 2 * self.m, self.h + 2 * self.m), (0, 0, 0, 0))
        _poser(out, carte, carte.width / 2, carte.height / 2, k, a)
        return out

    def sons(self):
        out = [(self._t(), "compteur")]
        if self.spec.get("ajout"):
            out.append((self._t_ajout() + C.VASES_GEO["chute"], "clic"))
        return out


# -------------------------------------------------------------- pieces
class Pieces(_Insert):
    """Deux piles de pieces : a chaque cycle, deux pieces s'empilent a gauche (vos revenus au-dela du
    seuil), une piece s'envole de la pile de droite (votre pension) ; les compteurs suivent."""

    def taille_nominale(self):
        return C.TEXTE_LARGEUR, C.PIECES_H

    def __init__(self, *a):
        super().__init__(*a)
        g, m = C.PIECES_GEO, self.m
        carte = _cadre(self.w, self.h, self.s, marge=m)
        d = ImageDraw.Draw(carte)
        _ecrire(d, (m + self.w / 2, m + self.px(g["pad"])), self.spec.get("titre", ""), self.px(g["titre_px"]),
                C.INSERT_GRAISSE_FORTE, C.NAVY + (255,), "mt")
        self.sol = m + self.px(g["sol_y"])
        self.cx = [m + self.w * c for c in g["col"]]
        for cx, lab in zip(self.cx, (self.spec.get("gauche", ""), self.spec.get("droite", ""))):
            _ecrire(d, (cx, self.sol + self.px(g["label_ecart"])), lab, self.px(g["label_px"]), C.INSERT_GRAISSE_FORTE,
                    C.NAVY + (255,), "mt")
        self.fond = carte
        self.pas = self.px(g["epaisseur"])
        self.pieces = {c: self._piece(c) for c in ("vert", "bleu", "rouge")}

    def _piece(self, ton):
        g = C.PIECES_GEO
        w, h, e = self.px(g["piece"][0]), self.px(g["piece"][1]), self.px(g["epaisseur"])
        couleur = {"vert": C.INSERT_VERT, "rouge": C.INSERT_ROUGE}.get(ton, tuple(self.rubrique))
        fonce = tuple(int(c * 0.72) for c in couleur)

        def dessin(dd, k):
            dd.rounded_rectangle([0, h * k / 2, w * k - 1, (h / 2 + e) * k], radius=2 * k, fill=fonce + (255,))
            dd.ellipse([0, e * k, w * k - 1, (h + e) * k - 1], fill=fonce + (255,))
            dd.ellipse([0, 0, w * k - 1, h * k - 1], fill=couleur + (255,))
            dd.ellipse([w * k * 0.2, h * k * 0.2, w * k * 0.8, h * k * 0.8], outline=_teinte(couleur, 0.4) + (255,),
                       width=max(1, int(2 * k)))
        return _net(w, h + e, dessin)

    def _cycles(self):
        g = C.PIECES_GEO
        t0 = self.t0(self.spec.get("temps", 1)) + C.INSERT_DELAI
        return [t0 + i * g["cycle"] for i in range(g["cycles"])]

    def image(self, t, final):
        g = C.PIECES_GEO
        k, a = _entree(t, self.t0(), final)
        if a <= 0:
            return None
        carte = self.fond.copy()
        cycles = self._cycles()
        gagne = perdu = 0
        chutes, envols = [], []
        for tc in cycles:
            for j in range(2):                            # deux pieces gagnees
                tj = tc + j * g["chute"] * g["chute_pas"]
                w2 = 1.0 if final else (t - tj) / g["chute"]
                if w2 >= 1:
                    gagne += 1
                elif w2 > 0:
                    chutes.append(w2)
            tp = tc + g["chute"] * g["envol_delai"]                    # puis une piece de pension s'envole
            w2 = 1.0 if final else (t - tp) / g["envol"]
            if w2 >= 1:
                perdu += 1
            elif w2 > 0:
                envols.append(w2)
        ph = self.pieces["vert"].height
        pile_d = self.spec.get("pension", g["pension"]) - perdu - len(envols)
        for i in range(gagne):
            carte.alpha_composite(self.pieces["vert"], (int(self.cx[0] - self.pieces["vert"].width / 2),
                                                        int(self.sol - ph - i * self.pas)))
        for w2 in chutes:                                 # une piece tombe sur la pile
            y_fin = self.sol - ph - gagne * self.pas
            y = y_fin - self.px(g["chute_haut"]) * (1 - w2 * w2)
            T.coller(carte, self.pieces["vert"], (self.cx[0] - self.pieces["vert"].width / 2, y), min(1.0, w2 * 3))
            gagne += 1
        for i in range(pile_d):
            carte.alpha_composite(self.pieces["bleu"], (int(self.cx[1] - self.pieces["bleu"].width / 2),
                                                        int(self.sol - ph - i * self.pas)))
        for w2 in envols:                                 # la piece du haut s'envole, rougit
            y0 = self.sol - ph - pile_d * self.pas
            x = self.cx[1] + self.px(g["envol_dx"]) * T.lisse(w2)
            y = y0 - self.px(g["envol_dy"]) * T.lisse(w2)
            T.coller(carte, self.pieces["rouge"], (x - self.pieces["rouge"].width / 2, y), 1 - w2)
        d = ImageDraw.Draw(carte)
        cp = self.px(g["compteur_px"])
        y_c = self.sol - ph - (g["pension"] + 1) * self.pas - self.px(g["compteur_ecart"])
        if gagne:
            _ecrire(d, (self.cx[0], y_c), f"+{gagne}{NBSP}€", cp, C.INSERT_GRAISSE_FORTE, C.INSERT_VERT + (255,), "ms")
        if perdu:
            _ecrire(d, (self.cx[1], y_c), f"−{perdu}{NBSP}€", cp, C.INSERT_GRAISSE_FORTE, C.INSERT_ROUGE + (255,), "ms")
        carte = _ombre(carte, self.s)
        out = Image.new("RGBA", (self.w + 2 * self.m, self.h + 2 * self.m), (0, 0, 0, 0))
        _poser(out, carte, carte.width / 2, carte.height / 2, k, a)
        return out

    def sons(self):
        g = C.PIECES_GEO
        out = []
        for tc in self._cycles():
            out += [(tc + g["chute"], "clic"), (tc + g["chute"] * (1 + g["chute_pas"]), "clic"),
                    (tc + g["chute"] * g["envol_delai"], "souffle")]
        return out


# ---------------------------------------------------------------- part
class Part(_Insert):
    """La part d'une activite : au temps 0, une pastille (« Cumul intégral, sans plafond ») ; au
    temps "temps_part", l'anneau se remplit (le reste de l'activite), puis la part plafonnee se
    detache en vert, son pourcentage au centre, la legende a droite."""

    def taille_nominale(self):
        return C.TEXTE_LARGEUR, C.PART_H

    def __init__(self, *a):
        super().__init__(*a)
        g, m = C.PART_GEO, self.m
        carte = _cadre(self.w, self.h, self.s, marge=m)
        self.fond = carte
        self.r, self.ep = self.px(g["rayon"]), self.px(g["epaisseur"])
        self.c = (m + self.px(g["pad"]) + self.r + self.ep / 2, m + self.h / 2)
        self.part = self.spec["part"]
        self.xl = self.c[0] + self.r + self.ep / 2 + self.px(g["colonne"])            # colonne de droite
        self.pastille = _ombre_marge(_bulle(self.spec.get("pastille", ""), self.px(g["pilule_px"]),
                                            self.px(g["pilule_h"]), self.px(g["pilule_pad"]), C.INSERT_VERT, queue=False), self.s)

    def _t_part(self):
        return self.t0(self.spec.get("temps_part", 1)) + C.INSERT_DELAI

    def _anneau(self, p_reste, p_part, eclat):
        g = C.PART_GEO
        W, H = self.fond.size
        cx, cy, r, e = self.c[0], self.c[1], self.r, self.ep
        part = self.part / 100

        def dessin(dd, k):
            box = [(cx - r) * k, (cy - r) * k, (cx + r) * k, (cy + r) * k]
            dd.arc(box, 0, 360, fill=C.INSERT_GRIS + (255,), width=int(e * k))
            if p_reste > 0:
                debut = -90 + 360 * part
                dd.arc(box, debut, debut + 360 * (1 - part) * p_reste, fill=tuple(self.rubrique) + (255,),
                       width=int(e * k))
            if p_part > 0:
                mil = math.radians(-90 + 180 * part)
                ox, oy = math.cos(mil) * eclat * k, math.sin(mil) * eclat * k
                b2 = [box[0] + ox, box[1] + oy, box[2] + ox, box[3] + oy]
                dd.arc(b2, -90, -90 + 360 * part * p_part, fill=C.INSERT_VERT + (255,), width=int(e * k))
        return _net(W, H, dessin)

    def image(self, t, final):
        g = C.PART_GEO
        k, a = _entree(t, self.t0(), final)
        if a <= 0:
            return None
        carte = self.fond.copy()
        tp = self._t_part()
        p_reste = 1.0 if final else T.lisse((t - tp) / g["remplissage"])
        u = 1.0 if final else (t - tp - g["remplissage"]) / g["part_duree"]
        p_part = 1.0 if final else T.lisse(u)
        eclat = self.px(g["eclat"]) * (1.0 if final else T.rebond(u) if u > 0 else 0)
        carte.alpha_composite(self._anneau(p_reste, p_part, eclat))
        d = ImageDraw.Draw(carte)
        cx, cy = self.c
        if p_part > 0:
            _ecrire(d, (cx, cy - self.px(g["centre_dy"])), f"{int(round(self.part * p_part))}{NBSP}%", self.px(g["centre_px"]),
                    C.INSERT_GRAISSE_FORTE, C.INSERT_VERT + (255,), "mm")
            _ecrire(d, (cx, cy + self.px(g["centre_px"]) * 0.62), self.spec.get("centre", ""), self.px(g["petit_px"]),
                    C.INSERT_GRAISSE_TEXTE, C.INSERT_GRIS_TEXTE + (255,), "mm")
        v = 1.0 if final else (t - self.t0() - C.INSERT_ENTREE * 0.5) / C.INSERT_ENTREE
        if v > 0:                                         # la pastille, en haut a droite
            kk = 0.3 + 0.7 * (1.0 if final else T.rebond(v))
            _poser(carte, self.pastille, self.xl + (self.pastille.width - 2 * self.m) / 2,
                   self.m + self.px(g["pad"]) + self.px(g["pilule_h"]) / 2, kk, 1.0 if final else T.lisse(v * 2))
        lp = self.px(g["legende_px"])
        for i, (texte, couleur) in enumerate(((self.spec.get("legende_part", ""), C.INSERT_VERT),
                                              (self.spec.get("legende_reste", ""), tuple(self.rubrique)))):
            w2 = 1.0 if final else (t - tp - (g["remplissage"] + g["part_duree"] * 0.5 if i == 0 else 0.3)) / 0.4
            if w2 <= 0:
                continue
            al = int(255 * min(1.0, w2))
            y = cy + self.px(g["legende_y"]) + i * lp * g["legende_pas"]
            r = self.px(g["point"])
            d.ellipse([self.xl, y - r, self.xl + 2 * r, y + r], fill=couleur + (al,))
            _ecrire(d, (self.xl + 2 * r + self.px(g["point_ecart"]), y), texte, lp, C.INSERT_GRAISSE_FORTE, C.NAVY + (al,), "lm")
        carte = _ombre(carte, self.s)
        out = Image.new("RGBA", (self.w + 2 * self.m, self.h + 2 * self.m), (0, 0, 0, 0))
        _poser(out, carte, carte.width / 2, carte.height / 2, k, a)
        return out

    def sons(self):
        g = C.PART_GEO
        return [(self.t0() + C.INSERT_ENTREE * 0.5, "clic"), (self._t_part(), "souffle"),
                (self._t_part() + g["remplissage"], "impact")]


# ------------------------------------------------------------- bascule
class Bascule(_Insert):
    """Un ephemeride : la page « avant » se plie vers le haut, la page « apres » apparait dessous ;
    a droite, la legende de chaque page, et une pilule rouge qui claque (« Nouvelles règles »)."""

    def taille_nominale(self):
        g = C.BASCULE_GEO
        return C.TEXTE_LARGEUR, C.BASCULE_H

    def _page(self, p):
        g = C.BASCULE_GEO
        w, h = self.px(g["page"][0]), self.px(g["page"][1])
        tete, ra = self.px(g["tete"]), self.px(g["page_rayon"])

        def dessin(dd, k):
            dd.rounded_rectangle([0, 0, w * k - 1, h * k - 1], radius=ra * k, fill=C.BLANC + (255,))
            dd.rounded_rectangle([0, 0, w * k - 1, (tete + ra) * k], radius=ra * k,
                                 fill=C.INSERT_ROUGE + (255,))
            dd.rectangle([0, tete * k, w * k - 1, (tete + ra) * k], fill=C.BLANC + (255,))
        im = _net(w, h, dessin)
        d = ImageDraw.Draw(im)
        _ecrire(d, (w / 2, tete / 2), T.normaliser(p["haut"]).upper(), self.px(g["mois_px"]), C.INSERT_GRAISSE_FORTE,
                C.BLANC + (255,), "mm")
        _ecrire(d, (w / 2, tete + (h - tete) * 0.46), p["jour"], self.px(g["jour_px"]), C.INSERT_GRAISSE_FORTE,
                C.NAVY + (255,), "mm")
        _ecrire(d, (w / 2, h - self.px(g["bas_y"])), p.get("bas", ""), self.px(g["bas_px"]), C.INSERT_GRAISSE_TEXTE,
                C.INSERT_GRIS_TEXTE + (255,), "mm")
        return im

    def __init__(self, *a):
        super().__init__(*a)
        g = C.BASCULE_GEO
        self.pages = [self._page(self.spec["avant"]), self._page(self.spec["apres"])]
        aw, ah = self.px(g["anneau"][0]), self.px(g["anneau"][1])
        self.anneau = _net(aw, ah, lambda dd, k: dd.rounded_rectangle([0, 0, aw * k - 1, ah * k - 1], radius=aw * k / 2,
                                                                        fill=C.NAVY + (255,)))
        self.px_x = self.m + self.px(g["page_marge"][0])                                    # gauche de la page
        self.py = self.m + self.h - self.pages[0].height - self.px(g["page_marge"][1])       # haut de la page
        self.carte = _ombre(_cadre(self.w, self.h, self.s, marge=self.m), self.s)
        self.xl = self.px_x + self.pages[0].width + self.px(g["ecart"])
        self.pilule = _ombre_marge(_bulle(self.spec.get("pilule", ""), self.px(g["pilule_px"]), self.px(g["pilule_h"]),
                                          self.px(g["pilule_pad"]), C.INSERT_ROUGE, queue=False), self.s)

    def _t_pli(self):
        return self.t0(self.spec.get("temps", 1)) + C.INSERT_DELAI

    def image(self, t, final):
        g = C.BASCULE_GEO
        k, a = _entree(t, self.t0(), final)
        if a <= 0:
            return None
        cal = self.carte.copy()
        p = 1.0 if final else max(0.0, min(1.0, (t - self._t_pli()) / g["pli"]))
        pw, ph = self.pages[0].size
        if p > 0:
            cal.alpha_composite(_ombre_marge(self.pages[1], self.s), (int(self.px_x - self.m), int(self.py - self.m)))
        if p < 1:                                         # la page « avant » se replie vers le haut
            hh = max(1, int(ph * (1 - T.lisse(p))))
            plie = self.pages[0].resize((pw, hh), Image.BICUBIC)
            if p > 0:
                ombre = Image.new("RGBA", plie.size, (0, 0, 0, int(90 * p)))
                ombre.putalpha(ImageChops.multiply(ombre.getchannel("A"), plie.getchannel("A")))
                plie.alpha_composite(ombre)
            cal.alpha_composite(_ombre_marge(plie, self.s), (int(self.px_x - self.m), int(self.py - self.m)))
        aw = self.anneau.width
        for fx in (0.28, 0.72):
            cal.alpha_composite(self.anneau, (int(self.px_x + pw * fx - aw / 2), int(self.py - self.anneau.height * 0.6)))
        d = ImageDraw.Draw(cal)
        lp = self.px(g["legende_px"])
        for i, cle in enumerate(("legende_avant", "legende_apres")):
            texte = self.spec.get(cle, "")
            q = 1 - min(1.0, p * 2) if i == 0 else max(0.0, p * 2 - 1)      # l'une s'efface, puis l'autre
            if not texte or q <= 0:
                continue
            al = int(255 * q)
            lignes = _couper(texte, lp, C.INSERT_GRAISSE_FORTE, self.m + self.w - self.xl)
            for j, l in enumerate(lignes):
                _ecrire(d, (self.xl, self.py + self.px(g["legende_y"]) + j * lp * 1.2), l, lp, C.INSERT_GRAISSE_FORTE,
                        C.NAVY + (al,))
        v = 1.0 if final else (t - self._t_pli() - g["pli"]) / C.TAMPON_FRAPPE
        if v > 0:
            kk = 1.0 if final or v >= 1 else C.TAMPON_ECHELLE - (C.TAMPON_ECHELLE - 1) * v * v
            _poser(cal, self.pilule, self.xl + (self.pilule.width - 2 * self.m) / 2,
                   self.py + self.pages[0].height - self.px(g["pilule_h"]) / 2 - self.px(g["pilule_dy"]), kk,
                   1.0 if final else min(1.0, v * 2), -4)
        out = Image.new("RGBA", cal.size, (0, 0, 0, 0))
        _poser(out, cal, cal.width / 2, cal.height / 2, k, a)
        return out

    def sons(self):
        g = C.BASCULE_GEO
        return [(self.t0(), "clic"), (self._t_pli(), "souffle"), (self._t_pli() + g["pli"] + C.TAMPON_FRAPPE, "impact")]


# -------------------------------------------------------------- icones
class Icones(_Insert):
    """Des cartes a icone dessinee (repere, lune, casque), qui arrivent l'une apres l'autre ; un
    « ? » se balance au coin de chacune : une question encore ouverte."""

    def taille_nominale(self):
        return C.TEXTE_LARGEUR, C.ICONES_H

    def __init__(self, *a):
        super().__init__(*a)
        g = C.ICONES_GEO
        self.items = self.spec["cartes"]
        n = len(self.items)
        self.ecart = self.px(g["ecart"])
        self.cw = (self.w - (n - 1) * self.ecart) // n
        self.cartes = [self._carte(c) for c in self.items]
        self.badge = _icone_choix(None, self.px(g["badge"]), self.px(C.CHOIX_GEO["trait"]), self.rubrique)

    def _dessin_icone(self, nom):
        g = C.ICONES_GEO
        s = self.px(g["icone"])
        tr = self.px(g["trait"])
        navy, rub = C.NAVY + (255,), tuple(self.rubrique) + (255,)
        gris = C.INSERT_GRIS + (255,)

        def dessin(dd, k):
            S, e = s * k, tr * k
            if nom == "repere":                           # un repere sur un territoire
                for x0, hh in ((0.08, 0.2), (0.62, 0.24)):
                    x, y = S * x0, S * 0.94
                    dd.rectangle([x, y - S * hh, x + S * 0.3, y], fill=gris)
                    dd.polygon([(x - S * 0.03, y - S * hh), (x + S * 0.15, y - S * (hh + 0.13)),
                                (x + S * 0.33, y - S * hh)], fill=gris)
                cx, cy, r = S / 2, S * 0.36, S * 0.24
                dd.polygon([(cx - r * 0.86, cy + r * 0.5), (cx, S * 0.86), (cx + r * 0.86, cy + r * 0.5)], fill=rub)
                dd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=rub)
                dd.ellipse([cx - r * 0.42, cy - r * 0.42, cx + r * 0.42, cy + r * 0.42], fill=C.BLANC + (255,))
            elif nom == "lune":                           # la nuit : lune et etoiles
                r = S * 0.36
                cx, cy = S * 0.46, S * 0.54
                dd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=navy)
                dd.ellipse([cx - r + S * 0.2, cy - r - S * 0.1, cx + r + S * 0.2, cy + r - S * 0.1], fill=(0, 0, 0, 0))
                for ex, ey, er in ((0.78, 0.2, 0.05), (0.88, 0.48, 0.035), (0.66, 0.08, 0.03)):
                    dd.ellipse([S * ex - S * er, S * ey - S * er, S * ex + S * er, S * ey + S * er], fill=rub)
            elif nom == "poubelle":                       # une dose perdue : poubelle et piece
                dd.rounded_rectangle([S * 0.38, S * 0.1, S * 0.62, S * 0.2], radius=S * 0.03, fill=navy)
                dd.rounded_rectangle([S * 0.12, S * 0.18, S * 0.78, S * 0.27], radius=S * 0.03, fill=navy)
                dd.polygon([(S * 0.18, S * 0.3), (S * 0.72, S * 0.3), (S * 0.65, S * 0.96), (S * 0.25, S * 0.96)],
                           fill=navy)
                for x in (0.34, 0.45, 0.56):
                    dd.line([(S * x, S * 0.42), (S * x, S * 0.84)], fill=C.BLANC + (255,), width=int(e * 0.55))
                r = S * 0.17
                dd.ellipse([S * 0.82 - r, S * 0.2 - r, S * 0.82 + r, S * 0.2 + r], fill=C.INSERT_ROUGE + (255,))
            elif nom == "bon":                            # le bon de prise en charge : un formulaire
                pli = S * 0.2
                dd.polygon([(S * 0.18, S * 0.05), (S * 0.82 - pli, S * 0.05), (S * 0.82, S * 0.05 + pli),
                            (S * 0.82, S * 0.96), (S * 0.18, S * 0.96)], fill=C.BLANC + (255,), outline=navy,
                           width=int(e * 0.6))
                dd.polygon([(S * 0.82 - pli, S * 0.05), (S * 0.82 - pli, S * 0.05 + pli), (S * 0.82, S * 0.05 + pli)],
                           fill=gris)
                dd.rounded_rectangle([S * 0.3, S * 0.3, S * 0.62, S * 0.38], radius=S * 0.02, fill=rub)
                for y in (0.5, 0.62, 0.74):
                    dd.rounded_rectangle([S * 0.3, S * y, S * 0.7, S * (y + 0.05)], radius=S * 0.02, fill=gris)
            elif nom == "enfant":                         # un enfant
                cx, r = S / 2, S * 0.15
                dd.ellipse([cx - r, S * 0.06, cx + r, S * 0.06 + 2 * r], fill=navy)
                dd.line([(cx - S * 0.15, S * 0.48), (cx - S * 0.3, S * 0.66)], fill=rub, width=int(e))
                dd.line([(cx + S * 0.15, S * 0.48), (cx + S * 0.3, S * 0.66)], fill=rub, width=int(e))
                dd.rounded_rectangle([cx - S * 0.17, S * 0.4, cx + S * 0.17, S * 0.74], radius=S * 0.08, fill=rub)
                dd.rounded_rectangle([cx - S * 0.13, S * 0.68, cx - S * 0.03, S * 0.96], radius=S * 0.04, fill=navy)
                dd.rounded_rectangle([cx + S * 0.03, S * 0.68, cx + S * 0.13, S * 0.96], radius=S * 0.04, fill=navy)
            elif nom == "compte_rendu":                   # un compte rendu : une page, son titre, ses lignes
                dd.rounded_rectangle([S * 0.16, S * 0.04, S * 0.84, S * 0.96], radius=S * 0.06, fill=C.BLANC + (255,),
                                     outline=navy, width=int(e * 0.6))
                dd.rounded_rectangle([S * 0.28, S * 0.15, S * 0.72, S * 0.27], radius=S * 0.03, fill=rub)
                for y, l in ((0.4, 0.44), (0.52, 0.36), (0.64, 0.44), (0.76, 0.26)):
                    dd.rounded_rectangle([S * 0.28, S * y, S * (0.28 + l), S * (y + 0.05)], radius=S * 0.02, fill=gris)
            elif nom == "concertation":                   # deux bulles : on se concerte
                dd.rounded_rectangle([S * 0.02, S * 0.1, S * 0.6, S * 0.5], radius=S * 0.13, fill=navy)
                dd.polygon([(S * 0.12, S * 0.48), (S * 0.3, S * 0.48), (S * 0.1, S * 0.66)], fill=navy)
                dd.rounded_rectangle([S * 0.38, S * 0.38, S * 0.98, S * 0.8], radius=S * 0.13, fill=rub)
                dd.polygon([(S * 0.7, S * 0.78), (S * 0.88, S * 0.78), (S * 0.9, S * 0.96)], fill=rub)
                for x in (0.55, 0.68, 0.81):
                    r = S * 0.045
                    dd.ellipse([S * x - r, S * 0.59 - r, S * x + r, S * 0.59 + r], fill=C.BLANC + (255,))
            elif nom == "patient":                        # un patient qui vous revient : la fleche du retour
                cx, r = S * 0.36, S * 0.13
                dd.ellipse([cx - r, S * 0.1, cx + r, S * 0.1 + 2 * r], fill=navy)
                dd.rounded_rectangle([cx - S * 0.21, S * 0.42, cx + S * 0.21, S * 0.94], radius=S * 0.12, fill=navy)
                dd.arc([S * 0.5, S * 0.2, S * 0.98, S * 0.68], -90, 90, fill=rub, width=int(e))
                dd.polygon([(S * 0.6, S * 0.68), (S * 0.76, S * 0.57), (S * 0.76, S * 0.79)], fill=rub)
            else:                                         # le casque de la regulation
                box = [S * 0.14, S * 0.1, S * 0.86, S * 0.82]
                dd.arc(box, 180, 360, fill=navy, width=int(e))
                for x in (S * 0.08, S * 0.74):
                    dd.rounded_rectangle([x, S * 0.42, x + S * 0.18, S * 0.72], radius=S * 0.06, fill=navy)
                dd.arc([S * 0.3, S * 0.4, S * 0.92, S * 0.98], 10, 100, fill=rub, width=int(e * 0.8))
                dd.ellipse([S * 0.42, S * 0.86, S * 0.56, S * 1.0 - 1], fill=rub)
        im = _net(s, s, dessin)
        if nom == "poubelle":                             # la piece porte « € »
            _ecrire(ImageDraw.Draw(im), (s * 0.82, s * 0.2), "€", max(6, int(s * 0.2)), C.INSERT_GRAISSE_FORTE,
                    C.BLANC + (255,), "mm")
        return im

    def _carte(self, c):
        g, m = C.ICONES_GEO, self.m
        im = _cadre(self.cw, self.h, self.s, marge=m)
        ic = self._dessin_icone(c.get("icone", ""))
        im.alpha_composite(ic, (int(m + (self.cw - ic.width) / 2), int(m + self.px(g["icone_y"]))))
        d = ImageDraw.Draw(im)
        px = self.px(g["label_px"])
        lignes = _couper(c["label"], px, C.INSERT_GRAISSE_FORTE, self.cw - self.px(g["label_marge"]))
        y0 = m + self.px(g["icone_y"]) + ic.height + self.px(g["label_ecart"])
        for i, l in enumerate(lignes):
            _ecrire(d, (m + self.cw / 2, y0 + i * px * 1.2), l, px, C.INSERT_GRAISSE_FORTE, C.NAVY + (255,), "mt")
        return _ombre(im, self.s)

    def _t(self, i):
        """Une carte arrive avec le temps du texte de son "temps" (celui de l'insert par defaut)."""
        defaut = self.spec.get("temps", 0)
        tps = self.items[i].get("temps", defaut)
        avant = [j for j in range(i) if self.items[j].get("temps", defaut) == tps]
        return self.t0(tps) + len(avant) * C.ICONES_GEO["decalage"]

    def image(self, t, final):
        g = C.ICONES_GEO
        out = Image.new("RGBA", (self.w + 2 * self.m, self.h + 2 * self.m), (0, 0, 0, 0))
        for i, carte in enumerate(self.cartes):
            k, a = _entree(t, self._t(i), final)
            if a <= 0:
                continue
            dy = 0 if final else C.INSERT_MONTEE * self.s * (1 - T.lisse((t - self._t(i)) / C.INSERT_ENTREE))
            cx = self.m + i * (self.cw + self.ecart) + self.cw / 2
            _poser(out, carte, cx, self.m + self.h / 2 + dy, k, a)
            if self.items[i].get("question") is False:   # une tache, pas une question ouverte
                continue
            tq = self.t0(self.items[i]["temps_question"]) if "temps_question" in self.items[i] else \
                self._t(i) + C.INSERT_ENTREE * 0.7
            v = 1.0 if final else (t - tq) / C.INSERT_ENTREE
            if v > 0:
                amp, freq = C.CHOIX_GEO["balance"]
                angle = 0.0 if final or v < 1 else amp * math.sin(2 * math.pi * freq * (t - self._t(i)))
                kk = 0.3 + 0.7 * (1.0 if final else T.rebond(v))
                _poser(out, self.badge, cx + self.cw / 2 - self.px(g["badge"]) * g["badge_pos"],
                       self.m + self.px(g["badge"]) * g["badge_pos"] + dy, kk, 1.0 if final else T.lisse(v * 2), angle)
        return out

    def sons(self):
        return [(self._t(i), "clic") for i in range(len(self.cartes))]


# ---------------------------------------------------------------- prix
class Prix(_Insert):
    """Des boites de vaccin dessinees ; une etiquette de prix tombe sur chacune, au temps de sa
    boite, se balance, puis une pastille (« plus du double ») claque au-dessus de la derniere."""

    def taille_nominale(self):
        return C.TEXTE_LARGEUR, C.PRIX_H

    def __init__(self, *a):
        super().__init__(*a)
        g = C.PRIX_GEO
        self.items = self.spec["boites"]
        n = len(self.items)
        self.boites = [_ombre_marge(self._boite(b["nom"]), self.s) for b in self.items]
        self.etiquettes = [_ombre_marge(_etiquette([b["prix"]], self.px(g["etiquette_px"]),
                                                   self.px(g["etiquette_pad"][0]), self.px(g["etiquette_pad"][1]),
                                                   _ton(b, self.rubrique)), self.s) for b in self.items]
        self.pastille = (_ombre_marge(_bulle(self.spec["pastille"], self.px(g["pastille_px"]), self.px(g["pastille_h"]),
                                             self.px(g["pastille_pad"]), C.INSERT_ROUGE, queue=False), self.s)
                         if self.spec.get("pastille") else None)
        self.bw, self.bh = self.px(g["boite"][0]), self.px(g["boite"][1])
        # l'etiquette deborde a droite de sa boite : les centres se resserrent d'autant, pour que la
        # derniere reste dans la colonne
        deborde = max(0.0, self.bw * g["etiquette_x"] + (self.etiquettes[-1].width - 2 * self.m) / 2
                      - self.bw / 2)
        utile = self.w - deborde
        self.cx = [self.m + utile * (i + 0.5) / n for i in range(n)]
        self.haut = self.m + self.h - self.px(g["sol"]) - self.bh            # haut des boites

    def _boite(self, nom):
        g = C.PRIX_GEO
        w, h, bande = self.px(g["boite"][0]), self.px(g["boite"][1]), self.px(g["bande"])
        ra, tr = self.px(g["rayon"]), max(1, self.px(g["trait"]))
        rub, navy = tuple(self.rubrique) + (255,), C.NAVY + (255,)

        def dessin(d, k):
            W, H, B, Q = w * k, h * k, bande * k, ra * k
            d.rounded_rectangle([0, 0, W - 1, H - 1], radius=Q, fill=C.BLANC + (255,))
            d.rounded_rectangle([0, 0, W - 1, B + Q], radius=Q, fill=rub)
            d.rectangle([0, B, W - 1, B + Q], fill=C.BLANC + (255,))
            cx, cy = W * 0.5, B + (H - B) * 0.55                # une seringue preremplie
            L, e = W * 0.42, (H - B) * 0.2
            d.rounded_rectangle([cx - L / 2, cy - e / 2, cx + L / 2, cy + e / 2], radius=e * 0.3,
                                fill=_teinte(self.rubrique, 0.75) + (255,), outline=navy, width=int(tr * k))
            d.rectangle([cx - L / 2 - L * 0.24, cy - e * 0.12, cx - L / 2, cy + e * 0.12], fill=navy)
            d.rectangle([cx - L / 2 - L * 0.28, cy - e * 0.55, cx - L / 2 - L * 0.22, cy + e * 0.55], fill=navy)
            d.rectangle([cx + L / 2, cy - e * 0.08, cx + L / 2 + L * 0.3, cy + e * 0.08], fill=navy)
            for i in range(1, 5):
                x = cx - L / 2 + L * i / 5
                d.line([(x, cy - e / 2), (x, cy - e * 0.05)], fill=navy, width=int(tr * k))
        im = _net(w, h, dessin)
        _ecrire(ImageDraw.Draw(im), (w / 2, bande / 2), nom, self.px(g["nom_px"]), C.INSERT_GRAISSE_FORTE,
                C.BLANC + (255,), "mm")
        return im

    def _t_boite(self, i):
        """Entree de la boite i : avec le temps du texte de son "temps" (celui de l'insert par
        defaut), les boites d'un meme temps a la suite."""
        defaut = self.spec.get("temps", 0)
        tps = self.items[i].get("temps", defaut)
        avant = [j for j in range(i) if self.items[j].get("temps", defaut) == tps]
        return self.t0(tps) + len(avant) * C.INSERT_DECALAGE

    def _t(self, i):
        """Chute de l'etiquette i, apres l'entree de sa boite ; les etiquettes d'un meme temps a
        la suite."""
        g = C.PRIX_GEO
        defaut = self.spec.get("temps", 0)
        tps = self.items[i].get("temps", defaut)
        avant = [j for j in range(i) if self.items[j].get("temps", defaut) == tps]
        return self.t0(tps) + C.INSERT_ENTREE * 0.5 + len(avant) * g["decalage"]

    def _t_pastille(self):
        g = C.PRIX_GEO
        return max(self._t(i) for i in range(len(self.items))) + g["chute"] + g["pastille_delai"]

    def image(self, t, final):
        g = C.PRIX_GEO
        out = Image.new("RGBA", (self.w + 2 * self.m, self.h + 2 * self.m), (0, 0, 0, 0))
        for i, boite in enumerate(self.boites):
            k, a = _entree(t, self._t_boite(i), final)
            if a <= 0:
                continue
            _poser(out, boite, self.cx[i], self.haut + self.bh / 2, k, a)
            u = 1.0 if final else (t - self._t(i)) / g["chute"]
            if u <= 0:
                continue
            dy = 0.0 if u >= 1 else -self.px(g["chute_haut"]) * (1 - u * u)
            angle = g["etiquette_angle"]
            if not final and u >= 1:                      # elle se balance, puis se pose
                amp, freq, amorti = g["balance"]
                tau = t - self._t(i) - g["chute"]
                angle += amp * math.sin(2 * math.pi * freq * tau) * math.exp(-amorti * tau)
            ex = self.cx[i] + self.bw * g["etiquette_x"]
            _poser(out, self.etiquettes[i], ex, self.haut + self.bh * g["etiquette_y"] + dy, 1.0,
                   1.0 if final else min(1.0, u * 3), angle)
        if self.pastille is not None:
            v = 1.0 if final else (t - self._t_pastille()) / C.TAMPON_FRAPPE
            if v > 0:
                kk = 1.0 if final or v >= 1 else C.TAMPON_ECHELLE - (C.TAMPON_ECHELLE - 1) * v * v
                _poser(out, self.pastille, self.cx[-1], self.haut - self.px(g["pastille_dy"]), kk,
                       1.0 if final else min(1.0, v * 2), 4)
        return out

    def sons(self):
        g = C.PRIX_GEO
        out = [(self._t(i) + g["chute"], "clic") for i in range(len(self.items))]
        if self.pastille is not None:
            out.append((self._t_pastille() + C.TAMPON_FRAPPE, "impact"))
        return out


def _coller_coupe(fond, im, x, y):
    """Compose im en (x, y), meme en partie hors de fond (la partie qui deborde est coupee)."""
    x, y = int(round(x)), int(round(y))
    g, h = max(0, -x), max(0, -y)
    d, b = min(im.width, fond.width - x), min(im.height, fond.height - y)
    if d > g and b > h:
        fond.alpha_composite(im.crop((g, h, d, b)), (x + g, y + h))


def _frappe(t, t0, final):
    """(echelle, opacite) d'un element qui claque comme un tampon a t0."""
    v = 1.0 if final else (t - t0) / C.TAMPON_FRAPPE
    if v <= 0:
        return 0.0, 0.0
    return (1.0 if final or v >= 1 else C.TAMPON_ECHELLE - (C.TAMPON_ECHELLE - 1) * v * v,
            1.0 if final else min(1.0, v * 2))


class _Pilules:
    """Pilules empilees a droite d'un dessin ("pilules" : [{"texte", "ton", "temps"}]) ; chacune
    claque au temps de son numero. geo : pilule_px, pilule_h, pilule_pad, pilule_ecart."""

    def _preparer_pilules(self, g, x, cy):
        self.pil_specs = self.spec.get("pilules", [])
        self.pil = [_ombre_marge(_bulle(p["texte"], self.px(g["pilule_px"]), self.px(g["pilule_h"]),
                                        self.px(g["pilule_pad"]), _ton(p, self.rubrique), queue=False), self.s)
                    for p in self.pil_specs]
        n, ph, ec = len(self.pil), self.px(g["pilule_h"]), self.px(g["pilule_ecart"])
        haut = cy - (n * ph + (n - 1) * ec) / 2
        self.pil_xy = [(x, haut + i * (ph + ec) + ph / 2) for i in range(n)]

    def _t_pilule(self, i):
        return self.t0(self.pil_specs[i].get("temps", 0)) + C.INSERT_ENTREE * 0.6

    def _pilules(self, out, t, final):
        for i, (im, (x, y)) in enumerate(zip(self.pil, self.pil_xy)):
            k, a = _frappe(t, self._t_pilule(i), final)
            if a > 0:
                _poser(out, im, x + (im.width - 2 * self.m) / 2, y, k, a, -3)

    def _sons_pilules(self):
        return [(self._t_pilule(i) + C.TAMPON_FRAPPE, "impact") for i in range(len(self.pil))]


# ---------------------------------------------------------------- carte
class Carte(_Insert):
    """Une carte CPS au nom de son titulaire, a cote du lecteur ; au temps "temps" (sinon un instant
    apres son arrivee), elle glisse dans la fente et l'ecran repond : une coche ("ok"), ou une croix,
    et la carte refusee tremble."""

    def taille_nominale(self):
        return C.TEXTE_LARGEUR, C.CARTE_H

    def __init__(self, *a):
        super().__init__(*a)
        g = C.CARTE_GEO
        self.ok = self.spec.get("ok", True)
        self.carte = _ombre_marge(self._carte(), self.s)
        self.lecteur = _ombre_marge(self._lecteur(), self.s)
        self.verdict = _icone_choix(self.ok, self.px(g["resultat"]), self.px(g["trait"]), self.rubrique)
        cw, lw = self.px(g["carte"][0]), self.px(g["lecteur"][0])
        self.lx = self.m + self.w - self.px(g["pad"]) - lw / 2           # centre du lecteur
        self.x0 = self.m + self.px(g["pad"]) + cw / 2                     # la carte posee a gauche
        self.x1 = self.lx - lw / 2 + cw * (g["profondeur"] - 0.5)         # engagee dans la fente
        self.cy = self.m + self.h / 2

    def _carte(self):
        g = C.CARTE_GEO
        w, h, ra = self.px(g["carte"][0]), self.px(g["carte"][1]), self.px(g["rayon"])
        pw, ph = self.px(g["puce"][0]), self.px(g["puce"][1])
        px0, py0 = self.px(g["puce_xy"][0]), self.px(g["puce_xy"][1])
        cl, ce, pad = self.px(g["croix"][0]), self.px(g["croix"][1]), self.px(g["pad"])
        rub = tuple(self.rubrique)
        im = _net(w, h, lambda d, k: d.rounded_rectangle([0, 0, w * k - 1, h * k - 1], radius=ra * k,
                                                         fill=rub + (255,)))
        reflet = _net(w, h, lambda d, k: d.ellipse([w * k * 0.5, h * k * 0.3, w * k * 1.4, h * k * 1.7],
                                                   fill=_teinte(rub, 0.16) + (255,)))
        reflet.putalpha(ImageChops.multiply(reflet.getchannel("A"), im.getchannel("A")))
        im.alpha_composite(reflet)

        def puce(d, k):
            d.rounded_rectangle([0, 0, pw * k - 1, ph * k - 1], radius=ph * k * 0.22, fill=C.INSERT_GRIS + (255,))
            trait, filet = max(1, int(ph * k * 0.07)), _teinte(rub, 0.45) + (255,)
            for y in (ph * k / 3, ph * k * 2 / 3):
                d.line([(0, y), (pw * k * 0.36, y)], fill=filet, width=trait)
                d.line([(pw * k * 0.64, y), (pw * k, y)], fill=filet, width=trait)
            d.rounded_rectangle([pw * k * 0.36, ph * k * 0.2, pw * k * 0.64, ph * k * 0.8], radius=ph * k * 0.08,
                                outline=filet, width=trait)
        im.alpha_composite(_net(pw, ph, puce), (px0, py0))
        d = ImageDraw.Draw(im)
        cx, cyc = w - pad - cl / 2, pad + cl / 2                          # la croix du soin
        d.rectangle([cx - cl / 2, cyc - ce / 2, cx + cl / 2, cyc + ce / 2], fill=C.BLANC + (255,))
        d.rectangle([cx - ce / 2, cyc - cl / 2, cx + ce / 2, cyc + cl / 2], fill=C.BLANC + (255,))
        _ecrire(d, (pad, pad), "CARTE CPS", self.px(g["titre_px"]), C.INSERT_GRAISSE_FORTE, C.BLANC + (255,))
        # le nom tient dans la part de la carte qui reste visible une fois engagee dans le lecteur
        nom, px = T.normaliser(self.spec.get("titulaire", "")), self.px(g["nom_px"])
        visible = w * (1 - g["profondeur"]) - 2 * pad
        while px > self.px(g["nom_px_min"]) and T.largeur(nom, px, C.INSERT_GRAISSE_FORTE, 0) > visible:
            px -= 1
        _ecrire(d, (pad, h - pad), nom, px, C.INSERT_GRAISSE_FORTE, C.BLANC + (255,), "ls")
        return im

    def _lecteur(self):
        g = C.CARTE_GEO
        w, h, ra = self.px(g["lecteur"][0]), self.px(g["lecteur"][1]), self.px(g["lecteur_rayon"])
        ew, eh, ey = self.px(g["ecran"][0]), self.px(g["ecran"][1]), self.px(g["ecran_y"])
        tr, ty, tp = self.px(g["touche"]), self.px(g["touches_y"]), self.px(g["touches_pas"])
        fw, fh = self.px(g["fente"][0]), self.px(g["fente"][1])

        def dessin(d, k):
            d.rounded_rectangle([0, 0, w * k - 1, h * k - 1], radius=ra * k, fill=C.NAVY + (255,))
            d.rounded_rectangle([(w - ew) / 2 * k, ey * k, (w + ew) / 2 * k, (ey + eh) * k], radius=ra * k * 0.4,
                                fill=(8, 5, 26, 255))
            for rang in range(2):
                for col in (-1, 0, 1):
                    x, y = (w / 2 + col * tp) * k, (ty + rang * tp) * k
                    d.ellipse([x - tr * k / 2, y - tr * k / 2, x + tr * k / 2, y + tr * k / 2],
                              fill=_teinte(C.NAVY, 0.3) + (255,))
            d.rounded_rectangle([0, (h - fh) / 2 * k, fw * k, (h + fh) / 2 * k], radius=fw * k / 2,
                                fill=(8, 5, 26, 255))                     # la fente, sur le bord gauche
        return _net(w, h, dessin)

    def _t_glisse(self):
        if "temps" in self.spec:
            return self.t0(self.spec["temps"])
        return self.t0() + C.CARTE_GEO["attente"]

    def image(self, t, final):
        g = C.CARTE_GEO
        k, a = _entree(t, self.t0(), final)
        if a <= 0:
            return None
        out = Image.new("RGBA", (self.w + 2 * self.m, self.h + 2 * self.m), (0, 0, 0, 0))
        tg, tv = self._t_glisse(), self._t_glisse() + g["course"]
        p = 1.0 if final else T.lisse((t - tg) / g["course"])
        x = self.x0 + (self.x1 - self.x0) * p
        if not final:                                    # la carte arrive de la gauche
            x -= self.px(g["glisse"]) * (1 - T.lisse((t - self.t0()) / C.INSERT_ENTREE))
            v = (t - tv) / g["refus"][1]
            if not self.ok and 0 < v < 1:                # refusee : elle tremble
                x += self.px(g["refus"][0]) * math.sin(2 * math.pi * 4 * v) * (1 - v)
        _poser(out, self.carte, x, self.cy, k, a)
        _poser(out, self.lecteur, self.lx, self.cy, k, a)   # le lecteur passe devant la carte engagee
        v = 1.0 if final else (t - tv) / C.INSERT_ENTREE
        if v > 0:
            kk = C.CHOIX_GEO["icone_depart"] + (1 - C.CHOIX_GEO["icone_depart"]) * (1.0 if final else T.rebond(v))
            ey = self.cy - self.px(g["lecteur"][1]) / 2 + self.px(g["ecran_y"]) + self.px(g["ecran"][1]) / 2
            _poser(out, self.verdict, self.lx, ey, kk, 1.0 if final else T.lisse(v * C.INSERT_FONDU))
        return out

    def sons(self):
        tv = self._t_glisse() + C.CARTE_GEO["course"]
        return [(self.t0(), "souffle"), (self._t_glisse(), "souffle"), (tv, "clic" if self.ok else "impact")]


# ---------------------------------------------------------------- compteur
class Compteur(_Insert):
    """Un compteur a rouleaux : les chiffres defilent, puis s'arretent un a un sur « ? » au temps
    "temps" ; une pilule rouge claque dessous (« Aucun chiffre officiel »). Aucun nombre n'y reste :
    le compteur dit que personne ne le publie."""

    def taille_nominale(self):
        return C.TEXTE_LARGEUR, C.COMPTEUR_H

    def __init__(self, *a):
        super().__init__(*a)
        g = C.COMPTEUR_GEO
        self.n = self.spec.get("chiffres", 4)
        self.cw, self.ch = self.px(g["case"][0]), self.px(g["case"][1])
        ra, pad = self.px(g["rayon"]), self.px(g["pad"])
        self.case = _net(self.cw, self.ch, lambda d, k: d.rounded_rectangle(
            [0, 0, self.cw * k - 1, self.ch * k - 1], radius=ra * k, fill=C.NAVY + (255,)))
        px = self.px(g["chiffre_px"])
        self.glyphes = {c: self._glyphe(c, px, C.BLANC) for c in "0123456789"}
        self.glyphes["?"] = self._glyphe("?", px, _teinte(self.rubrique, 0.4))
        carte = _cadre(self.w, self.h, self.s, marge=self.m)
        d = ImageDraw.Draw(carte)
        tp = self.px(g["titre_px"])
        _ecrire(d, (self.m + pad, self.m + pad), T.normaliser(self.spec.get("titre", "")).upper(), tp,
                C.INSERT_GRAISSE_FORTE, C.INSERT_GRIS_TEXTE + (255,))
        _ecrire(d, (self.m + self.w - pad, self.m + pad), self.spec.get("date", ""), tp, C.INSERT_GRAISSE_TEXTE,
                C.INSERT_GRIS_TEXTE + (255,), "ra")
        self.carte = _ombre(carte, self.s)
        largeur = self.n * self.cw + (self.n - 1) * self.px(g["ecart"])
        self.xs = [self.m + (self.w - largeur) / 2 + i * (self.cw + self.px(g["ecart"])) for i in range(self.n)]
        self.yc = self.m + self.px(g["case_y"])
        self.pilule = None
        if self.spec.get("pilule"):
            self.pilule = _ombre_marge(_bulle(self.spec["pilule"], self.px(g["pilule_px"]), self.px(g["pilule_h"]),
                                              self.px(g["pilule_pad"]), C.INSERT_ROUGE, queue=False), self.s)

    def _glyphe(self, c, px, couleur):
        im = Image.new("RGBA", (self.cw, self.ch), (0, 0, 0, 0))
        _ecrire(ImageDraw.Draw(im), (self.cw / 2, self.ch / 2), c, px, C.INSERT_GRAISSE_CHIFFRE, couleur + (255,), "mm")
        return im

    def _t_arret(self, i):
        return self.t0(self.spec.get("temps", 1)) + C.INSERT_DELAI + i * C.COMPTEUR_GEO["arret"]

    def _t_pilule(self):
        g = C.COMPTEUR_GEO
        return self._t_arret(self.n - 1) + g["chute"] + g["pilule_delai"]

    def _rouleau(self, i, t, final):
        g = C.COMPTEUR_GEO
        couche = Image.new("RGBA", (self.cw, self.ch), (0, 0, 0, 0))
        ta = self._t_arret(i)
        if final or t >= ta + g["chute"]:
            couche.alpha_composite(self.glyphes["?"])
        else:
            v = g["vitesse"] * (max(self.t0(), min(t, ta)) - self.t0()) + i * 3.7
            chiffre, f = int(v) % 10, v - int(v)
            if t < ta:                                   # le rouleau tourne : le chiffre suivant monte
                _coller_coupe(couche, self.glyphes[str(chiffre)], 0, -f * self.ch)
                _coller_coupe(couche, self.glyphes[str((chiffre + 1) % 10)], 0, (1 - f) * self.ch)
            else:                                        # il s'arrete : le « ? » tombe a sa place
                q = T.rebond((t - ta) / g["chute"])
                _coller_coupe(couche, self.glyphes[str(chiffre)], 0, q * self.ch)
                _coller_coupe(couche, self.glyphes["?"], 0, (q - 1) * self.ch)
        couche.putalpha(ImageChops.multiply(couche.getchannel("A"), self.case.getchannel("A")))
        im = self.case.copy()
        im.alpha_composite(couche)
        return im

    def image(self, t, final):
        g = C.COMPTEUR_GEO
        k, a = _entree(t, self.t0(), final)
        if a <= 0:
            return None
        cal = self.carte.copy()
        for i, x in enumerate(self.xs):
            cal.alpha_composite(self._rouleau(i, t, final), (int(x), int(self.yc)))
        if self.pilule is not None:
            kk, aa = _frappe(t, self._t_pilule(), final)
            if aa > 0:
                _poser(cal, self.pilule, self.m + self.w / 2,
                       self.m + self.h - self.px(g["pilule_dy"]) - self.px(g["pilule_h"]) / 2, kk, aa, -3)
        out = Image.new("RGBA", cal.size, (0, 0, 0, 0))
        _poser(out, cal, cal.width / 2, cal.height / 2, k, a)
        return out

    def sons(self):
        out = [(self.t0(), "compteur")] + [(self._t_arret(i), "clic") for i in range(self.n)]
        if self.pilule is not None:
            out.append((self._t_pilule() + C.TAMPON_FRAPPE, "impact"))
        return out


# ---------------------------------------------------------------- bouclier
_BOUCLIER = [(0.5, 0.0), (0.95, 0.12), (0.95, 0.48), (0.89, 0.68), (0.76, 0.85), (0.5, 1.0), (0.24, 0.85),
             (0.11, 0.68), (0.05, 0.48), (0.05, 0.12)]


class Bouclier(_Pilules, _Insert):
    """Un bouclier qui couvre une silhouette (le docteur junior) ; au temps "temps", son contour se
    defait en pointilles et un « ? » se balance : on ne sait pas s'il le couvre. A droite, les
    pilules du texte."""

    def taille_nominale(self):
        return C.TEXTE_LARGEUR, C.BOUCLIER_H

    def __init__(self, *a):
        super().__init__(*a)
        g = C.BOUCLIER_GEO
        bw, bh = self.px(g["bouclier"][0]), self.px(g["bouclier"][1])
        tr = self.px(g["trait"])
        navy, rub = C.NAVY + (255,), tuple(self.rubrique) + (255,)

        def pts(k, retrait=0):
            cx, cy = bw * k / 2, bh * k * 0.48
            fx, fy = 1 - 2 * retrait / bw, 1 - 2 * retrait / bh
            return [(cx + (x * bw * k - cx) * fx, cy + (y * bh * k - cy) * fy) for x, y in _BOUCLIER]

        def fond(d, k):
            d.polygon(pts(k), fill=C.BLANC + (255,))
            r, (lb, hb_) = self.px(g["tete"]) * k, (self.px(g["buste"][0]) * k, self.px(g["buste"][1]) * k)
            cx, cy = bw * k / 2, bh * k * 0.5
            d.ellipse([cx - r, cy - r * 2.4, cx + r, cy - r * 0.4], fill=rub)
            d.rounded_rectangle([cx - lb / 2, cy - r * 0.1, cx + lb / 2, cy - r * 0.1 + hb_], radius=hb_ * 0.45, fill=rub)
            cl, ce = self.px(g["croix"][0]) * k, self.px(g["croix"][1]) * k
            yc = cy - r * 0.1 + hb_ * 0.48
            d.rectangle([cx - cl / 2, yc - ce / 2, cx + cl / 2, yc + ce / 2], fill=C.BLANC + (255,))
            d.rectangle([cx - ce / 2, yc - cl / 2, cx + ce / 2, yc + cl / 2], fill=C.BLANC + (255,))

        def anneau(d, k):
            d.polygon(pts(k), fill=navy)
            d.polygon(pts(k, tr), fill=(0, 0, 0, 0))
        self.fond = _ombre_marge(_net(bw, bh, fond), self.s)
        plein = _net(bw, bh, anneau)
        periode, trace = (self.px(v) for v in g["pointilles"])
        self.anneaux = [_ombre_marge(plein, self.s), _ombre_marge(_pointilles(plein, periode, trace), self.s)]
        self.badge = _icone_choix(None, self.px(g["badge"]), self.px(C.CHOIX_GEO["trait"]), self.rubrique)
        self.bx, self.by = self.m + bw / 2, self.m + self.h / 2
        self.bw, self.bh = bw, bh
        self._preparer_pilules(g, self.m + bw + self.px(g["ecart"]), self.by)

    def _t_doute(self):
        return self.t0(self.spec.get("temps", 1)) + C.INSERT_DELAI

    def image(self, t, final):
        g = C.BOUCLIER_GEO
        k, a = _entree(t, self.t0(), final)
        if a <= 0:
            return None
        out = Image.new("RGBA", (self.w + 2 * self.m, self.h + 2 * self.m), (0, 0, 0, 0))
        q = 1.0 if final else T.lisse((t - self._t_doute()) / g["bascule"])
        _poser(out, self.fond, self.bx, self.by, k, a)
        _poser(out, self.anneaux[0], self.bx, self.by, k, a * (1 - q))
        _poser(out, self.anneaux[1], self.bx, self.by, k, a * q)
        v = 1.0 if final else (t - self._t_doute() - g["bascule"] * 0.5) / C.INSERT_ENTREE
        if v > 0:
            amp, freq = C.CHOIX_GEO["balance"]
            angle = 0.0 if final or v < 1 else amp * math.sin(2 * math.pi * freq * (t - self._t_doute()))
            kk = 0.3 + 0.7 * (1.0 if final else T.rebond(v))
            _poser(out, self.badge, self.bx + self.bw * 0.4, self.by - self.bh * 0.4, kk,
                   1.0 if final else T.lisse(v * 2), angle)
        self._pilules(out, t, final)
        return out

    def sons(self):
        return [(self.t0(), "souffle"), (self._t_doute(), "clic")] + self._sons_pilules()


# ---------------------------------------------------------------- departements
class Departements(_Insert):
    """Les departements concernes : des tuiles (numero, nom) qui se retournent l'une apres l'autre."""

    def taille_nominale(self):
        g = C.DEPARTEMENTS_GEO
        rangs = -(-len(self.spec["liste"]) // g["colonnes"])
        return C.TEXTE_LARGEUR, rangs * g["case_h"] + (rangs - 1) * g["ecart"]

    def __init__(self, *a):
        super().__init__(*a)
        g = C.DEPARTEMENTS_GEO
        self.ecart = self.px(g["ecart"])
        self.cw = (self.w - (g["colonnes"] - 1) * self.ecart) // g["colonnes"]
        self.ch = self.px(g["case_h"])
        self.tuiles = []
        for dep in self.spec["liste"]:
            im = _cadre(self.cw, self.ch, self.s, marge=self.m)
            d = ImageDraw.Draw(im)
            _ecrire(d, (self.m + self.cw / 2, self.m + self.ch * g["numero_y"]), dep["numero"],
                    self.px(g["numero_px"]), C.INSERT_GRAISSE_FORTE, tuple(self.rubrique) + (255,), "mm")
            _ecrire(d, (self.m + self.cw / 2, self.m + self.ch * g["nom_y"]), dep["nom"], self.px(g["nom_px"]),
                    C.INSERT_GRAISSE_FORTE, C.NAVY + (255,), "mm")
            self.tuiles.append(_ombre(im, self.s))

    def _t(self, i):
        return self.t0(self.spec.get("temps", 0)) + i * C.DEPARTEMENTS_GEO["decalage"]

    def image(self, t, final):
        g = C.DEPARTEMENTS_GEO
        out = Image.new("RGBA", (self.w + 2 * self.m, self.h + 2 * self.m), (0, 0, 0, 0))
        for i, tuile in enumerate(self.tuiles):
            p = 1.0 if final else (t - self._t(i)) / g["retourne"]
            if p <= 0:
                continue
            ky = 1.0 if final else max(0.02, T.rebond(p))     # la tuile se retourne : elle s'ouvre en hauteur
            im = tuile.resize((tuile.width, max(1, int(tuile.height * ky))), Image.BICUBIC)
            col, rang = i % g["colonnes"], i // g["colonnes"]
            cx = self.m + col * (self.cw + self.ecart) + self.cw / 2
            cy = self.m + rang * (self.ch + self.ecart) + self.ch / 2
            T.coller(out, im, (cx - im.width / 2, cy - im.height / 2), 1.0 if final else T.lisse(p * C.INSERT_FONDU))
        return out

    def sons(self):
        return [(self._t(i), "clic") for i in range(len(self.tuiles))]


# ---------------------------------------------------------------- ordonnance
class Ordonnance(_Insert):
    """Une ordonnance qui s'ecrit : chaque ligne (le traitement, puis sa condition en gris) se trace
    de gauche a droite, un stylo au bout du trait ; une pilule rouge claque au pied ("pied")."""

    def _mise_en_page(self, s):
        """Lignes de texte de chaque prescription et hauteur totale, a l'echelle s."""
        g = C.ORDONNANCE_GEO
        p = lambda v: max(1, int(round(v * s)))
        utile = p(g["w"]) - 2 * p(g["pad"])
        blocs = [(_couper(l["label"], p(g["label_px"]), C.INSERT_GRAISSE_FORTE, utile),
                  _couper(l.get("note", ""), p(g["note_px"]), C.INSERT_GRAISSE_TEXTE, utile) if l.get("note") else [])
                 for l in self.spec["lignes"]]
        hauteurs = [len(a) * p(g["label_px"]) * g["interligne"] + len(b) * p(g["note_px"]) * g["interligne"]
                    for a, b in blocs]
        h = p(g["tete"]) + p(g["pad"]) + sum(hauteurs) + (len(blocs) - 1) * p(g["ligne_ecart"]) + p(g["pad"])
        if self.spec.get("pied"):
            h += p(g["pilule_h"]) + p(g["pad"]) * 0.6
        return blocs, hauteurs, h

    def taille_nominale(self):
        return C.ORDONNANCE_GEO["w"], int(self._mise_en_page(1.0)[2])

    def __init__(self, *a):
        super().__init__(*a)
        g = C.ORDONNANCE_GEO
        blocs, hauteurs, _ = self._mise_en_page(self.s)
        pad, tete = self.px(g["pad"]), self.px(g["tete"])
        rub = tuple(self.rubrique)
        papier = _cadre(self.w, self.h, self.s, marge=self.m)
        bande = _net(self.w, tete, lambda d, k: (
            d.rounded_rectangle([0, 0, self.w * k - 1, tete * k * 1.5], radius=self.px(C.INSERT_RAYON) * k,
                                fill=_teinte(rub, 0.88) + (255,)),
            d.rectangle([0, (tete - self.px(g["filet"])) * k, self.w * k, tete * k], fill=rub + (255,))))
        bande.putalpha(ImageChops.multiply(bande.getchannel("A"),
                                           papier.crop((self.m, self.m, self.m + self.w, self.m + tete)).getchannel("A")))
        papier.alpha_composite(bande, (self.m, self.m))
        d = ImageDraw.Draw(papier)
        _ecrire(d, (self.m + pad, self.m + tete / 2), T.normaliser(self.spec.get("titre", "Ordonnance")).upper(),
                self.px(g["titre_px"]), C.INSERT_GRAISSE_FORTE, rub + (255,), "lm")
        if self.spec.get("marque"):
            marque = _bulle(self.spec["marque"], self.px(g["marque_px"]), self.px(g["marque_h"]),
                            self.px(g["marque_pad"]), rub, queue=False)
            papier.alpha_composite(marque, (int(self.m + self.w - pad - marque.width),
                                            int(self.m + (tete - marque.height) / 2)))
        self.papier = _ombre(papier, self.s)
        self.lignes, self.ly = [], []
        y = self.m + tete + pad
        for (labels, notes), hh in zip(blocs, hauteurs):
            im = Image.new("RGBA", (self.w - 2 * pad, int(hh) + 2), (0, 0, 0, 0))
            dl = ImageDraw.Draw(im)
            yy, lp, np_ = 0, self.px(g["label_px"]), self.px(g["note_px"])
            for l in labels:
                _ecrire(dl, (0, yy), l, lp, C.INSERT_GRAISSE_FORTE, C.NAVY + (255,))
                yy += lp * g["interligne"]
            for l in notes:
                _ecrire(dl, (0, yy), l, np_, C.INSERT_GRAISSE_TEXTE, C.INSERT_GRIS_TEXTE + (255,))
                yy += np_ * g["interligne"]
            self.lignes.append(im)
            self.ly.append(y)
            y += hh + self.px(g["ligne_ecart"])
        self.pied = None
        if self.spec.get("pied"):
            self.pied = _ombre_marge(_bulle(self.spec["pied"], self.px(g["pilule_px"]), self.px(g["pilule_h"]),
                                            self.px(g["pilule_pad"]), C.INSERT_ROUGE, queue=False), self.s)
            self.pied_y = self.m + self.h - pad * 0.6 - self.px(g["pilule_h"]) / 2
        sw, sl = self.px(g["stylo"][0]), self.px(g["stylo"][1])
        cote = 2 * sl + 4

        def stylo(dd, k):                                # pointe au centre, corps vers le haut
            c = cote * k / 2
            dd.rounded_rectangle([c - sw * k / 2, c - sl * k, c + sw * k / 2, c - sw * k * 1.2], radius=sw * k / 2,
                                 fill=C.NAVY + (255,))
            dd.polygon([(c - sw * k / 2, c - sw * k * 1.4), (c + sw * k / 2, c - sw * k * 1.4), (c, c)],
                       fill=(8, 5, 26, 255))
        self.stylo = _ombre_marge(_net(cote, cote, stylo).rotate(-g["stylo_angle"], resample=Image.BICUBIC), self.s)

    def _t_ligne(self, j):
        g = C.ORDONNANCE_GEO
        l = self.spec["lignes"][j]
        avant = [i for i in range(j) if self.spec["lignes"][i].get("temps", 0) == l.get("temps", 0)]
        return self.t0(l.get("temps", 0)) + C.INSERT_ENTREE * 0.6 + len(avant) * g["ecriture"]

    def _t_pied(self):
        g = C.ORDONNANCE_GEO
        fin = self._t_ligne(len(self.lignes) - 1) + g["ecriture"] + g["pilule_delai"]
        return max(fin, self.t0(self.spec["temps_pied"])) if "temps_pied" in self.spec else fin

    def image(self, t, final):
        g = C.ORDONNANCE_GEO
        k, a = _entree(t, self.t0(), final)
        if a <= 0:
            return None
        cal = self.papier.copy()
        x0 = self.m + self.px(g["pad"])
        plume = None
        for j, (im, y) in enumerate(zip(self.lignes, self.ly)):
            p = 1.0 if final else T.lisse((t - self._t_ligne(j)) / g["ecriture"])
            if p <= 0:
                continue
            larg = max(1, int(im.width * p))
            cal.alpha_composite(im.crop((0, 0, larg, im.height)), (int(x0), int(y)))
            if 0 < p < 1:
                plume = (x0 + larg, y + self.px(g["label_px"]) * 0.85)
        if self.pied is not None:
            kk, aa = _frappe(t, self._t_pied(), final)
            if aa > 0:
                _poser(cal, self.pied, x0 + (self.pied.width - 2 * self.m) / 2, self.pied_y, kk, aa, -2)
        if plume is not None:
            _poser(cal, self.stylo, plume[0], plume[1])
        out = Image.new("RGBA", cal.size, (0, 0, 0, 0))
        _poser(out, cal, cal.width / 2, cal.height / 2, k, a)
        return out

    def sons(self):
        out = [(self.t0(), "souffle")] + [(self._t_ligne(j), "clic") for j in range(len(self.lignes))]
        if self.pied is not None:
            out.append((self._t_pied() + C.TAMPON_FRAPPE, "impact"))
        return out


# ---------------------------------------------------------------- sablier
_VERRE = [(0.1, 0.0), (0.9, 0.0), (0.88, 0.2), (0.62, 0.44), (0.54, 0.5), (0.62, 0.56), (0.88, 0.8), (0.9, 1.0),
          (0.1, 1.0), (0.12, 0.8), (0.38, 0.56), (0.46, 0.5), (0.38, 0.44), (0.12, 0.2)]


class Sablier(_Pilules, _Insert):
    """Un sablier dont le sable coule, qui se retourne sans fin ; un « ? » se balance a son coin :
    aucun delai n'est fixe. A droite, les pilules du texte."""

    def taille_nominale(self):
        return C.TEXTE_LARGEUR, C.SABLIER_H

    def __init__(self, *a):
        super().__init__(*a)
        g = C.SABLIER_GEO
        self.sw, self.sh = self.px(g["sablier"][0]), self.px(g["sablier"][1])
        self.socle, self.tr = self.px(g["socle"]), self.px(g["trait"])
        self.cote = int(max(self.sw, self.sh) * 1.1)
        self.badge = _icone_choix(None, self.px(g["badge"]), self.px(C.CHOIX_GEO["trait"]), self.rubrique)
        self.cx, self.cy = self.m + self.cote / 2, self.m + self.h / 2
        self._preparer_pilules(g, self.m + self.cote + self.px(g["ecart"]), self.cy)
        self.cache = {}

    def _dessin(self, p):
        """Le sablier, sable ecoule a la fraction p (le haut se vide, le bas se remplit)."""
        cle = round(p, 2)
        if cle in self.cache:
            return self.cache[cle]
        sw, sh, so, tr, cote = self.sw, self.sh, self.socle, self.tr, self.cote
        rub, navy = tuple(self.rubrique) + (255,), C.NAVY + (255,)

        def geo(k):
            x0, y0 = (cote - sw) / 2 * k, (cote - sh) / 2 * k
            ya, yb = y0 + so * k, y0 + (sh - so) * k              # haut et bas du verre
            return x0, y0, ya, yb, [(x0 + sw * k * x, ya + (yb - ya) * y) for x, y in _VERRE]

        def verre(d, k):
            d.polygon(geo(k)[4], fill=C.BLANC + (235,))

        def sable(d, k):
            x0, _, ya, yb, _ = geo(k)
            col = (yb - ya) / 2
            d.rectangle([0, ya + col * p, cote * k, ya + col], fill=rub)            # le haut se vide
            d.rectangle([0, yb - col * p, cote * k, yb], fill=rub)                  # le bas se remplit
            if 0 < p < 1:
                d.line([(x0 + sw * k / 2, ya + col), (x0 + sw * k / 2, yb)], fill=rub, width=max(2, int(tr * k * 0.5)))

        def contour(d, k):
            x0, y0, _, _, pts = geo(k)
            d.line(pts + [pts[0]], fill=navy, width=int(tr * k), joint="curve")
            for y in (y0, y0 + (sh - so) * k):
                d.rounded_rectangle([x0 - so * k * 0.4, y, x0 + (sw + so * 0.4) * k, y + so * k], radius=so * k * 0.4,
                                    fill=navy)
        im = _net(cote, cote, verre)
        grains = _net(cote, cote, sable)
        grains.putalpha(ImageChops.multiply(grains.getchannel("A"), _net(cote, cote, lambda d, k: d.polygon(
            geo(k)[4], fill=C.BLANC + (255,))).getchannel("A")))
        im.alpha_composite(grains)
        im.alpha_composite(_net(cote, cote, contour))
        im = _ombre_marge(im, self.s)
        self.cache[cle] = im
        return im

    def image(self, t, final):
        g = C.SABLIER_GEO
        k, a = _entree(t, self.t0(), final)
        if a <= 0:
            return None
        out = Image.new("RGBA", (self.w + 2 * self.m, self.h + 2 * self.m), (0, 0, 0, 0))
        coule = g["cycle"] - g["retournement"]
        phase = 0.0 if final else (t - self.t0()) % g["cycle"]
        p, angle = (0.5, 0.0) if final else (min(1.0, phase / coule), 180 * T.lisse((phase - coule) / g["retournement"]))
        _poser(out, self._dessin(p), self.cx, self.cy, k, a, angle)
        v = 1.0 if final else (t - self.t0() - C.INSERT_ENTREE) / C.INSERT_ENTREE
        if v > 0:
            amp, freq = C.CHOIX_GEO["balance"]
            ang = 0.0 if final or v < 1 else amp * math.sin(2 * math.pi * freq * (t - self.t0()))
            _poser(out, self.badge, self.cx + self.sw * 0.55, self.cy - self.sh * 0.45,
                   0.3 + 0.7 * (1.0 if final else T.rebond(v)), 1.0 if final else T.lisse(v * 2), ang)
        self._pilules(out, t, final)
        return out

    def sons(self):
        return [(self.t0(), "souffle")] + self._sons_pilules()


# ---------------------------------------------------------------- pilule
class Pilule(_Insert):
    """Une pilule seule (« Aucune rémunération prévue ») qui claque au temps "temps", ton rouge par
    defaut : sous un dessin, elle ne cache rien, la ou un tampon couvrirait ses libelles."""

    def _sprite(self, s):
        g = C.PILULE_GEO
        # appele par taille_nominale, avant que _Insert.__init__ ne pose self.rubrique
        return _bulle(self.spec["texte"], max(8, int(g["px"] * s)), max(8, int(g["h"] * s)), int(g["pad"] * s),
                      _ton({"ton": self.spec.get("ton", "rouge")}, tuple(hb._RUBRIQUE)), queue=False)

    def taille_nominale(self):
        im = self._sprite(1.0)
        return im.width, im.height

    def __init__(self, *a):
        super().__init__(*a)
        self.sprite = _ombre_marge(self._sprite(self.s), self.s)

    def image(self, t, final):
        k, a = _frappe(t, self.t0(self.spec.get("temps", 0)), final)
        if a <= 0:
            return None
        out = Image.new("RGBA", (self.w + 2 * self.m, self.h + 2 * self.m), (0, 0, 0, 0))
        _poser(out, self.sprite, self.m + self.w / 2, self.m + self.h / 2, k, a, C.PILULE_GEO["angle"])
        return out

    def sons(self):
        return [(self.t0(self.spec.get("temps", 0)) + C.TAMPON_FRAPPE, "impact")]


TYPES = {"verrou": Verrou, "calendrier": Calendrier, "barres": Barres, "choix": Choix,
         "tampon": Tampon, "circuit": Circuit, "duel": Duel, "frise": Frise, "frigo": Frigo,
         "ticket": Ticket, "appel": Appel, "loupe": Loupe, "calcul": Calcul, "ages": Ages,
         "vases": Vases, "pieces": Pieces, "part": Part, "bascule": Bascule, "icones": Icones,
         "prix": Prix, "carte": Carte, "compteur": Compteur, "bouclier": Bouclier,
         "departements": Departements, "ordonnance": Ordonnance, "sablier": Sablier, "pilule": Pilule}


def inserts(ep, scenes, ouverture=None):
    """Les inserts du reel, un ou plusieurs par bloc qui en porte (scenes : habillage.scenes)."""
    out = []
    for k, bl in enumerate(ep["blocs"]):
        specs = bl.get("insert")
        if not specs:
            continue
        specs = [specs] if isinstance(specs, dict) else specs
        if bl.get("type") in ("phrase", "chiffre") or k == 0:
            raise SystemExit(f"[!] bloc {k} : un insert se pose sur un bloc de texte (pas sur "
                             "l'accroche, une phrase forte ou un chiffre cle).")
        scene = scenes[k]
        hauts = [b[1] for b in (hb._bbox(lay) for _, lay, _ in scene.couches()) if b]
        bas = min(hauts) if hauts else C.BLOC_Y
        if ouverture is not None and ouverture.scene is scene:
            bas = ouverture.pos[1]
        premier, haut = None, bas - C.INSERT_ECART
        for spec in specs:
            # "carre": false le retire de la version carree, plus basse : au bloc 1, la pastille
            # d'ouverture ne laisse pas toujours la place d'un insert (charte.CARRE)
            if spec.get("carre") is False and C.LARGEUR == C.HAUTEUR:
                continue
            if spec.get("type") not in TYPES:
                raise SystemExit(f"[!] bloc {k} : insert inconnu « {spec.get('type')} ». "
                                 f"Types : {', '.join(TYPES)}.")
            nom = f"insert bloc {k}" + (f" ({spec['type']})" if len(specs) > 1 else "")
            # "sur": true centre l'element sur le premier insert du bloc (un tampon sur un dessin) ;
            # sinon, chaque element s'empile au-dessus du precedent
            sur = spec.get("sur") and premier is not None
            ins = TYPES[spec["type"]](nom, spec, scene, bas - C.INSERT_ECART if sur else haut)
            if sur:
                ins.x = premier.x + (premier.w - ins.w) / 2
                ins.y = premier.y + (premier.h - ins.h) / 2
            else:
                haut = ins.y - C.INSERT_ECART_ELEMENTS
            premier = premier or ins
            out.append(ins)
    return out
