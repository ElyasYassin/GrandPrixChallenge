"""Which local track predicts portal off-tracks? (reads evals/px-<model>-<track>/ from tools/proxy_eval.sh)

Portal outcome per model: clean if score - best lap < 1.0 s (one off-track costs ~3 s on the 3-trial
average). For each track: off-tracks in 5 local trials per model, mean for portal-clean vs portal-off
models, and AUC (probability that a portal-off model has more local off-tracks than a portal-clean one;
1.0 = perfect predictor, 0.5 = useless). Also: correlation of local mean lap (clean models) with the
portal best lap.

Usage: python tools/proxy_compare.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
# model (without cedc-) -> (portal score, portal best lap)
PORTAL = {
    "m10v-c2-end": (7.130, 6.740), "m11c-v1-end": (7.457, 7.059), "m10-summit1-end": (10.096, 9.902),
    "m13-b4-end": (10.157, 10.100), "m10m-s1-end": (10.494, 10.356), "m10-champ2-pause": (10.442, 10.103),
    "m10v-w2-end": (10.425, 6.865), "m11c-w1-end": (10.039, 6.919), "m11c-r1-end": (11.224, 7.256),
    "m13-w4-end": (19.206, 6.333), "m13-w5-end": (13.002, 10.557), "m13c-w1-1317": (9.968, 6.796),
    "m10m-c2-end": (13.920, 10.497),
}


def main():
    res = {}
    for d in (ROOT / "evals").glob("px-*"):
        f = d / "EvaluationMetrics.json"
        if not f.exists() or (d / "INCOMPLETE").exists():
            continue
        name = d.name[3:]
        model = max((m for m in PORTAL if name.startswith(m + "-")), key=len, default=None)
        if not model:
            continue
        m = json.loads(f.read_text())["metrics"]
        t = [x["elapsed_time_in_milliseconds"] / 1000 for x in m]
        res.setdefault(name[len(model) + 1:], {})[model] = (sum(x["off_track_count"] for x in m), float(np.mean(t)), min(t))
    clean = {m for m, (s, b) in PORTAL.items() if s - b < 1.0}
    rows = []
    for track, r in res.items():
        c = [r[m][0] for m in r if m in clean]
        o = [r[m][0] for m in r if m not in clean]
        if not c or not o:
            continue
        auc = np.mean([(oo > cc) + 0.5 * (oo == cc) for oo in o for cc in c])
        lap = [(r[m][2], PORTAL[m][1]) for m in r if m in clean]
        corr = float(np.corrcoef(*zip(*lap))[0, 1]) if len(lap) > 2 else float("nan")
        rows.append((auc, track, np.mean(c), np.mean(o), corr, len(r)))
    print(f"{'track':28} models  off/5 clean  off/5 off   AUC   lap corr")
    for auc, track, mc, mo, corr, n in sorted(rows, reverse=True):
        print(f"{track:28} {n:6}  {mc:10.1f}  {mo:8.1f}  {auc:5.2f}   {corr:6.2f}")
    print(f"\nportal-clean models: {sorted(clean)}")


if __name__ == "__main__":
    main()
