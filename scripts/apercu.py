"""
Apercu sans voix d'un episode, pour valider texte, plans et inserts avant de payer la voix.

    python scripts/apercu.py episodes/<dossier> [...] [--carre]

Copie l'episode dans episodes/_apercu-<slug> (plans compris), retire les champs "voix" (chaque plan dure
alors son champ "duree"), puis lance render.py, et render_carre.py avec --carre. Aucun credit ElevenLabs.
Les dossiers _apercu-* ne se commitent pas : supprime-les une fois l'apercu valide.
"""
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import json
import shutil
import subprocess
from pathlib import Path

R = Path(__file__).resolve().parent.parent

carre = "--carre" in sys.argv
dossiers = [a for a in sys.argv[1:] if not a.startswith("--")]
if not dossiers:
    raise SystemExit(__doc__)
ok = True
for d in dossiers:
    src = (R / d).resolve()
    ep = json.loads((src / "script.json").read_text(encoding="utf-8"))
    slug = "apercu-" + ep["slug"]
    dst = R / "episodes" / f"_{slug}"
    (dst / "broll").mkdir(parents=True, exist_ok=True)
    for b in ep["blocs"]:
        b.pop("voix", None)
        shutil.copyfile(src / "broll" / b["fichier"], dst / "broll" / b["fichier"])
        plan_carre = src / "broll_carre" / b["fichier"]     # version carree propre a ce plan
        if plan_carre.exists():
            (dst / "broll_carre").mkdir(exist_ok=True)
            shutil.copyfile(plan_carre, dst / "broll_carre" / b["fichier"])
    ep["slug"] = slug
    (dst / "script.json").write_text(json.dumps(ep, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for script in ["render.py"] + (["render_carre.py"] if carre else []):
        r = subprocess.run([sys.executable, f"scripts/{script}", str(dst)], cwd=R)
        ok &= r.returncode == 0
        print(f"{src.name} {script} : {'OK' if r.returncode == 0 else 'ECHEC'}", flush=True)
    print(f"apercu : {dst / f'reel_{slug}.mp4'}")
sys.exit(0 if ok else 1)
