# usage: snapshot.sh <prefix> <snapshot-prefix>   copy the run's newest checkpoint into its own prefix (for later evaluation)
A="aws --profile minio --endpoint-url http://localhost:9000"
SRC=$1; DST=$2
latest=$($A s3 ls s3://bucket/$SRC/model/ | awk '{print $4}' | grep '\.ckpt\.index$' | sort -t_ -k1 -n | tail -1 | sed 's/\.ckpt\.index$//')
if [ -z "$latest" ]; then   # fresh resume, nothing saved yet: use the checkpoint it was started from
  pre=$(grep "^DR_LOCAL_S3_PRETRAINED_PREFIX=" ~/deepracer-for-cloud/run.env | cut -d= -f2)
  [ "$(grep "^DR_LOCAL_S3_MODEL_PREFIX=" ~/deepracer-for-cloud/run.env | cut -d= -f2)" = "$SRC" ] && [ -n "$pre" ] && [ "$pre" != none ] && exec bash "$0" "$pre" "$DST"
  echo "snapshot $DST: no checkpoint in $SRC"; exit 1
fi
it=${latest%%_*}
for f in $latest.ckpt.index $latest.ckpt.meta $latest.ckpt.data-00000-of-00001 model_$it.pb model_metadata.json; do
  $A s3 cp s3://bucket/$SRC/model/$f s3://bucket/$DST/model/$f > /dev/null
done
echo "{\"best_checkpoint\": {\"name\": \"$latest.ckpt\", \"avg_eval_metric\": null, \"time_stamp\": 0}, \"last_checkpoint\": {\"name\": \"$latest.ckpt\", \"avg_eval_metric\": null, \"time_stamp\": 0}}" > /tmp/snap.json
$A s3 cp /tmp/snap.json s3://bucket/$DST/model/deepracer_checkpoints.json > /dev/null
echo "$latest.ckpt" > /tmp/snap.coach; $A s3 cp /tmp/snap.coach s3://bucket/$DST/model/.coach_checkpoint > /dev/null
echo "snapshot $DST <- $SRC $latest"
