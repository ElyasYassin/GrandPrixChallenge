# Model 01 — Baseline

**Purpose:** Get a reference point. Every later model is compared against this one.
**Hypothesis:** The car will learn to stay on track but drive slowly and zig-zag, since nothing rewards speed or smooth steering.

## Configuration (fill in what the console actually shows)

| Setting | Value |
|---|---|
| Model name | `cedc-m01-baseline` |
| Race type | Time Trial |
| Training track | AWS Summit Raceway (Vegas) |
| Algorithm | PPO |
| Sensor | Single camera |
| Action space type | default (record: continuous / discrete) |
| Steering range | default (record: e.g. -30° to 30°) |
| Speed range | default (record: e.g. 0.5 to 1.0 m/s) |
| Hyperparameters | all defaults |
| Stop condition | 60 minutes |
| Reward function | [reward_function.py](reward_function.py) |

### Local DRfC run (started 2026-09-29 ~14:10 MDT)

| Setting | Value |
|---|---|
| Model prefix | `cedc-m01-baseline` |
| Track | `Vegas_track` (CCW, 22.55 m) |
| Action space | continuous, steering -30° to 30°, speed 0.5 to 1.0 m/s |
| Network | `DEEP_CONVOLUTIONAL_NETWORK_SHALLOW`, `clipped_ppo` |
| Hyperparameters | DRfC defaults (batch 64, lr 3e-4, γ 0.99, entropy 0.01, 20 episodes/iteration, 5 epochs) |
| Workers | 1 |
| Stop | manually after 60 min (`dr-stop-training`) |

### Local results (2026-09-29)

| Iteration | Mean reward | Mean progress | Max progress | Laps |
|---|---|---|---|---|
| 0 | 64 | 6% | 13% | 0 |
| 5 | 146 | 15% | 42% | 0 |
| 7 | 195 | 19% | 40% | 0 |
| — crash at 15:24, resumed from iteration 7 as `-gpu-2` — | | | | |
| 9 | 191 | 20% | 57% | 0 |
| 10 | 102 | 13% | 43% | 0 (dip right after resume) |
| 11 | 178 | **26%** | **65%** | 0 |

- **0 laps in 225 episodes.** The starter reward learns slowly: it pays the same for crawling as for driving well, and nothing tells the car how to take corners.
- Off-track hotspots: the S-section (waypoints 35–55, T3–T4), then T9/T10.
- Driving style (last 75 episodes): steering changes by **23° per step** on average, **40% of steps at full lock** (±30°), mean speed 0.75 m/s. Heavy zig-zag, which the reward never penalizes.
- Logs: `logs/cedc-m01-baseline*`; charts: TensorBoard runs of the same name.

## Results

| Metric | Value |
|---|---|
| Training: final avg. progress % | |
| Training: reward curve shape (rising / flat / noisy) | |
| Evaluation: laps completed / trials | |
| Evaluation: best lap time | |
| Practice race result (optional) | |
| Portal: completion rate / public score / best lap | |

## Observations

Watch the evaluation video and answer:

- Does it stay on track?
- Does it zig-zag on straights?
- Where does it fail (which turn)?
- Is it unnecessarily slow?

## Conclusion / next change

_One idea to change for Model 02:_
