"""Generalization check: how close each model gets to the theoretical best lap on each track.

efficiency = theoretical best lap (centre line, the model's own top speed, 4 m/s^2 grip) / actual mean
evaluation time (off-track penalties included). A model that understands driving scores similarly on
the training track (Vegas) and on unseen tracks; a model that memorized Vegas drops on the others.

Usage: python tools/efficiency.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lap_time_sim import lap_time, load_track  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TRACKS = ["Vegas_track", "2022_summit_speedway", "reinvent_base", "2024_reinvent_champ_cw"]
# eval folder prefix -> (label, model top speed)
MODELS = {"m02-best": ("Model 02 ckpt 11", 1.0), "m03-ckpt31": ("Model 03 ckpt 31 (uploaded)", 2.5),
          "m03b-m03b-snap0400": ("03b 04:00", 2.5), "m03b-m03b-final": ("03b final", 2.5),
          "m03b-m03b-snap0500": ("03b 05:00", 2.5)}


def best(track: str, vmax: float) -> float:
    center, _ = load_track(track)
    return lap_time(center, vmax, 4.0, 3.0, 3.0)[0]


def main() -> None:
    models = dict(MODELS)
    for d in sorted((ROOT / "evals").iterdir()):
        for t in TRACKS:
            if d.name.endswith("-" + t):
                prefix = d.name[: -len(t) - 1]
                if prefix.startswith(("m04", "m05")) and prefix not in models:
                    models[prefix] = (prefix, 3.0)
    print(f"{'model':28} " + " ".join(f"{t[:14]:>15}" for t in TRACKS) + "   unseen avg   gap vs Vegas")
    for prefix, (label, vmax) in models.items():
        effs = []
        for t in TRACKS:
            f = ROOT / "evals" / f"{prefix}-{t}" / "EvaluationMetrics.json"
            if not f.exists():
                effs.append(None); continue
            m = json.loads(f.read_text())["metrics"]
            actual = np.mean([x["elapsed_time_in_milliseconds"] / 1000 for x in m])
            effs.append(best(t, vmax) / actual)
        if all(e is None for e in effs):
            continue
        unseen = [e for e in effs[1:] if e is not None]
        row = " ".join(f"{(e * 100):14.0f}%" if e is not None else f"{'-':>15}" for e in effs)
        u = np.mean(unseen) if unseen else float("nan")
        gap = (effs[0] - u) * 100 if effs[0] is not None and unseen else float("nan")
        print(f"{label:28} {row}   {u * 100:9.0f}%   {gap:+8.0f} pts")


if __name__ == "__main__":
    main()
