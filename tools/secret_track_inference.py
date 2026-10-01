"""Which simulator track looks most like the secret evaluation track?

Each uploaded model is a probe with a known speed profile. For every candidate track we predict each
model's best secret-track lap as
    predicted = model's best clean Vegas lap (local eval) * LapSim(candidate) / LapSim(Vegas)
where LapSim uses that model's limits (top speed, grip, centre line vs racing line), and compare to the
portal best laps (log error, all 5 models). If the organizers reused a simulator track it should fit well;
if they built a new one, the best fits still describe its character (length, how fast it flows).

Usage: python tools/secret_track_inference.py [top_n]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lap_time_sim import lap_time, load_track, racing_line  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
# name, eval prefix, portal best lap, top speed, grip, path
PROBES = [("M02", "m02-best", 34.713, 1.0, 4.0, "centre"),
          ("M03", "m03-ckpt31", 15.706, 2.5, 4.0, "centre"),
          ("M04", "m04-m04-final", 14.710, 3.0, 4.0, "centre"),
          ("M05", "m05-m05-snap2", 14.713, 3.0, 4.0, "racing"),
          ("M06", "m06-m06-snap0339", 14.510, 4.0, 5.0, "racing")]


def vegas_best(prefix: str) -> float:
    m = json.loads((ROOT / "evals" / f"{prefix}-Vegas_track" / "EvaluationMetrics.json").read_text())["metrics"]
    clean = [x["elapsed_time_in_milliseconds"] / 1000 for x in m if x["off_track_count"] == 0]
    return min(clean or [x["elapsed_time_in_milliseconds"] / 1000 for x in m])


def sim_times(name: str) -> dict:
    center, width = load_track(name)
    line = racing_line(center, width, 0.30, 600)
    out = {}
    for p, _, _, vmax, grip, path in PROBES:
        out[p] = lap_time(line if path == "racing" else center, vmax, grip, 3.0, 3.0)[0]
    length = float(np.linalg.norm(np.roll(center, -1, 0) - center, axis=1).sum())
    return out, length, width


def main() -> None:
    top_n = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    vb = {p: vegas_best(prefix) for p, prefix, *_ in PROBES}
    actual = {p: best for p, _, best, *_ in PROBES}
    veg, _, _ = sim_times("Vegas_track")
    rows = []
    for f in sorted((ROOT / "tracks").glob("*.npy")):
        name = f.stem
        try:
            sim, length, width = sim_times(name)
        except Exception:
            continue
        pred = {p: vb[p] * sim[p] / veg[p] for p in sim}
        err = np.sqrt(np.mean([np.log(pred[p] / actual[p]) ** 2 for p in pred]))
        rows.append((err, name, length, width, pred))
    rows.sort()
    print("predicted best lap per probe vs portal (s); rms log error (lower = better fit)")
    print(f"{'track':28} {'len m':>6} {'width':>5}  " + "  ".join(f"{p:>6}" for p, *_ in PROBES) + "   err")
    print(f"{'PORTAL (actual)':28} {'':>6} {'':>5}  " + "  ".join(f"{actual[p]:6.2f}" for p, *_ in PROBES))
    for err, name, length, width, pred in rows[:top_n]:
        print(f"{name:28} {length:6.1f} {width:5.2f}  " + "  ".join(f"{pred[p]:6.2f}" for p, *_ in PROBES) + f"  {err:.3f}")


if __name__ == "__main__":
    main()
