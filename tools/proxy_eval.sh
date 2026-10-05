#!/usr/bin/env bash
# Which local test predicts the portal? Evaluate models with known portal outcomes on candidate tracks
# (tracks in the outer loop, so each finished track is a complete comparison) -> evals/px-<model>-<track>/
# Analyse with: python tools/proxy_compare.py
# usage: bash tools/proxy_eval.sh "<prefix> ..." "<track> ..."
cd "$(dirname "$0")/.."
MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu-22.04 -- bash -c 'exec sleep infinity' > /dev/null 2>&1 &
KEEPALIVE=$!; trap 'kill $KEEPALIVE 2>/dev/null' EXIT
MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu-22.04 -- bash "/mnt/c/Users/Elyas/OneDrive - The University of Colorado Denver/Desktop/projects/GrandPrixChallenge/tools/wsl/bootstrap.sh" | tr -d '\0'
for t in $2; do
  for p in $1; do
    [ -f "evals/px-${p#cedc-}-$t/EvaluationMetrics.json" ] && continue   # resumable
    echo "== $(date +%T) $t $p"
    MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu-22.04 -- bash /tmp/evalrun.sh "$p" "$t" "px-${p#cedc-}-$t" | tr -d '\0' | tail -1
  done
done
echo "== done $(date +%T)"
