"""Montage : normalisation des B-rolls, rendu de l'habillage, sortie sans piste audio."""
import subprocess
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import charte as C
from lcdg import binaires as B
from lcdg import habillage as hb
from lcdg import inserts as ins


# ------------------------------------------------------------------ 1. base
def base(episode: Path, blocs: list[dict]) -> tuple[Path, list, float]:
    """Concatene les B-rolls recadres en 1080x1920, avec un zoom lent."""
    seg_dir = episode / "segments"
    seg_dir.mkdir(parents=True, exist_ok=True)
    parts, bornes, t = [], [], 0.0

    for i, bl in enumerate(blocs):
        src = episode / "broll" / bl["fichier"]
        if not src.exists():
            raise SystemExit(f"[!] B-roll manquant : {src}")
        duree = bl["duree"] + (C.CROIX_DUREE + C.OUTRO_DUREE if i == len(blocs) - 1 else 0)
        out = seg_dir / f"s{i}.mp4"
        # a la coupe, l'image se pose (recul de p0 a 1 en n0 images), puis le zoom lent
        # reprend jusqu'a BROLL_ZOOM : l'entree du reel livre arrive en zoom et floue, une
        # phrase forte d'un coup de zoom, les autres plans d'une impulsion legere
        entree = i == (1 if C.ACCROCHE_COUVERTURE and len(blocs) > 1 else -1)
        if entree:
            n0, p0 = C.OUVERTURE_IMAGES, C.OUVERTURE_ZOOM
        elif bl.get("type") == "phrase":
            n0, p0 = C.PHRASE_IMAGES, C.PHRASE_ZOOM
        else:
            n0, p0 = C.IMPULSION_IMAGES, C.IMPULSION
        z = (f"if(lt(in,{n0}),{p0}-{p0 - 1:.4f}*(1-pow(1-in/{n0},3)),"
             f"min(1+{(C.BROLL_ZOOM-1)/170:.6f}*(in-{n0}),{C.BROLL_ZOOM}))")
        cadre = (f"scale={C.LARGEUR}:{C.HAUTEUR}:force_original_aspect_ratio=increase,"
                 f"crop={C.LARGEUR}:{C.HAUTEUR},")
        if bl.get("cadrage") == "largeur":
            # plan entier en pleine largeur, sur son propre fond floute et assombri
            source = (f"[0:v]split[pl][fd];[fd]{cadre}"
                      f"boxblur=luma_radius={C.PLAN_LARGEUR_FLOU}:luma_power=2:"
                      f"chroma_radius={C.PLAN_LARGEUR_FLOU // 2}:chroma_power=2,"
                      f"eq=brightness={C.PLAN_LARGEUR_LUMIERE}[fond];"
                      f"[pl]scale={C.LARGEUR}:-2[plan];"
                      f"[fond][plan]overlay=0:{C.PLAN_LARGEUR_Y}[cadre];[cadre]")
        else:
            source = f"[0:v]{cadre}"
        vf = (f"zoompan=z='{z}':d=1:"
              f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
              f"s={C.LARGEUR}x{C.HAUTEUR}:fps={C.FPS},"
              f"{C.ETALONNAGE},"
              f"tpad=stop_mode=clone:stop_duration=3,setsar=1,format=yuv420p")
        if bl.get("type") in hb.TYPES_FLOUS:
            # flou de profondeur : une copie floutee se fond par-dessus a l'entree du bloc
            # et s'efface avec la sortie du texte (le dernier bloc deborde sur la croix)
            fin = bl["duree"] + (C.BLOC_RESIDU if i == len(blocs) - 1 else 0)
            r = C.FLOU_RAYON
            filtre = ["-filter_complex",
                      f"{source}{vf},split[net][f0];"
                      f"[f0]boxblur=luma_radius={r}:luma_power=2:"
                      f"chroma_radius={r // 2}:chroma_power=2,format=yuva420p,"
                      f"fade=t=in:st=0:d={C.FLOU_ENTREE}:alpha=1,"
                      f"fade=t=out:st={max(0.0, fin - C.SORTIE_DUREE):.3f}:"
                      f"d={C.SORTIE_DUREE}:alpha=1[flou];"
                      f"[net][flou]overlay=format=auto,format=yuv420p[v]",
                      "-map", "[v]"]
        elif entree:
            r = C.OUVERTURE_FLOU
            filtre = ["-filter_complex",
                      f"{source}{vf},split[net][f0];"
                      f"[f0]boxblur=luma_radius={r}:luma_power=1:"
                      f"chroma_radius={r // 2}:chroma_power=1,format=yuva420p,"
                      f"fade=t=out:st=0:d={C.OUVERTURE_NET}:alpha=1[flou];"
                      f"[net][flou]overlay=format=auto,format=yuv420p[v]",
                      "-map", "[v]"]
        else:
            filtre = ["-filter_complex", f"{source}{vf}[v]", "-map", "[v]"]
        B.run(["-ss", str(C.BROLL_MARGE_S), "-i", str(src), "-t", f"{duree:.3f}",
               "-an", *filtre, "-r", str(C.FPS), "-c:v", "libx264",
               "-preset", "veryfast", "-crf", "18", str(out), "-y"])
        d = B.duree(out)
        bornes.append((round(t, 3), round(t + d, 3)))
        t += d
        parts.append(out)

    liste = episode / "concat.txt"
    liste.write_text("\n".join(f"file '{p.as_posix()}'" for p in parts), encoding="utf-8")
    sortie = episode / "base.mp4"
    B.run(["-f", "concat", "-safe", "0", "-i", str(liste), "-c", "copy", str(sortie), "-y"])
    return sortie, bornes, round(t, 3)


# --------------------------------------------------------------- 2. habillage
def bornes_nominales(ep: dict) -> list:
    """Bornes des plans selon les durees du script (les vraies sortent de base())."""
    t, bornes = 0.0, []
    for bl in ep["blocs"]:
        bornes.append((round(t, 3), round(t + bl["duree"], 3)))
        t += bl["duree"]
    return bornes


def verifier(ep: dict, bornes: list | None = None):
    """Un texte trop long sortirait du recadrage 4:5 du fil ou de sa colonne : on le
    verifie avant tout encodage. La mise en page ne depend pas des durees reelles, les
    bornes du script suffisent quand base() n'a pas encore tourne."""
    # chaque temps de l'ecran a sa phrase lue : sinon le texte et la voix se decalent
    for k, bl in enumerate(ep["blocs"][1:], 1):
        lu = (bl.get("voix") or "").strip()
        if not lu:
            continue
        if bl.get("type") == "chiffre":
            if "|" in lu:
                raise SystemExit(f"[!] bloc {k} : la voix d'un chiffre cle n'a qu'un temps, "
                                 "retire ses « | ».")
        elif lu.count("|") != (bl.get("texte") or "").count("|"):
            raise SystemExit(f"[!] bloc {k} : {lu.count('|')} « | » dans la voix, "
                             f"{(bl.get('texte') or '').count('|')} a l'ecran. Chaque temps de "
                             "l'ecran doit avoir sa phrase lue, dans le meme ordre.")
    bornes = bornes or bornes_nominales(ep)
    croix = bornes[-1][0] + ep["blocs"][-1]["duree"]
    hb.rubrique(ep.get("rubrique"))
    carte = hb.CarteFinale(croix + C.CROIX_DUREE, ep.get("appel"))
    if carte.lignes_appel > 1:
        raise SystemExit(f"[!] Appel a l'action trop long pour une ligne : "
                         f"« {carte.texte_appel} ». Raccourcis le champ appel de script.json.")
    couches = [("logo", hb.watermark(), C.LARGEUR), ("carte finale", carte.couche(), C.LARGEUR)]
    for sc in hb.scenes(ep, bornes, croix):
        couches += sc.couches()
    couches += [("credit", cr.couche(), C.LARGEUR) for cr in hb.credits(ep, bornes)]
    les_scenes = hb.scenes(ep, bornes, croix)
    ouv = hb.ouverture(ep, les_scenes)
    if ouv:
        couches.append(("pastille d'ouverture", ouv.couche(), hb.COLONNE))
    couches += [(i.nom, i.couche(), hb.COLONNE) for i in ins.inserts(ep, les_scenes, ouv)]
    if ep.get("bandeau"):
        # le bandeau s'arrete avant le logo, qui garde sa place
        logo_gauche = hb.watermark().getchannel("A").getbbox()[0]
        couches.append(("bandeau", hb.Bandeau(ep["bandeau"], 0, 1).couche(),
                        logo_gauche - C.BANDEAU_ECART_LOGO))
    zones = [(nom, hb.hors_zone(lay, droite)) for nom, lay, droite in couches]
    debords = [f"    {nom} : y {z[0]}-{z[1]}, x jusqu'a {z[2]}" for nom, z in zones if z]
    if debords:
        raise SystemExit(
            f"[!] Hors de la zone sure 4:5 (y {C.ZONE_SURE_HAUT}-{C.ZONE_SURE_BAS}) "
            f"ou de la colonne de texte (x <= {hb.COLONNE}) :\n"
            + "\n".join(debords) + "\n    Raccourcis le texte ou le surlignage dans script.json.")


def habiller(episode: Path, ep: dict, bornes: list, total: float) -> Path:
    """Compose l'habillage image par image et l'incruste sur la base."""
    n = int(round(total * C.FPS))
    croix = total - (C.CROIX_DUREE + C.OUTRO_DUREE)
    plein = croix + C.CROIX_DUREE

    verifier(ep, bornes)
    statique = Image.new("RGBA", (C.LARGEUR, C.HAUTEUR), (0, 0, 0, 0))
    statique.alpha_composite(hb.scrim())
    logo = hb.watermark()
    scenes = hb.scenes(ep, bornes, croix)
    carte = hb.CarteFinale(plein, ep.get("appel"))
    # ni pendant l'accroche, ni sur la carte finale
    # le bandeau laisse l'entree du reel livre a la pastille du sujet : il arrive au plan
    # suivant
    debut_bandeau = bornes[2][0] if C.ACCROCHE_COUVERTURE and len(bornes) > 2 else bornes[1][0]
    bandeau = (hb.Bandeau(ep["bandeau"], debut_bandeau, croix, scenes)
               if ep.get("bandeau") else None)
    ouverture = hb.ouverture(ep, scenes)
    les_inserts = ins.inserts(ep, scenes, ouverture)
    credits = hb.credits(ep, bornes)

    sortie = episode / "reel_muet.mp4"
    proc = subprocess.Popen(
        [B.FFMPEG, "-v", "error", "-i", str(episode / "base.mp4"),
         "-f", "rawvideo", "-pix_fmt", "rgba",
         "-s", f"{C.LARGEUR}x{C.HAUTEUR}", "-r", str(C.FPS), "-i", "-",
         "-filter_complex", "[0:v][1:v]overlay=format=auto:shortest=1[v]",
         "-map", "[v]", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
         "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(sortie), "-y"],
        stdin=subprocess.PIPE)

    for i in range(n):
        t = i / C.FPS
        lay = statique.copy()
        actives = [sc for sc in scenes if sc.debut <= t < sc.fin]
        for sc in actives:              # le voile passe sous le logo, qui garde sa lumiere
            sc.voiler(lay, t)
        lay.alpha_composite(logo)
        for cr in credits:
            if cr.debut <= t < cr.fin:
                cr.dessiner(lay, t)
        if bandeau and bandeau.debut <= t < bandeau.fin:
            bandeau.dessiner(lay, t)
        for sc in actives:
            sc.dessiner(lay, t)
        for i in les_inserts:
            if i.debut <= t < i.fin:
                i.dessiner(lay, t)
        if ouverture and ouverture.debut <= t < ouverture.fin:
            ouverture.dessiner(lay, t)
        if t >= croix:
            lay.alpha_composite(hb.cross_wipe((t - croix) / C.CROIX_DUREE))
        if t >= plein:
            carte.dessiner(lay, t)
        try:
            proc.stdin.write(lay.tobytes())
        except (BrokenPipeError, OSError) as e:
            proc.stdin.close(); proc.wait()
            raise RuntimeError(
                f"ffmpeg s'est arrete pendant le rendu (image {i}/{n}) : {e}\n"
                "Verifie l'espace disque et que base.mp4 est lisible.") from e

    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError("ffmpeg a echoue pendant l'incrustation de l'habillage.")
    return sortie


# ------------------------------------------------------------------ 3. sortie
def finaliser(muet: Path, sortie: Path, voix: Path | None = None) -> Path:
    """Pose la bande son (voix, musique, bruitages : lcdg/son.py) sur l'habillage.
    Sans bande son, le reel sort muet."""
    sortie.unlink(missing_ok=True)
    if voix is None:
        muet.replace(sortie)
        return sortie
    # la voix s'arrete avant la carte finale : du silence la prolonge jusqu'au bout
    B.run(["-i", str(muet), "-i", str(voix), "-map", "0:v", "-map", "1:a",
           "-c:v", "copy", "-af", "apad", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
           "-shortest", "-movflags", "+faststart", str(sortie), "-y"])
    muet.unlink(missing_ok=True)
    return sortie


def couverture(video: Path) -> list[Path]:
    """Images de couverture, prises quand l'accroche est en place : couverture_<slug>.jpg
    a cote du reel et, pour un reel 9:16, sa version 4:5 (zone sure du fil)."""
    dest = video.with_name(video.stem.replace("reel_", "couverture_", 1) + ".jpg")
    B.run(["-ss", str(C.COUVERTURE_T), "-i", str(video), "-frames:v", "1",
           "-q:v", "2", str(dest), "-y"])
    out = [dest]
    if C.HAUTEUR > C.LARGEUR:
        quatre_cinq = dest.with_name(dest.stem + "_4x5.jpg")
        B.run(["-i", str(dest), "-vf", f"crop={C.LARGEUR}:{C.ZONE_SURE_BAS - C.ZONE_SURE_HAUT}:"
               f"0:{C.ZONE_SURE_HAUT}", "-q:v", "2", str(quatre_cinq), "-y"])
        out.append(quatre_cinq)
    return out


def couper_accroche(video: Path, debut: float) -> Path:
    """Retire l'accroche (servie en couverture) : le reel livre commence au bloc 1."""
    tmp = video.with_name(video.stem + "_coupe.mp4")
    B.run(["-ss", f"{debut:.4f}", "-i", str(video), "-c:v", "libx264", "-crf", "17",
           "-preset", "slow", "-pix_fmt", "yuv420p", "-af", f"afade=t=in:st=0:d={C.COUPE_FONDU}",
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart",
           str(tmp), "-y"])
    tmp.replace(video)
    return video
