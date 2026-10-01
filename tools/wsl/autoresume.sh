# stop the current run and continue it from its LAST checkpoint as a new run:
#   <prefix>-N -> <prefix>-(N+1),  <prefix> (no number) -> <prefix>-2
# (dr-increment-training mis-names prefixes that don't end in a number, e.g. cedc-m03-speed -> cedc-m03-2)
sudo() { "$@"; }; export -f sudo
bash /tmp/drstop.sh > /dev/null 2>&1
cd ~/deepracer-for-cloud
CUR=$(grep "^DR_LOCAL_S3_MODEL_PREFIX=" run.env | cut -d= -f2)
if [[ "$CUR" =~ ^(.*)-([0-9]+)$ ]]; then NEW="${BASH_REMATCH[1]}-$((BASH_REMATCH[2] + 1))"; else NEW="$CUR-2"; fi
sed -i "s/^DR_LOCAL_S3_MODEL_PREFIX=.*/DR_LOCAL_S3_MODEL_PREFIX=$NEW/; s/^DR_LOCAL_S3_PRETRAINED=.*/DR_LOCAL_S3_PRETRAINED=True/; s/^DR_LOCAL_S3_PRETRAINED_PREFIX=.*/DR_LOCAL_S3_PRETRAINED_PREFIX=$CUR/; s/^DR_LOCAL_S3_PRETRAINED_CHECKPOINT=.*/DR_LOCAL_S3_PRETRAINED_CHECKPOINT=last/" run.env
source bin/activate.sh > /tmp/act.log 2>&1
dr-start-training -q -w > /dev/null 2>&1
echo "$NEW"
