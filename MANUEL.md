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

- **L'accroche** (`sous_titre`). Elle parle au médecin (« vos patients », « votre
  ordonnance ») et pose un enjeu : une perte, une injustice, une erreur à éviter. Si elle
  ressemble au titre de l'article, elle est à refaire.
- **La porte d'entrée.** Le reel donne les faits et ouvre les questions de « Ce qui pose
  question », mais **ne donne pas la solution** : tes lecteurs viennent la chercher sur
  le site. Si le reel livre la recommandation du Cercle, il supprime la raison de cliquer.
- **La chute et la promesse.** L'avant-dernier plan fait réagir ; le dernier promet ce que
  l'article donne (« Il existe une parade. Elle est dans votre ordonnance. »).
- **L'appel** (champ `appel`) : il nomme ce que l'article donne (« La parade, en
  détail : »). Une ligne. La carte finale ajoute « Inscription gratuite · lien en bio »
  (« … lien dans le post » sur la version carrée).
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
un autre reel : le public le reconnaîtrait. `choisir` le refuse de toute façon.

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

Deux à trois minutes chacun. Avant de rendre la moindre image, `render` vérifie que
chaque texte tient dans la zone sûre ; sinon il s'arrête et dit lequel raccourcir. Il
finit sur le bilan de contrôle :

```
  OK   logo (hauteur)         122 px (attendu 124 px ±8)
  OK   logo (position)        331 px (attendu 329 px ±8)
  OK   hors zone 4:5 (fin)    0 px (attendu 0 px ±0)
  OK   pistes audio           0 (attendu 0 ±0)
  OK   surlignages            9/9
  -> conforme
```

Dans le dossier de l'épisode :

- `reel_<slug>.mp4` : le reel 9:16, sans son. Pose ta musique au montage final.
- `couverture_<slug>.jpg` : l'image à choisir comme couverture, accroche en place.
- `reel_<slug>_carre.mp4` et `couverture_<slug>_carre.jpg` : la version LinkedIn.

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
| `ECHEC pistes audio` | Une piste son s'est glissée dans la sortie | Ne pas publier. Relancer `smoke_test.py` et signaler le problème |

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
lcdg/habillage.py              accroche, blocs, chiffres, transition en croix, carte finale
lcdg/pexels.py                 client de l'API Pexels
lcdg/registre.py               registre des plans utilisés
lcdg/montage.py                base vidéo, rendu image par image, sortie, couverture
lcdg/controles.py              mesures sur le fichier de sortie

scripts/doctor.py              vérifie que la machine est prête
scripts/prepare.py             premiers plans, planche contact
scripts/broll.py               chercher, choisir et contrôler les plans
scripts/render.py              monte, contrôle, sort la couverture
scripts/render_carre.py        déclinaison carrée LinkedIn
scripts/smoke_test.py          test de bout en bout sans Pexels ni B-roll

episodes/exemple/              modèle de script.json (le reel Franchises)
CLAUDE.md                      méthode d'écriture et règles pour Claude Code
```

---

# 6. Le gabarit, pour mémoire

| | |
|---|---|
| Format | 1080x1920, 30 fps, 50 à 55 s ; carré 1080x1080 pour LinkedIn |
| Zone sûre | 4:5 centrée (y 285 à 1635) : logo, textes et carte finale y tiennent, le fil Instagram et Facebook recadre le reel sans rien couper |
| Couleurs | `#047bbf`, `#1b1046` et les couleurs de rubrique, reprises du thème du site |
| Typographie | Montserrat, embarquée dans le dépôt, travaillée comme les titres du site |
| Logo | 124 px de haut, en haut à droite de la zone sûre |
| Accroche | pastille du sujet, phrase ExtraBold 92, voile sur l'image |
| Texte | Bold 66, ombre douce, 3 lignes au plus ; segment clé en ExtraBold, surligné au feutre |
| Chiffres | ExtraBold 230, valeur barrée, compteur, pictogrammes, fond flouté |
| Animation | mots posés un par un, sortie vers le haut ; l'image se pose à chaque coupe |
| Fin | ouverture en croix médicale, logo, appel à l'action, lien |
| Son | aucun : la musique est posée au montage final |
