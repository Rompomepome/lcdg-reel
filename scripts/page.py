"""
Plan d'une page web officielle (Service Public, ANSM, ameli...) : quand le texte cite un
decret, une fiche ou une institution qu'on ne peut pas filmer, on montre sa vraie page
(Romain, 02/10/2026).

    python scripts/page.py capturer episodes/<dossier> <nom> "<url>"
    python scripts/page.py monter   episodes/<dossier> <bloc> <nom> <y0>:<y1> [<y0>:<y1> ...]
                                    [--colonne x0:x1] [--flou x0,y0,x1,y1 ...] [--duree 10]

capturer : episodes/<dossier>/pages/<nom>.png, la page rendue par Chrome sans interface
           (1920 px de large), et <nom>_reperes.jpg, la meme page graduee en y pour choisir
           les passages a montrer. Une page protegee contre les robots (Legifrance) n'est pas
           contournee : on montre une page officielle qui cite le texte, ou Romain la filme.
monter   : broll/B<bloc>.mp4 (1080x1920) : la barre d'adresse puis les passages choisis
           (en px de la capture), empiles, defilent sur la page vue en diagonale, sous un
           voile leger ; la page se floute au loin et sous les sous-titres. Sur un telephone,
           seuls le titre de la page et l'adresse se lisent : le corps du texte fait decor,
           il remplit la fenetre (montre la page en continu, pas des lignes isolees).
           --colonne ecarte marges et menus lateraux, le texte grossit ; --flou masque une
           photo ou un visage de la page (coordonnees de la capture). Le plan s'inscrit au
           registre des plans (episodes/plans_utilises.json).
"""
import sys
# la console Windows est en cp1252 par defaut
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import html
import json
import os
import re
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import charte as C
from lcdg import binaires as B, registre
from lcdg.logo import police

NAVIGATEURS = [
    os.environ.get("CHROME_BIN", ""),
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
]


def navigateur() -> str:
    for n in NAVIGATEURS:
        if n and Path(n).exists():
            return n
    raise SystemExit("[!] Chrome ou Edge introuvable : renseigne CHROME_BIN dans .env.")


def lisse(t):
    t = min(1.0, max(0.0, t))
    return t * t * (3 - 2 * t)


# ---------------------------------------------------------------- capturer
def texte_page(url):
    """(titre, texte visible) de la page rendue par le navigateur."""
    dom = subprocess.run([navigateur(), "--headless=new", "--disable-gpu", "--no-first-run",
                          "--virtual-time-budget=9000", "--dump-dom", url],
                         capture_output=True, timeout=180).stdout.decode("utf-8", "replace")
    m = re.search(r"<title[^>]*>(.*?)</title>", dom, re.S | re.I)
    titre = html.unescape(re.sub(r"\s+", " ", m.group(1))).strip() if m else ""
    corps = re.sub(r"<(script|style|noscript)[\s\S]*?</\1>", " ", dom, flags=re.I)
    texte = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", corps))).strip()
    return titre, texte


def capturer(dossier, nom, url):
    episode = Path(dossier).resolve()
    pages = episode / "pages"
    pages.mkdir(parents=True, exist_ok=True)
    png = pages / f"{nom}.png"
    png.unlink(missing_ok=True)                  # jamais une ancienne capture sous une autre adresse
    r = subprocess.run([navigateur(), "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        "--no-first-run", f"--window-size={C.PAGE_LARGEUR_CSS},{C.PAGE_HAUTEUR_CSS}",
                        f"--force-device-scale-factor={C.PAGE_ECHELLE}", "--virtual-time-budget=9000",
                        f"--screenshot={png}", url], capture_output=True, timeout=180)
    if r.returncode != 0 or not png.exists():
        raise SystemExit(f"[!] capture impossible (code {r.returncode}) : {url}")
    # une verification anti-robots, une page d'erreur ou une page blanche ne se montent pas
    titre, texte = texte_page(url)
    mots = len(texte.split())
    signe = next((s for s in C.PAGE_SIGNES_BLOCAGE if s in texte.lower()), None)
    gris = np.asarray(Image.open(png).convert("L"), dtype=float)
    if (mots < C.PAGE_MOTS_MIN or (signe and mots < C.PAGE_MOTS_BLOCAGE)
            or gris.std() < C.PAGE_CONTRASTE_MIN):
        png.unlink(missing_ok=True)
        raise SystemExit(f"[!] page bloquee, vide ou en erreur ({mots} mots"
                         + (f", « {signe} »" if signe else "") + f", titre « {titre} ») : {url}\n"
                         "    On ne contourne pas un blocage : montre une autre page officielle qui "
                         "cite le texte, ou demande a Romain de filmer la page.")
    (pages / f"{nom}.json").write_text(json.dumps({"url": url, "titre": titre}, ensure_ascii=False),
                                       encoding="utf-8")
    print(f"titre de la page : {titre} ({mots} mots)")
    im = Image.open(png).convert("RGB")
    # reperes : la page en colonnes, graduee tous les 250 px de la capture
    pas, col_h, larg = 250, 2250, 480
    k = larg / im.width
    cols = (im.height + col_h - 1) // col_h
    rep = Image.new("RGB", (cols * (larg + 60), int(col_h * k) + 10), "white")
    d = ImageDraw.Draw(rep)
    f = police(13, "SemiBold")
    for c in range(cols):
        x = c * (larg + 60) + 55
        part = im.crop((0, c * col_h, im.width, min(im.height, (c + 1) * col_h)))
        rep.paste(part.resize((larg, int(part.height * k))), (x, 5))
        for y in range(c * col_h, min(im.height, (c + 1) * col_h), pas):
            yy = 5 + int((y - c * col_h) * k)
            d.line([(x - 8, yy), (x + larg, yy)], fill=(230, 60, 60), width=1)
            d.text((x - 52, yy - 7), str(y), font=f, fill=(230, 60, 60))
    rep.save(pages / f"{nom}_reperes.jpg", quality=85)
    print(png)
    print(pages / f"{nom}_reperes.jpg")


# ------------------------------------------------------------------ monter
def barre_adresse(url, largeur):
    h = C.PAGE_BARRE_H
    im = Image.new("RGB", (largeur, h), (222, 225, 230))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([40, 28, largeur - 40, h - 28], radius=(h - 56) // 2, fill=(255, 255, 255))
    cx, cy = 100, h // 2                                     # cadenas
    d.rounded_rectangle([cx - 15, cy - 4, cx + 15, cy + 20], radius=4, fill=(60, 64, 67))
    d.arc([cx - 11, cy - 24, cx + 11, cy + 6], 180, 360, fill=(60, 64, 67), width=5)
    adresse = url.split("://", 1)[-1].removeprefix("www.").rstrip("/")
    f = police(44, "Medium")
    place = largeur - 140 - 70
    if d.textlength(adresse, font=f) > place:       # adresse longue : coupee comme un navigateur
        while adresse and d.textlength(adresse + "…", font=f) > place:
            adresse = adresse[:-1]
        adresse += "…"
    d.text((140, cy), adresse, font=f, fill=(32, 33, 36), anchor="lm")
    return im


def coeffs(sortie, entree):
    """Coefficients PIL (sortie -> entree) d'une transformation perspective."""
    m = []
    for (x, y), (u, v) in zip(sortie, entree):
        m.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
        m.append([0, 0, 0, x, y, 1, -v * x, -v * y])
    return np.linalg.lstsq(np.array(m, float), np.array(entree, float).reshape(8), rcond=None)[0]


def monter(dossier, bloc, nom, passages, flous, duree, colonne=None):
    episode = Path(dossier).resolve()
    png = episode / "pages" / f"{nom}.png"
    url = json.loads((episode / "pages" / f"{nom}.json").read_text(encoding="utf-8"))["url"]
    page = Image.open(png).convert("RGB")
    for x0, y0, x1, y1 in flous:
        zone = page.crop((x0, y0, x1, y1)).filter(ImageFilter.GaussianBlur(C.PAGE_FLOU_PHOTO))
        page.paste(zone, (x0, y0))
    if colonne:                       # marges et menus lateraux ecartes : le texte grossit
        page = page.crop((colonne[0], 0, colonne[1], page.height))
    morceaux = [barre_adresse(url, page.width)] + [page.crop((0, a, page.width, b)) for a, b in passages]
    pile = Image.new("RGB", (page.width, sum(m.height for m in morceaux)), "white")
    y = 0
    for m in morceaux:
        pile.paste(m, (0, y)); y += m.height
    W, H = C.LARGEUR, C.HAUTEUR
    # la fenetre garde les proportions validees (page de 1920 px de large) : une colonne plus
    # etroite grossit le texte ; la page pleine defile jusqu'a son dernier passage
    fen_h = round(C.PAGE_FENETRE_H * page.width / (C.PAGE_LARGEUR_CSS * C.PAGE_ECHELLE))
    if pile.height < fen_h:
        fond = Image.new("RGB", (pile.width, fen_h), "white"); fond.paste(pile, (0, 0)); pile = fond
    course = pile.height - fen_h
    quad = C.PAGE_QUAD
    c = coeffs(quad, [(0, 0), (page.width, 0), (page.width, fen_h), (0, fen_h)])
    gx, gy = np.meshgrid(np.linspace(0, 1, W), np.linspace(0, 1, H))
    loin = np.clip((gx - gy + 0.35) * 1.4, 0, 1)                 # flou au loin (haut droite)
    sous_titres = np.clip((gy - 0.50) * 4, 0, 1)                 # et sous les textes du reel
    masque = Image.fromarray((np.maximum(loin, sous_titres) * 255).astype(np.uint8))
    noir = Image.new("RGB", (W, H), (0, 0, 0))
    dest = episode / "broll" / f"B{bloc}.mp4"
    dest.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.Popen([B.FFMPEG, "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                             "-s", f"{W}x{H}", "-r", str(C.FPS), "-i", "-", "-c:v", "libx264",
                             "-crf", "15", "-preset", "slow", "-pix_fmt", "yuv420p", str(dest), "-y"],
                            stdin=subprocess.PIPE)
    t_adresse = C.PAGE_ADRESSE_S
    for i in range(int(duree * C.FPS)):
        t = i / C.FPS
        y = course * lisse((t - t_adresse) / max(0.1, duree - t_adresse - 0.6))
        fen = pile.crop((0, int(y), pile.width, int(y) + fen_h))
        vue = fen.transform((W, H), Image.PERSPECTIVE, tuple(c), Image.BICUBIC,
                            fillcolor=C.PAGE_FOND)
        vue = Image.composite(vue.filter(ImageFilter.GaussianBlur(C.PAGE_FLOU_PROFONDEUR)), vue, masque)
        vue = Image.blend(vue, noir, C.PAGE_VOILE)
        proc.stdin.write(vue.tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit("[!] ffmpeg a echoue pendant le montage de la page")
    registre.inscrire(episode.name, bloc, {"id": f"page:{url}", "url_page": url, "auteur_id": url,
                                           "auteur": "capture d'ecran"})
    ep_f = episode / "script.json"
    if ep_f.exists():
        ep = json.loads(ep_f.read_text(encoding="utf-8"))
        ep["blocs"][bloc]["requete"] = f"page : {url}"
        ep["blocs"][bloc].pop("cadrage", None)
        ep_f.write_text(json.dumps(ep, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[{bloc}] <- page {url} ({duree:.0f} s)")


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) == 4 and a[0] == "capturer":
        capturer(a[1], a[2], a[3])
    elif len(a) >= 5 and a[0] == "monter":
        duree, flous, passages, colonne, reste = 10.0, [], [], None, a[4:]
        i = 0
        while i < len(reste):
            if reste[i] == "--duree":
                duree = float(reste[i + 1]); i += 2
            elif reste[i] == "--colonne":
                x0, x1 = reste[i + 1].split(":"); colonne = (int(x0), int(x1)); i += 2
            elif reste[i] == "--flou":
                i += 1
                while i < len(reste) and not reste[i].startswith("--") and reste[i].count(",") == 3:
                    flous.append(tuple(int(v) for v in reste[i].split(","))); i += 1
            else:
                y0, y1 = reste[i].split(":"); passages.append((int(y0), int(y1))); i += 1
        if not passages:
            raise SystemExit("[!] indique au moins un passage <y0>:<y1>")
        monter(a[1], int(a[2]), a[3], passages, flous, duree, colonne)
    else:
        raise SystemExit(__doc__)
