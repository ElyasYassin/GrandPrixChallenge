"""Compact performance summary of a run, compared with the baseline at the same episode count.

Usage: python tools/run_summary.py cedc-m02-imitation
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tb_export import LOGS, load_metrics, parse_trace  # noqa: E402

BASELINE = ["cedc-m01-baseline-gpu", "cedc-m01-baseline-gpu-2"]  # continued run, concatenated


def training_episodes(run: str) -> list[dict]:
    d = LOGS / run
    return [m for m in load_metrics(d) if m["phase"] == "training"] if d.exists() else []


def window_stats(eps: list[dict]) -> dict:
    p = [m["completion_percentage"] for m in eps]
    return {"n": len(eps), "mean": float(np.mean(p)) if p else 0.0, "max": max(p) if p else 0,
            "laps": sum(m["episode_status"] == "Lap complete" for m in eps)}


def main() -> None:
    runs = sys.argv[1:]  # a run and its continuations, in order
    if len(runs) == 1:  # base name only: include auto-resumed continuations <base>-2, <base>-3, ...
        base = runs[0]
        conts = sorted((int(d.name.rsplit("-", 1)[1]), d.name) for d in LOGS.glob(f"{base}-*")
                       if d.name.rsplit("-", 1)[1].isdigit())
        runs = [base] + [name for _, name in conts]
    run = " + ".join(runs)
    eps = [e for r in runs for e in training_episodes(r)]
    n = len(eps)
    if n == 0:
        print(f"{run}: no episodes yet")
        return
    last = window_stats(eps[-20:])
    total_laps = sum(m["episode_status"] == "Lap complete" for m in eps)
    base = [e for r in BASELINE for e in training_episodes(r)]
    base_same = window_stats(base[max(0, n - 20):n]) if len(base) >= n else None

    trace: dict = {}
    for r in runs:
        if (LOGS / r).exists():
            t = parse_trace(LOGS / r)
            trace.update({(r, k): v for k, v in t.items()})
    recent = [trace[k] for k in list(trace)[-20:]]
    steer_change = np.mean([np.mean(np.abs(np.diff([s["steer"] for s in ep]))) for ep in recent if len(ep) > 1]) if recent else float("nan")
    full_lock = np.mean([abs(s["steer"]) >= 29 for ep in recent for s in ep]) if recent else float("nan")
    speed = np.mean([s["speed"] for ep in recent for s in ep]) if recent else float("nan")
    lap_times = [ep[-1]["t"] - ep[0]["t"] for ep in trace.values() if ep and ep[-1]["status"] == "lap_complete"]
    off = Counter(ep[-1]["wp"] // 10 * 10 for ep in recent if ep and ep[-1]["status"] in ("off_track", "reversed"))

    print(f"{run}: {n} episodes (~{n // 20} iterations)")
    print(f"  last 20 eps : progress mean {last['mean']:.1f}%  max {last['max']}%  laps {last['laps']}/20   (total laps {total_laps})")
    if base_same:
        print(f"  baseline @ same episodes: progress mean {base_same['mean']:.1f}%  max {base_same['max']}%  laps {base_same['laps']}")
    print(f"  driving     : steering change {steer_change:.1f} deg/step (baseline 23.3), full lock {full_lock:.0%} (baseline 40%), mean speed {speed:.2f} m/s")
    if lap_times:
        print(f"  lap times   : best {min(lap_times):.1f}s, mean {np.mean(lap_times):.1f}s over {len(lap_times)} laps")
    if off:
        print("  off-track   : " + ", ".join(f"wp {k}-{k + 9}: {v}" for k, v in off.most_common(4)))


if __name__ == "__main__":
    main()
