# usage: lasttrace.sh [n]   last n SIM_TRACE_LOG lines of the training simulator
docker logs $(docker ps -q --filter name=deepracer-0-robomaker | head -1) 2>&1 | grep SIM_TRACE_LOG | tail -${1:-5} | sed 's/.*SIM_TRACE_LOG://'
