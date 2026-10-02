#!/usr/bin/env bash
# Run the grip sweep (tools/wsl/grip_test.sh) with WSL kept alive, then analyse it.
# usage: bash tools/grip_sweep.sh <discrete-source-snapshot> [steer:speed ...]
cd "$(dirname "$0")/.."
SRC=$1; shift
TESTS=${*:-"30:1.3 30:2.0 30:3.0 30:4.0 15:2.0 15:3.0 15:4.0 8:3.0 8:4.0"}
MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu-22.04 -- bash -c 'exec sleep infinity' > /dev/null 2>&1 &
KEEPALIVE=$!; trap 'kill $KEEPALIVE 2>/dev/null' EXIT
MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu-22.04 -- bash "/mnt/c/Users/Elyas/OneDrive - The University of Colorado Denver/Desktop/projects/GrandPrixChallenge/tools/wsl/bootstrap.sh" | tr -d '\0'
for sv in $TESTS; do
  MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu-22.04 -- bash /tmp/grip_test.sh "$SRC" "${sv%%:*}" "${sv##*:}" 150 | tr -d '\0'
done
python tools/grip_test_analyze.py
