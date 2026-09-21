"""Montage : normalisation des B-rolls, rendu de l'habillage, mixage."""
import subprocess
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import charte as C
from lcdg import audio as A
from lcdg import binaires as B
from lcdg import habillage as hb


def lisser(x: float) -> float:
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


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
        vf = (f"scale={C.LARGEUR}:{C.HAUTEUR}:force_original_aspect_ratio=increase,"
              f"crop={C.LARGEUR}:{C.HAUTEUR},"
              f"zoompan=z='min(1+{(C.BROLL_ZOOM-1)/170:.6f}*in,{C.BROLL_ZOOM})':d=1:"
              f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
              f"s={C.LARGEUR}x{C.HAUTEUR}:fps={C.FPS},"
              f"tpad=stop_mode=clone:stop_duration=3,setsar=1,format=yuv420p")
        B.run(["-ss", str(C.BROLL_MARGE_S), "-i", str(src), "-t", f"{duree:.3f}",
               "-an", "-vf", vf, "-r", str(C.FPS), "-c:v", "libx264",
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
def habiller(episode: Path, ep: dict, bornes: list, total: float) -> Path:
    """Compose l'habillage image par image et l'incruste sur la base."""
    n = int(round(total * C.FPS))
    croix = total - (C.CROIX_DUREE + C.OUTRO_DUREE)
    plein = croix + C.CROIX_DUREE
    blocs = ep["blocs"]

    statique = Image.new("RGBA", (C.LARGEUR, C.HAUTEUR), (0, 0, 0, 0))
    statique.alpha_composite(hb.scrim())
    statique.alpha_composite(hb.watermark())

    hb.rubrique(ep.get("rubrique"))
    # un surlignage ne se coupe jamais : trop long, il deborde de la colonne de texte
    # (marge du surlignage, +1 car getbbox donne un bord droit exclusif)
    colonne = C.BLOC_X + C.BLOC_LARGEUR_MAX + C.SURLIGNE_MARGE + 1
    couches = [("logo", hb.watermark(), C.LARGEUR),
               ("intro", hb.intro_layer(ep["label"], ep["sous_titre"]), C.LARGEUR),
               ("carte finale", hb.outro_card(), C.LARGEUR)]
    couches += [(f"bloc {k}", hb.bloc_layer(bl["texte"]), colonne)
                for k, bl in enumerate(blocs) if k]
    # avant les minutes de rendu : un texte trop long sortirait du recadrage 4:5 du fil
    zones = [(nom, hb.hors_zone(lay, droite)) for nom, lay, droite in couches]
    debords = [f"    {nom} : y {z[0]}-{z[1]}, x jusqu'a {z[2]}" for nom, z in zones if z]
    if debords:
        raise SystemExit(
            f"[!] Hors de la zone sure 4:5 (y {C.ZONE_SURE_HAUT}-{C.ZONE_SURE_BAS}) "
            f"ou de la colonne de texte (x <= {colonne}) :\n"
            + "\n".join(debords) + "\n    Raccourcis le texte ou le surlignage dans script.json.")

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
        a0, b0 = bornes[0]
        if t < b0:
            if t < 0.15:
                rev = 0.0
            elif t < 0.15 + C.INTRO_OUVERTURE:
                rev = lisser((t - 0.15) / C.INTRO_OUVERTURE)
            elif t < b0 - C.INTRO_FERMETURE:
                rev = 1.0
            else:
                rev = 1.0 - lisser((t - (b0 - C.INTRO_FERMETURE)) / C.INTRO_FERMETURE)
            lay.alpha_composite(hb.intro_layer(ep["label"], ep["sous_titre"], rev))
        else:
            for k in range(1, len(blocs)):
                a, b = bornes[k]
                if k == len(blocs) - 1:
                    b = croix + C.BLOC_RESIDU
                if a <= t < b:
                    e = lisser((t - a) / C.BLOC_ENTREE)
                    o = min(e, 1.0) * min(lisser((b - t) / C.BLOC_SORTIE), 1.0)
                    dx = -int(C.BLOC_GLISSEMENT * (1 - min(e, 1.0)))
                    lay.alpha_composite(hb.bloc_layer(blocs[k]["texte"], o, dx=dx))
                    break
        if t >= croix:
            lay.alpha_composite(hb.cross_wipe((t - croix) / C.CROIX_DUREE))
        if t >= plein:
            lay.alpha_composite(hb.outro_card(min(1.0, (t - plein) / C.OUTRO_FONDU)))
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


# ------------------------------------------------------------------ 3. audio
def _preparer_effet(fiche: dict, dest: Path) -> Path:
    src = A.chemin(fiche["cle"])
    B.run(["-i", str(src), "-t", str(fiche["coupe_a"]), "-af", fiche["traitement"],
           "-ar", "48000", "-ac", "2", str(dest), "-y"])
    return dest


def mixer(episode: Path, ep: dict, bornes: list, total: float) -> Path:
    man = A.manifeste()
    fiches = {f["cle"]: f for f in man["effets"]}
    tap = _preparer_effet(fiches["tap-texte"], episode / "tap.wav")
    bas = _preparer_effet(fiches["bass-structure"], episode / "bass.wav")
    musique = A.chemin(ep["musique"])
    hb.rubrique(ep.get("rubrique"))

    croix = total - (C.CROIX_DUREE + C.OUTRO_DUREE)
    t_bandeau = bornes[0][1] - C.INTRO_FERMETURE
    debuts = [bornes[k][0] for k in range(1, len(ep["blocs"]))]
    pas = max(1, len(debuts) // C.SFX_TEXTE_NB)
    marques = debuts[::pas][:C.SFX_TEXTE_NB]

    n = len(marques)
    f = [f"[1:a]aloop=loop=3:size=2e9,atrim=0:{total},asetpts=N/SR/TB,"
         f"volume={C.MUSIQUE_VOLUME},afade=t=in:st=0:d={C.MUSIQUE_FONDU_IN},"
         f"afade=t=out:st={total - C.MUSIQUE_FONDU_OUT:.2f}:d={C.MUSIQUE_FONDU_OUT}[mus]",
         "[2:a]asplit=2[g1][g2]",
         f"[g1]volume={C.SFX_STRUCTURE_VOLUME},"
         f"adelay={int(t_bandeau*1000)}|{int(t_bandeau*1000)}[wA]",
         # borne a 0 : un volume negatif inverse la phase au lieu de couper
         f"[g2]volume={max(0.0, C.SFX_STRUCTURE_VOLUME - 0.02):.2f},"
         f"adelay={int(croix*1000)}|{int(croix*1000)}[wB]",
         f"[3:a]asplit={n}" + "".join(f"[b{i}]" for i in range(n))]
    sorties = []
    for i, t in enumerate(marques):
        f.append(f"[b{i}]volume={C.SFX_TEXTE_VOLUME},"
                 f"adelay={int(t*1000)}|{int(t*1000)}[w{i}]")
        sorties.append(f"[w{i}]")
    f.append("[mus][wA][wB]" + "".join(sorties) +
             f"amix=inputs={3+n}:duration=first:normalize=0,"
             f"loudnorm=I={C.LUFS_CIBLE}:TP={C.TRUE_PEAK_CIBLE}:LRA=11,"
             f"alimiter=limit={C.LIMITEUR}:level=false,aresample=48000[a]")

    sortie = episode / f"reel_{ep['slug']}.mp4"
    B.run(["-i", str(episode / "reel_muet.mp4"), "-i", str(musique),
           "-i", str(bas), "-i", str(tap),
           "-filter_complex", ";".join(f),
           "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac",
           "-b:a", "192k", "-shortest", "-movflags", "+faststart",
           str(sortie), "-y"])
    return sortie
