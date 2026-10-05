#!/usr/bin/env bash
# overnight check-in: overall + per-direction progress, supervisor log, health
# usage: bash tools/checkin.sh <run-base> <supervisor-output-file>
source "$(dirname "$0")/env.sh"; cd "$ROOT"
date +%T
python tools/run_summary.py "$1" 2>&1 | grep -v -i "warn\|baseline @"
python tools/direction_summary.py "$1" 30 2>&1 | grep -v -i warn
echo "-- supervisor:"; tail -3 "$2" 2>/dev/null
WSLRUN_TIMEOUT=60 wslrun "bash /tmp/simstatus.sh"
powershell.exe -NoProfile 2>/dev/null -Command "'Windows available GB: {0:N1}' -f ((Get-Counter '\Memory\Available MBytes').CounterSamples[0].CookedValue/1024)" | tr -d '\r'
