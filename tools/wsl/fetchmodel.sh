ROOT=$(cat /tmp/gpc_root 2>/dev/null) || ROOT=$(cd "$(dirname "$0")/../.." && pwd)   # project root (set by bootstrap.sh)
O="$ROOT/models/$1/model"
mkdir -p "$O"
aws --profile minio --endpoint-url http://localhost:9000 s3 cp --recursive s3://bucket/$1/model/ "$O/" > /dev/null
ls -la "$O" | tail -n +2
