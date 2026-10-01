"""Theoretical best lap time on a DeepRacer track (quasi-steady-state lap simulation).

For a given path (centre line or our racing line), the fastest lap under the constraints:
  1. corner limit: v <= sqrt(max_lat_acc / |curvature|), and v <= v_max
  2. forward pass: accelerate out of corners at most max_accel
  3. backward pass: brake into corners at most max_brake (as late as possible)
The result is a lower bound for any driver with those limits on that path, i.e. the time our
model could reach if it drove perfectly.

Usage:
    python tools/lap_time_sim.py Vegas_track
    python tools/lap_time_sim.py 2022_summit_speedway --grip 4 5 6 --vmax 2.5 3 4
"""
from __future__ import annotations

import argparse
import importlib.util
import itertools
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
REWARD_WITH_LINE = ROOT / "experiments" / "model05-racingline" / "reward_function.py"


def load_track(name: str):
    w = np.load(ROOT / "tracks" / f"{name}.npy")
    if np.allclose(w[0, :2], w[-1, :2]):
        w = w[:-1]
    width = float(np.median(np.linalg.norm(w[:, 4:6] - w[:, 2:4], axis=1)))
    return w[:, 0:2], width


def racing_line(center: np.ndarray, width: float, margin: float, iterations: int) -> np.ndarray:
    spec = importlib.util.spec_from_file_location("rf05", REWARD_WITH_LINE)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.LINE_MARGIN_M, m.LINE_ITERATIONS = margin, iterations
    return np.array(m.racing_line([tuple(p) for p in center], width))


def curvature(path: np.ndarray, span: int = 2) -> np.ndarray:
    """|curvature| (1/m) through points i-span, i, i+span (span smooths waypoint noise)."""
    a, b, c = np.roll(path, span, 0), path, np.roll(path, -span, 0)
    ab, bc, ca = (np.linalg.norm(b - a, axis=1), np.linalg.norm(c - b, axis=1), np.linalg.norm(a - c, axis=1))
    cross = np.abs((b - a)[:, 0] * (c - b)[:, 1] - (b - a)[:, 1] * (c - b)[:, 0])
    with np.errstate(divide="ignore", invalid="ignore"):
        k = 2 * cross / (ab * bc * ca)
    return np.nan_to_num(k)


def lap_time(path: np.ndarray, v_max: float, lat: float, accel: float, brake: float):
    ds = np.linalg.norm(np.roll(path, -1, 0) - path, axis=1)       # segment i -> i+1
    k = curvature(path)
    with np.errstate(divide="ignore"):
        v = np.minimum(v_max, np.sqrt(lat / np.maximum(k, 1e-9)))
    n = len(path)
    for _ in range(3):  # a few laps of passes so the closed loop converges
        for i in range(n):                      # forward: limited acceleration
            j = (i + 1) % n
            v[j] = min(v[j], math.sqrt(v[i] ** 2 + 2 * accel * ds[i]))
        for i in range(n - 1, -1, -1):          # backward: limited braking
            j = (i + 1) % n
            v[i] = min(v[i], math.sqrt(v[j] ** 2 + 2 * brake * ds[i]))
    t = float(np.sum(2 * ds / (v + np.roll(v, -1))))
    return t, float(ds.sum()), v


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("tracks", nargs="+")
    ap.add_argument("--vmax", nargs="+", type=float, default=[2.5, 3.0, 4.0])
    ap.add_argument("--grip", nargs="+", type=float, default=[4.0, 6.0], help="max lateral acceleration m/s^2")
    ap.add_argument("--accel", type=float, default=3.0)
    ap.add_argument("--brake", type=float, default=3.0)
    ap.add_argument("--margin", type=float, default=0.30, help="racing line distance from the edges (m)")
    ap.add_argument("--iterations", type=int, default=2000)
    args = ap.parse_args()

    for name in args.tracks:
        center, width = load_track(name)
        paths = {"centre line": center, "racing line": racing_line(center, width, args.margin, args.iterations)}
        print(f"\n{name}  (width {width:.2f} m, accel {args.accel}, brake {args.brake} m/s^2)")
        print(f"  {'path':12} {'length':>7} {'v_max':>6} {'grip':>5}   best lap   avg speed")
        for (label, path), v_max, lat in itertools.product(paths.items(), args.vmax, args.grip):
            t, length, v = lap_time(path, v_max, lat, args.accel, args.brake)
            print(f"  {label:12} {length:6.2f}m {v_max:5.1f} {lat:5.1f}   {t:6.2f} s   {length / t:5.2f} m/s")


if __name__ == "__main__":
    main()
