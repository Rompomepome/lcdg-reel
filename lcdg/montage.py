"""Montage : normalisation des B-rolls, rendu de l'habillage, sortie sans piste audio."""
import subprocess
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import charte as C
from lcdg import binaires as B
from lcdg import habillage as hb


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
        # a la coupe, l'image se pose (recul de IMPULSION a 1 en IMPULSION_IMAGES images),
        # puis le zoom lent reprend jusqu'a BROLL_ZOOM
        n0, p0 = C.IMPULSION_IMAGES, C.IMPULSION
        z = (f"if(lt(in,{n0}),{p0}-{p0 - 1:.4f}*(1-pow(1-in/{n0},3)),"
             f"min(1+{(C.BROLL_ZOOM-1)/170:.6f}*(in-{n0}),{C.BROLL_ZOOM}))")
        vf = (f"scale={C.LARGEUR}:{C.HAUTEUR}:force_original_aspect_ratio=increase,"
              f"crop={C.LARGEUR}:{C.HAUTEUR},"
              f"zoompan=z='{z}':d=1:"
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
                      f"[0:v]{vf},split[net][f0];"
                      f"[f0]boxblur=luma_radius={r}:luma_power=2:"
                      f"chroma_radius={r // 2}:chroma_power=2,format=yuva420p,"
                      f"fade=t=in:st=0:d={C.FLOU_ENTREE}:alpha=1,"
                      f"fade=t=out:st={max(0.0, fin - C.SORTIE_DUREE):.3f}:"
                      f"d={C.SORTIE_DUREE}:alpha=1[flou];"
                      f"[net][flou]overlay=format=auto,format=yuv420p[v]",
                      "-map", "[v]"]
        else:
            filtre = ["-vf", vf]
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
        for sc in actives:
            sc.dessiner(lay, t)
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
def finaliser(muet: Path, sortie: Path) -> Path:
    """Le reel est livre sans piste audio : Romain pose la musique lui-meme au montage
    final (decision du 21/09/2026). L'habillage sort deja muet, on le nomme."""
    sortie.unlink(missing_ok=True)
    muet.replace(sortie)
    return sortie


def couverture(video: Path) -> Path:
    """Image de couverture (miniature du profil), prise quand l'accroche est en place :
    couverture_<slug>.jpg a cote du reel."""
    dest = video.with_name(video.stem.replace("reel_", "couverture_", 1) + ".jpg")
    B.run(["-ss", str(C.COUVERTURE_T), "-i", str(video), "-frames:v", "1",
           "-q:v", "2", str(dest), "-y"])
    return dest
