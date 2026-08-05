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

Il te dira ce qui manque. À ce stade, il doit tout valider **sauf** la bibliothèque
audio.

## 1.5 La bibliothèque audio

`doctor` liste huit fichiers avec leur titre exact et le lien de la catégorie Mixkit.
Télécharge-les depuis ton compte Mixkit et dépose-les dans `assets/audio/` **sous le
nom exact indiqué** (par exemple `relaxation-04.mp3`, pas le nom d'origine du
téléchargement).

Ils ne sont pas dans le dépôt : la licence Mixkit autorise l'usage commercial sans
attribution mais interdit la redistribution des fichiers. Le téléchargement officiel
depuis ton compte est aussi ce qui enregistre la licence et débloque la clearance
Content ID chez Meta.

Relance `doctor` : il doit afficher **prêt**.

## 1.6 Test final

```bash
python scripts/smoke_test.py
```

Deux à trois minutes. Il monte un épisode de trois plans à partir de mires générées,
sans clé Pexels ni B-roll, et doit finir sur `[OK] chaine de montage conforme`.

Si ça passe, la machine est opérationnelle.

## 1.7 Facultatif : le linter

Claude Code a signalé qu'aucun linter n'est installé. Pour compléter les vérifications
avant un futur commit :

```bash
pip install pyflakes
python -m pyflakes lcdg config scripts
```

---

# 2. Produire un épisode

## 2.1 Le déroulé

Ouvre Claude Code **dans le dossier du dépôt** et donne-lui la revue de la semaine.
Un prompt qui marche :

> Voici la revue de cette semaine. Lis CLAUDE.md, choisis le sujet et écris le script
> dans un nouveau dossier d'épisode. Montre-le-moi avant de lancer prepare.

Il lit `CLAUDE.md`, qui contient les règles éditoriales, et produit
`episodes/AAAA-MM-JJ-slug/script.json`.

## 2.2 Premier contrôle : le script

**C'est ton moment le plus important.** Ouvre le `script.json` et vérifie :

- **Le sujet.** Un seul dossier sur les quatre de la revue. Le bon critère est
  « est-ce qu'un généraliste s'arrête ? », pas « est-ce que ça fait des vues ». Un
  sujet à double lecture grand public (restes à charge, régime sans gluten) ramène une
  audience non convertible et pollue le signal du pixel Meta.
- **Les blocs.** Sept à huit, une idée chacun, phrases courtes.
- **Les surlignages.** Un segment par bloc, entre astérisques. Ça doit tomber sur un
  fait (une date, un nom de texte, une institution), pas sur un adjectif.
- **Les requêtes B-roll.** En anglais. Registre : solitude, procédure, institution.
  Jamais d'image de violence ni de sourire de banque d'images.
- **La musique.** `relaxation-04` pour un sujet grave, `lofi-05` pour un sujet
  factuel.

Corrige directement dans le fichier, ou demande-lui de corriger.

## 2.3 Récupération des plans

```bash
python scripts/prepare.py episodes/AAAA-MM-JJ-slug
```

Trois à quatre minutes. Il interroge Pexels, télécharge les neuf plans, fabrique
`planche_broll.jpg` et un extrait de 25 secondes du lit musical.

## 2.4 Deuxième contrôle : les plans et le son

Ouvre `planche_broll.jpg` : une vignette par plan, avec la requête et le texte qui
ira dessus. Écoute l'extrait musical.

**Pour changer un plan**, ouvre `broll/alternatives.json` : il contient trois autres
candidats Pexels par bloc, avec leur lien. Télécharge celui que tu veux et remplace
`broll/B<n>.mp4`. Tu peux aussi y mettre n'importe quelle vidéo à toi, du moment
qu'elle porte le bon nom.

**Prends au sérieux l'avertissement** « paysage sous 4K » s'il apparaît : ce plan sera
mou une fois recadré en vertical. Change-le.

## 2.5 Montage

```bash
python scripts/render.py episodes/AAAA-MM-JJ-slug
```

Six à sept minutes. Il finit sur le bilan de contrôle :

```
  OK   logo (hauteur)     122 px    (attendu 124 ±8)
  OK   filet (largeur)     21 px    (attendu 20 ±3)
  OK   loudness          -13.9 LUFS
  OK   true peak          -2.9 dBTP
  OK   ecretage           crete 0.93
  -> conforme
```

Le fichier est dans le dossier de l'épisode, sous `reel_<slug>.mp4`. Tu peux publier.

## 2.6 Temps réel

Vingt à vingt-cinq minutes au total, dont une dizaine seulement demandent ton
attention. Le reste tourne pendant que tu fais autre chose.

---

# 3. Dépannage

| Message | Cause | Solution |
|---|---|---|
| `python n'est pas reconnu` (Windows) | Python absent du PATH | Réinstaller en cochant *Add Python to PATH*, rouvrir le terminal |
| `command not found: python` (Mac) | Sur Mac c'est `python3` | Utiliser `python3`, ou activer le venv |
| `[!] Introuvable : ffmpeg, ffprobe` | ffmpeg pas installé, ou terminal pas rouvert | Réinstaller, **fermer et rouvrir le terminal**. Si installé ailleurs, définir `FFMPEG_BIN` et `FFPROBE_BIN` dans `.env` |
| `ModuleNotFoundError: No module named 'PIL'` | venv pas activé | `.venv\Scripts\activate` (Win) ou `source .venv/bin/activate` (Mac) |
| `[!] PEXELS_API_KEY absente` | `.env` manquant ou vide | Copier `.env.example` en `.env` et renseigner la clé |
| `[!] Fichier audio manquant` | Bibliothèque incomplète | `python scripts/doctor.py` pour la liste, déposer dans `assets/audio/` |
| `AUCUN resultat pour « ... »` | Requête Pexels trop précise ou trop française | Reformuler en anglais, plus générique. Modifier `script.json` et relancer `prepare` |
| `ffmpeg s'est arrete pendant le rendu` | Disque plein, ou `base.mp4` corrompu | Libérer de l'espace (compte 2 Go par épisode), supprimer `base.mp4` et `segments/`, relancer |
| `ECHEC logo (hauteur)` | Une valeur codée en dur écrase la charte | Ne pas publier. Vérifier que `lcdg/` n'a pas été modifié, relancer `smoke_test.py` |
| `ECHEC loudness` ou `true peak` | Mixage hors norme | Ne pas publier. Vérifier que le fichier musique n'est pas corrompu |
| `ECHEC ecretage` | Saturation audio | Ne pas publier. Le plus souvent un fichier audio remplacé par une version plus forte |

**Règle générale** : si un contrôle échoue, `render` sort en code 2 et affiche
`NON CONFORME`. Ne publie pas. C'est fait pour t'avertir avant, pas après.

---

# 4. Modifier la chaîne

## 4.1 Changer un réglage visuel ou sonore

Tout est dans `config/charte.py`, et nulle part ailleurs. Taille du logo, largeur du
filet, couleurs, graisses, positions, volumes, cible de loudness.

Après toute modification :

```bash
python scripts/smoke_test.py
```

Deux minutes, et tu sais si tu as cassé quelque chose.

**Ne modifie jamais une valeur directement dans `lcdg/`.** C'est exactement le bug qui
a coûté une heure pendant la conception : une taille de logo écrite en dur dans le
script de rendu écrasait la charte, les aperçus montraient la bonne taille, la vidéo
non, et l'erreur a survécu à quatre corrections. Les contrôles automatiques existent
pour ça.

## 4.2 Ajouter une musique

Télécharge la piste depuis Mixkit, dépose-la dans `assets/audio/` sous un nom en
minuscules avec tirets, puis ajoute une entrée dans `config/audio_manifest.json` :

```json
{
  "cle": "nouveau-titre",
  "titre": "Nouveau Titre",
  "fichier": "nouveau-titre.mp3",
  "source": "Mixkit",
  "registre": "news",
  "url_page": "https://mixkit.co/free-stock-music/...",
  "mixkit_id": "1234",
  "mesures": null
}
```

Laisse `mesures` à `null`, le code les calcule au besoin. Pour voir comment elle se
situe :

```bash
python -c "import sys; sys.path.insert(0,'.'); from lcdg import audio; print(audio.suggerer('news'))"
```

Le classement repose sur trois mesures : l'amplitude sur 60 secondes (plus c'est plat,
mieux ça porte le texte), le centroïde spectral (la brillance) et le nombre d'attaques
par seconde (une nappe figée sonne funèbre, une nappe qui avance porte la lecture).

## 4.3 Changer la couleur selon la rubrique

`script.json` porte un champ `rubrique`. Les valeurs possibles sont dans
`config/charte.py`, section `RUBRIQUES` : `pro`, `politique`, `clinique`, `numerique`,
`patient`. Le bandeau et le surlignage prennent la couleur correspondante, reprise du
thème du site.

## 4.4 Après toute modification du code

```bash
python scripts/smoke_test.py     # doit finir sur [OK]
python -m pyflakes lcdg config scripts
git add . && git commit -m "..." && git push
```

---

# 5. Ce que fait chaque fichier

```
config/charte.py            toutes les constantes du gabarit
config/audio_manifest.json  bibliothèque audio et mesures acoustiques

lcdg/binaires.py            localise ffmpeg sur Windows, macOS et Linux
lcdg/logo.py                détoure le logo et compose le lockup Montserrat
lcdg/habillage.py           intro, blocs de texte, transition en croix, carte finale
lcdg/pexels.py              client de l'API Pexels
lcdg/audio.py               sélection et analyse acoustique
lcdg/montage.py             base vidéo, rendu image par image, mixage
lcdg/controles.py           mesures sur le fichier de sortie

scripts/doctor.py           vérifie que la machine est prête
scripts/prepare.py          récupère les plans, prépare la validation
scripts/render.py           monte, mixe, contrôle
scripts/smoke_test.py       test de bout en bout sans Pexels ni B-roll

episodes/exemple/           modèle de script.json
CLAUDE.md                   règles pour Claude Code
```

---

# 6. Le gabarit, pour mémoire

| | |
|---|---|
| Format | 1080x1920, 30 fps, 50 à 55 s |
| Couleurs | `#047bbf`, `#1b1046` — reprises du thème du site |
| Typographie | Montserrat, embarquée dans le dépôt |
| Logo | 124 px de haut, en haut à droite |
| Filet | rectangle blanc de 20 px, angles vifs |
| Texte | Bold 58, contour bleu 3 px à 232 d'opacité |
| Surlignage | fond `#047bbf`, mot en blanc sans contour |
| Entrée des blocs | glissement de 150 px depuis la gauche, 0,42 s |
| Fin | ouverture en croix médicale, logo, slogan, lien |
| Son | lit à 33 %, bois sec sur 4 respirations, −14 LUFS, −2 dBTP |
