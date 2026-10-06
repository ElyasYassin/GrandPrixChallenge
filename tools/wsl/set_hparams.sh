# set DRfC training hyperparameters: set_hparams.sh key=value ...  (custom_files/hyperparameters.json; prints the result)
F=~/deepracer-for-cloud/custom_files/hyperparameters.json
python3 - "$F" "$@" <<'PY'
import json, sys
f = sys.argv[1]; d = json.load(open(f))
for kv in sys.argv[2:]:
    k, v = kv.split("=", 1)
    d[k] = type(d[k])(float(v)) if isinstance(d.get(k), (int, float)) and not isinstance(d.get(k), bool) else v
json.dump(d, open(f, "w"), indent=4)
print({k: d[k] for k in ("lr", "beta_entropy", "num_episodes_between_training", "batch_size", "discount_factor", "num_epochs")})
PY
