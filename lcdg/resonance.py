"""
Anti-resonance d'une narration : rabote les zones etroites du spectre qui « sonnent ».

Romain entend la voix femme_agee « comme dans un bocal en verre » (05/10/2026). Mesure :
une bosse etroite du spectre moyen de la parole, 4 a 8 dB au-dessus du spectre lisse sur
une octave, qui change de place d'une generation ElevenLabs a l'autre (2,9 kHz sur une
narration, 4 kHz sur la suivante). Un filtre fixe tomberait a cote : on mesure chaque
narration et on place un filtre en cloche negatif sur chaque bosse.
"""
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import charte as C
from lcdg import binaires as B

SR = 24000
N = 8192


def _pcm(f: Path) -> np.ndarray:
    brut = subprocess.run([B.FFMPEG, "-v", "error", "-i", str(f), "-ac", "1", "-ar", str(SR),
                           "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(brut, dtype=np.float32).astype(np.float64)


def relief(f: Path) -> tuple[np.ndarray, np.ndarray]:
    """(frequences, ecart en dB du spectre moyen de la parole au spectre lisse sur une
    octave), entre 150 Hz et 8 kHz."""
    x = _pcm(f)
    fen = np.hanning(N)
    trames = [x[i:i + N] * fen for i in range(0, len(x) - N, N // 2)]
    energie = np.array([np.sum(t ** 2) for t in trames])
    parole = energie > np.percentile(energie, 50)
    spec = np.mean([np.abs(np.fft.rfft(t)) ** 2 for t, p in zip(trames, parole) if p], axis=0)
    freq = np.fft.rfftfreq(N, 1 / SR)
    db = 10 * np.log10(spec + 1e-12)
    sel = (freq > 150) & (freq < 8000)
    freq, db = freq[sel], db[sel]
    lisse = np.array([np.mean(db[(freq > fi / 1.41) & (freq < fi * 1.41)]) for fi in freq])
    return freq, db - lisse


def mesure(f: Path) -> float:
    """Ecart-type du relief dans la bande surveillee (dB) : plus il est haut, plus la voix
    « sonne »."""
    freq, e = relief(f)
    lo, hi = C.VOIX_RESONANCE_BANDE
    return float(np.std(e[(freq > lo) & (freq < hi)]))


def filtres(f: Path) -> str:
    """Filtres ffmpeg (separes par des virgules, vide si rien a corriger) qui rabotent les
    bosses de la narration f au-dela de VOIX_RESONANCE_SEUIL dB."""
    freq, e = relief(f)
    lo, hi = C.VOIX_RESONANCE_BANDE
    bosses = []
    for i in range(2, len(freq) - 2):
        if lo < freq[i] < hi and e[i] > C.VOIX_RESONANCE_SEUIL and e[i] == max(e[i - 2:i + 3]):
            bosses.append((freq[i], e[i]))
    # une bosse = les pics a moins d'un sixieme d'octave les uns des autres
    groupes = []
    for fr, ec in sorted(bosses):
        if groupes and fr < groupes[-1][-1][0] * 2 ** (1 / 6):
            groupes[-1].append((fr, ec))
        else:
            groupes.append([(fr, ec)])
    out = []
    for g in sorted(groupes, key=lambda g: -max(ec for _, ec in g))[:C.VOIX_RESONANCE_MAX_FILTRES]:
        poids = np.array([ec for _, ec in g])
        centre = float(np.average([fr for fr, _ in g], weights=poids))
        gain = min(C.VOIX_RESONANCE_GAIN_MAX, float(poids.max()) - C.VOIX_RESONANCE_CIBLE)
        out.append(f"equalizer=f={centre:.0f}:t=q:w={C.VOIX_RESONANCE_Q}:g={-gain:.1f}")
    return ",".join(out)
