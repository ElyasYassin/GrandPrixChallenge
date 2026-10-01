# Model 02: Imitation through the reward

**Change vs Model 01:** reward function only. The action space, hyperparameters and track are identical.
**Hypothesis:** rewarding agreement with a simple expert (pure pursuit + slow down before curves) teaches cornering directly. We expect faster learning, far less zig-zag (baseline: 23° steering change per step, 40% of steps at full lock), and the first complete laps.

## The expert (computed inside the reward, every step)

- **Steering:** aim at a point 0.8 m ahead on the centre line (pure pursuit), clipped to ±30°.
- **Speed:** look 1.5 m ahead. If the centre line turns less than 10°, use 1.0 m/s; at 60° or more, use 0.5 m/s; linear in between.
- It only uses the **current track's** `waypoints` param, so there's no hard-coding and it works on any track.

## Reward

```
off track / reversed           -> 0.001
1 + 2·exp(-(steer error / 10°)²) + 1·(speed match)       (max 4)
× 0.5 if closer than 10% of the width to an edge
+ 0.5·pace (progress per step, capped)
+ 50 on lap completion
```

## Offline validation ([tools/test_reward.py](../../tools/test_reward.py))

The expert, driving a kinematic car model on its own, **completes a lap on all 10 test tracks**, including 9 it was never tuned for (17–62 m, 0.67–1.07 m wide). Expert actions earn 4.5 per step vs about 2.6 for random and about 2.9 for mirrored steering. Steering signs checked (left turn +, right turn −). Runtime 0.012 ms per call.

## Run configuration

| Setting | Value |
|---|---|
| Model prefix | `cedc-m02-imitation` (fresh, not continued from the baseline) |
| Track | `Vegas_track` |
| Action space | continuous, steering ±30°, speed 0.5–1.0 m/s (same as Model 01) |
| Hyperparameters | DRfC defaults (same as Model 01) |
| Workers | **2** (about 16 steps/s total vs 9.8 for Model 01), so compare against the baseline **by episode count**, not wall time |
| Start / planned stop | 2026-09-29 16:03 → 18:03 MDT |

## Results

### Training (2026-09-29 16:03–18:15, about 2 h with crashes and resumes)

Runs `cedc-m02-imitation` → `-2` → `-3` → `-4` → `-5` (continued after crashes; `-2` switched to compose mode; `-4` onward uses 1 worker).

| | Model 02 | Baseline (Model 01) |
|---|---|---|
| Episodes | 336 | 225 |
| Mean progress, last 20 episodes | **47%** | 26% |
| Laps in training | **13** (best 26.9 s) | 0 |
| At 185 episodes (same count) | 26% mean, first lap | 21% mean, 0 laps |
| Steering change per step | 21° | 23° |

The hypothesis was only partly confirmed: much better progress and laps, but **the zig-zag didn't go away** (about 21°/step, 45% of steps at full lock).

### Evaluation: checkpoint 11 (`cedc-m02-imitation-5` best, DRfC eval metric 94.7%)

Practice-race rules: 3 trials, individual lap, unlimited resets, 1 s off-track penalty.

| Track | Seen in training? | Lap times | Off-tracks per lap | Clean laps |
|---|---|---|---|---|
| **Vegas_track** (CCW) | yes | 26.98 / 27.50 / 27.19 s | 0 | **3/3** |
| 2022_summit_speedway | no | 29.04 / 28.32 / 29.15 s | 0 | **3/3** |
| reinvent_base (re:Invent 2018) | no | 27.31 / 27.76 / 27.40 s | 4 | 0/3 |
| 2024_reinvent_champ_cw (clockwise) | no | 39.86 / 39.07 / 38.80 s | 5 | 0/3 |

**Key finding: every off-track on the unseen tracks was in a tight RIGHT-hand turn** (radius 0.64–0.90 m). None happened on left turns or straights. Vegas counterclockwise is mostly left turns, so the model barely practised right-handers. It generalizes on left-dominant tracks and fails on right-dominant ones.

**Submission candidate:** `submissions/cedc-m02-best-ckpt11.tar.gz` (validated, 61.5 MB).

## Conclusion / next change

**Model 03: train Vegas in both directions** (`DR_TRAIN_ALTERNATE_DRIVING_DIRECTION=True`), continuing from checkpoint 11. That gives as many right turns as left, stays within the rules (Vegas only), and targets the one failure mode we found.
