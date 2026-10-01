# usage: eval_candidates.sh <label-prefix> <run-prefix>...   evaluate each run's "best" on the 4 standard tracks
LABEL=$1; shift
pkill -f evalmany.sh; pkill -f evalrun.sh
for run in "$@"; do
  echo "== $run"
  bash /tmp/evalmany.sh "$run" best "$LABEL-${run#cedc-}" Vegas_track 2022_summit_speedway reinvent_base 2024_reinvent_champ_cw
done
