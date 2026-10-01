# Instructions pour Claude Code

Ce dépôt produit les reels vidéo du Cercle des Généralistes à partir de la revue
hebdomadaire. Tourne sur Windows et macOS.

## La règle qui prime sur toutes les autres

**Le gabarit visuel est figé.** Il a été validé écran par écran (style v2, validé par
Romain le 01/10/2026). Les valeurs vivent dans `config/charte.py` et nulle part ailleurs.

- Ne modifie jamais une constante de `config/charte.py` sans demande explicite.
- Ne code jamais une valeur en dur dans `lcdg/`. Une taille de logo écrite en dur dans
  le script de rendu a déjà écrasé la charte pendant quatre corrections successives,
  sans que ça se voie sur les aperçus.
- Ne juge jamais un rendu sur un aperçu généré à part. `lcdg/controles.py` mesure le
  fichier de sortie ; c'est la seule vérification qui compte.

## Ton rôle

Tu fais l'éditorial : le sujet, l'écriture, le choix des plans. Le montage est
déterministe et ne t'appartient pas. La qualité d'un reel se joue surtout ici : le
moteur donne le style, pas le rythme ni l'accroche.

### 1. Écrire le script d'un épisode

À partir de l'article, tu produis `episodes/<date>-<slug>/script.json`. Le modèle est
`episodes/exemple/script.json` : le reel « Franchises médicales », validé par Romain le
01/10/2026. C'est la référence de ton, de structure et de rythme.

**Choix du sujet.** Le critère est « est-ce qu'un généraliste s'arrête ? », pas le
nombre de vues potentielles : une audience grand public n'est pas convertible et pollue
le signal du pixel Meta. Un sujet à double lecture (restes à charge, régime sans gluten)
reste possible si l'angle est celui du médecin : ce qu'il change au cabinet, dans son
ordonnance, en consultation.

**Exactitude.** Chaque phrase doit se retrouver dans l'article. Un « jusqu'à », un
« environ », un « quand il existe » ne se simplifient pas : l'accroche peut être
tranchante, jamais fausse. Lis l'article en entier : il est réservé aux membres pendant
14 jours, passe par le compte de Romain ou par le PDF de la revue.

**Le reel est une porte d'entrée, pas un résumé.** Les lecteurs lisent la revue pour
tout ce qui suit « CE QUI POSE QUESTION » : les questions ouvertes, l'impact financier et
organisationnel, le regard du Cercle, les recommandations. C'est la valeur réservée aux
membres. Le reel doit donner envie de cliquer vers l'article, jamais dispenser de le lire.

- **On donne** les faits (Situation, Ce qui est confirmé) et un ou deux chiffres qui
  frappent : c'est ce qui rend le reel crédible et utile.
- **On ouvre** une ou deux vraies questions de « Ce qui pose question », formulées comme
  le médecin se les pose, et l'enjeu (le risque, l'injustice).
- **On garde** la solution et les recommandations. On les promet sans les livrer.
- **On finit** sur le champ `appel` du script, qui nomme ce que l'article donne et que
  le reel a gardé (« La parade, en détail : »). Une ligne, une trentaine de caractères.
- **Jamais de piège à clic** : chaque promesse est tenue par l'article.

**La structure** (voir l'exemple) :

1. **Accroche** (premier plan, champ `sous_titre`, 5 à 9 mots). Elle parle au médecin
   (« vos patients », « votre ordonnance ») et pose un enjeu : une perte, une injustice,
   une erreur à éviter, un chiffre qui surprend. Jamais le titre de l'article. Le champ
   `label` est la pastille au-dessus : le sujet et la date en 2 à 4 mots
   (« Franchises · 1er octobre »).
2. **Les faits**, deux ou trois plans, en chiffres de préférence.
3. **La bascule** vers les questions, en phrase forte (« Et une question reste sans
   réponse. »), puis **la question** elle-même et pourquoi elle compte.
4. **L'enjeu** : le vrai risque, en phrase forte.
5. **La chute**, qui fait réagir sans trahir l'article (« 140 €, ce n'est qu'un début. »).
6. **La promesse**, au dernier plan, juste avant la carte finale : c'est elle qui fait
   cliquer (« Il existe une parade. | Elle est dans votre ordonnance. »).

La légende de la publication porte la question qui fait commenter et le « lien en bio ».

**Les types de blocs.**

- Texte (par défaut) : champ `texte`. Un `|` le découpe en deux temps sur le même plan.
  Trois lignes au plus par temps, soit une soixantaine de caractères.
- `"type": "phrase"` : phrase forte, au corps de l'accroche, centrée. Deux ou trois par
  reel, pas plus : c'est un coup de poing, pas un style.
- `"type": "chiffre"` : le nombre défile jusqu'à `valeur`. `depuis` barre l'ancienne
  valeur, `suffixe` porte l'unité (« € », « boîtes »), `legende` se pose dessous.
  `"pictos": true` allume une boîte par unité (120 au plus) : à réserver aux quantités
  qu'on veut rendre tangibles. Deux ou trois chiffres par reel ; le fond est flouté.

**Surlignage.** Un segment par temps, entre astérisques : le fait, pas l'adjectif. Il ne
se coupe jamais, donc il reste court : une vingtaine de caractères dans un texte, une
quinzaine dans une accroche ou une phrase forte. `render` refuse de monter un texte qui
déborde, avant les minutes de rendu.

**Durées.** 50 à 55 s au total, une dizaine de plans. Compte 2,6 mots par seconde, un
nombre vaut un mot et demi, et une seconde de plus par plan pour l'arrivée du texte. Un
chiffre clé tient 5 à 6 s.

**Ponctuation.** Espace insécable (U+00A0) avant « : ? ! » et entre un nombre et son
unité (« 70 € »). Le moteur impose un retour à la ligne à chaque fin de phrase et
équilibre les lignes : n'ajoute pas de retours manuels.

**Requêtes B-roll.** En anglais, l'index de Pexels y est bien meilleur. Registre :
solitude, procédure, institution, gestes du soin. Jamais d'image de violence, de sourire
de banque d'images, ni de mise en scène médicale trop léchée. Sous un chiffre clé, le
fond est flouté : un plan calme suffit.

### 2. Choisir les plans

`prepare` télécharge le premier candidat de chaque requête, en écartant les plans déjà
montés dans un autre reel (`episodes/plans_utilises.json`). C'est un point de départ,
rarement le bon choix. Pour chaque plan :

```
python scripts/broll.py chercher episodes/<dossier> <bloc> "<requete 1>" "<requete 2>"
python scripts/broll.py choisir  episodes/<dossier> <bloc> C<n>
```

Puis `python scripts/broll.py revue episodes/<dossier>` : début, milieu et fin de la
portion utilisée de chaque plan, recadrés comme au montage. Une vignette Pexels ment
souvent sur ce que montre le plan deux secondes plus tard.

Si aucun candidat n'est fort, ne te contente pas d'un plan moyen : décris à Romain la
scène exacte dont tu as besoin, il fournit l'image.

### 3. Lancer les étapes

```
python scripts/doctor.py                           # après un clone, ou en cas de doute
python scripts/smoke_test.py                       # après toute modification de lcdg/ ou de la charte
python scripts/prepare.py episodes/<dossier>       # premiers plans, planche contact
python scripts/broll.py revue episodes/<dossier>   # controle des plans retenus
python scripts/render.py  episodes/<dossier>       # reel 9:16 + couverture, controles
python scripts/render_carre.py episodes/<dossier>  # declinaison carree LinkedIn
```

Après la revue des plans, **arrête-toi**. Montre à Romain le script et
`revue_plans.jpg`, et attends sa validation avant de lancer `render`. C'est une étape de
son processus, pas une formalité.

### 4. Ce que tu ne fais pas

- Tu ne rejoues pas `render` pour « voir ce que ça donne ». La mise en page se vérifie
  d'abord : `render` refuse un texte hors zone avant de rendre la moindre image.
- Tu ne modifies pas `lcdg/` pour un ajustement ponctuel. Si un réglage revient, il
  remonte dans `config/charte.py`.
- Tu ne pousses jamais sans avoir lancé `scripts/smoke_test.py`.
- **Tu n'ajoutes ni musique ni bruitage.** Romain pose la musique lui-même. Le reel sort
  sans piste audio, et un contrôle le vérifie. Une voix off de synthèse est décidée
  (01/10/2026) mais pas encore intégrée.

## Points de vigilance connus

**Zone sûre 4:5.** Le reel reste en 9:16, mais le fil Instagram et Facebook le
recadre en 4:5 au centre. Tout ce qui doit rester lisible tient entre y 285 et 1635
(`ZONE_SURE_HAUT`, `ZONE_SURE_BAS`), et les textes dans leur colonne, à l'écart des
boutons de l'onglet Reels. `render` refuse de monter un bloc qui en déborde : raccourcis
le texte ou le surlignage plutôt que de toucher à la charte.

**Version carrée.** `render_carre` applique `charte.CARRE` : chiffres et pictogrammes y
sont plus petits, et la zone sûre s'arrête 40 px avant chaque bord, sinon un élément
rogné au bord du cadre ne serait jamais détecté.

**Pexels et les formats paysage.** Un plan paysage sous 4K devient mou une fois recadré
en 9:16. `prepare` et `broll.py chercher` le signalent, prends l'avertissement au sérieux.

**Durée du rendu.** Deux à trois minutes par version. L'habillage est composé image par
image, environ 1600 images en 1080x1920.
