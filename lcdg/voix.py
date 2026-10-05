"""
Voix off de synthese (ElevenLabs) : la narration pilote le rythme du reel.

Chaque bloc du script porte son texte lu dans le champ "voix". La narration entiere est
generee d'un seul appel, pour garder une prosodie continue ; l'horodatage de chaque
caractere renvoye par l'API sert ensuite a caler chaque plan sur sa phrase, et chaque
temps d'un texte ("|") sur le moment ou la voix le prononce.

Les generations sont gardees en cache dans episodes/<dossier>/voix/ : une narration deja
payee n'est jamais regeneree, ni pour la version carree, ni pour un nouveau rendu.
"""
import base64
import hashlib
import json
import os
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import charte as C
from lcdg import binaires as B

API = "https://api.elevenlabs.io/v1"


def _cle() -> str:
    cle = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not cle:
        raise SystemExit("[!] ELEVENLABS_API_KEY absente de .env (voir .env.example).")
    return cle


def corps(texte: str, modele: str | None = None, reglages: dict | None = None) -> dict:
    modele = modele or C.VOIX_MODELE
    if reglages:
        pass                                  # reglages propres a la voix (VOIX_CATALOGUE)
    elif modele.startswith("eleven_v3"):
        # v3 : le jeu passe par les indications entre crochets du texte, pas par les reglages
        reglages = {"stability": C.VOIX_STABILITE, "similarity_boost": C.VOIX_SIMILARITE}
    else:
        reglages = {"stability": C.VOIX_STABILITE, "similarity_boost": C.VOIX_SIMILARITE,
                    "style": C.VOIX_STYLE, "use_speaker_boost": True, "speed": C.VOIX_VITESSE}
    return {"text": texte, "model_id": modele, "voice_settings": reglages}


def chemins(texte: str, voice_id: str, dossier: Path, modele: str | None = None,
            reglages: dict | None = None) -> tuple[Path, Path]:
    """(mp3, alignement json) de ce texte lu par cette voix, dans le cache."""
    requete = corps(texte, modele, reglages)
    cle = hashlib.sha256(json.dumps([voice_id, requete], sort_keys=True,
                                    ensure_ascii=False).encode("utf-8")).hexdigest()[:16]
    return dossier / f"{cle}.mp3", dossier / f"{cle}.json"


def synthese(texte: str, voice_id: str, dossier: Path, modele: str | None = None,
             reglages: dict | None = None) -> tuple[Path, dict]:
    """(mp3, alignement par caractere) de la narration, depuis le cache si elle existe."""
    requete = corps(texte, modele, reglages)
    mp3, js = chemins(texte, voice_id, dossier, modele, reglages)
    if mp3.exists() and js.exists():
        return mp3, json.loads(js.read_text(encoding="utf-8"))
    dossier.mkdir(parents=True, exist_ok=True)
    r = requests.post(f"{API}/text-to-speech/{voice_id}/with-timestamps",
                      params={"output_format": "mp3_44100_128"},
                      headers={"xi-api-key": _cle()}, json=requete, timeout=300)
    if not r.ok:
        raise SystemExit(f"[!] ElevenLabs a refuse la generation ({r.status_code}) : {r.text[:300]}")
    reponse = r.json()
    alignement = reponse["alignment"]
    if len(alignement["characters"]) != len(texte):
        raise SystemExit("[!] ElevenLabs : l'horodatage ne correspond pas au texte envoye "
                         f"({len(alignement['characters'])} caracteres pour {len(texte)}).")
    mp3.write_bytes(base64.b64decode(reponse["audio_base64"]))
    js.write_text(json.dumps(alignement, ensure_ascii=False), encoding="utf-8")
    return mp3, alignement


def choix(ep: dict) -> dict:
    """Voix du reel : "voix_off" est une cle de charte.VOIX_CATALOGUE ou un dict
    (id, modele, reglages) ; a defaut, la voix par defaut de la charte."""
    v = ep.get("voix_off") or {}
    if isinstance(v, str):
        if v not in C.VOIX_CATALOGUE:
            raise SystemExit(f"[!] voix_off inconnue : « {v} ». Voix validees : "
                             + ", ".join(C.VOIX_CATALOGUE))
        if not C.VOIX_CATALOGUE[v].get("id"):
            raise SystemExit(f"[!] voix_off « {v} » : {C.VOIX_CATALOGUE[v]['nom']} n'est pas "
                             "encore enregistree dans l'espace ElevenLabs.")
        v = C.VOIX_CATALOGUE[v]
    return v


def active(ep: dict) -> bool:
    """Le reel a une voix des qu'un bloc porte un texte lu."""
    return any((bl.get("voix") or "").strip() for bl in ep["blocs"])


def _decouper(texte: str) -> tuple[str, list[int]]:
    """Texte lu sans les '|', et position du debut de chaque temps apres le premier."""
    propre, debuts = "", []
    for i, morceau in enumerate(texte.split("|")):
        morceau = morceau.strip()
        if i:
            propre += " "
            debuts.append(len(propre))
        propre += morceau
    return propre, debuts


def textes(ep: dict) -> tuple[bool, list[tuple[str, list[int]]]]:
    """(bloc 0 muet, [(texte lu, debut de chaque temps)] des blocs parlants).

    Accroche en couverture : le bloc 0 n'a pas de voix, la narration commence au bloc 1.
    La narration envoyee a ElevenLabs est ces textes joints par une espace."""
    blocs = ep["blocs"]
    muet = C.ACCROCHE_COUVERTURE and not (blocs[0].get("voix") or "").strip()
    parlants = blocs[1:] if muet else blocs
    return muet, [_decouper((bl.get("voix") or "").strip()) for bl in parlants]


def preparer(episode: Path, ep: dict) -> Path:
    """Genere (ou reprend) la narration et cale le reel dessus.

    Fixe en memoire la duree de chaque bloc (une coupe juste avant chaque phrase) et
    les instants de ses temps ("temps", relatifs au debut du bloc). Retourne la piste
    voix (wav 48 kHz) calee sur la video et mise au niveau de la charte."""
    blocs = ep["blocs"]
    muet, morceaux = textes(ep)
    if C.ACCROCHE_COUVERTURE and not muet:
        print("[i] bloc 0 : sa voix est coupee avec l'accroche, qui ne sert qu'a la couverture. "
              "Dans un nouveau script, ne mets pas de voix au bloc 0 : elle consomme le quota "
              "pour rien.")
    vides = [k + muet for k, (t, _) in enumerate(morceaux) if not t]
    if vides:
        raise SystemExit(f"[!] Bloc(s) sans texte lu (champ voix) : {vides}")
    texte = " ".join(t for t, _ in morceaux)
    v = choix(ep)
    mp3, al = synthese(texte, v.get("id") or C.VOIX_ID, episode / "voix",
                       v.get("modele"), v.get("reglages"))
    modele = v.get("modele") or C.VOIX_MODELE
    tempo = C.VOIX_TEMPO_V3 if modele.startswith("eleven_v3") else 1.0
    deb = [x / tempo for x in al["character_start_times_seconds"]]
    fin = [x / tempo for x in al["character_end_times_seconds"]]

    d0 = C.VOIX_DEBUT + (C.ACCROCHE_COUVERTURE_DUREE if muet else 0.0)
    pos, phrases = 0, []
    for t, debuts in morceaux:
        phrases.append((d0 + deb[pos], d0 + fin[pos + len(t) - 1],
                        [d0 + deb[pos + i] for i in debuts]))
        pos += len(t) + 1
    coupes = ([0.0, C.ACCROCHE_COUVERTURE_DUREE] if muet else [0.0])
    coupes += [max(0.0, a - C.VOIX_AVANCE) for a, _, _ in phrases[1:]]
    coupes.append(phrases[-1][1] + C.VOIX_TENUE)
    if muet:
        phrases.insert(0, (0.0, 0.0, []))
    for k, bl in enumerate(blocs):
        bl["duree"] = round(coupes[k + 1] - coupes[k], 3)
        bl["temps"] = [round(t - C.VOIX_AVANCE - coupes[k], 3) for t in phrases[k][2]]

    wav = episode / "voix" / f"voix_{ep['slug']}.wav"
    # correction propre a la voix (charte.VOIX_CATALOGUE) : filtres fixes ("traitement") et
    # anti-resonance mesuree sur cette narration ("anti_resonance"), avant tout le reste
    corrections = [v["traitement"]] if v.get("traitement") else []
    if v.get("anti_resonance"):
        from lcdg import resonance
        corrections.append(resonance.filtres(mp3))
    traitement = "".join(f"{c}," for c in corrections if c)
    B.run(["-i", str(mp3), "-af",
           f"{traitement}atempo={tempo},adelay={int(d0 * 1000)}:all=1,"
           f"loudnorm=I={C.VOIX_LUFS}:TP={C.VOIX_TP_CIBLE}:LRA=11,aresample=48000",
           "-ar", "48000", "-ac", "2", str(wav), "-y"])
    return wav
