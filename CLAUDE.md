# Instructions pour Claude Code

Ce dépôt produit les reels vidéo du Cercle des Généralistes à partir de la revue
hebdomadaire. Tourne sur Windows et macOS.

## La règle qui prime sur toutes les autres

**Le gabarit visuel et sonore est figé.** Il a été validé écran par écran. Les valeurs
vivent dans `config/charte.py` et nulle part ailleurs.

- Ne modifie jamais une constante de `config/charte.py` sans demande explicite.
- Ne code jamais une valeur en dur dans `lcdg/`. Une taille de logo écrite en dur dans
  le script de rendu a déjà écrasé la charte pendant quatre corrections successives,
  sans que ça se voie sur les aperçus.
- Ne juge jamais un rendu sur un aperçu généré à part. `lcdg/controles.py` mesure le
  fichier de sortie ; c'est la seule vérification qui compte.

## Ton rôle

Tu fais l'éditorial. Le montage est déterministe et ne t'appartient pas.

### 1. Écrire le script d'un épisode

À partir de l'article de la revue, tu produis `episodes/<date>-<slug>/script.json`.
Prends `episodes/exemple/script.json` comme modèle.

**Choix du sujet.** La revue contient quatre dossiers. Tu en retiens un seul, celui qui
ferait s'arrêter un médecin généraliste dans son fil. Le critère n'est pas le nombre de
vues potentielles : un sujet à double lecture grand public (restes à charge, régime sans
gluten) ramène une audience non convertible et pollue le signal du pixel Meta. Une
technicité qui filtre le grand public est un avantage, pas un défaut.

**Structure.** Un bloc d'intro sans texte, puis sept à huit blocs. Durée totale visée
50 à 55 s. Une idée par bloc, phrases courtes, registre journalistique.

**Surlignage.** Un segment par bloc, encadré d'astérisques : `*22 juillet*`. Choisis
le fait, pas l'adjectif : une date, un nom de texte, une institution, une condition.
Jamais deux segments dans le même bloc.

**Ponctuation.** Le moteur de texte gère la ponctuation collée et impose un retour à la
ligne à chaque fin de phrase. N'ajoute pas de retours manuels.

**Requêtes B-roll.** En anglais, l'index de Pexels y est bien meilleur. Registre visuel :
solitude, procédure, institution. Jamais d'image de violence, de sourire de banque
d'images, ni de mise en scène médicale trop léchée.

**Musique.** `relaxation-04` pour un sujet grave, `lofi-05` pour un sujet plus factuel.
`python -c "from lcdg import audio; print(audio.suggerer('news'))"` classe les lits
disponibles selon leurs mesures.

### 2. Lancer les deux étapes

```
python scripts/doctor.py                      # après un clone, ou en cas de doute
python scripts/smoke_test.py                  # après toute modification de lcdg/ ou de la charte
python scripts/prepare.py episodes/<dossier>  # récupère les B-rolls, ne monte rien
python scripts/render.py  episodes/<dossier>  # monte, mixe, contrôle
python scripts/render_carre.py episodes/<dossier>  # déclinaison carrée LinkedIn
```

Après `prepare`, **arrête-toi**. Montre à Romain `planche_broll.jpg` et l'aperçu
musical, et attends sa validation avant de lancer `render`. C'est une étape de son
processus, pas une formalité.

Si un plan ne convient pas : `broll/alternatives.json` contient les autres candidats
Pexels par bloc. Remplace le fichier `B<n>.mp4` et relance `render` seul.

### 3. Ce que tu ne fais pas

- Tu ne rejoues pas `render` pour « voir ce que ça donne » : chaque passe prend
  plusieurs minutes de CPU.
- Tu ne modifies pas `lcdg/habillage.py` pour un ajustement ponctuel. Si un réglage
  revient, il remonte dans `config/charte.py`.
- Tu ne pousses jamais sans avoir lancé `scripts/smoke_test.py`.
- Tu ne récupères pas d'audio en ligne. La bibliothèque est locale, dans
  `assets/audio/`, décrite par `config/audio_manifest.json`.

## Points de vigilance connus

**Zone sûre 4:5.** Le reel reste en 9:16, mais le fil Instagram et Facebook le
recadre en 4:5 au centre. Tout ce qui doit rester lisible tient entre y 285 et 1635
(`ZONE_SURE_HAUT`, `ZONE_SURE_BAS`). `render` refuse de monter un bloc qui en déborde :
au-delà de cinq lignes, raccourcis le texte plutôt que de toucher à la charte.

**Mixkit n'a pas d'API.** Les fichiers audio sont téléchargés une fois à la main depuis
le compte de Romain. C'est aussi ce qui enregistre la licence et débloque la clearance
Content ID chez Meta. Ne tente pas de les récupérer automatiquement.

**Pexels et les formats paysage.** Un plan paysage sous 4K devient mou une fois recadré
en 9:16. `prepare` le signale, prends l'avertissement au sérieux.

**Durée du rendu.** Comptez cinq à sept minutes selon la machine. C'est normal :
l'habillage est composé image par image, environ 1600 images en 1080x1920.
