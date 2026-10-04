# Model 11b: make "straight" pay

**Why:** after 1.5 h, Model 11 (straight-line braking actions + smoothness ×2) still drove like the 7.130 model: wheels straight on only 1–2% of straight-section steps, 3–4 left/right flips per second, 99% of braking while turning. The imitation reward scores a 6° action about as well as 0° when the expert asks for a small correction, so the new straight actions never won.

**Changes vs Model 11** (same 15 actions):
1. `STRAIGHT_BONUS = 1.0` when the expert's steering is below 5° and the car's wheels are straight.
2. `FLIP_PENALTY = 0.5` when the steering changes side (left ↔ right) between consecutive steps.
3. lr 0.0003 for the first two phases (habit change), then 0.0001.

Sanity check on a straight (expert: 0.1°, 4.0 m/s): straight step 10.5, 6° step 8.25, flip to −6° 7.34.

| | |
|---|---|
| Starts from | `cedc-m11-c1-stop` (Model 11 after rI2024 phase, ckpt 221) |
| Schedule | 30-min phases: reInvent2019_wide, reinvent_base (lr 0.0003), Bowtie, reInvent2019_wide, reinvent_carpet, rI2024, Vegas, reinvent_base, reInvent2019_wide (lr 0.0001), 16:18 → ~21:00 |
| Check | % straight on straights, flips/s, braking while turning; lap time and completion; portal uploads |

## Results

(pending)
