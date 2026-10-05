# Manuel — chaîne de production des reels LCDG

Tout ce qu'il faut pour installer, produire et dépanner, sur Windows comme sur macOS.
Ce document est fait pour être suivi seul.

---

# 1. Installation

À faire une fois par machine. Compte trente minutes la première fois.

## 1.1 Windows

**Python.** Ouvre PowerShell et tape :

```powershell
python --version
```

Il faut 3.10 ou plus. Si la commande n'est pas reconnue, installe Python depuis
python.org en cochant **Add Python to PATH** pendant l'installation, puis rouvre
PowerShell.

**ffmpeg.**

```powershell
winget install Gyan.FFmpeg
```

**Ferme et rouvre PowerShell**, sinon le PATH n'est pas rechargé. Vérifie :

```powershell
ffmpeg -version
```

**Le dépôt.**

```powershell
cd $HOME\tools
git clone https://github.com/Rompomepome/lcdg-reel.git
cd lcdg-reel
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Si PowerShell refuse d'activer le venv avec une erreur d'exécution de scripts :

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Puis réessaie l'activation.

## 1.2 macOS

**Homebrew et ffmpeg.**

```bash
brew install ffmpeg
ffmpeg -version
```

**Le dépôt.** Le dépôt est privé, il faut donc être authentifié. Le plus simple :

```bash
gh auth login          # une fois, choisir le compte Rompomepome
cd ~/tools
gh repo clone Rompomepome/lcdg-reel
cd lcdg-reel
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Sur Mac, la commande est `python3`, pas `python`. Une fois le venv activé, `python`
fonctionne aussi.

## 1.3 La clé Pexels

Récupère une clé gratuite sur https://www.pexels.com/api/ (200 requêtes par heure,
largement suffisant : un épisode en consomme neuf).

Copie `.env.example` en `.env` et renseigne la clé :

```
PEXELS_API_KEY=ta_cle_ici
```

Le fichier `.env` n'est jamais versionné, il reste sur ta machine.

## 1.4 Vérification

```bash
python scripts/doctor.py
```

Il te dira ce qui manque, et doit finir sur **prêt**.

## 1.5 Test final

```bash
python scripts/smoke_test.py
```

Une minute environ. Il monte un épisode de cinq plans à partir de mires générées, sans
clé Pexels ni B-roll, avec tous les types de blocs, et doit finir sur
`[OK] chaine de montage conforme`.

Si ça passe, la machine est opérationnelle.

## 1.6 Facultatif : le linter

Pour compléter les vérifications avant un futur commit :

```bash
pip install pyflakes
python -m pyflakes lcdg config scripts
```

---

# 2. Produire un épisode

## 2.1 Le déroulé

Ouvre Claude Code **dans le dossier du dépôt** et donne-lui l'article ou la revue de la
semaine. Un prompt qui marche :

> Voici l'article. Lis CLAUDE.md et écris le script dans un nouveau dossier d'épisode,
> au format du reel exemple. Montre-le-moi avant de lancer prepare.

Il lit `CLAUDE.md`, qui contient la méthode d'écriture, et produit
`episodes/AAAA-MM-JJ-slug/script.json`. Le modèle est `episodes/exemple/script.json` :
le reel « Franchises médicales » du 01/10/2026.

## 2.2 Premier contrôle : le script

**C'est ton moment le plus important.** Le style est dans l'outil ; le rythme et
l'accroche, eux, sont dans le script. Vérifie :

- **L'accroche** (`sous_titre`). C'est l'image de couverture : elle n'apparaît pas dans la
  vidéo, qui commence au premier fait (bloc 1). Elle parle au médecin (« vos patients »,
  « votre ordonnance ») et pose un enjeu : une perte, une injustice, une erreur à éviter. Si
  elle ressemble au titre de l'article, elle est à refaire.
- **Les mots.** Des mots qu'on dit, compris en une seconde : « et si c'est plus long que
  prévu ? », pas « si la date glisse ».
- **La porte d'entrée.** Le reel donne les faits et ouvre les questions de « Ce qui pose
  question », mais **ne donne pas la solution** : tes lecteurs viennent la chercher sur
  le site. Si le reel livre la recommandation du Cercle, il supprime la raison de cliquer.
- **La chute et la promesse.** L'avant-dernier plan fait réagir ; le dernier promet ce que
  l'article donne (« Que faire au cabinet ? Le Cercle fait 2 recommandations. »).
- **L'appel** (champ `appel`) : il nomme ce que l'article donne (« Nos 2
  recommandations : »). Une ligne. La carte finale ajoute « Inscription gratuite · lien en
  bio » (« … lien dans le post » sur la version carrée).
- **La voix** (champ `voix_off`) : l'une des quatre voix, selon le thème et la gravité
  (voir `CLAUDE.md`).
- **L'exactitude.** Chaque phrase se retrouve dans l'article. Un « jusqu'à » ou un
  « environ » ne disparaît pas.
- **La densité.** Trois lignes au plus par écran. Un `|` coupe un texte en deux temps.
- **Les surlignages.** Un segment par écran, entre astérisques, sur un fait.
- **Les chiffres** (`"type": "chiffre"`) et **phrases fortes** (`"type": "phrase"`) :
  deux ou trois de chaque, pas plus.

Corrige directement dans le fichier, ou demande-lui de corriger.

## 2.3 Récupération des plans

```bash
python scripts/prepare.py episodes/AAAA-MM-JJ-slug
```

Il interroge Pexels, télécharge un premier plan par bloc en écartant ceux déjà montés
dans un autre reel, et fabrique `planche_broll.jpg`.

## 2.4 Deuxième contrôle : les plans

Le premier candidat est rarement le bon. Pour un bloc, cherche avec plusieurs requêtes,
puis choisis sur la planche :

```bash
python scripts/broll.py chercher episodes/AAAA-MM-JJ-slug 3 "nurse home visit elderly" "blood pressure at home"
python scripts/broll.py choisir  episodes/AAAA-MM-JJ-slug 3 C8
```

La planche est dans `broll/candidats/3.jpg`. Un plan marqué **DEJA PRIS** a servi dans
un autre reel ; **TOURNAGE VU**, il vient du même tournage qu'un plan déjà monté (mêmes
acteurs, même décor) : le public le reconnaîtrait. `choisir` les refuse de toute façon.
Ajoute `--paysage` (plans paysage 4K) ou `--mixte` (les deux) quand les plans verticaux
manquent.

Quand le texte cite un décret ou une institution qu'on ne peut pas filmer, montre sa vraie
page : `python scripts/page.py capturer ...` puis `monter ...` (voir le README).

Quand tous les plans sont choisis :

```bash
python scripts/broll.py revue episodes/AAAA-MM-JJ-slug
```

Ouvre `revue_plans.jpg` : début, milieu et fin de chaque plan, recadrés comme au
montage. Une vignette Pexels ment souvent sur ce que montre le plan deux secondes plus
tard.

Tu peux aussi mettre n'importe quelle vidéo à toi dans `broll/`, du moment qu'elle porte
le bon nom (`B<n>.mp4`). **Prends au sérieux l'avertissement** « paysage sous 4K » : ce
plan sera mou une fois recadré en vertical.

## 2.5 Montage

```bash
python scripts/render.py episodes/AAAA-MM-JJ-slug
python scripts/render_carre.py episodes/AAAA-MM-JJ-slug
```

Trois à cinq minutes chacun. Avant de rendre la moindre image, `render` vérifie que
chaque texte et chaque insert tiennent dans la zone sûre ; sinon il s'arrête et dit lequel
raccourcir. Il finit sur le bilan de contrôle :

```
  OK   logo (hauteur)         122 px (attendu 124 px ±8)
  OK   logo (position)        331 px (attendu 329 px ±8)
  OK   hors zone 4:5 (fin)    0 px (attendu 0 px ±0)
  OK   pistes audio           1 (attendu 1 ±0)
  OK   son (loudness)         -14.1 LUFS (attendu -14 LUFS ±1.5)
  OK   son (true peak)        -1.4 dBTP (plafond -1.0 dBTP)
  OK   surlignages            8/8
  -> conforme
```

Dans le dossier de l'épisode :

- `reel_<slug>.mp4` : le reel 9:16, voix, musique et bruitages mixés. Il commence au
  premier fait : l'accroche est coupée, elle sert de couverture.
- `couverture_<slug>.jpg` (9:16) et `couverture_<slug>_4x5.jpg` : l'image à choisir comme
  couverture, accroche en place.
- `voix_<slug>.wav` : la voix seule, si tu veux remonter le son toi-même.
- `reel_<slug>_carre.mp4` et `couverture_<slug>_carre.jpg` : la version LinkedIn.
- `legendes.md` (écrit par Claude Code) : les textes Instagram, Facebook et LinkedIn.

**À la publication sur Instagram et Facebook**, active l'étiquette « Info IA » (paramètres
avancés) : Meta impose de déclarer une voix de synthèse réaliste, et peut pénaliser un
oubli.

## 2.6 Temps réel

Une vingtaine de minutes au total, dont l'essentiel pour relire le script et choisir les
plans. Les rendus tournent pendant que tu fais autre chose.

---

# 3. Dépannage

| Message | Cause | Solution |
|---|---|---|
| `python n'est pas reconnu` (Windows) | Python absent du PATH | Réinstaller en cochant *Add Python to PATH*, rouvrir le terminal |
| `command not found: python` (Mac) | Sur Mac c'est `python3` | Utiliser `python3`, ou activer le venv |
| `[!] Introuvable : ffmpeg, ffprobe` | ffmpeg pas installé, ou terminal pas rouvert | Réinstaller, **fermer et rouvrir le terminal**. Si installé ailleurs, définir `FFMPEG_BIN` et `FFPROBE_BIN` dans `.env` |
| `ModuleNotFoundError: No module named 'PIL'` | venv pas activé | Activer le venv (voir 1.1 ou 1.2) |
| `[!] PEXELS_API_KEY absente` | `.env` manquant ou vide | Copier `.env.example` en `.env` et renseigner la clé |
| `AUCUN resultat pour « ... »` | Requête Pexels trop précise ou trop française | Reformuler en anglais, plus générique. Ou `broll.py chercher` avec d'autres requêtes |
| `[!] Hors de la zone sure 4:5` | Un texte ou un surlignage trop long | Raccourcir le texte, couper en deux temps avec `\|`, ou surligner moins de mots |
| `[!] plan ... deja utilise` | Le plan a servi dans un autre reel | Choisir un autre candidat |
| `ffmpeg s'est arrete pendant le rendu` | Disque plein, ou `base.mp4` corrompu | Libérer de l'espace (compte 2 Go par épisode), supprimer `base.mp4` et `segments/`, relancer |
| `ECHEC logo (hauteur)` | Une valeur codée en dur écrase la charte | Ne pas publier. Vérifier que `lcdg/` n'a pas été modifié, relancer `smoke_test.py` |
| `ECHEC surlignages` | Un texte n'est pas à sa place, ou pas dessiné, sur la vidéo livrée | Ne pas publier. Vérifier que `lcdg/` n'a pas été modifié, relancer `smoke_test.py` |
| `ECHEC pistes audio` ou `son` | Piste absente, en double ou à un mauvais niveau | Ne pas publier. Vérifier `ELEVENLABS_API_KEY`, le champ `voix` des blocs et `assets/audio`, relancer `smoke_test.py` |
| `[!] pas la place pour l'insert` | Le texte du bloc est trop haut pour l'insert | Raccourcir le texte du bloc, ou retirer l'insert |
| `[!] voix_off inconnue` ou `pas encore enregistree` | Clé de voix absente du catalogue, ou voix pas dans l'espace ElevenLabs | Choisir une des quatre voix de `charte.VOIX_CATALOGUE` |
| `ElevenLabs a refuse la generation` | Clé invalide ou quota mensuel épuisé | Vérifier la clé dans `.env` et le quota sur elevenlabs.io |

**Règle générale** : si un contrôle échoue, `render` sort en code 2 et affiche
`NON CONFORME`. Ne publie pas. C'est fait pour t'avertir avant, pas après.

---

# 4. Modifier la chaîne

## 4.1 Changer un réglage visuel

Tout est dans `config/charte.py`, et nulle part ailleurs : tailles, graisses,
couleurs, positions, vitesses d'animation, voile, flou, pictogrammes. Les valeurs de la
version carrée sont dans le dictionnaire `CARRE`.

Après toute modification :

```bash
python scripts/smoke_test.py
```

Une minute, et tu sais si tu as cassé quelque chose.

**Ne modifie jamais une valeur directement dans `lcdg/`.** C'est exactement le bug qui
a coûté une heure pendant la conception : une taille de logo écrite en dur dans le
script de rendu écrasait la charte, les aperçus montraient la bonne taille, la vidéo
non, et l'erreur a survécu à quatre corrections. Les contrôles automatiques existent
pour ça.

## 4.2 Changer la couleur selon la rubrique

`script.json` porte un champ `rubrique`. Les valeurs possibles sont dans
`config/charte.py`, section `RUBRIQUES` : `pro`, `politique`, `clinique`, `numerique`,
`patient`. La pastille, les surlignages, les unités des chiffres et le lien final
prennent la couleur correspondante, reprise du thème du site.

## 4.3 Après toute modification du code

```bash
python scripts/smoke_test.py     # doit finir sur [OK]
python -m pyflakes lcdg config scripts
git add . && git commit -m "..." && git push
```

---

# 5. Ce que fait chaque fichier

```
config/charte.py               toutes les constantes du gabarit
episodes/plans_utilises.json   registre des plans Pexels déjà montés

lcdg/binaires.py               localise ffmpeg sur Windows, macOS et Linux
lcdg/logo.py                   détoure le logo et compose le lockup Montserrat
lcdg/texte.py                  mise en page et animation du texte
lcdg/habillage.py              accroche, entrée animée, blocs, chiffres, bandeau, croix, carte finale
lcdg/inserts.py                inserts animés (cadenas, calendrier, barres, oui/non, tampon)
lcdg/voix.py                   voix off ElevenLabs, calage du reel sur la narration
lcdg/resonance.py              correction de la résonance d'une voix
lcdg/son.py                    mixage voix, musique et bruitages
lcdg/pexels.py                 client de l'API Pexels
lcdg/registre.py               registre des plans utilisés et de leurs tournages
lcdg/montage.py                base vidéo, rendu image par image, sortie, couvertures
lcdg/controles.py              mesures sur le fichier de sortie

scripts/doctor.py              vérifie que la machine est prête
scripts/prepare.py             premiers plans, planche contact
scripts/broll.py               chercher, choisir et contrôler les plans
scripts/page.py                capturer une page officielle et la monter en plan
scripts/render.py              monte, contrôle, sort les couvertures, coupe l'accroche
scripts/render_carre.py        déclinaison carrée LinkedIn
scripts/smoke_test.py          test de bout en bout sans Pexels ni B-roll

episodes/exemple/              modèle de script.json (le reel Franchises)
CLAUDE.md                      méthode d'écriture et règles pour Claude Code
```

---

# 6. Le gabarit, pour mémoire

| | |
|---|---|
| Format | 1080x1920, 30 fps, une minute environ (la voix fixe la durée) ; carré 1080x1080 pour LinkedIn |
| Zone sûre | 4:5 centrée (y 285 à 1635) : logo, textes et carte finale y tiennent, le fil Instagram et Facebook recadre le reel sans rien couper |
| Couleurs | `#047bbf`, `#1b1046` et les couleurs de rubrique, reprises du thème du site |
| Typographie | Montserrat, embarquée dans le dépôt, travaillée comme les titres du site |
| Logo | 124 px de haut, en haut à droite de la zone sûre |
| Accroche | couverture seulement : pastille du sujet, phrase ExtraBold 92, voile sur l'image |
| Entrée | image qui arrive floue et se pose, éclair bref, pastille `badge` avec un reflet |
| Texte | Bold 66, ombre douce, 3 lignes au plus ; segment clé en ExtraBold, surligné au feutre |
| Chiffres | ExtraBold 230, valeur barrée, compteur, pictogrammes, fond flouté |
| Animation | mots posés un par un, inserts animés, sortie vers le haut ; l'image se pose à chaque coupe |
| Fin | ouverture en croix médicale, logo, appel à l'action, lien |
| Son | voix off ElevenLabs (quatre voix), musique atténuée sous la voix, bruitages sur le motion, −14 LUFS |
