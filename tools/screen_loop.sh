#!/usr/bin/env bash
# Train in hourly blocks and screen every new snapshot before it goes to the portal (strategy R3).
#   each block: 2 x 30-min phases (tools/track_rotation.sh, snapshots every SNAP_MIN), then every new
#   snapshot is evaluated on SCREEN_TRACK (trials from run.env, 5), ranked by off-tracks then mean
#   time, and the best clean ones (up to KEEP) are packaged into submissions/.
# Training and evaluation can't share the machine (simulator cross-talk), so they alternate.
# Stops when C: has less than MIN_FREE_GB free or after BLOCKS blocks.
# usage: bash tools/screen_loop.sh <expdir> <label> <start-prefix> <blocks> [lr]
set -u
EXP=$1; LABEL=$2; PRE=$3; BLOCKS=$4; LR=${5:-0.0001}
SNAP_MIN=${SNAP_MIN:-15}; SCREEN_TRACK=${SCREEN_TRACK:-reInvent2019_wide}; KEEP=${KEEP:-2}; MIN_FREE_GB=${MIN_FREE_GB:-3}
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
OUT="logs/${LABEL}_screen.txt"
wsl() { MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu-22.04 -- "$@" | tr -d '\0\r'; }
MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu-22.04 -- bash -c 'exec sleep infinity' > /dev/null 2>&1 &
KEEPALIVE=$!; trap 'kill $KEEPALIVE 2>/dev/null' EXIT
# phase pairs per block (short tracks most, rI2024 sometimes)
PAIRS=("reInvent2019_wide:w reinvent_base:b" "2024_reinvent_champ_cw:c reInvent2019_wide:w" "reinvent_base:b Bowtie_track:t")
for k in $(seq 1 "$BLOCKS"); do
  free_gb=$(( $(df -BM /c | awk 'NR==2 {gsub("M","",$4); print $4}') / 1024 ))
  if [ "$free_gb" -lt "$MIN_FREE_GB" ]; then echo "== $(date +%T) stopping: only ${free_gb} GB free on C:" >> "$OUT"; break; fi
  pair=${PAIRS[$(( (k - 1) % ${#PAIRS[@]} ))]}
  legs=""; for p in $pair; do legs="$legs ${p%%:*}:${p##*:}$k:30:$LR"; done
  echo "== $(date +%T) block $k from $PRE:$legs" >> "$OUT"
  before=$(grep -c "^snapshot" "logs/${LABEL}_rotation.txt" 2>/dev/null); before=${before:-0}
  rm -f logs/.supervise.pid
  SNAP_MIN=$SNAP_MIN bash tools/track_rotation.sh "$EXP" "$LABEL" "$PRE" last $legs
  snaps=$(grep "^snapshot" "logs/${LABEL}_rotation.txt" | tail -n +$((before + 1)) | awk '{print $2}' | grep -v -- "-end$")   # timed snapshots (the -end one duplicates the last)
  PRE=$(grep "^snapshot" "logs/${LABEL}_rotation.txt" | awk '{print $2}' | grep -- "-end$" | tail -1)
  wsl bash "/mnt/c/Users/Elyas/OneDrive - The University of Colorado Denver/Desktop/projects/GrandPrixChallenge/tools/wsl/bootstrap.sh" > /dev/null
  for s in $snaps; do
    wsl bash /tmp/evalrun.sh "$s" "$SCREEN_TRACK" "scr-${s#cedc-}" | tail -1 | sed "s/^/   $s: /" >> "$OUT"
  done
  # rank: fewest off-tracks, then mean time; package up to KEEP clean ones
  best=$(python - "$SCREEN_TRACK" $snaps <<'PY'
import json, sys
from pathlib import Path
rows = []
for s in sys.argv[2:]:
    f = Path("evals") / f"scr-{s[5:]}" / "EvaluationMetrics.json"
    if not f.exists() or (f.parent / "INCOMPLETE").exists():
        continue
    m = json.loads(f.read_text())["metrics"]
    t = [x["elapsed_time_in_milliseconds"] / 1000 for x in m]
    rows.append((sum(x["off_track_count"] for x in m), sum(t) / len(t), min(t), s))
rows.sort()
for off, mean, best, s in rows:
    print(f"{s} {off} {mean:.2f} {best:.2f}")
PY
)
  echo "$best" | sed 's/^/   rank: /' >> "$OUT"
  n=0
  while read -r s off mean bestlap; do
    [ -z "${s:-}" ] && continue
    [ "$n" -ge "$KEEP" ] && break
    [ "$off" -gt 0 ] && continue
    wsl bash /tmp/fetchmodel.sh "$s" > /dev/null 2>&1
    c=$(ls "models/$s/model" | grep -oE "^model_[0-9]+" | grep -oE "[0-9]+" | sort -n | tail -1)
    f="submissions/${s#cedc-}-ckpt$c.tar.gz"
    python cedc_package_model.py "models/$s/model" "$f" --checkpoint "$c" > /dev/null 2>&1 && \
      python validate_cedc_bundle.py "$f" 2>&1 | grep -q '"ok": true' && echo "   packaged $f (0 off, mean $mean s, best $bestlap s)" >> "$OUT" && n=$((n + 1))
  done <<< "$best"
  [ "$n" -eq 0 ] && echo "   no clean snapshot this block" >> "$OUT"
done
echo "== $(date +%T) screen loop done" >> "$OUT"
