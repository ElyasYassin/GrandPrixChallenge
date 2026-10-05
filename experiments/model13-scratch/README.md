# Model 13: everything we learned, from scratch (wiggle-free from day one)

**Why:** goal ~5.4 s on the secret track (best 7.130 / 6.740). The 7.130 model wiggles (wheels straight on ~2% of straight steps, braking only while turning), and Model 11/11b/11c showed those habits can't be trained out of a model that has 200+ iterations of them. Model 12 (faster limits on that line) would inherit the wiggle. So: start from random weights with the right incentives from the first episode.

| Ingredient | From |
|---|---|
| Grip 9 m/s², top speed 5 m/s | Model 12 |
| Pure-pursuit expert with the measured geometry (0.34 m) | Model 11c |
| Straight-line braking (straight at 2.5), only straight reaches 5.0 | Model 11 |
| Straight bonus (+1) and flip penalty (−0.5), smoothness 1.0 | Model 11b |
| Distance reward, lap bonus ∝ speed², off-track −5 | Model 09 |
| Short tracks (reInvent2019_wide, reinvent_base, Bowtie) + rI2024 from the start | Model 10 variety (7.130) |

Actions (15): 0° at 2.5 / 3.6 / 5.0; ±6° at 3.8 / 4.3; ±12° at 3.1 / 3.7; ±20° at 2.9; ±30° at 2.5.

Closed-loop expert (measured car, 5° noise, actions snapped): wide 5.07 s, base 5.02 s, rI2024 7.64 s, Bowtie 5.87 s; occasional off-tracks on the narrow tracks (0.3–1 per lap): it drives at the grip limit.

| | |
|---|---|
| Starts from | scratch |
| Schedule | lr 0.0003; wide 60 min, then 30-min phases rotating base / rI2024 / wide / Bowtie; 01:21 → ~08:00 |
| Check | first laps (~1 h), completion trend, wiggle metrics (wheels straight on straights, flips/s, braking while turning) vs the 7.130 model |

## Results

(pending)
