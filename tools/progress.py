"""Training progress of a run or a whole track rotation, per iteration (no extra packages needed).

Reads the logs that supervise.sh saves every 2 min (logs/<prefix>*/part*_TrainingMetrics.json +
TrainingMetrics.json; a simulator restart starts a new part).
Usage: python3 tools/progress.py cedc-m11-jason          # every leg whose prefix starts with this
       python3 tools/progress.py cedc-m11-jason --watch  # refresh every 2 min
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

LOGS = Path(__file__).resolve().parent.parent / "logs"
EPISODES_PER_ITER = 20


def episodes(run_dir: Path, name: str = "TrainingMetrics.json") -> list[dict]:
    """One worker's episodes; worker N > 0 of a multi-worker run writes TrainingMetrics_N.json."""
    parts = sorted(run_dir.glob(f"part*_{name}"), key=lambda f: int(re.match(r"part(\d+)_", f.name)[1]))
    out = []
    for f in [*parts, run_dir / name]:
        if f.exists():
            try:
                out += [m for m in json.loads(f.read_text())["metrics"] if m["phase"] == "training"]
            except (json.JSONDecodeError, KeyError):
                pass
    return out


def report(base: str) -> str:
    runs = sorted((d for d in LOGS.glob(f"{base}*") if d.is_dir()), key=lambda d: d.stat().st_ctime)
    if not runs:
        return f"no logs under {LOGS}/{base}* yet"
    out = [time.strftime("%H:%M:%S") + " " + base,
           f"{'run':28} {'iter':>4} {'eps':>5} {'progress':>8} {'laps':>4} {'best lap':>8}"]
    for d in runs:
        world = next((l.split("=", 1)[1].strip() for l in (d / "run.env").read_text().splitlines()
                      if l.startswith("DR_WORLD_NAME=")), "?") if (d / "run.env").exists() else "?"
        names = sorted({re.sub(r"^part\d+_", "", f.name) for f in d.glob("*TrainingMetrics*.json")})
        for name in names or ["TrainingMetrics.json"]:
            out += table(d.name, world if name == "TrainingMetrics.json" else "worker " + name[16:-5], episodes(d, name))
    return "\n".join(out)


def table(run: str, label: str, eps: list[dict]) -> list[str]:
    out = [f"-- {run} ({label}): {len(eps)} episodes"]
    for i in range(0, len(eps), EPISODES_PER_ITER):
        c = eps[i:i + EPISODES_PER_ITER]
        laps = [m["elapsed_time_in_milliseconds"] / 1000 for m in c if m["completion_percentage"] == 100]
        mean = sum(m["completion_percentage"] for m in c) / len(c)
        bar = "#" * round(mean / 5)
        out.append(f"{'':28} {i // EPISODES_PER_ITER:4} {len(c):5} {mean:7.0f}% {len(laps):4} "
                   f"{min(laps) if laps else float('nan'):8.2f}  {bar}")
    return out


if __name__ == "__main__":
    base = sys.argv[1] if len(sys.argv) > 1 else "cedc-"
    if "--watch" in sys.argv:
        while True:
            print("\033[2J\033[H" + report(base)); time.sleep(120)
    else:
        print(report(base))
