# after a WSL restart: start storage and continue the current run from its last checkpoint
sudo() { "$@"; }; export -f sudo
echo "WSL: $(nproc) cpus, $(free -g | awk '/Mem/{print $2}') GB"
until docker info > /dev/null 2>&1; do sleep 2; done
cd ~/deepracer-for-cloud
source bin/activate.sh > /tmp/act.log 2>&1
for i in $(seq 1 30); do curl -s -o /dev/null -w "%{http_code}" localhost:9000/minio/health/live | grep -q 200 && break; sleep 2; done
echo "minio: $(curl -s -o /dev/null -w '%{http_code}' localhost:9000/minio/health/live)"
bash /tmp/autoresume.sh   # continue the run from its last checkpoint as <prefix>-N+1
grep -E "^DR_LOCAL_S3_(MODEL_PREFIX|PRETRAINED_PREFIX|PRETRAINED_CHECKPOINT)=" run.env
