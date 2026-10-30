"""
Rendu final d'un ou plusieurs episodes : render.py (9:16), puis render_carre.py, puis les livrables sous
leurs noms habituels dans episodes/<dossier>/final/.

    python scripts/livrer.py episodes/<dossier> [episodes/<dossier>-pub ...]

S'arrete au premier rendu non conforme. Environ 10 min par reel et par format.
"""
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import json
import shutil
import subprocess
from pathlib import Path

R = Path(__file__).resolve().parent.parent
GARDER = ("OK", "[!]", "conforme", "Traceback", "Error")

if len(sys.argv) < 2:
    raise SystemExit(__doc__)
for d in sys.argv[1:]:
    ep_dir = (R / d).resolve()
    for script in ("render.py", "render_carre.py"):
        print(f"== {ep_dir.name} : {script}", flush=True)
        r = subprocess.run([sys.executable, f"scripts/{script}", str(ep_dir.relative_to(R))], cwd=R,
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        lignes = (r.stdout + r.stderr).strip().splitlines()
        print("\n".join(l for l in lignes if any(g in l for g in GARDER))[-1500:], flush=True)
        if r.returncode:
            print("\n".join(lignes[-15:]))
            sys.exit(f"[!] {ep_dir.name} : {script} a echoue")
    slug = json.loads((ep_dir / "script.json").read_text(encoding="utf-8"))["slug"]
    final = ep_dir / "final"
    final.mkdir(exist_ok=True)
    for src, dst in {f"reel_{slug}.mp4": f"reel_{slug}_9x16.mp4", f"reel_{slug}_carre.mp4": f"reel_{slug}_1x1.mp4",
                     f"couverture_{slug}.jpg": f"couverture_{slug}_9x16.jpg",
                     f"couverture_{slug}_4x5.jpg": f"couverture_{slug}_4x5.jpg",
                     f"couverture_{slug}_carre.jpg": f"couverture_{slug}_1x1.jpg"}.items():
        shutil.copyfile(ep_dir / src, final / dst)
    print(f"{ep_dir.name} : livrables dans {final}", flush=True)
print("FINI", flush=True)
