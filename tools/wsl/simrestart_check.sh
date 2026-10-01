S=$(docker ps -q --filter name=algo-)
echo "trainer: $(docker ps --filter id=$S --format '{{.Status}}'), episodes: $(docker logs $S 2>&1 | grep -c 'Training>')"
docker logs $S 2>&1 | grep -E "Training>|Policy training>" | tail -2 | cut -c1-150
bash /tmp/simstatus.sh
R=$(docker ps -q --filter name=robomaker | head -1); echo "sim steps since restart: $(docker logs --since 5m $R 2>&1 | grep -c SIM_TRACE_LOG)"
