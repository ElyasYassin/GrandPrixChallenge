# Model 14b (jason): Model 14 reward with Model 12a/13 speeds

Model 14's reward (completion bonus, racing-line term, smoothness + straight bonus, multi-scale racing line; see `../model14-jason-smooth/README.md`) with the slow-start speeds, because Model 14's faster actions left training progress flat at 30-37 %. From `cedc-m13-jason-wooc1-end`, 13:44 → 18:39, legs as in Model 14 (Vegas in 4 of 6).

## Results

Training was the best so far (Vegas 79-83 % progress, ~70 % finished laps; carpet 76 %; Summit 83-90 %), but the evaluation (DR off, 3 trials, practice-race rules; `logs/m14b_eval.txt`) did **not** beat Model 13 `wooc1-end`:

| Snapshot | Textured (carpet, wood, concrete) | 6 standard tracks | Vegas mean |
|---|---|---|---|
| Model 13 wooc1-end (start) | 9/9, 4 off, 11.16 s | 18/18, **0 off**, **12.53 s** | **11.16 s** |
| vk1-end (ckpt 266) | 9/9, 4 off, 11.26 s | 18/18, 5 off, 13.03 s | 12.25 s |
| rs1-end (ckpt 283) | 9/9, 7 off, 11.74 s | 18/18, 6 off, 12.86 s | 12.87 s |
| vs1-end (ckpt 302) | 9/9, 7 off, 11.63 s | 18/18, 6 off, 12.67 s | 11.84 s |
| rs2-end (ckpt 313) | 9/9, 7 off, 11.74 s | 18/18, 2 off, 12.69 s | 12.50 s |

Weaving (`tools/zigzag.py`, straights): Summit >= 12 deg share 61 → 46-50 %, flips 4.8 → 2.7-3.1 /s; Vegas mixed (42-69 % vs 47 %). The expert term (weight 2) still pays for copying a twitchy expert → Model 15 replaces the expert.
