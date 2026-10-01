"""
Charte visuelle et sonore du reel LCDG.

Toutes ces valeurs ont ete validees une par une avec Romain.
Ne les modifier qu'a la demande explicite : le gabarit est fige.
"""
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
ASSETS = RACINE / "assets"
POLICE = ASSETS / "fonts" / "Montserrat.ttf"
LOGO_SRC = ASSETS / "logo" / "LOGO_LCDG.png"
EPISODES = RACINE / "episodes"

# ---------------------------------------------------------------- format
LARGEUR, HAUTEUR, FPS = 1080, 1920, 30

# Zone sure 4:5. Le fil Instagram et Facebook recadre le reel en 4:5 (1080x1350,
# centre) : tout ce qui doit rester lisible tient dans cette bande. Adoptee le
# 17/09/2026 a la demande de Romain, le logo a 44 px du haut sortait du recadrage.
# Le 9:16 est conserve pour garder le plein ecran dans l'onglet Reels.
ZONE_SURE_HAUT = (HAUTEUR - LARGEUR * 5 // 4) // 2   # 285
ZONE_SURE_BAS = ZONE_SURE_HAUT + LARGEUR * 5 // 4    # 1635

# ------------------------------------------------- couleurs (theme.css du site)
PRIMARY = (4, 123, 191)      # --primary        #047bbf
STRONG = (3, 99, 153)        # --primary-strong #036399  (reserve, non utilise au montage)
NAVY = (27, 16, 70)          # --titles         #1b1046
BLANC = (255, 255, 255)
RADIUS = 16                  # --radius .625rem, remis a l'echelle du 1080

# Couleur de bandeau par rubrique du site. Le reel prend celle de l'article.
RUBRIQUES = {
    "pro": (4, 123, 191),        # #047bbf  Vie Pro & Metier
    "politique": (79, 70, 229),  # #4f46e5
    "clinique": (5, 150, 105),   # #059669
    "numerique": (124, 58, 237), # #7c3aed
    "patient": (225, 29, 72),    # #e11d48
}

# ------------------------------------------------------------- typographie
# Style v2, propose le 01/10/2026 : plus de contour bleu ni de filet blanc, qui
# dataient le rendu. Le texte tient par une ombre douce et le voile sombre ; la
# hierarchie passe par la taille et la graisse, comme les titres du site
# (Montserrat 700, interlettrage resserre de -0,01 a -0,02 em).
TEXTE_X = 96                   # marge gauche commune a tous les textes
TEXTE_LARGEUR = 840            # colonne : a l'ecart des boutons de l'onglet Reels, a droite

ACCROCHE_PX, ACCROCHE_GRAISSE = 92, "ExtraBold"   # phrase d'ouverture (champ sous_titre)
ACCROCHE_INTERLIGNE = 100
ACCROCHE_APPROCHE = -0.025     # interlettrage, en fraction du corps
SURTITRE_PX, SURTITRE_GRAISSE = 34, "Bold"        # pastille du sujet (champ label)
SURTITRE_APPROCHE = 0.10
SURTITRE_H = 64
SURTITRE_PAD = 22
SURTITRE_ECART = 30            # entre la pastille et l'accroche

BLOC_PX, BLOC_GRAISSE = 66, "Bold"
CLE_GRAISSE = "ExtraBold"      # segment entre asterisques
BLOC_INTERLIGNE = 78
BLOC_APPROCHE = -0.012

CHIFFRE_PX, CHIFFRE_GRAISSE = 230, "ExtraBold"    # bloc de type "chiffre"
CHIFFRE_APPROCHE = -0.03
CHIFFRE_ECART = 34             # entre la ligne de base du chiffre et la legende
ANCIEN_PX, ANCIEN_GRAISSE = 76, "Bold"            # valeur precedente, barree
ANCIEN_ALPHA = 0.78
ANCIEN_ECART = 22              # entre la valeur barree et le haut du chiffre
BARRE_PX = 9
BARRE_DEBORD = 8               # la barre deborde la valeur de chaque cote

SURLIGNE_MARGE = 12            # le surlignage deborde du mot de chaque cote
# Voile : l'image s'assombrit le temps de l'accroche et d'un chiffre cle, pour que le
# texte reste lisible meme sur un plan clair et que l'oeil aille a l'information
VOILE_ACCROCHE = 0.22
VOILE_CHIFFRE = 0.26           # le flou de profondeur fait le reste
VOILE_PHRASE = 0.26
VOILE_DUREE = 0.35

# Flou de profondeur : sous un chiffre cle, l'image se floute le
# temps du bloc (montage.base), comme une mise au point qui passe au texte
FLOU_RAYON = 24
FLOU_ENTREE = 0.45

# Chiffre cle : une unite en toutes lettres ("boites") passe a cette fraction du corps
UNITE_ECHELLE = 0.36

# Pictogrammes ("pictos": true) : une boite par unite, au-dessus du chiffre
PICTO_PX, PICTO_ECART, PICTO_COLONNES = 38, 12, 10
PICTO_GRAND, PICTO_GRAND_ECART = 92, 26
PICTO_GRAND_MAX = 10           # jusqu'a 10 unites : grandes boites, sur une ligne
PICTO_MAX = 120
PICTO_MARGE = 34               # entre les boites et le chiffre (ou la valeur barree)
PICTO_ETEINT = 0.22            # opacite d'une unite retiree
PICTO_DECALAGE = 0.05
PICTO_OPACITE = 245            # boite blanche, a peine transparente
PICTO_RAYON = 1 / 6            # arrondi, en fraction du cote
PICTO_CROIX = (0.40, 0.12)     # croix de la rubrique : longueur et epaisseur des branches
PICTO_OMBRE = 130
SURLIGNE_RAYON = 8
SURLIGNE_HAUT = 0.16           # debord au-dessus des capitales, en fraction du corps
SURLIGNE_BAS = 0.18            # debord sous la ligne de base, en fraction du corps
# Controle sur le fichier livre : pixels de la couleur de rubrique (a cet ecart RVB
# pres, compression comprise) attendus la ou chaque surlignage doit se trouver
SURLIGNE_CONTROLE_MIN = 3000
SURLIGNE_CONTROLE_ECART = 60

# Ombre du texte : un halo large qui assourdit le fond, une ombre courte qui detache
OMBRE_FLOU, OMBRE_ALPHA, OMBRE_DECALAGE = 8, 190, 4
HALO_FLOU, HALO_ALPHA = 28, 120

# ------------------------------------------------------------- mise en page
LOGO_PX = 124                  # 248 trop gros, 88 trop petit -> valide a 124
LOGO_MARGE = 44
LOGO_Y = ZONE_SURE_HAUT + LOGO_MARGE   # etait LOGO_MARGE (44) avant la zone sure
BLOC_Y = 1030                  # haut de la premiere ligne, juste sous la mediane
ACCROCHE_CENTRE = (ZONE_SURE_HAUT + ZONE_SURE_BAS) // 2   # pastille + accroche centrees

# Voile sombre (scrim). En haut, il assombrit le fond du logo : il suit donc le logo
# dans la zone sure, sur la meme hauteur qu'avant, et reste plein au-dessus.
SCRIM_HAUT_ALPHA = 115
SCRIM_HAUT_PX = 326            # portee du degrade sous le haut de la zone sure
SCRIM_BAS_DEBUT = 0.44         # en fraction de la hauteur, porte la lisibilite des blocs
SCRIM_BAS_ALPHA = 205
SCRIM_MAX = 210

# Carte finale. v2 : l'appel a l'action remplace le slogan, pour envoyer vers
# l'analyse ; le bloc logo-appel-lien reste centre sur la ligne mediane. Le reel est une
# porte d'entree : chaque script porte de preference son propre "appel", qui nomme ce
# que l'article donne et que le reel a garde (« La parade, en detail : »). APPEL est le
# texte par defaut. Une ligne, une trentaine de caracteres au plus.
APPEL = "L’analyse complète sur"
APPEL_PX, APPEL_GRAISSE = 50, "SemiBold"
LIEN_PX, LIEN_GRAISSE = 44, "Bold"
LIEN_H = 88
# Instagram ne rend pas les liens cliquables dans la legende : on dit ou cliquer, et que
# l'inscription au Cercle est gratuite (les analyses sont reservees aux membres 14 jours)
APPEL_RAPPEL = "Inscription gratuite · lien en bio"
RAPPEL_PX, RAPPEL_GRAISSE = 34, "SemiBold"
OUTRO_LOGO_Y = 700
OUTRO_APPEL_Y = 975
OUTRO_LIEN_Y = 1058
OUTRO_RAPPEL_Y = OUTRO_LIEN_Y + LIEN_H + 36
OUTRO_MENTION_Y = ZONE_SURE_BAS - 130   # 1505, etait 1790

# ------------------------------------------------- declinaison carree (LinkedIn)
# 1080x1080, ajoutee le 18/09/2026. scripts/render_carre.py applique ces valeurs avant
# d'importer lcdg/ (habillage fige W et H a l'import). Tout le cadre est visible dans le
# fil LinkedIn. Memes proportions que le 9:16 : blocs juste sous la mediane, carte
# finale centree, mention a 80 px du bas. La zone sure s'arrete 40 px avant chaque bord :
# une couche est rognee au bord du canevas, un element qui le toucherait ne serait sinon
# jamais detecte (constat de la review Codex du 18/09/2026 pour le bas ; le 01/10/2026,
# les pictogrammes d'un chiffre cle depassaient en haut sans etre signales). Les chiffres
# et pictogrammes y sont plus petits : ils montent au-dessus de BLOC_Y.
CARRE = {
    "LARGEUR": 1080, "HAUTEUR": 1080,
    "ZONE_SURE_HAUT": 40, "ZONE_SURE_BAS": 1040,
    "LOGO_Y": LOGO_MARGE,
    "ACCROCHE_CENTRE": 520,
    "BLOC_Y": 560,
    "CHIFFRE_PX": 190,
    "PICTO_PX": 26, "PICTO_ECART": 8, "PICTO_GRAND": 70, "PICTO_GRAND_ECART": 20,
    "OUTRO_LOGO_Y": 300, "OUTRO_APPEL_Y": 575, "OUTRO_LIEN_Y": 658, "OUTRO_RAPPEL_Y": 782,
    "OUTRO_MENTION_Y": 1000,
    "APPEL_RAPPEL": "Inscription gratuite · lien dans le post",   # LinkedIn : lien dans la publication
}

# --------------------------------------------------------------- animations
ENTREE_DELAI = 0.08            # le premier mot arrive juste apres la coupe
MOT_DECALAGE = 0.055           # entre deux mots : le texte se pose en moins d'une seconde
MOT_DUREE = 0.28               # fondu et montee d'un mot
MOT_MONTEE = 24                # px
SURLIGNE_RETARD = 0.10         # le trait suit les mots du segment pendant qu'ils se posent
SURLIGNE_DUREE = 0.34
SORTIE_DUREE = 0.22            # tout le texte sort vers le haut avant la coupe suivante
SORTIE_MONTEE = 16
PASTILLE_DUREE = 0.30          # ouverture de la pastille du sujet
TENUE_MIN = 0.25               # temps minimal ou le texte reste complet avant sa sortie
CHIFFRE_DELAI = 0.06           # le chiffre arrive juste apres la valeur barree
COMPTE_DELAI = 0.30            # le chiffre commence a defiler
COMPTE_DUREE = 0.95
BARRE_DELAI = 0.18             # la valeur precedente se barre
BARRE_DUREE = 0.32
CROIX_DUREE = 1.10             # ouverture de la croix medicale
OUTRO_DUREE = 2.43             # carte finale, apres la croix
BLOC_RESIDU = 0.25             # le dernier bloc deborde un peu sur la croix
OUTRO_FONDU = 0.45

COUVERTURE_T = 2.2             # image extraite pour la couverture : accroche en place

LIEN = "lecercledesgeneralistes.fr"
MENTION = "Images d\u2019illustration"

# ------------------------------------------------------------------- son
# Aucun. Depuis le 21/09/2026 les reels sont livres sans piste audio : Romain pose la
# musique lui-meme au montage final. Le controle verifie qu'aucune piste ne sort.

# --------------------------------------------------------------- B-roll
BROLL_ZOOM = 1.06              # zoom lent sur la duree du plan
BROLL_MARGE_S = 0.4            # on entre dans le plan apres ce delai
# v2 : a chaque coupe, l'image se pose (leger recul en 8 images) en meme temps que
# le texte arrive ; un etalonnage commun unifie des plans venus de sources differentes.
IMPULSION = 1.05
IMPULSION_IMAGES = 8
ETALONNAGE = ("eq=contrast=1.05:saturation=0.86:brightness=-0.012,"
              "colorbalance=bs=0.035:bm=0.012:rh=0.012,"
              "vignette=angle=0.55")
