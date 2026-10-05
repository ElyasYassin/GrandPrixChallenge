# Load a portal bundle (cedc_package_model.py output) or a downloaded model folder into local MinIO,
# so it can be evaluated or used as the pretrained start of a run (e.g. a teammate's checkpoint).
# usage: import_bundle.sh <bundle.tar.gz | model-dir> <prefix>      -> s3://bucket/<prefix>/model/
SRC=$1; PREFIX=$2
A="aws --profile minio --endpoint-url http://localhost:9000"
# this MinIO build fails multipart uploads ("ETag" error, file silently missing): upload in one piece
aws --profile minio configure set s3.multipart_threshold 1GB
TMP=$(mktemp -d)
if [ -d "$SRC" ]; then cp -r "$SRC"/. "$TMP/"; else tar -xzf "$SRC" -C "$TMP"; fi
# the bundle holds model/<files>; a model folder holds the files directly
D=$(dirname "$(find "$TMP" -name model_metadata.json | head -1)")
[ -f "$D/deepracer_checkpoints.json" ] || { echo "no deepracer_checkpoints.json in $SRC"; rm -rf "$TMP"; exit 1; }
# portal bundles store the checkpoint name without ".ckpt"; the trainer only restores "<name>.ckpt"
# (same format as tools/wsl/snapshot.sh), otherwise: "No checkpoint to restore"
CK=$(python3 -c "import json;n=json.load(open('$D/deepracer_checkpoints.json'))['best_checkpoint']['name'];print(n if n.endswith('.ckpt') else n+'.ckpt')")
[ -f "$D/$CK.data-00000-of-00001" ] || { echo "missing $CK.data-00000-of-00001 in $SRC"; rm -rf "$TMP"; exit 1; }
echo "{\"best_checkpoint\": {\"name\": \"$CK\", \"avg_eval_metric\": null, \"time_stamp\": 0}, \"last_checkpoint\": {\"name\": \"$CK\", \"avg_eval_metric\": null, \"time_stamp\": 0}}" > "$D/deepracer_checkpoints.json"
echo "$CK" > "$D/.coach_checkpoint"
$A s3 rm --recursive --quiet s3://bucket/$PREFIX/
$A s3 cp --recursive "$D/" s3://bucket/$PREFIX/model/ > /dev/null
# verify every file arrived with the right size (a large upload once went missing silently)
bad=0; for f in "$D"/* "$D"/.coach_checkpoint; do
  n=$(basename "$f"); sz=$($A s3 ls s3://bucket/$PREFIX/model/$n | awk -v n="$n" '$4==n {print $3}')
  [ "$sz" = "$(stat -c %s "$f")" ] || { echo "upload check failed: $n"; bad=1; }
done
[ "$bad" = 0 ] && echo "imported $PREFIX: $CK ($(ls -A "$D" | wc -l) files, sizes verified)"
rm -rf "$TMP"
exit $bad
