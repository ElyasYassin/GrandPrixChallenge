# trainer (sagemaker) status: episode count and last lines
S=$(docker ps -q --filter name=algo-)
echo "trainer: $(docker ps --filter id=$S --format '{{.Status}}'), episodes seen: $(docker logs $S 2>&1 | grep -c 'Training>')"
docker logs --since ${1:-15m} $S 2>&1 | grep -vE "^\s*$" | tail -12 | cut -c1-180
