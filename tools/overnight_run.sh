#!/usr/bin/env bash
# Unattended overnight pipeline for one training run (run from the project root in Git Bash):
#   every SNAP_MIN minutes until STOP_AT: snapshot the current checkpoint + log a check-in
#   after the supervisor's planned stop: snapshot the final checkpoint, evaluate every snapshot on
#   the 4 standard tracks, write a ranked summary to logs/<label>_overnight_summary.txt
# usage: bash tools/overnight_run.sh <run-base> <label> <STOP_AT HH:MM> <supervisor-output-file> [SNAP_MIN]
set -u
BASE=$1; LABEL=$2; STOP_AT=$3; SUP_OUT=$4; SNAP_MIN=${5:-30}
source "$(dirname "$0")/env.sh"; cd "$ROOT"
WSLRUN_TIMEOUT=300
end=$(date -d "$STOP_AT" +%s)
LOGF="logs/${LABEL}_overnight.txt"
snaps=()
while [ $(( $(date +%s) + SNAP_MIN * 60 )) -le "$end" ]; do
  sleep $((SNAP_MIN * 60))
  name="cedc-${LABEL}-snap$(date +%H%M)"
  prefix=$(wslrun "grep ^DR_LOCAL_S3_MODEL_PREFIX= ~/deepracer-for-cloud/run.env | cut -d= -f2")
  { echo "== $(date +%T) check-in"; bash tools/checkin.sh "$BASE" "$SUP_OUT"; wslrun "bash /tmp/snapshot.sh $prefix $name"; } >> "$LOGF" 2>&1
  snaps+=("$name")
done
until grep -q "planned stop" "$SUP_OUT" 2>/dev/null; do sleep 30; done
prefix=$(wslrun "grep ^DR_LOCAL_S3_MODEL_PREFIX= ~/deepracer-for-cloud/run.env | cut -d= -f2")
wslrun "bash /tmp/snapshot.sh $prefix cedc-${LABEL}-final" >> "$LOGF" 2>&1
snaps+=("cedc-${LABEL}-final")
echo "== $(date +%T) evaluating: ${snaps[*]}" >> "$LOGF"
bootstrap > /dev/null
for s in "${snaps[@]}"; do
  wsl_exec bash /tmp/eval_candidates.sh "$LABEL" "$s" 2>&1 | tr -d '\0' >> "$LOGF"
done
python - "$LABEL" > "logs/${LABEL}_overnight_summary.txt" 2>&1 <<'PY'
import json, sys
from pathlib import Path
import numpy as np
label = sys.argv[1]
T = ["Vegas_track", "2022_summit_speedway", "reinvent_base", "2024_reinvent_champ_cw"]
rows = []
for d in sorted(Path("evals").glob(f"{label}-*-Vegas_track")):
    c = d.name[: -len("-Vegas_track")]
    means, offs, ok = [], 0, True
    for t in T:
        f = Path("evals") / f"{c}-{t}" / "EvaluationMetrics.json"
        if not f.exists():
            ok = False; break
        m = json.loads(f.read_text())["metrics"]
        means.append(np.mean([x["elapsed_time_in_milliseconds"] / 1000 for x in m]))
        offs += sum(x["off_track_count"] for x in m)
    if ok:
        rows.append((np.mean(means), c, means, offs))
print("candidate                      Vegas  Summit  rI2018  rI2024CW   mean  off-tracks")
for mean, c, ms, offs in sorted(rows):
    print(f"{c:30} " + " ".join(f"{v:6.2f}" for v in ms) + f"  {mean:6.2f}  {offs:4}")
print("\nreference: M05 snap2 (portal 17.877) mean 16.51, 14 off-tracks; M04 final (portal 18.008) mean 17.04")
PY
python tools/efficiency.py >> "logs/${LABEL}_overnight_summary.txt" 2>/dev/null
echo "== $(date +%T) done" >> "$LOGF"
cat "logs/${LABEL}_overnight_summary.txt"
