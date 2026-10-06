# Model 16 (E3): "free racing"

From `m14b-w8-end` (portal **6.338** / 6.270, clean). The reward no longer asks the car to copy the expert: it is paid only for **distance covered per step** (15 × % of the lap) and for **fast laps** (300 × (avg speed / 2 m/s)²), minus the speed-scaled off-track penalty (−2 × speed); a wheel over the line still earns ~0 for that step. No steering/speed imitation, smoothness, straight bonus, flip penalty or edge-safety factor. Goal: beat the expert's own line and braking (our models drive ~80 % as fast as the expert, and the expert is near the theoretical limit, so only an expert-free reward can go beyond it).

Settings back to standard (lr 0.0001, entropy 0.01, 20 episodes/update, batch 64, discount 0.99) after E1 (Model 15: lr 0.00005, entropy 0.002, 40 eps, batch 128, discount 0.995) made the model slightly *worse* in 1.5 h (A to Z 59 → 52 %, re:Invent 2018 26 % vs 14b's 39–45 %).

Same 4 m/s actions and tracks (A to Z + re:Invent 2018, alternating 30-min phases), 2026-10-06 15:03 → ~18:20, snapshots every 30 min. Risk: may first get worse / more aggressive without the expert; judge by uploads.

## Results

(pending)
