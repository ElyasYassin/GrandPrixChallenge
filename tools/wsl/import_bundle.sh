# Load a portal bundle (cedc_package_model.py output) or a downloaded model folder into local MinIO,
# so it can be evaluated or used as the pretrained start of a run (e.g. a teammate's checkpoint).
# usage: import_bundle.sh <bundle.tar.gz | model-dir> <prefix>      -> s3://bucket/<prefix>/model/
SRC=$1; PREFIX=$2
A="aws --profile minio --endpoint-url http://localhost:9000"
TMP=$(mktemp -d)
if [ -d "$SRC" ]; then cp -r "$SRC"/. "$TMP/"; else tar -xzf "$SRC" -C "$TMP"; fi
# the bundle holds model/<files>; a model folder holds the files directly
D=$(dirname "$(find "$TMP" -name model_metadata.json | head -1)")
[ -f "$D/deepracer_checkpoints.json" ] || { echo "no deepracer_checkpoints.json in $SRC"; rm -rf "$TMP"; exit 1; }
$A s3 rm --recursive --quiet s3://bucket/$PREFIX/
$A s3 cp --recursive --quiet "$D/" s3://bucket/$PREFIX/model/
echo "imported $PREFIX: $(python3 -c "import json;print(json.load(open('$D/deepracer_checkpoints.json'))['best_checkpoint']['name'])") ($(ls "$D" | wc -l) files)"
rm -rf "$TMP"
