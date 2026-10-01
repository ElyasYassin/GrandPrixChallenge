# Model 05: Racing line + smooth steering

**Why:** racing-driver principles the centre-line expert lacked. The lap-time simulation ([../ANALYSIS_limits.md](../ANALYSIS_limits.md)) says a racing line is worth about 1.6 s per Vegas lap (10.3 → 8.65 s theoretical). Our logs show heavy steering sawing (about 15° change per step, 53% of steps at full lock), and off-tracks happen at low lateral acceleration (steering errors, not grip).
**Starts from:** the best Model 04 checkpoint (chosen by the 17:00 evaluation). Same action space (1.3–3.0 m/s), both directions, Vegas only.

## Changes vs Model 04 (two ideas)

1. **Racing line** (outside → apex → outside). For the current track, the reward computes (and caches per track and direction) a line in the spirit of the **K1999** algorithm: each point moves sideways until its curvature equals the average of its neighbours', within 0.30 m of the edges. The expert steers toward that line and plans its speed from *its* curves.
   - First attempt (simple neighbour-midpoint smoothing) shrank the whole loop onto the inside edge → off track on 10/10 tracks. Replaced by curvature averaging.
   - Margin 0.22 m went off on 6/10 tracks (pure pursuit cuts inside the line); **0.30 m laps all 10**.
   - Tightest radius on Vegas 0.58 → about 0.8 m.
2. **Smooth hands.** A bonus of up to +0.5 per step for small steering changes (0 at ≥15° change). Remembers the previous step's steering, resets at each episode.

Everything is computed from the runtime `waypoints` / `track_width` of whatever track the car is on, so nothing is hard-coded.

## Offline validation (kinematic car, 10 tracks)

| Track | M04 expert (centre) | **M05 expert (racing line)** |
|---|---|---|
| Vegas | 9.1 s | **8.2 s** |
| Summit Speedway | 9.7 s | **8.7 s** |
| re:Invent 2022 champ | 13.2 s | **12.2 s** |
| Jyllandsringen | 22.1 s | **20.7 s** |
| Arctic | 21.3 s | **20.3 s** |
| Spain | 22.2 s | 21.5 s |
| reinvent_base / reInvent2019 / Oval / 2024 CW | 6.7 / 8.5 / 7.0 / 9.4 s | 6.5 / 8.5 / 7.0 / 9.1 s |

All 10 lapped; peak lateral acceleration 4.0 m/s² (5.5 on the tightest). Reward on a straight: smooth steering 5.15, ±12° zig-zag 3.15, full-lock sawing 2.68 per step. Racing line build about 0.8 s once per track and direction; reward call about 0.1 ms.

## Evaluation criteria

Upload if the mean eval time over the 4 tracks (penalties included) beats the current best, and check **generalization efficiency** ([tools/efficiency.py](../../tools/efficiency.py)): the unseen-track efficiency should not drop and the Vegas gap should stay small.

## Results

Training 17:50–21:00 (`cedc-m05-racingline`, 546 episodes, stopped early). It started strong (inherited M04 skill) but **reliability fell instead of improving**:

| Episodes | M04 laps / 60 | **M05 laps / 60** |
|---|---|---|
| 0–59 | 19 | 33 |
| 120–179 | 23 | 32 |
| 300–359 | 32 | 36 (best stretch, snap2 = ckpt 125) |
| 360–419 | 36 | 22 |
| 420–479 | 39 | 16 |
| 480–539 | 38 | 20 |

Laps were not faster either (≈14.7–14.9 s vs M04 ≈14.6 s). Likely causes: the full racing line runs closer to the edges and pure pursuit cuts inside it (less margin); wider radii raise the expert's corner speeds; the smoothness bonus may suppress quick corrections. **Stopped at 21:00.** Snapshots: snap1 ckpt 116, snap2 ckpt 125, snap3 ckpt 134, final ckpt 135. Snap2 evaluated on 4 tracks (see LOG). Follow-up: **Model 05b**, a gentler line (50% blend) and half the smoothness bonus.
