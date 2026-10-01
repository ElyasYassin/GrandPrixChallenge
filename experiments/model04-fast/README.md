# Model 04: Fast (keep right turns, push speed)

**Why:** Model 03b fixed right turns (about a third of Model 03's off-tracks) but learned to drive cautiously (1.46 → 1.28 m/s), so its average evaluation time (20.3 s) was worse than Model 03 (17.7 s, uploaded, portal 22.5). The leaderboard counts time *including* off-track penalties, so we need 03b's reliability **and** Model 03's speed.
**Starts from:** `cedc-m03b-final` (checkpoint 69). Still Vegas, still alternating direction every episode.

## Changes vs 03b

| | 03b | Model 04 |
|---|---|---|
| Speed action range | 1.0–2.5 m/s | **1.3–3.0 m/s**. Floor above 03b's 1.28 m/s average, so it can't creep back into cautious driving |
| Lap bonus | +50 flat | **+100 × (average lap speed / 2 m/s)**: 65 at 1.3 m/s, 100 at 2 m/s, 150 at 3 m/s |
| Expert | 1.0–2.5 m/s, grip 4 m/s², braking 3 m/s² | same, with MIN/MAX 1.3/3.0 |

Floor choice (offline test, kinematic model): the floor doesn't change the expert's lap times (Vegas 9.1 s at 1.2, 1.3, 1.4 or 1.5), only the grip demand at the tightest moments: 1.3 keeps Vegas/Summit at 4.0 m/s² and the tightest tracks ≤ 5.9 (1.5 → up to 7.9). All 10 tracks lapped.

## Incident at start

The first start trained on **reinvent_base** for about a minute: this morning's interrupted evaluation loop had left `DR_WORLD_NAME=reinvent_base` in run.env. Stopped, wiped (`-w`), restarted on Vegas. Prevention: `tools/wsl/start_run.sh` now always forces `DR_WORLD_NAME=Vegas_track`, and `evalrun.sh` restores run.env on exit even if interrupted.

## Run

| | |
|---|---|
| Prefix | `cedc-m04-fast` |
| Pretrained | `cedc-m03b-final`, best (= ckpt 69) |
| Start / stop | 2026-09-30 ~11:30 → 17:00 |

## Upload rule

Mean evaluation time over Vegas + Summit + re:Invent 2018 + re:Invent 2024 CW (off-track penalties included, all trials complete) **below 17.7 s** (Model 03).

## Results

Training 11:30–17:00 (`cedc-m04-fast` → `-2` → `-3`): two silent trainer stalls after mid-iteration simulator restarts (fixed: restart only at iteration boundaries, plus stuck-trainer detection). Last hour: about 15/20 laps, 87% mean progress, both directions balanced, laps about 14.5 s.

Evaluation (3 trials per track, penalties included, all trials completed):

| Candidate | Vegas | Summit | re:Invent 2018 | 2024 CW | **Mean** | Off-tracks | Unseen eff. | Gap |
|---|---|---|---|---|---|---|---|---|
| **final (ckpt 108)** | 15.83 | **19.00** | **13.01** | 20.33 | **17.04 s** | **15** | **55%** | **+10** |
| 13:30 (ckpt 84) | 14.54 | 20.37 | 14.66 | 19.66 | 17.31 s | 24 | 52% | +19 |
| 15:00 (ckpt 93) | 15.90 | 18.65 | 16.01 | 21.30 | 17.97 s | 30 | 51% | +14 |
| 16:00 (ckpt 100) | 15.40 | 18.39 | 18.30 | 24.24 | 19.08 s | 35 | 48% | +19 |
| *Model 03 ckpt 31 (uploaded)* | *14.7* | *21.6* | *14.0* | *20.5* | *17.7 s* | *30* | *54%* | *+18* |

**Model 04 final is our best model**: faster on average than Model 03, half the off-tracks, the best unseen-track efficiency and the smallest Vegas gap. Packaged: `submissions/cedc-m04-final-ckpt108.tar.gz` (validated, 62.2 MB). **Recommended upload.**
