# stop evaluation scripts + eval containers only (leaves a running training untouched), restore run.env
pkill -f eval_set.sh; pkill -f eval_candidates.sh; pkill -f evalmany.sh; pkill -f evalrun.sh; sleep 2
for c in $(docker ps -aq --filter name=deepracer-eval); do docker rm -f $c > /dev/null; done
[ -f /tmp/run.env.eval.bak ] && cp /tmp/run.env.eval.bak ~/deepracer-for-cloud/run.env
grep -E "^DR_(WORLD_NAME|LOCAL_S3_MODEL_PREFIX|LOCAL_S3_PRETRAINED_PREFIX)=" ~/deepracer-for-cloud/run.env
docker ps --format "{{.Names}}"
