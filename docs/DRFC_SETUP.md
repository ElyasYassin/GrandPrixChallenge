# DeepRacer-for-Cloud (DRfC): local training setup on Windows

How we run DeepRacer training locally on an RTX 3090 under WSL2. Follow this on each teammate's PC.

## Requirements

- Windows 11, NVIDIA driver installed on **Windows** (don't install a driver inside WSL)
- WSL2 with **Ubuntu 22.04** and systemd enabled (the default for new distros)
- Don't enable Docker Desktop's WSL integration for this distro: DRfC runs its own Docker engine inside Ubuntu.

## 1. Give WSL enough resources

Create `C:\Users\<you>\.wslconfig`:

```ini
[wsl2]
memory=16GB
processors=10
swap=4GB

[experimental]
autoMemoryReclaim=dropCache
```

Training needs about 5 GB. **Don't give WSL too much:** with 24 GB + 8 GB swap on a 32 GB PC (plus Discord, browsers, etc.), Windows dropped to 0.8 GB free, WSL stopped responding and the simulator died. Leave Windows at least about 12 GB and 2 CPU threads. `autoMemoryReclaim` makes WSL give back memory it no longer uses.

**Keep WSL alive during training:** WSL shuts its VM down a few seconds after the last Windows process attached to it exits, **even if Docker is still running inside**, which silently kills training. Keep a terminal open in the distro, or run `wsl -d Ubuntu-22.04 -- sleep infinity` in the background (`tools/supervise.sh` does this for you).

## 2. Install (needs your sudo password)

```bash
wsl -d Ubuntu-22.04
git clone https://github.com/aws-deepracer-community/deepracer-for-cloud.git ~/deepracer-for-cloud
cd ~/deepracer-for-cloud && ./bin/prepare.sh
exit
```

Then, from Windows, restart WSL to apply `.wslconfig` and the `docker` group:

```bash
wsl --shutdown
```

`prepare.sh` installs Docker, the NVIDIA container toolkit (as the default Docker runtime), awscli, jq and a Python venv. On WSL2 it skips the NVIDIA driver install.

## 3. Check that the GPU works in Docker

```bash
docker run --rm --gpus all ubuntu:22.04 nvidia-smi -L
```

## 4. Initialize DRfC

```bash
mkdir -p /tmp/sagemaker && chmod g+w /tmp/sagemaker
cd ~/deepracer-for-cloud && ./bin/init.sh -c local -a gpu
```

This pulls the simulator image (`awsdeepracercommunity/deepracer-simapp:<ver>-gpu`, several GB), creates local MinIO (S3-compatible storage) credentials, and sets up a Docker Swarm network.

`/tmp` is cleared whenever WSL restarts, so recreate `/tmp/sagemaker` if training complains about it.

**Gotcha:** `init.sh` calls `sudo mkdir /tmp/sagemaker`. If you run it non-interactively, it hangs silently waiting for a password. Run it in your own terminal, or create the folder first as shown above.

## 4b. Fix MinIO (required since Sep 2026)

MinIO deleted `minio/minio` from Docker Hub (and quay.io now returns 401), so DRfC's local storage won't start ("No such image: minio/minio"). Use the Chainguard build, re-tagged so DRfC's compose file doesn't need editing:

```bash
cd ~/deepracer-for-cloud
docker pull cgr.dev/chainguard/minio:latest
docker tag cgr.dev/chainguard/minio:latest minio/minio:chainguard
sed -i 's/^DR_MINIO_IMAGE=.*/DR_MINIO_IMAGE=chainguard/' system.env
chmod -R a+rwX data/minio        # the Chainguard image runs as a non-root user
docker stack rm s3; sleep 8
source bin/activate.sh           # redeploys MinIO
curl -s -o /dev/null -w "%{http_code}\n" localhost:9000/minio/health/live   # expect 200
```

`activate.sh` prints `line 341: [: : integer expression expected`. That's harmless, but it means you shouldn't source it under `set -e`, and don't pipe it (`source ... | tail` runs it in a subshell, so the `dr-*` commands won't exist).

## 4c. GPU rendering for the simulator (3.5× faster)

By default the simulator (Gazebo) renders the camera on the **CPU** (Mesa `llvmpipe`): about 3 steps/s instead of about 15. On WSL2 the fix is:

```bash
sudo apt install -y x11-xserver-utils mesa-utils
cd ~/deepracer-for-cloud
sed -i 's/^DR_HOST_X=.*/DR_HOST_X=True/; s/^# DR_DISPLAY=.*/DR_DISPLAY=:0/' system.env
# DRfC's WSL compose file misses this: tell Mesa to use the D3D12 (GPU) driver
sed -i 's#      - LD_LIBRARY_PATH=/usr/lib/wsl/lib#      - LD_LIBRARY_PATH=/usr/lib/wsl/lib\n      - GALLIUM_DRIVER=d3d12#' docker/docker-compose-local-xorg-wsl.yml
```

Verify inside a running simulator: `docker exec <robomaker> glxinfo -B | grep renderer` should say `D3D12 (NVIDIA GeForce RTX 3090)`, not `llvmpipe`. Measured: **2.8 → 9.8 steps/s**. (The swarm warning `Ignoring unsupported options: devices` is harmless: `/dev/dxg` is still present.)

**⚠️ Memory leak with GPU rendering:** with the D3D12 path, the simulator (robomaker) container grows by about 0.7–1 GB per minute (12.7 GB after 14 min), until the PC runs out of memory and the simulator or WSL dies. Turning off the extra cameras doesn't help. Workaround: **restart only the simulator** container every ~10 min (`docker restart deepracer-0-robomaker-1`). The trainer keeps running and the run continues in place (no new run, no dip). `tools/supervise.sh` does this automatically above 9 GB (`tools/wsl/simrestart.sh`, which first saves the run's metrics because a restarted simulator starts a fresh metrics file).

## 4d. Stopping training without a sudo password

`dr-stop-training` runs `sudo find/sed/docker compose` on root-owned files in `/tmp/sagemaker` and **hangs silently** when there's no terminal to type a password. Workaround, which also stops the trainer container directly:

```bash
sudo() { "$@"; }; export -f sudo
source bin/activate.sh
dr-stop-training
for c in $(docker ps -q --filter name=algo-); do docker stop $c && docker rm -v $c; done
```

## 4e. Use compose mode, not swarm (important on WSL)

On a single WSL machine, Docker Swarm's manager can time out under load (`agent: session failed ... DeadlineExceeded`, `node not registered`). It then reschedules every service: the simulators (restart policy "none") stay **Shutdown** and training silently stalls (this happened on 2026-09-29 16:26). Compose mode avoids the swarm manager and also honours the `/dev/dxg` GPU device:

```bash
docker stack rm deepracer-0 s3; docker swarm leave --force
cd ~/deepracer-for-cloud
sed -i 's/^DR_DOCKER_STYLE=.*/DR_DOCKER_STYLE=compose/' system.env
docker network rm sagemaker-local; docker network create sagemaker-local --subnet 192.168.200.0/24
source bin/activate.sh     # MinIO starts as container s3-minio-1
```

In compose mode, containers are named `deepracer-0-robomaker-1`, `-2`, ... (swarm: `deepracer-0_robomaker.1`).

**With several workers, DRfC writes one metrics file per worker** (`metrics/TrainingMetrics.json`, `TrainingMetrics_1.json`, ...). Merge them before counting episodes (`tools/tb_export.py: load_metrics`).

## 5. Everyday use

```bash
cd ~/deepracer-for-cloud && source bin/activate.sh
```

| File | Purpose |
|---|---|
| `run.env` | Track (`DR_WORLD_NAME`), race type, start position, direction, domain randomization, evaluation settings |
| `system.env` | Workers, GPU/CPU, docker style, storage |
| `custom_files/reward_function.py` | Reward function |
| `custom_files/model_metadata.json` | Action space, sensor, network |
| `custom_files/hyperparameters.json` | PPO hyperparameters |

```bash
dr-update                 # reload env after editing run.env / system.env
dr-upload-custom-files    # push custom_files/ to local storage
dr-start-training         # train (add -w to wipe a previous model with the same prefix)
dr-logs-robomaker         # simulator logs
dr-stop-training
dr-start-evaluation / dr-stop-evaluation
```

Handy defaults in `run.env`: `DR_WORLD_NAME=reinvent_base` (the re:Invent 2018 track), `DR_ENABLE_DOMAIN_RANDOMIZATION`, `DR_TRAIN_REVERSE_DIRECTION`, `DR_TRAIN_ALTERNATE_DRIVING_DIRECTION`.
