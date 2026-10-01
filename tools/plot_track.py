"""Draw a DeepRacer track map and list its corners.

Usage:
    python tools/plot_track.py Vegas_track
    python tools/plot_track.py reinvent_base --out tracks/reinvent_base.png

Track files (tracks/<name>.npy) hold one row per waypoint:
    [center_x, center_y, inner_x, inner_y, outer_x, outer_y]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection

ROOT = Path(__file__).resolve().parent.parent
CORNER_RADIUS_M = 1.5  # sections tighter than this count as a corner


def load(name: str) -> np.ndarray:
    w = np.load(ROOT / "tracks" / f"{name}.npy")
    if np.allclose(w[0, :2], w[-1, :2]):  # drop duplicated closing point
        w = w[:-1]
    return w


def turn_radius(center: np.ndarray, span: int = 2) -> np.ndarray:
    """Signed radius (m) of the circle through points i-span, i, i+span. + = left turn."""
    a, b, c = np.roll(center, span, 0), center, np.roll(center, -span, 0)
    ab, bc, ca = np.linalg.norm(b - a, axis=1), np.linalg.norm(c - b, axis=1), np.linalg.norm(a - c, axis=1)
    cross = (b - a)[:, 0] * (c - b)[:, 1] - (b - a)[:, 1] * (c - b)[:, 0]
    with np.errstate(divide="ignore", invalid="ignore"):
        r = ab * bc * ca / (2 * cross)
    r[~np.isfinite(r)] = np.inf
    return r


def find_corners(center: np.ndarray, radius: np.ndarray) -> list[dict]:
    tight = np.abs(radius) < CORNER_RADIUS_M
    n = len(center)
    if tight.all() or not tight.any():
        return []
    start = int(np.argmin(tight))  # begin scanning on a straight so corners don't wrap
    corners, i = [], 0
    while i < n:
        k = (start + i) % n
        if tight[k]:
            idx = []
            while i < n and tight[(start + i) % n]:
                idx.append((start + i) % n)
                i += 1
            r = radius[idx]
            heading = np.degrees(np.arctan2(*np.diff(center[[idx[0], idx[-1]]], axis=0)[0][::-1]))
            corners.append({
                "from": idx[0], "to": idx[-1], "apex": idx[int(np.argmin(np.abs(r)))],
                "dir": "left" if np.median(r) > 0 else "right",
                "min_radius": float(np.min(np.abs(r))),
            })
        else:
            i += 1
    return corners


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("track")
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    w = load(args.track)
    center, inner, outer = w[:, 0:2], w[:, 2:4], w[:, 4:6]
    seg = np.linalg.norm(np.diff(np.vstack([center, center[:1]]), axis=0), axis=1)
    length = seg.sum()
    width = float(np.median(np.linalg.norm(outer - inner, axis=1)))
    x, y = center[:, 0], center[:, 1]
    area = 0.5 * np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y)
    radius = turn_radius(center)
    corners = find_corners(center, radius)

    print(f"{args.track}: {len(w)} waypoints, length {length:.2f} m, width {width:.2f} m, "
          f"{'counterclockwise' if area > 0 else 'clockwise'}")
    print(f"{len(corners)} corners (radius < {CORNER_RADIUS_M} m):")
    for i, c in enumerate(corners, 1):
        print(f"  T{i}: waypoints {c['from']:>3}-{c['to']:<3} {c['dir']:<5} min radius {c['min_radius']:.2f} m (apex wp {c['apex']})")

    fig, ax = plt.subplots(figsize=(11, 8))
    for border in (inner, outer):
        ax.plot(*np.vstack([border, border[:1]]).T, color="0.35", lw=1.5)
    ax.fill(*np.vstack([outer, outer[:1]]).T, color="0.92", zorder=0)
    ax.fill(*np.vstack([inner, inner[:1]]).T, color="white", zorder=0)

    # centre line coloured by tightness (1 / radius)
    pts = np.vstack([center, center[:1]])
    segs = np.stack([pts[:-1], pts[1:]], axis=1)
    lc = LineCollection(segs, cmap="plasma_r", linewidths=4)
    lc.set_array(np.clip(1 / np.abs(radius), 0, 1 / 0.5))
    ax.add_collection(lc)
    fig.colorbar(lc, ax=ax, shrink=0.7, label="tightness = 1 / radius (1/m)")

    for i in range(0, len(center), 10):
        ax.annotate(str(i), center[i], fontsize=7, color="0.3", xytext=(4, 4), textcoords="offset points")
    for i, c in enumerate(corners, 1):
        ax.annotate(f"T{i}", center[c["apex"]], fontsize=12, weight="bold", color="crimson",
                    xytext=(10, -14), textcoords="offset points")

    ax.plot(*center[0], "o", color="limegreen", ms=12, zorder=5, label="start (wp 0)")
    ax.annotate("", center[3], center[0], arrowprops=dict(arrowstyle="-|>", color="limegreen", lw=2.5))
    ax.set_title(f"{args.track}: {length:.2f} m, {width:.2f} m wide, "
                 f"{'counterclockwise' if area > 0 else 'clockwise'}, {len(corners)} corners")
    ax.set_aspect("equal")
    ax.legend(loc="upper right")
    ax.grid(alpha=0.2)

    out = args.out or ROOT / "tracks" / f"{args.track}.png"
    fig.savefig(out, dpi=130, bbox_inches="tight")
    print(f"saved {out}")


if __name__ == "__main__":
    main()
