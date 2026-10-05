# lcdg-reel

Chaîne de production des reels vidéo du **Cercle des Généralistes**.
Un article de la revue hebdomadaire en entrée, un reel 1080x1920 prêt à publier
sur Instagram, Facebook et LinkedIn en sortie, avec sa couverture et sa version carrée.

Fonctionne sur Windows et macOS.

Pour l'installation pas à pas, le déroulé hebdomadaire et le dépannage, voir
[MANUEL.md](MANUEL.md).

---

## Installation

### 1. ffmpeg

| Système | Commande |
|---|---|
| Windows | `winget install Gyan.FFmpeg` (ou `choco install ffmpeg`) |
| macOS | `brew install ffmpeg` |

Ferme et rouvre le terminal après l'installation, pour que le PATH soit rechargé.

### 2. Le dépôt

```bash
git clone https://github.com/<toi>/lcdg-reel.git
cd lcdg-reel
python -m venv .venv
```

Puis, selon la machine :

```bash
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS
pip install -r requirements.txt
```

### 3. La clé Pexels

Copie `.env.example` en `.env` et renseigne `PEXELS_API_KEY`.
La clé est gratuite sur https://www.pexels.com/api/ (200 requêtes par heure).

### 4. La clé ElevenLabs (voix off)

Renseigne aussi `ELEVENLABS_API_KEY` dans `.env`. Les quatre voix du reel (un homme et une
femme plus âgés, un homme et une femme jeunes) sont dans `charte.VOIX_CATALOGUE`. Sans texte
lu dans le script, le reel sort sans voix.

### 5. La musique et les bruitages

La musique de fond (`charte.MUSIQUE_DEFAUT`) se pose dans `assets/audio/`, les bruitages du
motion dans `assets/sfx/` (`souffle`, `clic`, `compteur`, `impact`, `transition`,
`carillon`, en mp3). Ces dossiers ne sont pas versionnés : s'ils manquent, le reel sort
avec la seule voix.

```bash
python scripts/doctor.py
```

Le doctor doit afficher **prêt**.

---

## Produire un épisode

```bash
mkdir episodes/2026-10-05-mon-sujet
cp episodes/exemple/script.json episodes/2026-10-05-mon-sujet/
```

Écris le script (ou demande-le à Claude Code, voir `CLAUDE.md`), puis :

```bash
python scripts/prepare.py episodes/2026-10-05-mon-sujet
```

`prepare` télécharge un premier plan Pexels par bloc, en écartant ceux déjà montés dans
un autre reel. Pour en changer, puis contrôler chaque plan sur toute sa durée :

```bash
python scripts/broll.py chercher episodes/2026-10-05-mon-sujet 3 "doctor writing prescription"
python scripts/broll.py choisir  episodes/2026-10-05-mon-sujet 3 C4
python scripts/broll.py revue    episodes/2026-10-05-mon-sujet
```

Quand `revue_plans.jpg` te va :

```bash
python scripts/render.py episodes/2026-10-05-mon-sujet
python scripts/render_carre.py episodes/2026-10-05-mon-sujet
```

Chaque rendu prend trois à cinq minutes et se termine par un bilan de contrôle. Il sort
`reel_<slug>.mp4` (voix, musique et bruitages mixés), les couvertures `couverture_<slug>.jpg`
(9:16) et `couverture_<slug>_4x5.jpg`, et `voix_<slug>.wav`, la voix seule ; `render_carre`
sort les versions `_carre` pour LinkedIn. L'accroche ne sert qu'à la couverture : elle est
coupée de la vidéo, qui commence au premier fait.

Quand un texte cite un décret ou une institution qu'on ne peut pas filmer (Service Public,
ANSM...), on montre sa vraie page, capturée puis montée en diagonale :

```bash
python scripts/page.py capturer episodes/2026-10-05-mon-sujet ansm "https://ansm.sante.fr/..."
python scripts/page.py monter   episodes/2026-10-05-mon-sujet 2 ansm 0:1600 --colonne 392:1880
```
Un plan composé pour le 9:16 (photo posée en bandeau au-dessus du texte) peut avoir sa
version carrée dans `broll_carre/`, sous le même nom : elle est alors prise à la place.

---

## Le script

`episodes/exemple/script.json` est le modèle de référence. Trois types de blocs :

| Type | Champs | À l'écran |
|---|---|---|
| texte (défaut) | `texte` ; `\|` découpe en deux temps | mots posés un par un, segment `*surligné*` tracé au feutre |
| `phrase` | `texte` | phrase forte, au corps de l'accroche, centrée |
| `chiffre` | `valeur`, `depuis`, `suffixe`, `pictos`, `legende` | le nombre défile, l'ancienne valeur est barrée, une boîte s'allume par unité, fond flouté |

Le premier bloc porte l'accroche de la couverture (`label` pour la pastille, `sous_titre`
pour la phrase), sans voix. `badge` est la pastille de l'entrée animée du reel, `voix_off`
la voix choisie, `bandeau` l'invitation à commenter un mot clé. Un bloc de texte peut porter
un `insert` animé (`verrou`, `calendrier`, `barres`, `choix`, `tampon`). Le champ `appel`
donne l'appel à l'action de la carte finale (« Nos 2 recommandations : ») ; le reel est une
porte d'entrée vers l'analyse, il garde la solution pour le site (voir `CLAUDE.md`).

---

## Le gabarit

Toutes les valeurs sont dans `config/charte.py`, et nulle part ailleurs.

| | |
|---|---|
| Format | 1080x1920, 30 fps, une minute environ (la voix fixe la durée) ; carré 1080x1080 pour LinkedIn |
| Zone sûre | 4:5 centrée (y 285 à 1635) : le fil Instagram et Facebook recadre le reel sans rien couper |
| Couleurs | `#047bbf`, `#1b1046` et les couleurs de rubrique, reprises du thème du site |
| Typographie | Montserrat (comme les titres du site), interlettrage resserré, lignes équilibrées, ombre douce |
| Texte | Bold 66, segment clé en ExtraBold surligné ; accroche et phrases fortes ExtraBold 92 |
| Animation | entrée animée (pastille, image qui se pose), mots posés un par un, surlignage tracé, inserts animés, sortie vers le haut |
| Image | étalonnage commun, lumineux ; voile léger sous l'accroche, flou de profondeur sous les chiffres |
| Logo | 124 px de haut, en haut à droite de la zone sûre |
| Fin | ouverture en croix médicale, puis logo et appel à l'action vers le site |
| Son | voix off ElevenLabs, qui fixe le rythme ; musique atténuée sous la voix, bruitages calés sur le motion (jamais à l'ouverture) ; −14 LUFS |

## Test de fumée

```bash
python scripts/smoke_test.py
```

Monte un épisode de cinq plans à partir de mires générées, sans clé Pexels ni B-roll,
avec tous les types de blocs, et vérifie que les contrôles passent. Compte une minute.
À lancer après un clone, après une modification de `config/charte.py`, et avant tout
push touchant `lcdg/`.

## Contrôles automatiques

Avant le rendu, `render` vérifie que chaque texte tient dans la zone sûre et dans sa
colonne, et refuse de démarrer sinon. Après le rendu, il mesure le fichier de sortie :
hauteur et position du logo, chaque surlignage présent là où son texte doit être posé,
rien hors de la zone sûre sur la carte finale, une seule piste audio, au niveau de la charte.
Le code retour vaut
2 si un contrôle échoue.

Ces contrôles existent à cause d'un bug réel : une taille de logo codée en dur dans le
script de rendu écrasait la charte. Les aperçus montraient la bonne taille, la vidéo
non, et l'erreur a survécu à quatre corrections. On ne valide donc plus sur un aperçu.

## Structure

```
config/charte.py           toutes les constantes du gabarit
episodes/plans_utilises.json  registre des plans Pexels déjà montés (jamais deux fois)
lcdg/binaires.py           localisation de ffmpeg (Windows, macOS, Linux)
lcdg/logo.py               détourage du logo et composition du lockup
lcdg/texte.py              mise en page et animation du texte
lcdg/habillage.py          accroche, entrée animée, blocs, chiffres, bandeau, croix, carte finale
lcdg/inserts.py            inserts animés (cadenas, calendrier, barres, oui/non, tampon)
lcdg/voix.py               voix off ElevenLabs, calage du reel sur la narration
lcdg/resonance.py          correction de la résonance d'une voix
lcdg/son.py                mixage voix, musique et bruitages
lcdg/pexels.py             client API Pexels
lcdg/registre.py           registre des plans utilisés (et des tournages)
lcdg/montage.py            base vidéo, rendu, sortie, couvertures, coupe de l'accroche
lcdg/controles.py          mesures sur le fichier de sortie
scripts/                   doctor, prepare, broll, page, render, render_carre, smoke_test
episodes/                  un dossier par épisode
```

## Licences

Montserrat sous SIL Open Font License (`assets/fonts/OFL.txt`).
Vidéos Pexels : usage commercial libre, sans attribution.
