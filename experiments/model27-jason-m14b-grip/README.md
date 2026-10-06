# Model J27 (jason): Model 14b with sharp-turn speeds inside the measured grip

**Why (Jason, 2026-10-06):** "it always goes off track when it turns, it's either perfect or completely out; reduce the minimum speed to ~2.2, keep the max". Physics check with Elyas's grip test (radius ≈ 0.34 m / tan(steer), the car holds ~8.4 m/s² sideways): Model 14b's **30° at 2.5 m/s needs 10.6 m/s²** and **20° at 2.9 m/s needs 9.0 m/s²**, both beyond the grip, so the sharpest actions slide wide; 12° at 3.1 (6.0 m/s²) is fine.

**Change vs Model 14b (`experiments/model14b-cap4`):** 30° 2.5 → **2.2 m/s** (8.2 m/s²), 20° 2.9 → **2.7 m/s** (7.8 m/s²); expert `MIN_SPEED` 2.5 → 2.2. Same 15 actions in the same order, top speed 4.0, reward otherwise unchanged, so it fine-tunes from Elyas's `m14b-w8-end` (portal 6.338). Offline expert (`tools/test_reward.py`, measured geometry): completes all 10 test tracks.

Two simulators, reInvent2019_wide + reinvent_base, no DR, lr 0.0001, 45-min legs, snapshots every 30 min. Replaces J26 (20 min, unchanged Model 14b).

## Results

**Test after leg 1 (14:28, 5 trials, DR off; `logs/m27_test.txt`):**

| Model | reInvent2019_wide off / mean | reinvent_base off / mean |
|---|---|---|
| Elyas's m14b-w8-end (portal 6.338) | 3 / 7.70 s | 11 / 9.92 s |
| **J27 wb1-end** (45 min) | **1 / 7.05 s** | **9 / 9.58 s** |

Better on both after one leg. Packaged `submissions/m27-jason-wb1-end-ckpt388.tar.gz`. Resumed as `m27b-jason-*`.

Side finding: m14b-w8-end leaves reinvent_base 11× in 5 laps locally but ran clean on the portal (6.338 / 6.270), so the secret track is unlikely to be re:Invent 2018-like in its tight corners; A to Z (reInvent2019_wide) fits better.
