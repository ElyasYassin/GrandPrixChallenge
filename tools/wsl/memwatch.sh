# usage: memwatch.sh [samples] [interval_s]   -> simulator container memory over time
R=$(docker ps -q --filter name=robomaker | head -1)
echo "simulator started: $(docker inspect -f '{{.State.StartedAt}}' $R)"
for i in $(seq 1 ${1:-3}); do echo "$(date +%T) $(docker stats --no-stream --format '{{.MemUsage}}' $R)"; sleep ${2:-30}; done
