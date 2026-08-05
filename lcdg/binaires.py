"""Localise ffmpeg et ffprobe sur Windows comme sur macOS et Linux."""
import os
import shutil
import subprocess
import sys
from pathlib import Path


def _chercher(nom: str) -> str | None:
    # 1) variable d'environnement explicite (FFMPEG_BIN / FFPROBE_BIN)
    env = os.environ.get(f"{nom.upper()}_BIN")
    if env and Path(env).exists():
        return env
    # 2) PATH
    trouve = shutil.which(nom)
    if trouve:
        return trouve
    # 3) emplacements frequents sous Windows
    if sys.platform == "win32":
        for base in (
            Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "ffmpeg" / "bin",
            Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft/WinGet/Links",
            Path("C:/ffmpeg/bin"),
        ):
            cible = base / f"{nom}.exe"
            if cible.exists():
                return str(cible)
    return None


FFMPEG = _chercher("ffmpeg")
FFPROBE = _chercher("ffprobe")

INSTALL = {
    "win32": "winget install Gyan.FFmpeg   (ou : choco install ffmpeg)",
    "darwin": "brew install ffmpeg",
}.get(sys.platform, "sudo apt install ffmpeg")


def exiger():
    """Arrete proprement si ffmpeg manque, avec la commande d'installation."""
    manquants = [n for n, v in (("ffmpeg", FFMPEG), ("ffprobe", FFPROBE)) if not v]
    if manquants:
        raise SystemExit(
            f"[!] Introuvable : {', '.join(manquants)}\n"
            f"    Installe ffmpeg puis relance :\n      {INSTALL}\n"
            f"    Si ffmpeg est deja installe hors PATH, definis FFMPEG_BIN et FFPROBE_BIN."
        )


def run(args, **kw):
    """Appelle ffmpeg. Leve une erreur lisible en cas d'echec."""
    exiger()
    r = subprocess.run([FFMPEG, "-v", "error", *args],
                       capture_output=True, text=True, **kw)
    if r.returncode:
        raise RuntimeError(f"ffmpeg a echoue :\n{r.stderr[-1200:]}")
    return r


def probe(chemin, entrees="format=duration"):
    exiger()
    r = subprocess.run([FFPROBE, "-v", "error", "-show_entries", entrees,
                        "-of", "csv=p=0", str(chemin)],
                       capture_output=True, text=True)
    return r.stdout.strip()


def duree(chemin) -> float:
    v = probe(chemin, "format=duration").split(",")[0]
    return float(v) if v else 0.0


def pcm(chemin, mono=True, sr=44100, debut=None, duree_s=None):
    """Decode l'audio en float32 pour analyse. Retourne un numpy array."""
    import numpy as np
    exiger()
    args = [FFMPEG, "-v", "error"]
    if debut is not None:
        args += ["-ss", str(debut)]
    args += ["-i", str(chemin)]
    if duree_s is not None:
        args += ["-t", str(duree_s)]
    args += ["-ac", "1" if mono else "2", "-ar", str(sr), "-f", "f32le", "-"]
    out = subprocess.run(args, capture_output=True).stdout
    return np.frombuffer(out, dtype=np.float32).astype(np.float64)
