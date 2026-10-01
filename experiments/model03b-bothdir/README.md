# Model 03b: Speed + both directions

**Why:** Model 03 (checkpoint 31) is fast and clean on Vegas (3/3, 14.5–15.2 s), but on unseen tracks it goes off in **right-hand turns** at speed. On Summit Speedway (which Model 02 drove 3/3 clean) it had 4–7 off-tracks per lap, 10 of 16 in right-handers (T6, T8, T9, radius 0.76–0.93 m). Vegas counterclockwise is mostly left turns, so the model barely practised right-handers.
**Change vs Model 03:** `DR_TRAIN_ALTERNATE_DRIVING_DIRECTION=True`: every other episode drives Vegas clockwise, which turns its left-handers into right-handers. Still Vegas only (within the rules).
**Starts from:** `cedc-m03-speed-3` checkpoint 31.

## Bug found while starting (fixed)

The reward returned 0.001 whenever `params["is_reversed"]` was true, which I had read as "driving the wrong way". In DeepRacer it means **"driving the track clockwise"**, so every reversed episode earned nothing (first test: mean reward per step 0.00 in all odd episodes, about 4 in even ones). Removed from all reward functions (Models 02 and 03 only drove counterclockwise, so their results are unaffected). Verified: in reversed episodes the simulator also reverses the waypoint list (indices still increase), so the expert steers correctly in both directions.

## Evaluation plan

Same as Model 03: Vegas (3 trials) + Summit Speedway, re:Invent 2018, re:Invent 2024 CW. **Upload only if** Vegas stays 3/3 clean and Summit Speedway is 3/3 clean (as Model 02 was).

## Results

Training 00:05–06:31: 990 episodes, 516 laps, 0 crashes (19 routine simulator restarts for the memory leak). Clockwise progress rose from 26% to about 77%, matching counterclockwise. Average speed drifted down from about 1.46 to 1.28 m/s.

| Model | Vegas | Summit | re:Invent 2018 | re:Invent 2024 CW | Mean | Off-tracks / 12 trials |
|---|---|---|---|---|---|---|
| Model 03 ckpt 31 | 14.7 | 21.6 | 14.0 | 20.5 | **17.7 s** | 30 |
| 03b ckpt 56 (04:00) | 17.0 | 24.5 | 16.6 | 22.2 | 20.1 s | 28 |
| 03b ckpt 69 (final) | 18.3 | 23.4 | 16.9 | 22.8 | 20.3 s | **11** |
| 03b ckpt 63 (05:00) | 18.5 | 24.8 | 17.9 | 21.9 | 20.8 s | 26 |

**Hypothesis confirmed (right turns) but net result worse:** fewer off-tracks, slower laps. Not uploaded. `cedc-m03b-final` kept as the most reliable model (physical-race candidate). Details: [../OVERNIGHT_2026-09-30.md](../OVERNIGHT_2026-09-30.md).
