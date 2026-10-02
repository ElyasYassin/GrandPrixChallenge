#!/usr/bin/env bash
# Supervise a local DRfC training run from Windows (Git Bash). DRfC runs in compose mode.
#   every 2 min: save logs from WSL -> logs/<prefix>/, update TensorBoard (tb/) in place
#   if the simulators stop: save logs, resume from the last checkpoint as <prefix>-N (max 5 times)
#   stops training at STOP_AT (HH:MM)
# usage: bash tools/supervise.sh 18:15
set -u
STOP_AT="$1"
MAX_RESUMES=20
MAX_SIM_MEM_MIB=${MAX_SIM_MEM_MIB:-9000}   # planned restart above this (WSL has 16 GB); override via env
STALL_MIN=${STALL_MIN:-8}                  # minutes without a new trainer episode -> full resume
HARD_SIM_MEM_MIB=${HARD_SIM_MEM_MIB:-11000}  # restart the simulator even mid-iteration above this
EPISODES_PER_ITER=20                       # hyperparameters.json num_episodes_between_training
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# only one supervisor at a time: two would both auto-resume the same crash
LOCK="$ROOT/logs/.supervise.pid"
if [ -f "$LOCK" ] && kill -0 "$(cat "$LOCK")" 2>/dev/null; then
  echo "another supervisor is running (pid $(cat "$LOCK")); stop it first"; exit 1
fi
echo $$ > "$LOCK"
trap 'rm -f "$LOCK"' EXIT
wslrun() { MSYS_NO_PATHCONV=1 timeout 120 wsl.exe -d Ubuntu-22.04 -- bash -c "$1" | tr -d '\0\r'; }
end=$(date -d "$STOP_AT" +%s)
[ "$end" -le "$(date +%s)" ] && end=$((end + 86400))   # a stop time after midnight means tomorrow

# WSL shuts its VM down when no Windows process is attached (even with Docker running inside),
# which kills training. Keep one idle connection open for as long as we supervise.
start_keepalive() {
  MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu-22.04 -- bash -c 'exec sleep infinity' > /dev/null 2>&1 &
  KEEPALIVE=$!
}
# WSL's /tmp is wiped on every WSL restart: (re)install helpers, DRfC temp dir, start MinIO
bootstrap() {
  wslrun "sed 's/\r$//' '/mnt/c/Users/Elyas/OneDrive - The University of Colorado Denver/Desktop/projects/GrandPrixChallenge/tools/wsl/bootstrap.sh' | bash"
}
start_keepalive
trap 'rm -f "$LOCK"; kill $KEEPALIVE 2>/dev/null' EXIT
bootstrap
resumes=0
simrestarts=0

ensure_tensorboard() {  # start once; tb_export.py updates runs in place, no restarts
  curl -s -o /dev/null localhost:6006/ || { nohup python -m tensorboard.main --logdir tb --port 6006 --reload_interval 15 > /dev/null 2>&1 & }
}

while true; do
  wslrun "bash /tmp/savelogs.sh" > /dev/null 2>&1
  python tools/tb_export.py 2>&1 | grep -E "skipped"
  ensure_tensorboard
  # WSL's virtual disk lives on C:. When C: filled up (2026-10-02 01:44) Linux got I/O errors and
  # crashed; stop cleanly (checkpoints are safe in MinIO) before that happens.
  free_mib=$(df -BM /c | awk 'NR==2 {gsub("M","",$4); print $4}')
  if [ -n "$free_mib" ] && [ "$free_mib" -lt "${MIN_FREE_MIB:-2000}" ]; then
    wslrun "bash /tmp/drstop.sh"
    echo "STOPPED at $(date +%T): only ${free_mib} MiB free on C:"; exit 4
  fi
  if [ "$(date +%s)" -ge "$end" ]; then
    wslrun "bash /tmp/drstop.sh"
    python tools/tb_export.py > /dev/null 2>&1
    echo "planned stop at $(date +%T) after $resumes auto-resumes, $simrestarts simulator restarts"; exit 0
  fi
  status=$(wslrun "bash /tmp/simstatus.sh")          # running=N exited=M mem_mib=K
  running=$(echo "$status" | sed -nE 's/.*running=([0-9]+).*/\1/p')
  exited=$(echo "$status" | sed -nE 's/.*exited=([0-9]+).*/\1/p')
  mem=$(echo "$status" | sed -nE 's/.*mem_mib=([0-9]+).*/\1/p')
  trainer=$(echo "$status" | sed -nE 's/.* trainer=([0-9]+).*/\1/p')
  teps=$(echo "$status" | sed -nE 's/.*trainer_eps=([0-9]+).*/\1/p')
  if ! echo "$status" | grep -q "running="; then   # empty, or a wsl.exe error message
    # seen 2026-10-01: the Ubuntu distribution stopped and would not start again
    # ("Wsl/Service/CreateInstance/E_FAIL") until `wsl --shutdown`. After 3 failed checks, restart WSL.
    down=$(( ${down:-0} + 1 ))
    echo "$(date +%T) WSL not responding ($down)"
    if [ "$down" -ge 3 ]; then
      echo "$(date +%T) restarting WSL"; kill $KEEPALIVE 2>/dev/null
      wsl.exe --shutdown > /dev/null 2>&1; sleep 10
      start_keepalive; down=0; wsl_restarted=1
    fi
    sleep 30; continue
  fi
  down=0
  if [ "${wsl_restarted:-0}" -eq 1 ]; then
    # /tmp was wiped and every container stopped: reinstall helpers, then resume from the last checkpoint
    wsl_restarted=0; bootstrap > /dev/null 2>&1
    resumes=$((resumes + 1))
    new=$(wslrun "bash /tmp/autoresume.sh" | tail -1)
    echo "$(date +%T) WSL restarted -> auto-resume #$resumes as $new"
    last_teps=x; sleep 60; continue
  fi
  # Stuck trainer: the simulator keeps driving but the trainer stops receiving episodes (seen
  # after a simulator-only restart). No new trainer episode for STALL_MIN minutes -> full resume.
  now=$(date +%s)
  if [ "${teps:-0}" != "${last_teps:-x}" ]; then last_teps=$teps; last_change=$now; fi
  if [ "${trainer:-0}" -gt 0 ] && [ "${running:-0}" -gt 0 ] && [ $((now - ${last_change:-$now})) -gt $((STALL_MIN * 60)) ]; then
    resumes=$((resumes + 1))
    new=$(wslrun "bash /tmp/autoresume.sh" | tail -1)
    echo "$(date +%T) trainer stuck at ${teps} episodes for > ${STALL_MIN} min -> full resume #$resumes as $new"
    last_teps=x; sleep 60; continue
  fi
  # The simulator leaks memory with WSL GPU rendering (about 0.7-1 GB/min) and sometimes crashes.
  # While the trainer is alive, restarting just the simulator continues the same run (no reset),
  # BUT only between iterations: restarted mid-iteration, the trainer waits forever for the lost
  # episodes (seen at 58/60). So above MAX_SIM_MEM_MIB wait for a multiple of EPISODES_PER_ITER
  # trainer episodes, unless memory passes HARD_SIM_MEM_MIB.
  at_boundary=0; [ -n "${teps:-}" ] && [ "${teps}" -gt 0 ] && [ $((teps % EPISODES_PER_ITER)) -eq 0 ] && at_boundary=1
  if [ "${trainer:-0}" -gt 0 ] && { [ "${exited:-0}" -gt 0 ] || { [ "${mem:-0}" -gt "$MAX_SIM_MEM_MIB" ] && { [ "$at_boundary" -eq 1 ] || [ "${mem:-0}" -gt "$HARD_SIM_MEM_MIB" ]; }; }; }; then
    simrestarts=$((simrestarts + 1))
    msg=$(wslrun "bash /tmp/simrestart.sh" | tail -1)
    echo "$(date +%T) simulator ${mem} MiB, exited=${exited} -> $msg (#$simrestarts)"
    sleep 60
    continue
  fi
  if [ "${exited:-0}" -gt 0 ] || [ "${running:-0}" -eq 0 ] || [ "${trainer:-0}" -eq 0 ]; then
    if [ "$resumes" -ge "$MAX_RESUMES" ]; then echo "SIMULATOR DOWN at $(date +%T), giving up after $resumes resumes"; exit 2; fi
    resumes=$((resumes + 1))
    wslrun "[ -f /tmp/autoresume.sh ] && echo ok" | grep -q ok || bootstrap > /dev/null 2>&1   # WSL restarted: /tmp is empty
    new=$(wslrun "bash /tmp/autoresume.sh" | tail -1)
    echo "$(date +%T) simulator down ($status) -> auto-resume #$resumes as $new"
    sleep 60
    continue
  fi
  # waiting for an iteration boundary to restart the simulator: check often (the window is ~1-2 min)
  if [ "${mem:-0}" -gt "$MAX_SIM_MEM_MIB" ]; then sleep 20; else sleep 120; fi
done
