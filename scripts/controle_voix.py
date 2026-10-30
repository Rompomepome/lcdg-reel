"""
Controle de la narration d'un episode, sans pouvoir l'ecouter :

    python scripts/controle_voix.py episodes/<dossier> ["passage a risque" ...]

1. Debit de chaque bloc, blancs de plus de 0,9 s, et indication de jeu peut-etre prononcee (une [indication]
   qui dure plus de 0,4 s dans l'horodatage).
2. Transcription Scribe (ElevenLabs, incluse dans le compte gratuit) comparee au texte lu : un mot deforme
   ressort (« bandette » pour « bandelette »). Les sigles epeles (« C.S.M.F. ») et les nombres en lettres
   s'ecrivent autrement : ces ecarts-la sont normaux. Scribe « corrige » parfois une mauvaise prononciation
   (« consulpation » transcrit « consultation », 28/10/2026) : il ne remplace pas l'ecoute.
3. Avec des passages en argument : un extrait sonore de ces passages (noms de medicaments, sigles, mots longs),
   episodes/<dossier>/final/extrait_voix_mots_difficiles.mp3, a faire ecouter a Romain avec chaque nouvelle voix.
"""
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import difflib
import json
import os
import re
import subprocess
import unicodedata
from pathlib import Path

import requests

R = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(R))
try:
    from dotenv import load_dotenv
    load_dotenv(R / ".env")
except ImportError:
    pass
from config import charte as C
from lcdg import binaires as B, voix

if len(sys.argv) < 2:
    raise SystemExit(__doc__)
D = (R / sys.argv[1]).resolve()
passages = sys.argv[2:]
ep = json.loads((D / "script.json").read_text(encoding="utf-8"))
_, morceaux = voix.textes(ep)
tv = [t for t, _ in morceaux]
texte = " ".join(tv)
v = voix.choix(ep)
# sans voix_off, la voix par defaut de la charte (comme voix.preparer)
mp3, js = voix.chemins(texte, v.get("id") or C.VOIX_ID, D / "voix", v.get("modele"), v.get("reglages"))
if not (mp3.exists() and js.exists()):
    raise SystemExit("[!] narration absente du cache : lance d'abord render.py")
al = json.loads(js.read_text(encoding="utf-8"))
deb, fin = al["character_start_times_seconds"], al["character_end_times_seconds"]
print(f"{mp3.name} : {fin[-1]:.1f} s pour {len(texte)} caracteres")


def lisible(i0, i1):
    """Index des caracteres lus (hors indications entre crochets) de [i0, i1)."""
    out, dans = [], False
    for i in range(i0, i1):
        c = texte[i]
        if c == "[":
            dans = True
        elif c == "]":
            dans = False
        elif not dans and c.strip():
            out.append(i)
    return out


# 1. debit, blancs, indications
p = 0
for k, t in enumerate(tv, 1):
    idx = lisible(p, p + len(t))
    a, z = deb[idx[0]], fin[idx[-1]]
    lu = len(re.sub(r"\[[^\]]*\]", "", t))
    print(f"  B{k:<2} {a:6.2f}-{z:6.2f} s  {z - a:5.2f} s  {lu / (z - a):5.1f} car/s")
    p += len(t) + 1
blancs = []
idx = lisible(0, len(texte))
for i, j in zip(idx, idx[1:]):
    if deb[j] - fin[i] > 0.9:
        blancs.append((deb[j] - fin[i], texte[max(0, i - 30):i + 1]))
for g, ctx in sorted(blancs, reverse=True)[:6]:
    print(f"  blanc de {g:.2f} s apres « …{ctx} »")
for m in re.finditer(r"\[[^\]]*\]", texte):
    if fin[m.end() - 1] - deb[m.start()] > 0.4:
        print(f"  [!] indication {m.group()} : {fin[m.end() - 1] - deb[m.start()]:.2f} s, peut-etre prononcee")

# 2. transcription comparee au texte lu
cache = mp3.with_suffix(".transcription.json")
if not cache.exists():
    with open(mp3, "rb") as f:
        r = requests.post("https://api.elevenlabs.io/v1/speech-to-text",
                          headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"]},
                          data={"model_id": "scribe_v1", "language_code": "fra", "tag_audio_events": "false"},
                          files={"file": (mp3.name, f, "audio/mpeg")}, timeout=300)
    if not r.ok:
        raise SystemExit(f"[!] transcription refusee ({r.status_code}) : {r.text[:200]}")
    cache.write_text(json.dumps(r.json(), ensure_ascii=False), encoding="utf-8")


def mots(s):
    s = re.sub(r"\[[^\]]*\]", " ", s)
    s = unicodedata.normalize("NFKD", s.lower().replace("’", "'"))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.findall(r"[a-z0-9]+", s)


attendu, entendu = mots(texte), mots(json.loads(cache.read_text(encoding="utf-8"))["text"])
print(f"transcription : {len(attendu)} mots attendus, {len(entendu)} transcrits")
for op, a0, a1, b0, b1 in difflib.SequenceMatcher(None, attendu, entendu, autojunk=False).get_opcodes():
    if op != "equal":
        print(f"  {op:8} attendu « {' '.join(attendu[a0:a1])} »  entendu « {' '.join(entendu[b0:b1])} »")

# 3. extrait sonore des passages a risque
segments = []
for ps in passages:
    i = texte.find(ps)
    if i < 0:
        print(f"  [!] passage introuvable dans le texte lu : « {ps} »")
        continue
    segments.append((max(0.0, deb[i] - 0.3), fin[i + len(ps) - 1] + 0.35))
if segments:
    filtres = [f"[0:a]atrim={a:.2f}:{z:.2f},asetpts=PTS-STARTPTS,apad=pad_dur=0.5[s{k}]"
               for k, (a, z) in enumerate(segments)]
    filtres.append("".join(f"[s{k}]" for k in range(len(segments))) +
                   f"concat=n={len(segments)}:v=0:a=1,loudnorm=I=-16:TP=-1.5")
    (D / "final").mkdir(exist_ok=True)
    sortie = D / "final" / "extrait_voix_mots_difficiles.mp3"
    subprocess.run([B.FFMPEG, "-v", "error", "-y", "-i", str(mp3), "-filter_complex", ";".join(filtres),
                    "-c:a", "libmp3lame", "-b:a", "192k", str(sortie)], check=True)
    print(f"extrait : {sortie} ({len(segments)} passages)")
