# usage: evalmany.sh <prefix> <checkpoint|best> <label> <world>...   -> evals/<label>-<world>/
PREFIX=$1; CKPT=$2; LABEL=$3; shift 3
[ "$CKPT" = "best" ] && CKPT=""
for w in "$@"; do bash /tmp/evalrun.sh "$PREFIX" "$w" "$LABEL-$w" $CKPT | tail -1; done
