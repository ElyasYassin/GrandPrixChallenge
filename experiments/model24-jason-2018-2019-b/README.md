# Model J24 (jason): J23 recipe continued from J23 bw8-end

Same as J23 (reinvent_base + reInvent2019_wide on the two simulators, Model 10 reward + actions, no DR, lr 0.0001, alternating direction), 5 × 45-min legs from `cedc-m23-jason-bw8-end` (04:50 → ~09:00) while waiting for portal feedback.

## Results

Trained 04:48 → 08:38 (5 × 45 min). Training peaked in leg 2 (reinvent_base 59 % progress, 34/120 laps, the best on that track so far; reInvent2019_wide 77 %), then slipped (legs 3–5: base 37–46 %, wide 80 → 54 %).

Eval of the peak (`bw2-end`, 5 trials, DR off): reinvent_base 5 off / 8.77 s, reInvent2019_wide 4 off / 7.87 s — **worse than J23 bw8-end** (1 / 7.37 s, 1 / 7.09 s). The training peak did not carry into evaluation. J23 bw8-end stays the pick; `m24-jason-bw2-end` packaged anyway.
