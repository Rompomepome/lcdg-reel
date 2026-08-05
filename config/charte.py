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
AUDIO = ASSETS / "audio"
EPISODES = RACINE / "episodes"

# ---------------------------------------------------------------- format
LARGEUR, HAUTEUR, FPS = 1080, 1920, 30

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
TITRE_PX, TITRE_GRAISSE = 72, "ExtraBold"
SOUS_TITRE_PX, SOUS_TITRE_GRAISSE = 56, "Bold"
BLOC_PX, BLOC_GRAISSE = 58, "Bold"
BLOC_INTERLIGNE = 82
BLOC_LARGEUR_MAX = 780

CONTOUR = (4, 123, 191, 232)   # bleu du site, allege
CONTOUR_PX = 3                 # 4 px etait trop marque

# ------------------------------------------------------------- mise en page
LOGO_PX = 124                  # 248 trop gros, 88 trop petit -> valide a 124
LOGO_MARGE = 44
FILET_PX = 20                  # 28 etait trop epais
FILET_COULEUR = BLANC
BLOC_Y = 1030                  # juste sous la ligne mediane
BLOC_X = 148
INTRO_Y = 980

# --------------------------------------------------------------- animations
INTRO_OUVERTURE = 0.60         # ouverture laterale du bandeau
INTRO_FERMETURE = 0.55         # retraction avant le premier bloc
BLOC_ENTREE = 0.42             # glissement depuis la gauche
BLOC_GLISSEMENT = 150          # px
BLOC_SORTIE = 0.30
CROIX_DUREE = 1.10             # ouverture de la croix medicale
OUTRO_DUREE = 2.43             # carte finale, apres la croix
BLOC_RESIDU = 0.25             # le dernier bloc deborde un peu sur la croix
OUTRO_FONDU = 0.45

SLOGAN = ["L\u2019actualité médicale décryptée", "pour les généralistes."]
LIEN = "lecercledesgeneralistes.fr"
MENTION = "Images d\u2019illustration"

# ------------------------------------------------------------------- audio
MUSIQUE_VOLUME = 0.33
MUSIQUE_FONDU_IN = 1.4
MUSIQUE_FONDU_OUT = 2.6
SFX_STRUCTURE_VOLUME = 0.46    # retraction du bandeau, ouverture de la croix
SFX_TEXTE_VOLUME = 0.30        # bois sec sur les respirations
SFX_TEXTE_NB = 4               # 4 respirations, PAS les 8 changements de bloc
LUFS_CIBLE = -14
TRUE_PEAK_CIBLE = -2
LIMITEUR = 0.72                # absorbe le depassement inter-echantillons de l'AAC

# --------------------------------------------------------------- B-roll
BROLL_ZOOM = 1.06              # zoom lent sur la duree du plan
BROLL_MARGE_S = 0.4            # on entre dans le plan apres ce delai
