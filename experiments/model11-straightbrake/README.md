# Model 11: brake in a straight line, stop wiggling

**Why:** the 7.130 model (Model 10 variety `c2-end`) still wiggles (seen in the ghost-race video). Measured on its completed training laps:

| On straights | reInvent2019_wide (66 laps) | rI2024 (27 laps) |
|---|---|---|
| left/right flips per second | 3.8 | 2.9 |
| steps with steering ≠ 0 | 98% | 98% |
| braking steps taken while steering ≥ 12° | 100% | 100% |

The action set had no slow *straight* action (slowest straight 3.0 m/s; the slow actions were all 12–30°), so the car could only brake while turning, and "6° at 4.0" was as fast as "straight at 4.0", so it alternated ±6° on straights.

**Changes vs Model 10** (same 15 actions, fine-tunes from the 7.130 model):
1. Actions: straight 3.0 → **2.0**, straight 3.5 → **3.0** (straight-line braking); ±6° at 4.0 → **3.5** (only straight reaches 4.0). Straight speeds: 2.0 / 3.0 / 4.0.
2. Smoothness bonus weight 0.5 → 1.0.

A closed-loop kinematic check could not show a difference (the simulated expert barely wiggles and the kinematic car has no penalty for braking while turning), so this is judged in the simulator / on the portal.

| | |
|---|---|
| Starts from | `cedc-m10v-c2-end` (portal **7.130** / 6.740) |
| Schedule | lr 0.0001, 30-min phases: reInvent2019_wide, reinvent_base, rI2024, Bowtie, reInvent2019_wide, reinvent_carpet, Vegas, reinvent_base, reInvent2019_wide (14:44 → ~19:30, or until C: < 2 GB) |
| Check | wiggle numbers above (flips/s, % straight, braking while steering) + portal uploads of 2–3 snapshots |

## Results

(pending)
