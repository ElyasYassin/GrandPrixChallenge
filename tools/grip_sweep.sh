#!/usr/bin/env bash
# Run the grip sweep (tools/wsl/grip_test.sh) with WSL kept alive, then analyse it.
# usage: bash tools/grip_sweep.sh <discrete-source-snapshot> [steer:speed ...]
source "$(dirname "$0")/env.sh"; cd "$ROOT"
SRC=$1; shift
TESTS=${*:-"30:1.3 30:2.0 30:3.0 30:4.0 15:2.0 15:3.0 15:4.0 8:3.0 8:4.0"}
start_keepalive; trap 'kill $KEEPALIVE 2>/dev/null' EXIT
bootstrap
for sv in $TESTS; do
  wsl_exec bash /tmp/grip_test.sh "$SRC" "${sv%%:*}" "${sv##*:}" 150 | tr -d '\0'
done
python tools/grip_test_analyze.py
