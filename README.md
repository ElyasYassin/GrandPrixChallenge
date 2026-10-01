# Student submission instructions

Submit a compact simulator model generated from your DeepRacer-for-Cloud training run.

## Create the submission

```bash
./cedc_package_model.sh /path/to/your/model cedc_submission.tar.gz
```

The default `auto` mode tries the best checkpoint recorded in `deepracer_checkpoints.json`, then safe fallbacks.

To explicitly submit the latest complete checkpoint:

```bash
./cedc_package_model.sh /path/to/your/model cedc_submission.tar.gz --checkpoint latest
```

To submit a particular iteration:

```bash
./cedc_package_model.sh /path/to/your/model cedc_submission.tar.gz --checkpoint 50
```

Validate it:

```bash
python3 validate_cedc_bundle.py cedc_submission.tar.gz
```

Upload **only** `cedc_submission.tar.gz` in the competition portal. Do not upload the expanded training `model/` directory and do not upload DRfC's physical-car `outputs/model.tar.gz` containing only `agent/model.pb`.
