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
AUDIO = ASSETS / "audio"        # musiques (non versionnees : licences)
SFX = ASSETS / "sfx"            # bruitages de motion (non versionnes)
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
# Marge laterale : sur un telephone plus allonge que le 9:16 (19,5:9), Instagram agrandit
# le reel pour remplir l'ecran et en rogne environ 100 px de chaque cote. Le logo, a 44 px
# du bord, etait rogne (signale par Romain le 01/10/2026) : rien de lisible a moins de 110 px.
MARGE_LATERALE = 110
TEXTE_X = MARGE_LATERALE + 2   # marge gauche commune a tous les textes
TEXTE_LARGEUR = 828            # colonne : a l'ecart des boutons de l'onglet Reels, a droite

ACCROCHE_PX, ACCROCHE_GRAISSE = 92, "ExtraBold"   # phrase d'ouverture (champ sous_titre)
ACCROCHE_INTERLIGNE = 100
ACCROCHE_APPROCHE = -0.025     # interlettrage, en fraction du corps
ACCROCHE_LIGNES_MAX = 4        # au-dela, le corps de l'accroche (et des phrases fortes) diminue
ACCROCHE_PX_MIN = 68
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
# texte reste lisible meme sur un plan clair et que l'oeil aille a l'information.
# Allege le 02/10/2026 (0.22 / 0.26 / 0.26) : Romain trouvait le reel sombre ; l'ombre
# portee des textes suffit a la lisibilite sur des plans de jour.
VOILE_ACCROCHE = 0.14
VOILE_CHIFFRE = 0.18           # le flou de profondeur fait le reste
VOILE_PHRASE = 0.18
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
PICTO_ECHELLE = 0.45           # une boite qui s'allume part de cette taille et rebondit
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
LOGO_MARGE_X = MARGE_LATERALE          # du bord droit ; etait 44
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

# Bandeau (champ "bandeau" du script, facultatif) : une invitation a commenter. En haut
# a gauche, a cote du logo : loin des textes et des bandeaux d'Instagram en bas d'ecran.
# Ni pendant l'accroche, ni sur la carte finale. Syntaxe : « Pour recevoir l'analyse, |
# commentez *140* ». Voulu « ultra discret » le 01/10/2026 (27 px) ; le 02/10, Romain veut
# qu'on voie l'appel : la ligne du mot cle passe a BANDEAU_ACTION_PX, la raison reste petite.
BANDEAU_PX, BANDEAU_GRAISSE = 30, "SemiBold"
BANDEAU_ACTION_PX = 45         # ligne qui porte le mot cle ; 46 touche l'ombre du logo
BANDEAU_ACTION_PX_MIN = 36     # un mot cle long fait descendre le corps, jusqu'ici
BANDEAU_INTERLIGNE = 1.48      # en fraction du corps de la ligne
BANDEAU_ALPHA = 1.0            # pas attenue
# le mot cle : encadre de la couleur de la rubrique, blanc, penche ; marges et rayon en
# fraction du corps
BANDEAU_BOITE_PAD = (0.4, 0.26)
BANDEAU_BOITE_RAYON = 0.22
BANDEAU_INCLINAISON = 3        # degres, sens inverse des aiguilles d'une montre
BANDEAU_Y = LOGO_Y + 22
BANDEAU_ECART_LOGO = 24        # distance minimale entre le bandeau et le logo
BANDEAU_FONDU = 0.5            # (sortie)
# le bandeau s'efface le temps d'un bloc qui entrerait dans sa zone (pictogrammes d'un
# chiffre cle) puis revient ; une apparition plus courte que SEGMENT_MIN est sautee
BANDEAU_ECART_BLOC = 16        # px, entre le bandeau et un bloc
BANDEAU_SEGMENT_MIN = 1.5      # s
# mouvement : chaque ligne glisse depuis la gauche, l'encadre du mot cle s'ouvre avec un
# leger rebond ; a la sortie, le bandeau repart vers la gauche en s'effacant
BANDEAU_ENTREE = 0.45
BANDEAU_GLISSEMENT = 40        # px
BANDEAU_DECALAGE = 0.12        # entre deux lignes
BANDEAU_BOITE_RETARD = 0.3
BANDEAU_BOITE_POP = 0.45
BANDEAU_BOITE_ECHELLE = 0.4    # l'encadre part de cette taille

# Inserts (champ "insert" d'un bloc de texte, lcdg/inserts.py, 05/10/2026) : de petites
# illustrations animees au-dessus du texte, pour comprendre d'un coup d'oeil (« les inserts
# et les illustrations en plus, ca aide a la comprehension », Romain). Cartes blanches
# arrondies a l'ombre douce, dans la couleur de la rubrique ; elles arrivent juste apres le
# texte et sortent avec lui.
INSERT_HAUT_MIN = 540          # sous le bandeau et le logo
INSERT_ECHELLE_MIN = 0.5       # en dessous, l'insert serait illisible : render le refuse
INSERT_ECART = 44              # entre l'insert et le haut du texte (ou de la pastille)
INSERT_ECART_ELEMENTS = 24     # entre deux cartes d'un meme insert
INSERT_RAYON = 26
INSERT_OMBRE = (18, 115, 8)    # flou, opacite, decalage vertical
INSERT_GRIS = (226, 230, 238)  # lignes masquees, barre de reference
INSERT_GRIS_TEXTE = (128, 136, 152)
INSERT_VERT = RUBRIQUES["clinique"]
INSERT_ROUGE = RUBRIQUES["patient"]
INSERT_DELAI = 0.2             # apres le debut du temps qui l'appelle
INSERT_ENTREE = 0.45
INSERT_MONTEE = 40             # px
INSERT_ECHELLE = 0.86          # un element part de cette taille et rebondit
INSERT_DECALAGE = 0.14         # entre deux cartes
INSERT_POUSSE = 0.6            # pousse d'une barre, balayage du calendrier
VERROU_CARTE_H = 300           # recommandations fermees d'un cadenas
VERROU_LIGNES = (0.9, 0.72, 0.84, 0.5)
VERROU_SECOUSSE = (9, 0.55, 0.4)   # amplitude (degres), delai apres l'arrivee, duree (s)
CAL_W, CAL_H, CAL_TETE = 540, 460, 84
CAL_BALAYAGE_DELAI = 0.55
CAL_ETIQUETTE_PX, CAL_ETIQUETTE_PAD, CAL_ETIQUETTE_H = 34, 28, 72
BARRES_PAD, BARRES_LIGNE_H = 30, 110
BARRES_LABEL_PX, BARRES_VALEUR_PX, BARRES_EPAISSEUR = 32, 44, 34
BARRES_DELAI, BARRES_DECALAGE = 0.2, 0.45
BARRES_OUVERTURE = 0.3         # la carte s'agrandit d'une ligne
CHOIX_PX, CHOIX_PAD, CHOIX_ICONE = 40, 20, 62
CHOIX_LIGNE_H, CHOIX_ECART, CHOIX_LARGEUR_MIN = 104, 18, 460
CHOIX_DECALAGE, CHOIX_ICONE_DELAI = 0.22, 0.12
TAMPON_PX, TAMPON_PAD = 64, (30, 16)
TAMPON_ANGLE = 7               # degres, sens inverse des aiguilles d'une montre
TAMPON_FOND = 225              # fond blanc du tampon, a peine transparent
TAMPON_ECHELLE, TAMPON_FRAPPE = 1.9, 0.2
TAMPON_SECOUSSE = (8, 0.3)     # amplitude (px), duree (s)
# geometrie fine des inserts, en px a l'echelle 1 (l'insert entier se met a l'echelle
# de la place disponible) ; les proportions internes des icones (coche, croix, anse du
# cadenas) restent dans leur dessin
INSERT_GRAISSE_FORTE, INSERT_GRAISSE_TEXTE, INSERT_GRAISSE_CHIFFRE = "ExtraBold", "SemiBold", "Bold"
INSERT_FONDU = 1.6             # l'opacite d'un element arrive plus vite que son mouvement
INSERT_MARGE_OMBRE = 2.5       # marge autour d'un element, en multiples du flou de l'ombre
VERROU_GEO = dict(rond=32, rond_marge=26, numero_px=34, pad=26, ligne_y=118, ligne_pas=36,
                  ligne_h=16, pastille=54, corps=(48, 38), corps_rayon=7, corps_bas=10,
                  anse=30, trait=8, trou=6, cadenas_y=0.14)
CAL_GEO = dict(pad=22, jours_y=38, grille_y=30, titre_px=32, jour_px=22, numero_px=26,
               bande_retrait=6, bande_rayon=14)
BARRES_GEO = dict(label_ecart=12, valeur_ecart=14, valeur_marge=16, tolerance=4,
                  fondu_ligne=3)
CHOIX_GEO = dict(trait=7, icone_depart=0.3, fondu_icone=2)
TAMPON_GEO = dict(rayon=14, trait=7, filet_retrait=5, filet_rayon=9, fondu=2)

# Credit (champ "credit" d'un bloc) : la source d'un plan qui ne vient pas d'une banque
# d'images libre de droits, en petit sous le logo, le temps du plan (02/10/2026)
CREDIT_PX, CREDIT_GRAISSE = 24, "SemiBold"
CREDIT_ECART = 14              # sous le logo
CREDIT_ALPHA = 0.9
CREDIT_FONDU = 0.3

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
    "LOGO_Y": LOGO_MARGE, "LOGO_MARGE_X": LOGO_MARGE,   # LinkedIn montre le carre entier
    "ACCROCHE_CENTRE": 520,
    "BLOC_Y": 560,
    "CHIFFRE_PX": 190,
    "PICTO_PX": 26, "PICTO_ECART": 8, "PICTO_GRAND": 70, "PICTO_GRAND_ECART": 20,
    "OUTRO_LOGO_Y": 300, "OUTRO_APPEL_Y": 575, "OUTRO_LIEN_Y": 658, "OUTRO_RAPPEL_Y": 782,
    "OUTRO_MENTION_Y": 1000,
    "APPEL_RAPPEL": "Inscription gratuite · lien dans le post",   # LinkedIn : lien dans la publication
    "BANDEAU_Y": LOGO_MARGE + 22,
    "PLAN_LARGEUR_Y": 220,         # plan en pleine largeur centre dans le carre
    "INSERT_HAUT_MIN": 228,        # sous le bandeau (bas a 208 px) et le logo (189 px)
    "INSERT_ECART": 30,
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
REBOND = 1.70158               # depassement des apparitions en rebond (courbe easeOutBack)
OUTRO_FONDU = 0.45

COUVERTURE_T = 2.2             # image extraite pour la couverture : accroche en place
# L'accroche (bloc 0) ne sert que d'image de couverture : le reel livre commence au bloc 1,
# sur un fait (Romain, 02/10/2026). Le bloc 0 est rendu sans voix, le temps de la
# couverture, puis coupe ; le son commence sans bruitage.
ACCROCHE_COUVERTURE = True
ACCROCHE_COUVERTURE_DUREE = 3.0   # s
DEBUT_SANS_BRUITAGE = 0.25        # s : pas de souffle sur la premiere image ; le compteur (0,3 s) reste
COUPE_FONDU = 0.08                # s, contre le claquement a la coupe
# Entree du reel livre (bloc 1), voulue soignee par Romain (05/10/2026) : l'image arrive
# en zoom et floue puis se pose nette, un eclair blanc tres bref, la pastille du sujet
# (champ "badge" du script, sinon le label) s'ouvre au-dessus du premier texte avec un
# reflet qui la traverse. Le bandeau n'entre qu'au bloc 2. Aucun bruitage a l'entree.
OUVERTURE_ZOOM = 1.12
OUVERTURE_IMAGES = 14             # duree du recul, en images
OUVERTURE_FLOU = 18               # rayon du flou de depart
OUVERTURE_NET = 0.35              # s : flou -> net
OUVERTURE_ECLAIR = 0.22           # opacite de l'eclair blanc
OUVERTURE_ECLAIR_DUREE = 0.25     # s
OUVERTURE_BADGE_DELAI = 0.05      # s
OUVERTURE_TEXTE_DELAI = 0.18      # s : le premier texte laisse la pastille s'ouvrir
OUVERTURE_REFLET = (0.55, 0.5)    # debut et duree du reflet sur la pastille, s
OUVERTURE_REFLET_ALPHA = 120
# coup de zoom a l'entree des phrases fortes (au lieu de l'impulsion des autres plans)
PHRASE_ZOOM, PHRASE_IMAGES = 1.08, 10

LIEN = "lecercledesgeneralistes.fr"
MENTION = "Images d\u2019illustration"

# ------------------------------------------------------------------- son
# Voix off de synthese ElevenLabs (decidee le 01/10/2026) : elle pilote le rythme du reel
# (lcdg/voix.py). Un script sans texte lu sort muet. Musique et bruitages : Romain les
# posait lui-meme (21/09/2026) ; depuis le 01/10/2026, il veut sa musique (assets/audio,
# non versionnee) sous la voix et des bruitages cales sur le motion (lcdg/son.py).
# « Romain de Marseille » (01/10/2026) laissait entendre les respirations : ecartee.
# Les indications de jeu entre crochets ([curious], [thoughtful]...) passent dans le texte
# lu (modele v3).
#
# Quatre voix (Romain, 02/10/2026) : un homme et une femme plus ages, un homme et une
# femme jeunes, a choisir selon le theme, la gravite et l'urgence du sujet (CLAUDE.md).
# "voix_off" dans le script prend une de ces cles (ou un dict id / modele / reglages).
# Compte ElevenLabs gratuit : 3 emplacements ; Guillaume vient de la bibliotheque et n'en
# prend pas. Une voix sans id n'est pas encore enregistree dans l'espace de Romain.
VOIX_CATALOGUE = {
    # posee, documentaire ; « la voix du gars est super » (reel Franchises)
    "homme_age": {"nom": "Guillaume, documentaire (v3)", "id": "3HZyQcLKlT0a3RDeXVsP",
                  "modele": "eleven_v3"},
    # creee le 01/10 ; « ca fait jeune » ; silences un peu bruites a la creation (-27 dB)
    "homme_jeune": {"nom": "LCDG homme 2 (creee), jeune", "id": "Dgpg0WcilBNRm5h3jupj",
                    "modele": "eleven_v3"},
    # creee le 02/10 (essai F40_3, « top ») : 40 ans, petillante, chaleureuse. Le 05/10,
    # Romain y entend « de la resonance, comme dans un bocal en verre » : des zones etroites
    # qui sonnent, a une frequence differente a chaque generation (2,9 kHz, puis 4 kHz).
    # "anti_resonance" les mesure sur chaque narration et les rabote (lcdg/resonance.py).
    "femme_agee": {"nom": "LCDG femme 40 ans (creee)", "id": "qSjNKhS5SxoMSi5a8f7j",
                   "modele": "eleven_v3", "anti_resonance": True},
    # creee le 02/10 (essai F23_1) : 23 ans, petillante ; enregistree le 02/10
    "femme_jeune": {"nom": "LCDG femme 23 ans (creee)", "id": "g46Ltvy4v0xVIHvbT0Fi",
                    "modele": "eleven_v3"},
}
# anti-resonance (lcdg/resonance.py) : bosses du spectre de la parole, mesurees en dB
# au-dessus du spectre lisse sur une octave ; la voix de Guillaume n'en a pas au-dela de 4,5
VOIX_RESONANCE_BANDE = (1500, 5000)   # Hz : la zone ou l'oreille entend le « bocal »
VOIX_RESONANCE_SEUIL = 4.0            # dB : une bosse plus haute est rabotee...
VOIX_RESONANCE_CIBLE = 1.5            # ...jusqu'a ce niveau
VOIX_RESONANCE_GAIN_MAX = 6.0         # dB, coupe maximale d'un filtre
VOIX_RESONANCE_Q = 4
VOIX_RESONANCE_MAX_FILTRES = 4
VOIX_ID = "3HZyQcLKlT0a3RDeXVsP"
VOIX_MODELE = "eleven_v3"       # "voix_off.modele" dans le script le remplace
# v3 ignore le reglage de vitesse et joue plus lentement : on accelere la voix au montage,
# sans changer sa hauteur (atempo), et l'horodatage suit
VOIX_TEMPO_V3 = 1.05           # 1.0 = rythme naturel ; la duree n'est pas une contrainte (Romain, 01/10)
VOIX_STABILITE, VOIX_SIMILARITE, VOIX_STYLE = 0.5, 0.75, 0.0
VOIX_VITESSE = 1.05
VOIX_DEBUT = 0.25              # la voix demarre avec l'accroche
VOIX_AVANCE = 0.12             # la coupe precede de peu la phrase qu'elle introduit
VOIX_TENUE = 0.5               # apres la derniere phrase, avant la croix
VOIX_LUFS = -16                # voix seule : laisse de la place a la musique posee ensuite
VOIX_LUFS_TOLERANCE = 1.5
VOIX_TP_CIBLE = -1.5           # vise au mixage
VOIX_TP_PLAFOND = -1.0         # controle sur le fichier livre
# Correction d'une phrase d'un reel deja valide (scripts/revoix.py, 05/10/2026) : seuls les
# blocs modifies sont relus, puis colles dans l'ancienne narration, au silence entre deux
# phrases et au niveau de l'ancienne lecture
VOIX_RACCORD_PAS = 0.01        # s : finesse de la recherche du silence
VOIX_RACCORD_GARDE = 0.02      # s : le raccord ne mord jamais sur une phrase
VOIX_RACCORD_FONDU = 0.01      # s : de part et d'autre du raccord, contre les clics
VOIX_RACCORD_ECART_MAX = 6.0   # dB : au-dela, les deux lectures sont trop differentes

# Musique de fond et bruitages (01/10/2026 : Romain revient sur sa decision du 21/09 et
# veut un fond sonore « attrayant », avec des sons sur le motion). lcdg/son.py.
MUSIQUE_DEFAUT = "echo-sax-no4.mp3"   # dans assets/audio ; "musique": false la retire
MUSIQUE_LUFS = -27             # avant compression : environ 13 dB sous la voix
MUSIQUE_DUCKING = "threshold=0.03:ratio=4:attack=30:release=400"
MUSIQUE_FONDU_IN = 0.6
MUSIQUE_FONDU_OUT = 3.0        # la musique s'eteint avec la croix et la carte finale
# niveau de chaque bruitage, en dB sous son propre sommet : presents mais jamais
# au-dessus de la voix
SFX_GAINS = {"souffle": -20, "clic": -22, "compteur": -24, "impact": -17,
             "transition": -15, "carillon": -18}
IMPACT_COMPTE = 0.8            # l'impact tombe quand le compteur se pose
SON_LUFS = -14                 # mixage final (voix + musique + bruitages), cible Instagram
SON_TP_CIBLE = -1.5
SON_TP_PLAFOND = -1.0

# --------------------------------------------------------------- B-roll
BROLL_ZOOM = 1.06              # zoom lent sur la duree du plan
# deux plans Pexels du meme auteur a moins de cet ecart de numero viennent du meme
# tournage (registre.meme_tournage) ; mesure sur le registre du 02/10/2026
TOURNAGE_ECART = 60000
# Page officielle a l'ecran (scripts/page.py, 02/10/2026) : capture 1280 px CSS a l'echelle
# 1,5 (1920 px), vue en diagonale, adresse lisible PAGE_ADRESSE_S secondes, voile leger.
# Valeurs validees par Romain sur le reel Franchises (version « B »).
PAGE_LARGEUR_CSS, PAGE_HAUTEUR_CSS, PAGE_ECHELLE = 1280, 6000, 1.5
PAGE_BARRE_H = 150             # barre d'adresse, en px de la capture
PAGE_FENETRE_H = 1700          # hauteur de page visible a la fois, en px de la capture
PAGE_QUAD = [(-40, 640), (1180, 340), (1300, 1940), (-200, 2520)]   # coins de la page a l'ecran
PAGE_ADRESSE_S = 2.0
PAGE_VOILE = 0.26
PAGE_FLOU_PROFONDEUR = 5
PAGE_FLOU_PHOTO = 22           # photo ou visage de la page (--flou)
PAGE_FOND = (12, 18, 32)
# capture refusee (scripts/page.py) : verification anti-robots, page vide ou blanche. On
# ne contourne jamais un blocage : on montre une autre page officielle, ou Romain filme.
PAGE_SIGNES_BLOCAGE = ("verify you are human", "verifying you are human", "just a moment",
                       "access denied", "accès refusé", "pardon our interruption",
                       "you have been blocked", "êtes-vous un robot", "vérification de sécurité",
                       "captcha")
PAGE_MOTS_MIN = 80             # moins de mots visibles : page vide ou en erreur
PAGE_MOTS_BLOCAGE = 400        # un signe de blocage ne compte que sur une page courte
PAGE_CONTRASTE_MIN = 8         # ecart-type des gris : en dessous, capture blanche

# Plan en pleine largeur (bloc "cadrage": "largeur") : un plan paysage sous la 4K, ou
# dont l'enseigne serait coupee par un recadrage 9:16, se pose sous le logo et le credit,
# sur son propre fond floute (02/10/2026) ; le haut du plan reste au-dessus de l'accroche
PLAN_LARGEUR_Y = 470            # juste sous le logo
PLAN_LARGEUR_FLOU = 40
PLAN_LARGEUR_LUMIERE = -0.03
BROLL_MARGE_S = 0.4            # on entre dans le plan apres ce delai
# Le zoom lent emet une image par image de la source, a FPS : un plan tourne a 24 ou 25 i/s
# defile un peu plus vite et dure moins longtemps que sa source. S'il ne couvre plus son
# bloc, ses images sont dupliquees pour qu'il le couvre (05/10/2026 : deux plans trop courts
# decalaient l'image de 1,7 s et 2,6 s sur la voix, sans erreur)
BROLL_IMAGES_MARGE = 2         # images en plus de la duree du bloc
BROLL_VITESSE_MIN = 0.8        # en dessous, le ralenti se voit : render previent
BROLL_TOLERANCE_IMAGES = 1.5   # un plan plus court que son bloc de plus que ca : render s'arrete
# v2 : a chaque coupe, l'image se pose (leger recul en 8 images) en meme temps que
# le texte arrive ; un etalonnage commun unifie des plans venus de sources differentes.
IMPULSION = 1.05
IMPULSION_IMAGES = 8
# 02/10/2026 : plus lumineux et plus chaud (etait contrast=1.05:saturation=0.86:
# brightness=-0.012, ombres bleutees, vignette 0.55) : le reel paraissait sombre.
ETALONNAGE = ("eq=contrast=1.03:saturation=0.98:brightness=0.02,"
              "colorbalance=rm=0.012:rh=0.01:bs=-0.008,"
              "vignette=angle=0.32")
