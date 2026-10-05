# delete training-run prefixes from MinIO (used by track_rotation.sh CLEAN_RUNS=1 once a leg's -end
# snapshot exists); refuses snapshot-looking names (-HHMM / -end) as a safety net
A="aws --profile minio --endpoint-url http://localhost:9000"
for p in "$@"; do
  if [[ "$p" =~ -([0-9]{4}|end|stop|pause)$ ]]; then echo "refusing to delete snapshot $p"; continue; fi
  $A s3 rm --recursive --quiet "s3://bucket/$p/" && echo "deleted run $p"
done
