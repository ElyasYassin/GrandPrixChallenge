# Model 15 (jason): follow the racing line (path tracking) for lap time

**Why (Jason, 2026-10-04):** "looks great, now just get better time on path choosing".

What the evaluation laps show (Model 13 `wooc1-end`, `evals/m13-*`):

| Track | dist to racing line | dist to centre | within 0.10 m of line | mean speed |
|---|---|---|---|---|
| Vegas | 0.19 m | 0.15 m | 30 % | 1.94 m/s |
| Summit | 0.19 m | 0.13 m | 26 % | 2.01 m/s |
| reInvent2019 | 0.21 m | 0.16 m | 29 % | 1.86 m/s |

The car drives nearer the centre than the racing line and never picks the 4 m/s actions on straights (0-1 %); the expert itself only asked ~2.6-2.8 m/s there. The ideal lap on the line (`tools/lap_time_sim.py`) is ~6.5 s on Vegas vs ~11 s driven. Model 14b's straight bonus cut flips (Summit 4.8 → 3.2 /s) but not the hard-steering share (61 → 62 %): the expert term (weight 2) still pays for copying a twitchy expert.

**Change vs Model 14b (one idea):** the expert becomes a Stanley-type path tracker on the racing line: steering = feed-forward from the line's curvature just ahead (atan(0.34 m × κ)) + heading error to the line + atan(1.5 × lateral offset / (v + 0.5)); speed from the line's curvature profile, still capped by the commanded steering (keeps completion). Reward otherwise identical (completion bonus, racing-line term, smoothness/straight bonus, multi-scale line, slow-start speeds).

Closed-loop check (`tools/expert_closed_loop.py` with the measured 0.34 m geometry, 8° steering noise, 1-step delay, 5 tracks × 3 seeds):

| Expert | lap total | off-tracks | full lock | mean speed |
|---|---|---|---|---|
| Model 14b (aim ~1 m ahead) | 40.8 s | 3.0 | 15 % | 2.96 |
| Stanley, gain 1.0 / 1.5 / 2.5, no steering cap | 35.3 / 33.8 / 34.7 s | 3.7 / 2.0 / 2.7 | 9-12 % | 3.5 |
| **Stanley, gain 1.5 + steering cap** | **36.9 s** | **1.0** | 7 % | 3.10 |

`tools/test_reward.py` (measured geometry): the expert completes all 10 test tracks; reward expert / random / mirrored ~4.6 / 2.6 / 3.2.

## Run

From the best Model 14b snapshot (evaluation decides), two workers, DR on, Vegas-heavy pairs as in Model 14b, lr 0.0003 then 0.0001.

## Results

(pending)
