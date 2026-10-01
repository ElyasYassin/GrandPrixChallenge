sudo() { "$@"; }; export -f sudo
bash /tmp/savelogs.sh
cd ~/deepracer-for-cloud && source bin/activate.sh > /tmp/act.log 2>&1
dr-stop-training > /dev/null 2>&1
for c in $(docker ps -q --filter name=algo-); do docker stop $c >/dev/null && docker rm -v $c >/dev/null; done
until [ -z "$(docker ps -q --filter name=deepracer-)" ]; do sleep 2; done
echo "stopped"
