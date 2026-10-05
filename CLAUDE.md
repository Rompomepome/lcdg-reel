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
tranchante, jamais fausse. Chaque phrase dit explicitement de quoi elle
parle : « vos patients vont payer plus » ne suffit pas, il faut « paieront jusqu'à 40 € de
plus par an » et le dispositif (les franchises). Une formule vague ou approximative est une
erreur de fond, pas un effet de style : c'est un média pour médecins (Romain, 01/10/2026). Lis l'article en entier : il est réservé aux membres pendant
14 jours, passe par le compte de Romain ou par le PDF de la revue.

**Des mots qu'on dit.** Le reel s'écoute et se lit en une seconde : on doit être compris
presque instantanément (Romain, 05/10/2026). Pas de tournure d'écrit ou de communiqué :
« si la date glisse » devient « et si c'est plus long que prévu ? », « contingentée »
devient « les livraisons sont limitées », « une prévision fondée sur » devient « c'est ce
que prévoient », « présente un épisode dépressif » devient « fait un épisode dépressif ».
Pas de « or », de « car », de « dans la limite de » dans le texte lu. Le terme technique
reste quand il est exact et que les médecins le disent (épisode dépressif, ALD) ; sinon,
la phrase simple qui dit la même chose. Relis chaque phrase à voix haute.

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
  le reel a gardé (« Nos 2 recommandations : »). Une ligne, une trentaine de caractères.
- **Le bandeau** (champ `bandeau`) invite à commenter un mot clé pour recevoir l'analyse :
  « Pour recevoir l'analyse, | commentez *140* ». Un mot court et propre au sujet (un
  chiffre du reel, par exemple). Il s'efface tout seul le temps d'un bloc qui entrerait
  dans sa zone.
- **Jamais de piège à clic** : chaque promesse est tenue par l'article.

**La structure** (voir l'exemple) :

1. **Accroche** (bloc 0, champ `sous_titre`, 5 à 9 mots) : **c'est l'image de couverture,
   pas le début du reel** (Romain, 02/10/2026). Le bloc 0 n'a pas de voix ; il est rendu
   le temps d'exporter la couverture (9:16, 4:5 et 1:1), puis coupé
   (`charte.ACCROCHE_COUVERTURE`). Elle parle au médecin (« vos patients », « votre
   ordonnance ») et pose un enjeu : une perte, une injustice, une erreur à éviter, un
   chiffre qui surprend. Jamais le titre de l'article. Le champ `label` est la pastille
   au-dessus : le sujet en 2 à 4 mots. Son plan est l'image de couverture : net, lumineux,
   lisible en vignette.
2. **Les faits**, deux ou trois plans, en chiffres de préférence. **Le reel livré commence
   ici** : le bloc 1 ouvre sur un fait fort, dit et écrit (« Depuis le 1er octobre, … »).
   L'entrée est animée (Romain, 05/10/2026 : « c'est l'entrée qu'il faut soigner ») :
   l'image arrive en zoom et floue puis se pose nette, un éclair blanc très bref, et la
   pastille du champ `badge` (2 à 4 mots : « Tension d'approvisionnement », « Nouveau
   remboursement », « Pharmacovigilance · ANSM ») s'ouvre au-dessus du premier texte, un
   reflet la traverse. Le bandeau n'entre qu'au bloc 2. Aucun bruitage à l'entrée.
3. **La bascule** vers les questions, en phrase forte (« Et une question reste sans
   réponse. »), puis **la question** elle-même et pourquoi elle compte.
4. **L'enjeu** : le vrai risque, en phrase forte.
5. **La chute**, qui fait réagir sans trahir l'article (« 140 €, ce n'est qu'un point de
   départ. »).
6. **La promesse**, au dernier plan, juste avant la carte finale : c'est elle qui fait
   cliquer (« Que faire au cabinet ? | Le Cercle fait 2 recommandations. »). Elle ne
   promet que ce que l'article contient : le Cercle ne propose pas de « parade ».

**Le ton.** Grave sur les faits, jamais sombre : le reel décrypte et donne envie d'en
savoir plus, il n'inquiète pas pour inquiéter. Les mots de l'article plutôt que les
formules qui dramatisent (« un point de départ, pas un maximum » plutôt que « ce n'est
qu'un début »).

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

**Les inserts** (champ `insert` d'un bloc de texte, `lcdg/inserts.py`) : une petite
illustration animée au-dessus du texte, pour comprendre d'un coup d'œil (Romain,
05/10/2026 : « les inserts et les illustrations en plus, ça aide à la compréhension »).
Deux ou trois par reel, là où ils éclairent le propos, jamais en décor :

- `{"type": "verrou", "n": 3}` : les recommandations gardées pour le site, en cartes
  fermées d'un cadenas, sur le dernier bloc (« Le Cercle fait 3 recommandations »).
- `{"type": "calendrier", "annee": 2026, "mois": 10, "du": 12, "au": 18, "legende":
  "mi-octobre"}` : une date ou une période (sur une même semaine).
- `{"type": "barres", "unite": "×", "lignes": [{"label": "Sans désogestrel", "valeur": 1},
  ...]}` : comparer des valeurs ; une première ligne à ×1 sert de référence (grise).
- `{"type": "choix", "lignes": [{"label": "En pharmacie", "ok": true}, ...]}` : oui / non.
- `{"type": "tampon", "texte": "Export interdit", "temps": 1}` : une interdiction.

`"temps"` fait arriver un élément avec le temps du texte de ce numéro (0 = début du
bloc). Un insert n'invente rien : il dit ce que dit le texte, avec les mots de l'article.
`render` refuse un insert sans place au-dessus du texte.

**Surlignage.** Un segment par temps, entre astérisques : le fait, pas l'adjectif. Il ne
se coupe jamais, donc il reste court : une vingtaine de caractères dans un texte, une
quinzaine dans une accroche ou une phrase forte. `render` refuse de monter un texte qui
déborde, avant les minutes de rendu.

**Durées.** 50 à 55 s au total, une dizaine de plans. Compte 2,6 mots par seconde, un
nombre vaut un mot et demi, et une seconde de plus par plan pour l'arrivée du texte. Un
chiffre clé tient 5 à 6 s.

**La voix off.** Chaque bloc porte son texte lu dans le champ `voix`, sauf le bloc 0
(couverture, sans voix). C'est la voix qui fixe la durée de chaque plan : le champ `duree` ne sert
plus qu'à vérifier la mise en page, et à un reel sans voix. Le texte lu peut être plus
développé que l'écran, mais dit la même chose dans le même ordre ; un `|` y marque
l'instant où le temps suivant de l'écran apparaît (autant de `|` qu'à l'écran). Nombres
en toutes lettres (« cent quarante euros »), sigles épelés avec des points (« A.L.D. »).
Compte 140 à 150 mots pour une cinquantaine de secondes. Le dernier plan dit où aller
(« on vous la détaille sur le site du Cercle ») sans « lien en bio » : la même voix sert à
LinkedIn. La première phrase lue (bloc 1) entre directement dans un fait : jamais le
libellé du sujet (« Franchises médicales : … », « Fluoxétine 20 mg : … »). Relis le texte lu comme une phrase dite
à voix haute : articles compris (« ni la fiche de Service Public », pas « ni Service
Public »).

Le champ `voix_off` prend une des quatre voix de `charte.VOIX_CATALOGUE` (Romain,
02/10/2026) : un homme et une femme plus âgés, un homme et une femme jeunes. On choisit
selon le thème, la gravité et l'urgence, et on alterne d'un reel à l'autre :

- `homme_age` (Guillaume, posé) : alertes de sécurité sanitaire, sujets graves ou
  réglementaires lourds.
- `femme_agee` (40 ans, chaleureuse) : prévention, santé des patientes, sujets qui
  demandent de l'empathie ; urgence pratique (rupture, contingentement) dite calmement.
- `homme_jeune` : organisation du cabinet, numérique, tarifs, bonnes nouvelles.
- `femme_jeune` (23 ans, pétillante) : sujets pratiques ou légers, jeunes patients,
  contraception, remboursements nouveaux.

Sans `voix_off`, c'est `charte.VOIX_ID`. Le compte ElevenLabs reste gratuit (Romain ne
paiera pas d'abonnement) : trois emplacements de voix ; Guillaume vient de la
bibliothèque et n'en prend pas. Les indications de jeu entre
crochets (v3) donnent le ton : `[curious]`, `[thoughtful]`, `[matter-of-fact]`, `[warm]` ;
`[serious]` et `[concerned]` se gardent pour les vrais sujets de gravité.
Une narration est générée une fois puis gardée en cache (`episodes/<dossier>/voix/`) :
changer une virgule du texte lu la régénère et consomme le quota ElevenLabs.

**Ponctuation.** Espace insécable (U+00A0) avant « : ? ! » et entre un nombre et son
unité (« 70 € »). Le moteur impose un retour à la ligne à chaque fin de phrase et
équilibre les lignes : n'ajoute pas de retours manuels.

**Requêtes B-roll.** En anglais, l'index de Pexels y est bien meilleur. Registre : le
quotidien du soin en lumière du jour (consultation, pharmacie, domicile éclairé, gestes du
soin), des patients actifs plutôt que fragiles. Le reel ne doit être ni sombre ni morbide
(Romain, 02/10/2026) : pas de personne âgée seule dans la pénombre, de pilulier dans le
noir, d'escalier dans l'ombre. Jamais d'image de violence, de sourire de banque d'images,
ni de mise en scène médicale trop léchée. Une image dit le sens du texte, jamais son
contraire (un escalator qui descend sous « les plafonds vont monter »). Sous un chiffre
clé, le fond est flouté : un plan calme suffit.

### 2. Choisir les plans

`prepare` télécharge le premier candidat de chaque requête, en écartant les plans déjà
montés dans un autre reel (`episodes/plans_utilises.json`). C'est un point de départ,
rarement le bon choix. Pour chaque plan :

```
python scripts/broll.py chercher episodes/<dossier> <bloc> [--paysage] "<requete 1>" "<requete 2>"
python scripts/broll.py choisir  episodes/<dossier> <bloc> C<n>
python scripts/broll.py tournages     # tournages vus dans plusieurs reels
```

**Jamais deux fois le même tournage.** Romain reconnaît une actrice ou un décor d'un reel
à l'autre (la même femme médecin, 02/10/2026). La planche marque en orange
(« TOURNAGE VU ») un plan du même auteur Pexels et du même tournage qu'un plan d'un autre
reel, et `choisir` le refuse. Le fonds médical vertical de Pexels est épuisé (cabinets,
pharmacies) : `--paysage` cherche des plans paysage 4K, recadrés au centre sans perte.
Préfère aussi les mains, les objets, les patients à domicile, moins reconnaissables
qu'un visage. La « pharmacie » de Pexels est un décor d'époque : Romain la refuse.

**Textes officiels et institutions sans lieu.** Quand le texte cite un décret, un arrêté,
une fiche ou une institution qu'on ne peut pas filmer (Service Public, Légifrance, ameli,
la HAS), le plan montre la vraie page officielle, capturée à l'écran (Romain, 02/10/2026) :
« Ni le décret ni la fiche de Service Public » ne se comprend pas sans elle. Romain a
retenu la présentation en diagonale, barre d'adresse lisible, voile léger :

```
python scripts/page.py capturer episodes/<dossier> <nom> "<url>"     # + <nom>_reperes.jpg
python scripts/page.py monter episodes/<dossier> <bloc> <nom> 0:1600 --colonne 392:1880 --flou x0,y0,x1,y1
```

Sur un téléphone, seuls l'adresse et le titre se lisent : montre la page en continu (un
passage qui remplit la fenêtre), pas des lignes isolées, et resserre la colonne pour
grossir le texte. Floute les photos de la page où l'on voit un visage. Légifrance bloque
les navigateurs automatiques (vérification anti-robots) : on ne la contourne pas, on
montre la page officielle qui cite le texte, ou Romain filme la page lui-même.

**Plans fournis.** De préférence des images dont LCDG a les droits : tournées par Romain
ou sous licence. Un extrait de reportage télé ou de réseau social expose à une réclamation
de droits : le dire à Romain, c'est sa décision (le 02/10/2026, il a choisi d'utiliser des
captures d'un reportage France 24 pour le reel Franchises, et pose lui-même le crédit). Dans
tous les cas : aucun visage visible (Romain, 02/10/2026) ; on écarte ou on recadre les
passages où l'on voit un visage, reflets compris, les personnes de dos restent ; on ne
retire jamais un filigrane (on écarte le passage) ; on rogne les incrustations du lecteur.
Un plan paysage sous la 4K, ou dont l'enseigne serait coupée en 9:16, se monte en pleine
largeur sur fond flou : `"cadrage": "largeur"` dans le bloc. Le champ `"credit"` affiche
la source sous le logo, si Romain le demande.

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
- **Tu ne changes pas la musique de toi-même.** Depuis le 01/10/2026, Romain veut sa
  musique (`charte.MUSIQUE_DEFAUT`, dans `assets/audio`, non versionnée) sous la voix,
  et des bruitages calés sur le motion (`lcdg/son.py`). Un contrôle vérifie qu'il n'y a
  qu'une piste audio, et son niveau.

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
