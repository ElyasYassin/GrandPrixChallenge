# usage: start_run.sh <experiment-dir-name> <new-prefix> <pretrained-prefix> <pretrained-checkpoint: best|last> [world, default Vegas_track]
# copies the experiment's reward + action space into DRfC, points run.env at the new run and starts training
EXP="/mnt/c/Users/Elyas/OneDrive - The University of Colorado Denver/Desktop/projects/GrandPrixChallenge/experiments/$1"
sudo() { "$@"; }; export -f sudo
cd ~/deepracer-for-cloud
cp "$EXP/reward_function.py" custom_files/reward_function.py
cp "$EXP/model_metadata.json" custom_files/model_metadata.json
sed -i 's/\r$//' custom_files/reward_function.py custom_files/model_metadata.json
python3 -c "import ast,json;ast.parse(open('custom_files/reward_function.py').read());json.load(open('custom_files/model_metadata.json'));print('files ok')"
# always set the world explicitly (evaluations may leave another track in run.env); Vegas unless a world is given
sed -i "s/^DR_WORLD_NAME=.*/DR_WORLD_NAME=${5:-Vegas_track}/" run.env
sed -i "s/^DR_LOCAL_S3_MODEL_PREFIX=.*/DR_LOCAL_S3_MODEL_PREFIX=$2/; s/^DR_LOCAL_S3_PRETRAINED=.*/DR_LOCAL_S3_PRETRAINED=True/; s/^DR_LOCAL_S3_PRETRAINED_PREFIX=.*/DR_LOCAL_S3_PRETRAINED_PREFIX=$3/; s/^DR_LOCAL_S3_PRETRAINED_CHECKPOINT=.*/DR_LOCAL_S3_PRETRAINED_CHECKPOINT=$4/" run.env
grep -E "^DR_(LOCAL_S3_MODEL_PREFIX|LOCAL_S3_PRETRAINED_PREFIX|LOCAL_S3_PRETRAINED_CHECKPOINT|WORLD_NAME|TRAIN_ALTERNATE_DRIVING_DIRECTION|WORKERS)=" run.env system.env
source bin/activate.sh > /tmp/act.log 2>&1
dr-upload-custom-files > /dev/null 2>&1
dr-start-training -q -w 2>&1 | grep -E "Started|rror" | tail -2
