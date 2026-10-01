# usage: listckpt.sh <prefix>...   list saved checkpoints of runs
for r in "$@"; do echo "-- $r"; aws --profile minio --endpoint-url http://localhost:9000 s3 ls s3://bucket/$r/model/ | grep -E "index|checkpoints"; done
