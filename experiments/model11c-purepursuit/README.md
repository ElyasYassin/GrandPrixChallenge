# Model 11c: a calmer expert (pure pursuit with the measured car geometry)

**Why:** Model 11 / 11b didn't stop the wiggle. Replaying 11b's laps on reInvent2019_wide through the expert: on straights the expert said "straight" (< 5°) only **7%** of the time and asked for a **median of 30°**; the car answered with ±12–20° swings (0° on 11 of 608 straight steps). The expert set steering = heading error to the target point, which over-steers ~2× for this car (it turns ~2× wider per degree than nominal, `model10-realcar/grip_test.txt`).

**Change vs Model 11b:** expert steering by pure pursuit with the measured geometry: `steer = atan(2 · 0.34 m · sin(alpha) / distance)`. Speed logic unchanged; straight bonus and flip penalty kept.

Closed-loop check (kinematic car with the measured geometry, 5° steering noise, actions snapped to the 15 actions):

| Track | old expert: flips/s, full lock, lap | pure pursuit |
|---|---|---|
| reInvent2019_wide | 1.6, 19%, 5.5 s | **0.9, 10%, 5.5 s** |
| reinvent_base | 1.7, 15%, 5.9 s | **0.7, 7%, 5.9 s** |
| 2024_reinvent_champ_cw | 2.3, 16%, 7.9 s | **0.7, 3%, 7.5 s** |
| Vegas | 1.3, 17%, 7.1 s | **1.0, 5%, 7.3 s** |

| | |
|---|---|
| Starts from | `cedc-m11b-b1-stop` (ckpt 228; lineage: 7.130 model → M11 → M11b) |
| Schedule | 30-min phases: wide, base, rI2024 (lr 0.0003), Bowtie, wide, carpet, Vegas, base, wide (lr 0.0001); 16:57 → ~21:40 |

## Results

(pending)
