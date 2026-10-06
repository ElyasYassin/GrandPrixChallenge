# Model J27 (jason): Model 14b with sharp-turn speeds inside the measured grip

**Why (Jason, 2026-10-06):** "it always goes off track when it turns, it's either perfect or completely out; reduce the minimum speed to ~2.2, keep the max". Physics check with Elyas's grip test (radius ≈ 0.34 m / tan(steer), the car holds ~8.4 m/s² sideways): Model 14b's **30° at 2.5 m/s needs 10.6 m/s²** and **20° at 2.9 m/s needs 9.0 m/s²**, both beyond the grip, so the sharpest actions slide wide; 12° at 3.1 (6.0 m/s²) is fine.

**Change vs Model 14b (`experiments/model14b-cap4`):** 30° 2.5 → **2.2 m/s** (8.2 m/s²), 20° 2.9 → **2.7 m/s** (7.8 m/s²); expert `MIN_SPEED` 2.5 → 2.2. Same 15 actions in the same order, top speed 4.0, reward otherwise unchanged, so it fine-tunes from Elyas's `m14b-w8-end` (portal 6.338). Offline expert (`tools/test_reward.py`, measured geometry): completes all 10 test tracks.

Two simulators, reInvent2019_wide + reinvent_base, no DR, lr 0.0001, 45-min legs, snapshots every 30 min. Replaces J26 (20 min, unchanged Model 14b).

## Results

(pending)
