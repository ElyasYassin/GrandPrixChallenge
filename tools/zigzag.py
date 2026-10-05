"""How much does a model weave on straights? Reads evaluation traces (evals/<name>/robomaker.log).

A step counts as "straight" when the centre line within 1.5 m ahead turns less than 15 degrees.
Reports, on straights: steps steering >= 12 deg, steering sign flips per second, mean |steering|.
Usage: python3 tools/zigzag.py <eval-name-glob>...   e.g. python3 tools/zigzag.py "m12a-*csa3-end-*"
"""
import glob
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
TRACKS = ROOT / "tracks"


def heading_change_ahead(center, i, dist=1.5):
    """Absolute turn (deg) of the centre line over the next `dist` metres from waypoint i."""
    n = len(center)
    j, d = i, 0.0
    while d < dist and j < i + n:
        d += np.linalg.norm(center[(j + 1) % n] - center[j % n]); j += 1
    def hd(k):
        v = center[(k + 1) % n] - center[k % n]
        return math.degrees(math.atan2(v[1], v[0]))
    total, prev = 0.0, hd(i)
    for k in range(i + 1, j):
        h = hd(k); total += (h - prev + 180) % 360 - 180; prev = h
    return abs(total)


def analyse(eval_dir: Path):
    world = eval_dir.name.rsplit("-", 1)[-1]
    for cand in [world, *[w for w in [world.replace("_cw", ""), world.replace("_ccw", "")]]]:
        f = TRACKS / f"{cand}.npy"
        if f.exists():
            break
    else:
        return None
    center = np.load(f)[:, 0:2]
    rows = []
    for line in (eval_dir / "robomaker.log").read_text(errors="ignore").splitlines():
        if "SIM_TRACE_LOG:" not in line:
            continue
        p = line.split("SIM_TRACE_LOG:")[1].split(",")
        if p[15] != "in_progress":
            continue
        rows.append((int(p[0]), float(p[5]), int(p[12])))
    straight = [(ep, s) for ep, s, wp in rows if heading_change_ahead(center, wp) < 15]
    if not straight:
        return None
    steer = np.array([s for _, s in straight])
    flips = sum(1 for a, b in zip(straight, straight[1:]) if a[0] == b[0] and a[1] * b[1] < 0)
    return world, len(straight), float(np.mean(np.abs(steer) >= 12)), flips / (len(straight) / 15), float(np.mean(np.abs(steer)))


if __name__ == "__main__":
    print(f"{'eval':55} {'steps':>6} {'>=12deg':>8} {'flips/s':>8} {'mean|deg|':>9}")
    for pat in sys.argv[1:]:
        for d in sorted(glob.glob(str(ROOT / "evals" / pat))):
            r = analyse(Path(d))
            if r:
                print(f"{Path(d).name:55} {r[1]:6} {r[2]:8.0%} {r[3]:8.2f} {r[4]:9.1f}")
