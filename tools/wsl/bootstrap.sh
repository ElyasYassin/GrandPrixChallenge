# Prepare WSL after a (re)start: install helpers into /tmp, DRfC temp dir, clean exited containers, start MinIO.
# usage: bootstrap.sh [project-root-in-WSL]   (default: this script's repo)
ROOT=${1:-$(cd "$(dirname "$0")/../.." && pwd)}
HERE="$ROOT/tools/wsl"
echo "$ROOT" > /tmp/gpc_root   # lets the helpers in /tmp find the project
cp "$HERE"/*.sh /tmp/ && sed -i 's/\r$//' /tmp/*.sh
mkdir -p /tmp/sagemaker && chmod g+w /tmp/sagemaker
until docker info > /dev/null 2>&1; do sleep 2; done
old=$(docker ps -aq --filter status=exited)
[ -n "$old" ] && docker rm -f $old > /dev/null
cd ~/deepracer-for-cloud
source bin/activate.sh > /tmp/act.log 2>&1
for i in $(seq 1 40); do curl -s -o /dev/null -w "%{http_code}" localhost:9000/minio/health/live | grep -q 200 && break; sleep 2; done
echo "minio: $(curl -s -o /dev/null -w '%{http_code}' localhost:9000/minio/health/live), current run: $(grep ^DR_LOCAL_S3_MODEL_PREFIX= run.env | cut -d= -f2)"
