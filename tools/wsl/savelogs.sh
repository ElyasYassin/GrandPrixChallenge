# save trainer + simulator logs for the current run into the project
PREFIX=$(grep "^DR_LOCAL_S3_MODEL_PREFIX=" ~/deepracer-for-cloud/run.env | cut -d= -f2)
ROOT=$(cat /tmp/gpc_root 2>/dev/null) || ROOT=$(cd "$(dirname "$0")/../.." && pwd)   # project root (set by bootstrap.sh)
OUT="$ROOT/logs/$PREFIX"
mkdir -p "$OUT"
# write to a temp file first: never replace a saved log with an empty one (e.g. container already removed)
save() { docker logs "$1" > /tmp/savelog.tmp 2>&1; [ -s /tmp/savelog.tmp ] && cp /tmp/savelog.tmp "$2"; }
S=$(docker ps -aq --filter name=algo- | head -1)
[ -n "$S" ] && save "$S" "$OUT/sagemaker.log"
i=0; for R in $(docker ps -aq --filter name=deepracer-0-robomaker); do save "$R" "$OUT/robomaker_$i.log"; i=$((i+1)); done
rm -f "$OUT/robomaker.log"
A="aws --profile minio --endpoint-url http://localhost:9000"
$A s3 cp --recursive s3://bucket/$PREFIX/metrics/ "$OUT/" --exclude "*" --include "TrainingMetrics*.json" >/dev/null 2>&1
$A s3 cp s3://bucket/$PREFIX/model/model_metadata.json "$OUT/model_metadata.json" >/dev/null 2>&1
$A s3 cp s3://bucket/custom_files/reward_function.py "$OUT/reward_function.py" >/dev/null 2>&1
cp ~/deepracer-for-cloud/run.env "$OUT/run.env"
ls -la "$OUT" | tail -n +2
