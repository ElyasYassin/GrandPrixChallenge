# Model J34 (jason): wb7 on A to Z only, with a straighter racing line through the S-bend

**Why (Jason, 2026-10-07):** "why does the car follow the flow through the S-bend instead of going straight? If the narrow track can't, train wb7 on the wider track only." The reward's racing line (J29 / Model 14b: single-scale, 0.30 m from each edge) can move only ±0.23 m off the centre on A to Z (1.07 m) and ±0.08 m on re:Invent 2018 (0.76 m), so it follows the flow.

Closed-loop expert check (measured geometry, 5° steering noise, J29 speeds, 3 seeds):

| Line | A to Z lap / off-tracks | re:Invent 2018 lap / off-tracks |
|---|---|---|
| current (single-scale, 0.30 m) | 4.60 / 0 | 4.89 / 0 |
| **multi-scale, 0.30 m** | **4.47 / 0** | 4.87 / 0 |
| multi-scale, 0.25 m | 4.82 / 0.3 | 5.82 / 1.0 |
| multi-scale, 0.20 m | 6.58 / 2.0 | 6.80 / 2.0 |
| multi-scale, 0.15 m | 9.47 / 4.7 | 8.91 / 4.0 |

Going closer to the edges also moves every apex outward and the expert leaves the track; the multi-scale line at the safe 0.30 m straightens the S on A to Z with no extra off-tracks. On re:Invent 2018 a safe line barely leaves the centre, so **J34 trains on A to Z only**.

**Recipe:** J29's reward + actions with the multi-scale racing line (0.30 m), from **wb7-end** (portal 5.814 clean), both simulators on reInvent2019_wide, no DR, lr 0.00005, 30-min legs, tested hourly on A to Z (stop if less reliable than wb7 after ~2 h). Replaces J33.

## Results

**Test 1 (18:55, A to Z 10 trials, DR off; `logs/m34_test1.txt`):**

| Model | clean laps | mean | clean median | best clean |
|---|---|---|---|---|
| wb7-end (portal 5.814) | 4/10 | 6.96 | 5.84 | 5.28 |
| **J34 sz1-end** (30 min) | **8/10** | **5.93** | **5.62** | 5.34 |
| J34 sz2-end (1 h) | 7/10 | 6.34 | 5.74 | 5.42 |

The straighter S-line made wb7 both steadier and faster. Packaged `submissions/m34-jason-sz1-end` (upload candidate: P(3 clean trials) ≈ 0.5, clean laps ≈ leader pace).

**Narrow-track check (19:19, reinvent_base 5 trials; `logs/narrow_test.txt`):** sz1-end 5 off (one per lap, 7.2–7.3 s), wb7-end 10 off, wb16-end 18 off: no sign that 30 min of A to Z-only training specialised sz1.

**21:05: switched to both tracks.** Elyas's Model 21 (wb7 + A to Z only, ~8 h; locally 7/10 clean, median 5.42) scored **12.472 / 11.877** on the portal (#75): A to Z-only training overfits. J34 continues from sz1-end on **A to Z + re:Invent 2018** (`m34d-jason-*`), lr 0.00005. Later A to Z-only snapshots (sz2–sz6) are not upload candidates.
