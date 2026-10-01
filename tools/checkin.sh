#!/usr/bin/env bash
# overnight check-in: overall + per-direction progress, supervisor log, health
# usage: bash tools/checkin.sh <run-base> <supervisor-output-file>
cd "$(dirname "$0")/.."
date +%T
python tools/run_summary.py "$1" 2>&1 | grep -v -i "warn\|baseline @"
python tools/direction_summary.py "$1" 30 2>&1 | grep -v -i warn
echo "-- supervisor:"; tail -3 "$2" 2>/dev/null
MSYS_NO_PATHCONV=1 timeout 60 wsl.exe -d Ubuntu-22.04 -- bash /tmp/simstatus.sh | tr -d '\0'
powershell.exe -NoProfile -Command "'Windows available GB: {0:N1}' -f ((Get-Counter '\Memory\Available MBytes').CounterSamples[0].CookedValue/1024)" | tr -d '\r'
