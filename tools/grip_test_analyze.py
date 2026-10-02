"""Analyse the grip sweep (tools/wsl/grip_test.sh): how much sideways acceleration does the simulated car hold?

Each test drives a steady circle at a fixed steering angle and commanded speed. If the tyres hold, the car
turns at the kinematic radius R = wheelbase / tan(steer). When it slides, the real radius grows and the
lateral acceleration v^2/R stops rising: that plateau is the grip limit our reward's expert should use.

Usage: python tools/grip_test_analyze.py   (reads evals/grip/s<steer>-v<speed>/robomaker.log)
"""
from __future__ import annotations

import math
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tb_export import _parse_trace_file  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
WHEELBASE = 0.165
SETTLE_S = 1.0          # ignore the first second after each (re)start: the car is still accelerating


def analyse(log: Path):
    rows = []
    for ep in _parse_trace_file(log).values():
        e = [s for s in ep if s["status"] == "in_progress"]
        if len(e) < 10:
            continue
        t = np.array([s["t"] for s in e])
        xy = np.array([[s["x"], s["y"]] for s in e])
        yaw = np.unwrap(np.radians([s["yaw"] for s in e]))
        dt = np.diff(t)
        ok = (dt > 0.02) & (dt < 0.3) & (t[1:] - t[0] > SETTLE_S)
        v = np.linalg.norm(np.diff(xy, axis=0), axis=1) / np.maximum(dt, 1e-3)
        w = np.abs(np.diff(yaw)) / np.maximum(dt, 1e-3)
        rows.append(np.column_stack([v[ok], w[ok]]))
    if not rows:
        return None
    a = np.vstack(rows)
    if len(a) < 5:
        return None
    v, w = np.median(a[:, 0]), np.median(a[:, 1])
    return v, w, len(a)


def main():
    print(f"{'steer':>5} {'cmd v':>5} | {'real v':>6} {'turn rate':>9} | {'R cmd':>6} {'R real':>6} | {'lat acc':>7} {'kinematic':>9}  steps")
    tests = []
    for d in (ROOT / "evals" / "grip").glob("s*-v*"):
        m = re.match(r"s([\d.]+)-v([\d.]+)", d.name)
        if m and (d / "robomaker.log").exists():
            tests.append((float(m.group(1)), float(m.group(2)), d))
    for steer, speed, d in sorted(tests, key=lambda x: (-x[0], x[1])):
        r = analyse(d / "robomaker.log")
        r_cmd = WHEELBASE / math.tan(math.radians(steer))
        if r is None:
            print(f"{steer:5.0f} {speed:5.1f} | no steady data")
            continue
        v, w, n = r
        r_real = v / w if w > 1e-3 else float("inf")
        print(f"{steer:5.0f} {speed:5.1f} | {v:6.2f} {w:9.2f} | {r_cmd:6.2f} {r_real:6.2f} | {v * w:7.2f} {v * v / r_cmd:9.2f}  {n}")
    print("\nlat acc = real speed x turn rate (m/s^2); 'kinematic' = what it would be with no sliding.")
    print("Grip limit: where lat acc stops following the kinematic value as speed rises.")


if __name__ == "__main__":
    main()
