# Delete old/redundant model prefixes from MinIO (2026-10-02, approved by the team to free disk).
# Keeps: cedc-m05-snap2 (reference) and every M08/M09 snapshot (cedc-m08-*-HHMM/-end, cedc-m08-now-1940, cedc-m09-*-HHMM/-end).
# Deletes: M01-M07 (results in experiments/LOG.md + evals/), M08/M09 full training-run prefixes (metrics in logs/), test prefixes.
A="aws --profile minio --endpoint-url http://localhost:9000"
KEEP_RE='^(cedc-m05-snap2|cedc-m08-.*-([0-9]{4}|end)|cedc-m08-now-1940|cedc-m09-.*-([0-9]{4}|end))$'
for p in $($A s3 ls s3://bucket/ | awk '{print $2}' | sed 's#/$##'); do
  case "$p" in custom_files|model) continue;; esac
  if [[ "$p" =~ $KEEP_RE ]]; then echo "keep   $p"; continue; fi
  if [[ "$p" =~ ^cedc-(m0[1-9]|speedcap) ]]; then
    if [ -n "${DRY:-}" ]; then echo "delete $p (dry run)"; else $A s3 rm --recursive --quiet s3://bucket/$p/ && echo "delete $p"; fi
  else
    echo "skip   $p (not matched)"
  fi
done
du -sh ~/deepracer-for-cloud/data/minio; df -h / | tail -1
