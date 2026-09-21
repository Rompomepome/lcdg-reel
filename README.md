# lcdg-reel

Chaîne de production des reels vidéo du **Cercle des Généralistes**.
Un article de la revue hebdomadaire en entrée, un reel 1080x1920 prêt à publier
sur Instagram, Facebook et LinkedIn en sortie.

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

### 4. La bibliothèque audio

```bash
python scripts/doctor.py
```

Le doctor liste les fichiers manquants avec leur titre exact et le lien Mixkit.
Télécharge-les depuis ton compte, dépose-les dans `assets/audio/` sous le nom indiqué.

Ils ne sont pas versionnés : la licence Mixkit autorise l'usage commercial sans
attribution mais interdit la redistribution des fichiers. Le téléchargement officiel
est aussi ce qui enregistre la licence et débloque la clearance Content ID chez Meta.

Une fois fait, `doctor` doit afficher **prêt**.

---

## Produire un épisode

```bash
mkdir episodes/2026-08-12-restes-a-charge
cp episodes/exemple/script.json episodes/2026-08-12-restes-a-charge/
```

Écris le script (ou demande-le à Claude Code, voir `CLAUDE.md`), puis :

```bash
python scripts/prepare.py episodes/2026-08-12-restes-a-charge
```

Regarde `planche_broll.jpg` et l'aperçu musical. Pour changer un plan, pioche dans
`broll/alternatives.json` ou remplace `B<n>.mp4` à la main. Quand ça te va :

```bash
python scripts/render.py episodes/2026-08-12-restes-a-charge
```

Le rendu prend cinq à sept minutes et se termine par un bilan de contrôle.

Pour LinkedIn, la déclinaison carrée 1080x1080 (mise en page `CARRE` de la charte) :

```bash
python scripts/render_carre.py episodes/2026-08-12-restes-a-charge
```

Elle sort `reel_<slug>_carre.mp4`, contrôlée comme le reel. Un plan composé pour le 9:16
(photo posée en bandeau au-dessus du texte) peut avoir sa version carrée dans
`broll_carre/`, sous le même nom : elle est alors prise à la place.

---

## Le gabarit

Toutes les valeurs sont dans `config/charte.py`, et nulle part ailleurs.

| | |
|---|---|
| Format | 1080x1920, 30 fps, 50 à 55 s |
| Zone sûre | 4:5 centrée (y 285 à 1635) : logo, textes et carte finale y tiennent, le fil Instagram et Facebook recadre le reel sans rien couper |
| Couleurs | `#047bbf`, `#036399`, `#1b1046` — reprises de `theme.css` du site |
| Typographie | Montserrat, embarquée dans le dépôt (licence OFL) |
| Logo | 124 px de haut, en haut à droite de la zone sûre |
| Filet | rectangle blanc de 20 px, angles vifs, pleine hauteur du bloc |
| Texte | Bold 58, contour bleu 3 px à 232 d'opacité, surlignage `#047bbf` |
| Entrée des blocs | glissement de 150 px depuis la gauche, 0,42 s |
| Fin | ouverture en croix médicale, puis logo, slogan et lien |
| Son | lit à 33 %, sans bruitage (coupés le 04/09/2026), −14 LUFS, true peak ≤ −1 dBTP |

## Test de fumée

```bash
python scripts/smoke_test.py
```

Monte un épisode de trois plans à partir de mires générées, sans clé Pexels ni B-roll,
et vérifie que les contrôles passent. Compte deux à trois minutes. À lancer après un
clone, après une modification de `config/charte.py`, et avant tout push touchant `lcdg/`.

Il a déjà servi : il a révélé que les contrôles échantillonnaient à des instants fixes,
ce qui plantait sur une vidéo courte, et que la fenêtre de mesure du filet supposait un
bloc de quatre lignes.

## Contrôles automatiques

`render` mesure le fichier de sortie et refuse de le déclarer conforme si un écart
apparaît : hauteur et position du logo, largeur du filet, rien hors de la zone sûre 4:5 sur la
carte finale, loudness intégrée, true peak (plafond −1 dBTP), écrêtage (canal par canal). Le code retour vaut 2 si un contrôle échoue.

Ces contrôles existent à cause d'un bug réel : une taille de logo codée en dur dans le
script de rendu écrasait la charte. Les aperçus montraient la bonne taille, la vidéo
non, et l'erreur a survécu à quatre corrections. On ne valide donc plus sur un aperçu.

## Structure

```
config/charte.py          toutes les constantes du gabarit
config/audio_manifest.json  bibliothèque audio et mesures acoustiques
lcdg/binaires.py          localisation de ffmpeg (Windows, macOS, Linux)
lcdg/logo.py              détourage du logo et composition du lockup
lcdg/habillage.py         intro, blocs, transition en croix, carte finale
lcdg/pexels.py            client API Pexels
lcdg/audio.py             sélection et analyse acoustique
lcdg/montage.py           base vidéo, rendu, mixage
lcdg/controles.py         mesures sur le fichier de sortie
scripts/                  doctor, prepare, render
episodes/                 un dossier par épisode
```

## Licences

Montserrat sous SIL Open Font License (`assets/fonts/OFL.txt`).
Vidéos Pexels : usage commercial libre, sans attribution.
Audio Mixkit : usage commercial libre sans attribution, redistribution interdite,
d'où l'exclusion des fichiers du dépôt.
