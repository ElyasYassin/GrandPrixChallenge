# prints: running=<n> exited=<n> mem_mib=<largest simulator memory use in MiB> trainer=<n> trainer_eps=<episodes the trainer received>
mem=0
for R in $(docker ps -q --filter name=robomaker); do
  m=$(docker stats --no-stream --format '{{.MemUsage}}' $R | awk '{v=$1; u=v; gsub(/[0-9.]/,"",u); gsub(/[A-Za-z]/,"",v); if (u=="GiB") v*=1024; if (u=="KiB") v/=1024; printf "%d", v}')
  [ "$m" -gt "$mem" ] && mem=$m
done
S=$(docker ps -q --filter name=algo- | head -1)
teps=0
[ -n "$S" ] && teps=$(docker logs $S 2>&1 | grep -c "Training>")
echo "running=$(docker ps -q --filter name=robomaker | wc -l) exited=$(docker ps -aq --filter name=robomaker --filter status=exited | wc -l) mem_mib=$mem trainer=$(docker ps -q --filter name=algo- | wc -l) trainer_eps=$teps"
