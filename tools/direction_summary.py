"""Progress per driving direction for runs trained with alternating direction.

Direction is measured from the car's actual path (sign of its rotation around the track centre),
so it doesn't depend on episode numbering (which restarts when the simulator is restarted).

Usage: python tools/direction_summary.py cedc-m03b-bothdir [last_n] [track]
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tb_export import LOGS, TRACKS, parse_trace  # noqa: E402


def main() -> None:
    base = sys.argv[1]
    last_n = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    track = sys.argv[3] if len(sys.argv) > 3 else "Vegas_track"
    centre = np.load(TRACKS / f"{track}.npy")[:, :2].mean(axis=0)
    runs = [base] + sorted((int(d.name.rsplit("-", 1)[1]), d.name) for d in LOGS.glob(f"{base}-*")
                           if d.name.rsplit("-", 1)[1].isdigit())
    runs = [base] + [n for _, n in runs[1:]]
    by_dir: dict[str, list[list[dict]]] = {"counterclockwise": [], "clockwise": []}
    for r in runs:
        if not (LOGS / r).exists():
            continue
        for _, ep in sorted(parse_trace(LOGS / r).items()):
            if len(ep) < 5:
                continue
            p = np.array([[s["x"], s["y"]] for s in ep]) - centre
            turn = np.sum(p[:-1, 0] * np.diff(p[:, 1]) - p[:-1, 1] * np.diff(p[:, 0]))
            by_dir["counterclockwise" if turn > 0 else "clockwise"].append(ep)
    for name, eps in by_dir.items():
        recent = eps[-last_n:]
        if not recent:
            print(f"{name:17} no episodes")
            continue
        laps = [e for e in recent if e[-1]["status"] == "lap_complete"]
        line = (f"{name:17} total {len(eps):4} eps | last {len(recent)}: mean progress "
                f"{np.mean([e[-1]['progress'] for e in recent]):.0f}%, laps {len(laps)}")
        if laps:
            line += f", lap time {np.mean([e[-1]['t'] - e[0]['t'] for e in laps]):.1f}s"
        print(line)


if __name__ == "__main__":
    main()
