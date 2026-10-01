# usage: eval_set.sh <label> <run-prefix>...   evaluate each run's "best" on the stand-in + held-out track set
# stand-ins for the secret track: 2022_summit_speedway, 2024_reinvent_champ cw/ccw; held out: Vegas, reinvent_base, reInvent2019
LABEL=$1; shift
pkill -f evalmany.sh; pkill -f evalrun.sh
for run in "$@"; do
  echo "== $run $(date +%T)"
  bash /tmp/evalmany.sh "$run" best "$LABEL-${run#cedc-}" 2022_summit_speedway 2024_reinvent_champ_cw 2024_reinvent_champ_ccw reInvent2019_track reinvent_base Vegas_track
done
echo "== done $(date +%T)"
