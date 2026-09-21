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
TITRE_PX, TITRE_GRAISSE = 72, "ExtraBold"
SOUS_TITRE_PX, SOUS_TITRE_GRAISSE = 56, "Bold"
BLOC_PX, BLOC_GRAISSE = 58, "Bold"
BLOC_INTERLIGNE = 82
BLOC_LARGEUR_MAX = 780
SURLIGNE_MARGE = 11            # le surlignage deborde du mot de chaque cote

CONTOUR = (4, 123, 191, 232)   # bleu du site, allege
CONTOUR_PX = 3                 # 4 px etait trop marque

# ------------------------------------------------------------- mise en page
LOGO_PX = 124                  # 248 trop gros, 88 trop petit -> valide a 124
LOGO_MARGE = 44
LOGO_Y = ZONE_SURE_HAUT + LOGO_MARGE   # etait LOGO_MARGE (44) avant la zone sure
FILET_PX = 20                  # 28 etait trop epais
FILET_COULEUR = BLANC
BLOC_Y = 1030                  # juste sous la ligne mediane
BLOC_X = 148
INTRO_Y = 980

# Voile sombre (scrim). En haut, il assombrit le fond du logo : il suit donc le logo
# dans la zone sure, sur la meme hauteur qu'avant, et reste plein au-dessus.
SCRIM_HAUT_ALPHA = 115
SCRIM_HAUT_PX = 326            # portee du degrade sous le haut de la zone sure
SCRIM_BAS_DEBUT = 0.44         # en fraction de la hauteur, porte la lisibilite des blocs
SCRIM_BAS_ALPHA = 205
SCRIM_MAX = 210

# Carte finale. Le bloc logo-slogan-lien etait deja centre sur la ligne mediane ;
# seule la mention remonte, a la meme distance du bas de la zone sure qu'avant du bas
# de l'image (130 px).
OUTRO_LOGO_Y = 690
OUTRO_SLOGAN_Y = 960
OUTRO_LIEN_Y = 1150
OUTRO_MENTION_Y = ZONE_SURE_BAS - 130   # 1505, etait 1790

# ------------------------------------------------- declinaison carree (LinkedIn)
# 1080x1080, ajoutee le 18/09/2026. scripts/render_carre.py applique ces valeurs avant
# d'importer lcdg/ (habillage fige W et H a l'import). Tout le cadre est visible dans le
# fil LinkedIn. Memes proportions que le 9:16 : blocs juste sous la mediane, carte
# finale centree, mention a 80 px du bas. La zone sure s'arrete 40 px avant le bas :
# une couche est rognee au bord du canevas, un texte qui toucherait le bord ne serait
# sinon jamais detecte (constat de la review Codex du 18/09/2026). Rien ne deborde en
# haut : les blocs partent de BLOC_Y et grandissent vers le bas.
CARRE = {
    "LARGEUR": 1080, "HAUTEUR": 1080,
    "ZONE_SURE_HAUT": 0, "ZONE_SURE_BAS": 1040,
    "LOGO_Y": LOGO_MARGE,
    "INTRO_Y": 520,
    "BLOC_Y": 560,
    "OUTRO_LOGO_Y": 268, "OUTRO_SLOGAN_Y": 538, "OUTRO_LIEN_Y": 728, "OUTRO_MENTION_Y": 1000,
}

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
SFX_STRUCTURE_VOLUME = 0.0     # bruitages coupes le 04/09/2026 a la demande de Romain
SFX_TEXTE_VOLUME = 0.0         # (valeurs d'origine : 0.46 et 0.30)
SFX_TEXTE_NB = 4               # 4 respirations, PAS les 8 changements de bloc
LUFS_CIBLE = -14
TRUE_PEAK_CIBLE = -2           # cible visee par loudnorm au mixage
TRUE_PEAK_PLAFOND = -1.0       # le controle est un plafond : un true peak plus bas
                               # n'est pas un defaut. Remplace le 17/09/2026 la fenetre
                               # centree sur -4 (calibree sur relaxation-04 sans
                               # bruitages, -4.4), qui rejetait lofi-05 a -2.4
LIMITEUR = 0.72                # absorbe le depassement inter-echantillons de l'AAC

# --------------------------------------------------------------- B-roll
BROLL_ZOOM = 1.06              # zoom lent sur la duree du plan
BROLL_MARGE_S = 0.4            # on entre dans le plan apres ce delai
