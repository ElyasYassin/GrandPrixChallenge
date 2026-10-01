# usage: evalrun.sh <prefix> <world> <out-name> [checkpoint]
#   checkpoint: a name like 31_Step-21752 (default: the run's "best"); race rules come from run.env
PREFIX=$1; WORLD=$2; NAME=$3; CKPT=${4:-}
OUT="/mnt/c/Users/Elyas/OneDrive - The University of Colorado Denver/Desktop/projects/GrandPrixChallenge/evals/$NAME"; mkdir -p "$OUT"
sudo() { "$@"; }; export -f sudo
A="aws --profile minio --endpoint-url http://localhost:9000"
cd ~/deepracer-for-cloud
cp run.env /tmp/run.env.eval.bak
trap 'cp /tmp/run.env.eval.bak ~/deepracer-for-cloud/run.env' EXIT   # restore settings even if interrupted
source bin/activate.sh > /tmp/act.log 2>&1
dr-stop-evaluation > /dev/null 2>&1; for c in $(docker ps -aq --filter name=deepracer-eval); do docker rm -f $c > /dev/null; done
if [ -n "$CKPT" ]; then
  # point the run's "best" marker at the requested checkpoint for this evaluation, restore it afterwards
  $A s3 cp s3://bucket/$PREFIX/model/deepracer_checkpoints.json /tmp/ckpt.orig.json > /dev/null
  python3 -c "import json;d=json.load(open('/tmp/ckpt.orig.json'));d['best_checkpoint']={'name':'$CKPT.ckpt','avg_eval_metric':None,'time_stamp':0};json.dump(d,open('/tmp/ckpt.json','w'))"
  $A s3 cp /tmp/ckpt.json s3://bucket/$PREFIX/model/deepracer_checkpoints.json > /dev/null
fi
sed -i "s/^DR_LOCAL_S3_MODEL_PREFIX=.*/DR_LOCAL_S3_MODEL_PREFIX=$PREFIX/; s/^DR_WORLD_NAME=.*/DR_WORLD_NAME=$WORLD/; s/^DR_EVAL_CHECKPOINT=.*/DR_EVAL_CHECKPOINT=best/" run.env
source bin/activate.sh > /tmp/act.log 2>&1
dr-start-evaluation -q > /dev/null 2>&1
sleep 20
R=$(docker ps -aq --filter name=deepracer-eval-0-robomaker | head -1)
TRIALS=$(grep "^DR_EVAL_NUMBER_OF_TRIALS=" run.env | cut -d= -f2); TRIALS=${TRIALS:-3}
end=$(( $(date +%s) + 120 + 90 * TRIALS ))
until [ "$(docker logs $R 2>&1 | grep -c 'Finished evaluation phase')" -ge "$TRIALS" ] || [ -z "$(docker ps -q --filter id=$R)" ] || [ $(date +%s) -ge $end ]; do sleep 5; done
sleep 5
docker logs $R > "$OUT/robomaker.log" 2>&1
f=$($A s3 ls --recursive s3://bucket/$PREFIX/metrics/evaluation/ | sort | tail -1 | awk '{print $4}')
$A s3 cp s3://bucket/$f "$OUT/EvaluationMetrics.json" > /dev/null
dr-stop-evaluation > /dev/null 2>&1; for c in $(docker ps -aq --filter name=deepracer-eval); do docker rm -f $c > /dev/null; done
[ -n "$CKPT" ] && $A s3 cp /tmp/ckpt.orig.json s3://bucket/$PREFIX/model/deepracer_checkpoints.json > /dev/null
cp /tmp/run.env.eval.bak run.env
python3 - "$OUT/EvaluationMetrics.json" "$WORLD" "${CKPT:-best}" <<'PY'
import json,sys
m=json.load(open(sys.argv[1]))["metrics"]
print(f"{sys.argv[2]} [{sys.argv[3]}]:", "  ".join(f"T{x['trial']}: {x['completion_percentage']}% {x['elapsed_time_in_milliseconds']/1000:.2f}s off={x['off_track_count']}" for x in m))
PY
