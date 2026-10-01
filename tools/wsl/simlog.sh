# usage: simlog.sh [minutes]  -> recent non-trace simulator log lines + trace step count
R=$(docker ps -aq --filter name=robomaker | head -1)
echo "steps in last ${1:-5}m: $(docker logs --since ${1:-5}m $R 2>&1 | grep -c SIM_TRACE_LOG)"
docker logs --since ${1:-5}m $R 2>&1 | grep -v SIM_TRACE_LOG | tail -15 | cut -c1-200
