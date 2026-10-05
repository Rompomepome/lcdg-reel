"""
Bande son du reel : voix off, musique de fond et bruitages cales sur le motion.

La musique s'efface sous la voix (compression declenchee par la voix) et suit la duree
du reel. Les bruitages tombent sur les instants des animations, calcules sur les memes
scenes que l'image (habillage.evenements) : ils restent synchrones quoi qu'il arrive.
Musique et bruitages vivent dans assets/ (non versionnes). S'ils manquent, le reel sort
avec la seule voix ; sans voix ni musique, il sort muet.
"""
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import charte as C
from lcdg import binaires as B
from lcdg import habillage as hb

SR = 48000


def musique(ep: dict) -> Path | None:
    """Morceau de fond : celui du script ("musique", un fichier de assets/audio, avec ou
    sans .mp3), sinon celui de la charte ; "musique": false le retire. Un morceau nomme
    par le script et introuvable arrete le rendu ; celui de la charte absent (assets/audio
    n'est pas versionne) est signale, et le reel sort avec la seule voix."""
    choix = ep.get("musique", C.MUSIQUE_DEFAUT)
    if not choix:
        return None
    f = C.AUDIO / choix
    if not f.suffix:
        f = f.with_suffix(".mp3")
    if f.exists():
        return f
    if "musique" in ep:
        raise SystemExit(f"[!] Musique « {choix} » introuvable dans assets/audio : mets le nom "
                         "d'un fichier present, ou \"musique\": false pour un reel sans musique.")
    print(f"[i] Musique de la charte absente ({f.name} dans assets/audio) : le reel sort sans "
          "musique.")
    return None


def _pcm(f: Path) -> np.ndarray:
    brut = subprocess.run([B.FFMPEG, "-v", "error", "-i", str(f), "-ac", "2", "-ar", str(SR),
                           "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(brut, dtype=np.float32).reshape(-1, 2).astype(np.float64)


def _ecrire(a: np.ndarray, dest: Path) -> Path:
    subprocess.run([B.FFMPEG, "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "2",
                    "-i", "-", str(dest), "-y"], input=a.astype(np.float32).tobytes(), check=True)
    return dest


def sonie(f: Path, filtre: str = "") -> float:
    """Sonie integree (LUFS) d'un fichier audio, apres un filtre facultatif."""
    af = (filtre + "," if filtre else "") + "ebur128=framelog=quiet"
    err = subprocess.run([B.FFMPEG, "-hide_banner", "-nostats", "-i", str(f), "-af", af,
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    mesures = re.findall(r"I:\s+(-?\d+(?:\.\d+)?) LUFS", err)
    if not mesures:
        raise RuntimeError(f"sonie illisible pour {f}")
    return float(mesures[-1])


def effets(ep: dict, bornes: list, total: float, dest: Path) -> Path | None:
    """Piste des bruitages, de la duree du reel. None si la banque est absente."""
    croix = total - (C.CROIX_DUREE + C.OUTRO_DUREE)
    piste = np.zeros((int(total * SR) + SR, 2))
    sons, poses = {}, 0
    for t, nom in hb.evenements(ep, bornes, croix):
        f = C.SFX / f"{nom}.mp3"
        if not f.exists():
            continue
        if nom not in sons:
            a = _pcm(f)
            # chaque son est ramene au meme sommet, puis au niveau voulu par la charte
            sons[nom] = a / (np.abs(a).max() + 1e-9) * 10 ** (C.SFX_GAINS[nom] / 20)
        a = sons[nom]
        i = int(max(0.0, t) * SR)
        j = min(len(piste), i + len(a))
        piste[i:j] += a[:j - i]
        poses += 1
    if not poses:
        return None
    return _ecrire(piste[:int(total * SR)], dest)


def bande(episode: Path, ep: dict, bornes: list, total: float, voix: Path | None) -> Path | None:
    """Mixe voix, musique (sous la voix) et bruitages en une piste stereo 48 kHz au niveau
    de la charte. None si le reel n'a ni voix ni musique."""
    # Gain fixe partout : une normalisation dynamique (loudnorm) au milieu du graphe
    # remonte les fondus et decale la piste qu'elle traite (02/10/2026, la musique
    # disparaissait 2,7 s avant la fin du reel).
    fond = musique(ep)
    if voix is None and fond is None:
        return None
    travail = episode / "voix"
    travail.mkdir(parents=True, exist_ok=True)
    sfx = effets(ep, bornes, total, travail / "effets.wav")
    entrees, graphe, mix = [], [], []
    if voix is not None:
        entrees += ["-i", str(voix)]
        graphe.append(f"[{len(entrees) // 2 - 1}:a]apad,atrim=0:{total:.3f},asplit=2[voix][cle]")
        mix.append("[voix]")
    if fond is not None:
        entrees += ["-i", str(fond)]
        k = len(entrees) // 2 - 1
        extrait = f"aresample={SR},atrim=0:{total:.3f},asetpts=N/SR/TB"
        gain = C.MUSIQUE_LUFS - sonie(fond, extrait)
        graphe.append(f"[{k}:a]{extrait},volume={gain:.2f}dB,"
                      f"afade=t=in:st=0:d={C.MUSIQUE_FONDU_IN},"
                      f"afade=t=out:st={max(0.0, total - C.MUSIQUE_FONDU_OUT):.3f}:"
                      f"d={C.MUSIQUE_FONDU_OUT}[fond]")
        if voix is not None:
            # la musique s'efface quand la voix parle
            graphe.append(f"[fond][cle]sidechaincompress={C.MUSIQUE_DUCKING}[fond_d]")
            mix.append("[fond_d]")
        else:
            mix.append("[fond]")
    elif voix is not None:
        graphe[-1] = graphe[-1].replace(",asplit=2[voix][cle]", "[voix]")
    if sfx is not None:
        entrees += ["-i", str(sfx)]
        graphe.append(f"[{len(entrees) // 2 - 1}:a]apad,atrim=0:{total:.3f}[sfx]")
        mix.append("[sfx]")
    graphe.append("".join(mix) + f"amix=inputs={len(mix)}:duration=longest:normalize=0[a]")
    brute = travail / f"bande_{ep['slug']}_brute.wav"
    B.run([*entrees, "-filter_complex", ";".join(graphe), "-map", "[a]",
           "-ar", str(SR), "-ac", "2", "-t", f"{total:.3f}", str(brute), "-y"])
    # mise au niveau final : un gain fixe, puis le limiteur pour les cretes
    gain = C.SON_LUFS - sonie(brute)
    dest = travail / f"bande_{ep['slug']}.wav"
    B.run(["-i", str(brute), "-af",
           f"volume={gain:.2f}dB,alimiter=limit={10 ** (C.SON_TP_CIBLE / 20):.3f}:level=false,"
           f"aresample={SR}", "-ar", str(SR), "-ac", "2", str(dest), "-y"])
    brute.unlink(missing_ok=True)
    return dest
