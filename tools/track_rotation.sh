#!/usr/bin/env bash
# Train one run across several tracks in turn (one simulator, so tracks take turns). Each leg is a new
# DRfC run on its own world, pretrained from the previous leg's last checkpoint, kept alive by
# supervise.sh, snapshotted every SNAP_MIN minutes and at its end as cedc-<label>-<tag>-HHMM.
# PRE=none trains the first leg from scratch; LR=<lr> sets the learning rate (custom_files/hyperparameters.json).
# Run from the project root in Git Bash:
#   bash tools/track_rotation.sh <expdir> <label> <pretrained-prefix> <ckpt: best|last> <world:tag:minutes[:lr]>...
# e.g. bash tools/track_rotation.sh model08-standins m08 cedc-m07-snap1332 best \
#        2024_reinvent_champ_cw:champ:75 2022_summit_speedway:summit:75 Vegas_track:vegas:30
set -u
EXP=$1; LABEL=$2; PRE=$3; CKPT=$4; shift 4
SNAP_MIN=${SNAP_MIN:-30}
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
LOGF="logs/${LABEL}_rotation.txt"
wslrun() { MSYS_NO_PATHCONV=1 timeout 300 wsl.exe -d Ubuntu-22.04 -- bash -c "$1" | tr -d '\0\r'; }
curprefix() { wslrun "grep ^DR_LOCAL_S3_MODEL_PREFIX= ~/deepracer-for-cloud/run.env | cut -d= -f2"; }
# Keep WSL alive for the whole rotation: between legs no supervisor is attached, WSL went idle and
# shut down, /tmp was wiped and start_run.sh "did not exist" (2026-10-02: every leg kept the first track).
MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu-22.04 -- bash -c 'exec sleep infinity' > /dev/null 2>&1 &
KEEPALIVE=$!
trap 'kill $KEEPALIVE 2>/dev/null' EXIT
# install the current helpers (start_run.sh runs before supervise.sh bootstraps)
wslrun "sed 's/\r$//' '/mnt/c/Users/Elyas/OneDrive - The University of Colorado Denver/Desktop/projects/GrandPrixChallenge/tools/wsl/bootstrap.sh' | bash > /dev/null"
for leg in "$@"; do
  IFS=: read -r world tag minutes lr <<< "$leg"
  prefix="cedc-${LABEL}-${tag}"
  stop_at=$(date -d "+${minutes} minutes" +%H:%M)
  # reinstall helpers if WSL restarted anyway (start_run.sh must exist before the leg starts)
  wslrun "[ -f /tmp/start_run.sh ] && echo ok" | grep -q ok || wslrun "sed 's/\r$//' '/mnt/c/Users/Elyas/OneDrive - The University of Colorado Denver/Desktop/projects/GrandPrixChallenge/tools/wsl/bootstrap.sh' | bash > /dev/null"
  { echo "== $(date +%T) leg $tag: $world for $minutes min, lr ${lr:-${LR:-unchanged}} (until $stop_at), from $PRE ($CKPT)"
    MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu-22.04 -- bash /tmp/start_run.sh "$EXP" "$prefix" "$PRE" "$CKPT" "$world" "${lr:-${LR:-}}" | tr -d '\0'; } >> "$LOGF" 2>&1
  sup_out="logs/${LABEL}_${tag}_supervise.txt"
  MAX_SIM_MEM_MIB=${MAX_SIM_MEM_MIB:-4000} HARD_SIM_MEM_MIB=${HARD_SIM_MEM_MIB:-8500} bash tools/supervise.sh "$stop_at" > "$sup_out" 2>&1 &
  sup=$!
  next=$(( $(date +%s) + SNAP_MIN * 60 ))
  while kill -0 $sup 2>/dev/null; do
    sleep 30
    if [ "$(date +%s)" -ge "$next" ] && kill -0 $sup 2>/dev/null; then
      p=$(curprefix); wslrun "bash /tmp/snapshot.sh $p cedc-${LABEL}-${tag}-$(date +%H%M)" >> "$LOGF" 2>&1
      next=$(( next + SNAP_MIN * 60 ))
    fi
  done
  tail -1 "$sup_out" >> "$LOGF"
  wait $sup; rc=$?
  if [ "$rc" -eq 4 ]; then echo "== $(date +%T) rotation stopped: C: is almost full" >> "$LOGF"; exit 4; fi
  # supervisor auto-resumes may have renamed the run (<prefix>-2, ...): continue from whatever is current
  PRE=$(curprefix); CKPT=last
  wslrun "bash /tmp/snapshot.sh $PRE cedc-${LABEL}-${tag}-end" >> "$LOGF" 2>&1
done
echo "== $(date +%T) rotation done" >> "$LOGF"
