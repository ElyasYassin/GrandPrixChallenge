# usage: start_run.sh <experiment-dir-name> <new-prefix> <pretrained-prefix> <pretrained-checkpoint: best|last> [world, default Vegas_track] [lr]
#   pretrained-prefix "none" = train from scratch (needed when the action space changes)
# copies the experiment's reward + action space into DRfC, points run.env at the new run and starts training
ROOT=$(cat /tmp/gpc_root 2>/dev/null) || ROOT=$(cd "$(dirname "$0")/../.." && pwd)   # project root (set by bootstrap.sh)
EXP="$ROOT/experiments/$1"
sudo() { "$@"; }; export -f sudo
cd ~/deepracer-for-cloud
cp "$EXP/reward_function.py" custom_files/reward_function.py
cp "$EXP/model_metadata.json" custom_files/model_metadata.json
sed -i 's/\r$//' custom_files/reward_function.py custom_files/model_metadata.json
python3 -c "import ast,json;ast.parse(open('custom_files/reward_function.py').read());json.load(open('custom_files/model_metadata.json'));print('files ok')"
# always set the world explicitly (evaluations may leave another track in run.env); Vegas unless a world is given.
# "A+B" trains one model on several tracks at once: one simulator (worker) per track (DRfC multi-config);
# workers 2.. copy domain randomization and direction settings from run.env
# optional: DR=True|False sets domain randomization for this run (workers 2.. copy it below)
[ -n "${DR:-}" ] && sed -i "s/^DR_ENABLE_DOMAIN_RANDOMIZATION=.*/DR_ENABLE_DOMAIN_RANDOMIZATION=$DR/" run.env
IFS=+ read -r -a WORLDS <<< "${5:-Vegas_track}"
sed -i "s/^DR_WORLD_NAME=.*/DR_WORLD_NAME=${WORLDS[0]}/" run.env
sed -i "s/^DR_WORKERS=.*/DR_WORKERS=${#WORLDS[@]}/" system.env
rm -f worker-*.env
if [ "${#WORLDS[@]}" -gt 1 ]; then
  sed -i "s/^DR_TRAIN_MULTI_CONFIG=.*/DR_TRAIN_MULTI_CONFIG=True/" run.env
  for i in $(seq 2 ${#WORLDS[@]}); do
    { grep -vE "^DR_(WORLD_NAME|ENABLE_DOMAIN_RANDOMIZATION|TRAIN_ALTERNATE_DRIVING_DIRECTION)=" defaults/template-worker.env
      echo "DR_WORLD_NAME=${WORLDS[$((i - 1))]}"
      grep -E "^DR_(ENABLE_DOMAIN_RANDOMIZATION|TRAIN_ALTERNATE_DRIVING_DIRECTION)=" run.env; } > worker-$i.env
  done
else
  sed -i "s/^DR_TRAIN_MULTI_CONFIG=.*/DR_TRAIN_MULTI_CONFIG=False/" run.env
fi
sed -i "s/^DR_LOCAL_S3_MODEL_PREFIX=.*/DR_LOCAL_S3_MODEL_PREFIX=$2/; s/^DR_LOCAL_S3_PRETRAINED=.*/DR_LOCAL_S3_PRETRAINED=True/; s/^DR_LOCAL_S3_PRETRAINED_PREFIX=.*/DR_LOCAL_S3_PRETRAINED_PREFIX=$3/; s/^DR_LOCAL_S3_PRETRAINED_CHECKPOINT=.*/DR_LOCAL_S3_PRETRAINED_CHECKPOINT=$4/" run.env
[ "$3" = none ] && sed -i "s/^DR_LOCAL_S3_PRETRAINED=.*/DR_LOCAL_S3_PRETRAINED=False/" run.env
[ -n "${6:-}" ] && sed -i "s/\"lr\": [0-9.e-]*/\"lr\": $6/" custom_files/hyperparameters.json
grep -o '"lr": [0-9.e-]*' custom_files/hyperparameters.json
grep -E "^DR_(ENABLE_DOMAIN_RANDOMIZATION|LOCAL_S3_MODEL_PREFIX|LOCAL_S3_PRETRAINED|LOCAL_S3_PRETRAINED_PREFIX|LOCAL_S3_PRETRAINED_CHECKPOINT|WORLD_NAME|TRAIN_ALTERNATE_DRIVING_DIRECTION|WORKERS)=" run.env system.env
source bin/activate.sh > /tmp/act.log 2>&1
dr-upload-custom-files > /dev/null 2>&1
dr-start-training -q -w 2>&1 | grep -E "Started|rror" | tail -2
