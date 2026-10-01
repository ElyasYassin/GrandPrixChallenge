# stop any running evaluation (scripts + containers) and restore run.env from evalrun's backup
pkill -f eval_set.sh; pkill -f eval_candidates.sh; pkill -f evalmany.sh; pkill -f evalrun.sh; sleep 2
for c in $(docker ps -aq --filter name=deepracer-eval); do docker rm -f $c > /dev/null; done
cd ~/deepracer-for-cloud
[ -f /tmp/run.env.eval.bak ] && cp /tmp/run.env.eval.bak run.env
grep -E "^DR_(WORLD_NAME|LOCAL_S3_MODEL_PREFIX|EVAL_NUMBER_OF_TRIALS)=" run.env
docker ps --format "{{.Names}}"
