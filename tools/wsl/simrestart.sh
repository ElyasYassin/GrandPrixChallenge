# Restart only the simulator container(s) (memory leak / crash). The trainer keeps its state and
# the run continues. A restarted simulator starts a fresh TrainingMetrics file, so first save the
# current ones as part<N>_TrainingMetrics*.json next to the run's logs (tools/tb_export.py stitches them).
PREFIX=$(grep "^DR_LOCAL_S3_MODEL_PREFIX=" ~/deepracer-for-cloud/run.env | cut -d= -f2)
OUT="/mnt/c/Users/Elyas/OneDrive - The University of Colorado Denver/Desktop/projects/GrandPrixChallenge/logs/$PREFIX"
mkdir -p "$OUT"
A="aws --profile minio --endpoint-url http://localhost:9000"
n=$(ls "$OUT" | grep -c "^part.*_TrainingMetrics.json$"); n=$((n + 1))
for f in $($A s3 ls s3://bucket/$PREFIX/metrics/ | awk '{print $4}' | grep "^TrainingMetrics.*\.json$"); do
  $A s3 cp s3://bucket/$PREFIX/metrics/$f "$OUT/part${n}_$f" > /dev/null 2>&1
done
S=$(docker ps -q --filter name=algo-)
before=$(docker logs $S 2>&1 | grep -c "Training>")
for R in $(docker ps -aq --filter name=robomaker); do docker restart $R > /dev/null; done
echo "restarted simulator (part $n saved, trainer at $before episodes)"
