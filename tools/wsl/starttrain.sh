# upload custom_files and start training for the prefix in run.env (wipes that prefix first)
sudo() { "$@"; }; export -f sudo
cd ~/deepracer-for-cloud
source bin/activate.sh > /tmp/act.log 2>&1
dr-upload-custom-files > /dev/null 2>&1
dr-start-training -q -w 2>&1 | grep -E "Started|rror" | tail -2
grep -E "^DR_(LOCAL_S3_MODEL_PREFIX|LOCAL_S3_PRETRAINED_PREFIX|TRAIN_ALTERNATE_DRIVING_DIRECTION)=" run.env
