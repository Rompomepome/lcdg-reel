"""
Moteur d'habillage du reel LCDG : intro, blocs de texte, transition en croix, carte finale.
Toutes les constantes viennent de config/charte.py — ne rien coder en dur ici.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import charte as C
from lcdg.logo import lockup, police as font

W, H = C.LARGEUR, C.HAUTEUR
PRIMARY, NAVY, WHITE = C.PRIMARY, C.NAVY, C.BLANC

_RUBRIQUE = C.PRIMARY


def rubrique(nom: str | None):
    """Fixe la couleur d'accent selon la categorie de l'article (cf. charte.RUBRIQUES)."""
    global _RUBRIQUE, PRIMARY, SURLIGNE
    _RUBRIQUE = C.RUBRIQUES.get(nom or "pro", C.PRIMARY)
    PRIMARY = SURLIGNE = _RUBRIQUE
    _INTRO.clear(); _BLOC.clear()
    return _RUBRIQUE
RADIUS, STROKE = C.RADIUS, C.CONTOUR
FILET, FILET_COL, SURLIGNE = C.FILET_PX, C.FILET_COULEUR, C.PRIMARY


def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if d.textbbox((0, 0), t, font=f)[2] <= maxw:
            cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines


def shadow(layer, blur=16, alpha=150, offset=(0, 5)):
    a = layer.split()[3].filter(ImageFilter.GaussianBlur(blur))
    sh = Image.new('RGBA', layer.size, (0, 0, 0, 0))
    sh.putalpha(a.point(lambda p: int(p * alpha / 255)))
    out = Image.new('RGBA', layer.size, (0, 0, 0, 0))
    out.paste(sh, offset, sh)
    out.alpha_composite(layer)
    return out


def hors_zone(layer, droite=W):
    """(haut, bas, droite) des pixels opaques si la couche sort de la zone sure 4:5
    ou depasse `droite`, sinon None."""
    bbox = layer.split()[3].point(lambda p: 255 if p > 128 else 0).getbbox()
    if bbox and (bbox[1] < C.ZONE_SURE_HAUT or bbox[3] > C.ZONE_SURE_BAS or bbox[2] > droite):
        return bbox[1], bbox[3], bbox[2]
    return None


def cross_mask(size, cx=W // 2, cy=H // 2, canvas=(W, H)):
    """Masque en croix medicale, aux proportions du logo."""
    m = Image.new('L', canvas, 0)
    if size <= 2: return m
    d = ImageDraw.Draw(m)
    a, r = size * 0.335, max(2, size * 0.055)
    d.rounded_rectangle([cx - a / 2, cy - size / 2, cx + a / 2, cy + size / 2], radius=r, fill=255)
    d.rounded_rectangle([cx - size / 2, cy - a / 2, cx + size / 2, cy + a / 2], radius=r, fill=255)
    return m


# ---------- couches ----------
_WM = {}
def watermark(size=C.LOGO_PX, margin=C.LOGO_MARGE):
    if size not in _WM:
        logo = lockup(size)
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        lay.paste(logo, (W - logo.width - margin, C.LOGO_Y), logo)
        _WM[size] = shadow(lay, blur=12, alpha=140, offset=(0, 4))
    return _WM[size]


def scrim():
    g = Image.new('L', (1, H))
    bas = C.SCRIM_BAS_DEBUT
    for i in range(H):
        t = i / H
        v = int(C.SCRIM_BAS_ALPHA * ((t - bas) / (1 - bas)) ** 1.25) if t > bas else 0
        haut = 1 - (i - C.ZONE_SURE_HAUT) / C.SCRIM_HAUT_PX
        if haut > 0: v = max(v, int(C.SCRIM_HAUT_ALPHA * min(1.0, haut)))
        g.putpixel((0, i), min(v, C.SCRIM_MAX))
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    lay.putalpha(g.resize((W, H)))
    return lay


_INTRO = {}
def intro_layer(label, sub, reveal=1.0, y=C.INTRO_Y):
    """Bandeau rubrique arrondi + sous-titre contoure. reveal 0->1 = ouverture laterale."""
    key = (label, sub, y)
    if key not in _INTRO:
        d0 = ImageDraw.Draw(Image.new('RGBA', (8, 8)))
        fl, fs = (font(C.TITRE_PX, C.TITRE_GRAISSE),
                  font(C.SOUS_TITRE_PX, C.SOUS_TITRE_GRAISSE))
        bw = d0.textbbox((0, 0), label, font=fl)[2] + 76
        bh, bx = 104, (W - (d0.textbbox((0, 0), label, font=fl)[2] + 76)) // 2

        band = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        bd = ImageDraw.Draw(band)
        bd.rounded_rectangle([bx, y, bx + bw, y + bh], radius=RADIUS, fill=PRIMARY + (255,))
        bd.text((W // 2, y + bh // 2), label, font=fl, fill=WHITE + (255,), anchor='mm')

        sublay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        sd = ImageDraw.Draw(sublay)
        yy = y + bh + 34
        for ln in wrap(sd, sub, fs, 900):
            sd.text((W // 2, yy), ln, font=fs, fill=WHITE + (255,), anchor='ma',
                    stroke_width=C.CONTOUR_PX, stroke_fill=STROKE)
            yy += 74
        _INTRO[key] = (shadow(band, 20, 120, (0, 7)), shadow(sublay, 16, 195, (0, 5)), bx, bw)

    band, sublay, bx, bw = _INTRO[key]
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    vis = max(0.0, min(1.0, reveal))
    cw = int(bw * vis)
    if cw > 6:
        cx = bx + (bw - cw) // 2
        strip = band.crop((cx - 26, 0, cx + cw + 26, H))
        lay.paste(strip, (cx - 26, 0), strip)
    if vis > 0.15:
        s = sublay.copy()
        s.putalpha(s.split()[3].point(lambda p: int(p * min(1.0, (vis - 0.15) / 0.5))))
        lay.alpha_composite(s)
    return lay


_BLOC = {}
FILET = 20          # largeur du filet, affinee
FILET_COL = WHITE   # bande rectangulaire blanche
SURLIGNE = PRIMARY  # surlignage bleu clair, mot en blanc sans contour


def atomes(texte):
    """Transforme '*mot* suivant' en atomes (texte, surligne), espaces compris.
    La ponctuation collee reste collee, et un surlignage multi-mots reste continu."""
    runs, surl = [], False
    for part in texte.split('*'):
        if part: runs.append((part, surl))
        surl = not surl
    out = []
    for txt, hl in runs:
        buf = ''
        for ch in txt:
            if ch == ' ':
                if buf: out.append((buf, hl)); buf = ''
                out.append((' ', hl))
            else:
                buf += ch
        if buf: out.append((buf, hl))
    # un espace n'est surligne que s'il est encadre de deux atomes surlignes
    for i, (t, hl) in enumerate(out):
        if t == ' ' and hl:
            g = out[i-1][1] if i > 0 else False
            dr = out[i+1][1] if i+1 < len(out) else False
            out[i] = (' ', g and dr)
    return out


def lignes(d, texte, f, maxw):
    """Retour a la ligne impose a chaque fin de phrase (. ? !), puis habillage a la largeur.
    On ne coupe que sur une espace ordinaire : des atomes sans espace entre eux (mot
    surligne et sa ponctuation, apostrophe devant un surlignage) changent de ligne ensemble."""
    res = []
    for fin in '.?!':
        texte = texte.replace(fin + ' ', fin + '\n')
    phrases = [p.strip() for p in texte.split('\n') if p.strip()]
    for ph in phrases:
        cur, larg = [], 0
        for at in atomes(ph):
            w = d.textbbox((0, 0), at[0], font=f)[2] if at[0] != ' ' else d.textbbox((0, 0), 'i i', font=f)[2] - 2 * d.textbbox((0, 0), 'i', font=f)[2]
            if larg + w > maxw and cur and at[0] != ' ':
                report = []
                # atome colle au precedent (pas d'espace entre eux) : ils partent ensemble
                while cur and cur[-1][0] != ' ':
                    report.insert(0, cur.pop())
                # ne jamais couper au milieu d'un surlignage : on reporte le segment entier
                if (report or [at])[0][1]:
                    while cur and cur[-1][1]:
                        report.insert(0, cur.pop())
                    while report and report[0][0] == ' ': report.pop(0)
                while cur and cur[-1][0] == ' ': cur.pop()
                if cur: res.append(cur)
                cur = report
                larg = sum((d.textbbox((0, 0), a[0], font=f)[2] if a[0] != ' ' else 12) for a in cur)
            if not (not cur and at[0] == ' '):
                cur.append(at); larg += w
        while cur and cur[-1][0] == ' ': cur.pop()
        if cur: res.append(cur)
    return res


def bloc_layer(text, opacity=1.0, y=C.BLOC_Y, dx=0):
    """Bloc de texte sous la ligne mediane. Filet rectangulaire bleu fonce,
    surlignage bleu clair continu sur les segments importants."""
    if (text, y) not in _BLOC:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        f = font(C.BLOC_PX, C.BLOC_GRAISSE)
        x0, lh = C.BLOC_X, C.BLOC_INTERLIGNE
        ls = lignes(d, text, f, C.BLOC_LARGEUR_MAX)
        d.rectangle([x0 - 52, y - 12, x0 - 52 + FILET, y + lh * len(ls) - 8],
                    fill=FILET_COL + (255,))

        for i, ligne in enumerate(ls):
            yy, x = y + i * lh, x0
            pos = []
            for txt, hl in ligne:
                w = d.textbbox((0, 0), txt, font=f)[2] if txt != ' ' else \
                    d.textbbox((0, 0), 'i i', font=f)[2] - 2 * d.textbbox((0, 0), 'i', font=f)[2]
                pos.append((txt, hl, x, w)); x += w
            # 1) rectangles de surlignage, fusionnes sur les atomes contigus
            j = 0
            while j < len(pos):
                if pos[j][1]:
                    k = j
                    while k + 1 < len(pos) and pos[k+1][1]: k += 1
                    a, b = pos[j][2], pos[k][2] + pos[k][3]
                    d.rounded_rectangle([a - C.SURLIGNE_MARGE, yy - 3, b + C.SURLIGNE_MARGE, yy + 69], radius=5,
                                        fill=SURLIGNE + (255,))
                    j = k + 1
                else:
                    j += 1
            # 2) texte par-dessus
            for txt, hl, xx, _ in pos:
                if txt == ' ': continue
                if hl:
                    d.text((xx, yy), txt, font=f, fill=WHITE + (255,))
                else:
                    d.text((xx, yy), txt, font=f, fill=WHITE + (255,),
                           stroke_width=C.CONTOUR_PX, stroke_fill=STROKE)
        _BLOC[(text, y)] = shadow(lay, 20, 205, (0, 6))

    lay = _BLOC[(text, y)]
    if opacity >= 1 and dx == 0: return lay
    if dx:
        c = Image.new('RGBA', (W, H), (0, 0, 0, 0)); c.paste(lay, (int(dx), 0), lay)
    else:
        c = lay.copy()
    if opacity < 1:
        c.putalpha(c.split()[3].point(lambda p: int(p * max(0.0, opacity))))
    return c


def outro_card(fade=1.0):
    """Carte finale navy : logo, slogan du site, lien, mention."""
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    logo = lockup(200)
    lay.paste(logo, ((W - logo.width) // 2, C.OUTRO_LOGO_Y), logo)

    d = ImageDraw.Draw(lay)
    fsl = font(46, 'Medium')
    for i, ln in enumerate(C.SLOGAN):
        d.text((W // 2, C.OUTRO_SLOGAN_Y + i * 62), ln, font=fsl,
               fill=(214, 210, 232, 255), anchor='ma')

    f = font(44, 'SemiBold')
    t = C.LIEN
    bw = d.textbbox((0, 0), t, font=f)[2] + 64
    bx, by, bh = (W - bw) // 2, C.OUTRO_LIEN_Y, 84
    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=RADIUS, fill=PRIMARY + (255,))
    d.text((W // 2, by + bh // 2), t, font=f, fill=WHITE + (255,), anchor='mm')

    d.text((W // 2, C.OUTRO_MENTION_Y), C.MENTION, font=font(30, 'Medium'),
           fill=(150, 146, 175, 255), anchor='mm')

    if fade < 1:
        lay.putalpha(lay.split()[3].point(lambda p: int(p * max(0.0, fade))))
    return lay


def cross_wipe(p):
    """Transition finale : la croix medicale s'ouvre et remplit le cadre en navy.
    p 0->1. Phase 1 : la croix grandit et se lit. Phase 2 : elle envahit tout."""
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    if p <= 0: return lay
    if p < 0.42:
        e = (p / 0.42) ** 0.55
        size = 620 * e
    else:
        e = ((p - 0.42) / 0.58) ** 2.1
        size = 620 + (3400 - 620) * e
    fill = Image.new('RGBA', (W, H), NAVY + (255,))
    lay.paste(fill, (0, 0), cross_mask(size))
    return lay
