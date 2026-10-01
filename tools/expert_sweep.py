"""Tune the reward's expert in simulation: which settings give the fastest *robust* laps?

The policy imitates the expert imperfectly, so each setting is scored in closed loop
(tools/expert_closed_loop.py: 1-step delay + steering noise) on several tracks: mean lap time
including off-track resets, and off-track count.

Usage: STEER_NOISE=7 python tools/expert_sweep.py <reward_function.py>
"""
from __future__ import annotations

import itertools
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import expert_closed_loop as E  # noqa: E402
from test_reward import Track, load_module  # noqa: E402

TRACKS = ["Vegas_track", "2022_summit_speedway", "2024_reinvent_champ_cw", "reInvent2019_track", "reinvent_base"]
GRID = dict(MAX_LAT_ACC=[4.0, 5.0, 6.0], MAX_BRAKE=[2.0, 3.0, 4.0], LOOK_BASE=[0.45, 0.6, 0.75])


def main():
    path = sys.argv[1]
    tracks = {t: Track(t) for t in TRACKS}
    rows = []
    for vals in itertools.product(*GRID.values()):
        cfg = dict(zip(GRID, vals))
        mod = load_module(path)
        mod.MAX_LAT_ACC, mod.MAX_BRAKE = cfg["MAX_LAT_ACC"], cfg["MAX_BRAKE"]
        mod._lookahead_m = lambda v, b=cfg["LOOK_BASE"]: b + 0.15 * v
        rs = [E.drive(mod, tracks[t], s) for t in TRACKS for s in range(2)]
        rows.append((np.mean([r["time"] for r in rs]), np.mean([r["offs"] for r in rs]), cfg))
        print(f"{cfg}  lap {rows[-1][0]:5.2f}s  offs {rows[-1][1]:.1f}", flush=True)
    print("\nbest (mean lap time incl. off-track resets):")
    for t, o, cfg in sorted(rows, key=lambda r: r[0])[:6]:
        print(f"  {t:5.2f}s  offs {o:.1f}  {cfg}")


if __name__ == "__main__":
    main()
