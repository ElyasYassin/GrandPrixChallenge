# Model 14b: 4 m/s cap, the two closest tracks

Model 13c's reward and Model 13's 15 actions with every speed above 4 m/s lowered to 4.0 (straight 5.0 → 4.0, ±6° 4.3 → 4.0; expert top speed 4 m/s; grip budget 9 unchanged). Reasons: the portal (and certainly the physical car) likely caps speed at 4 m/s, and a model trained on 5 m/s would mistime braking where 5 is not reachable; on a ~17 m track a perfect driver gains only ~2.5% from 5 m/s (lap_time_sim: A to Z 4.69 vs 4.57 s at grip 10).

Training: from `m13-w4-end` (portal best lap 6.333; 64% laps on A to Z), no domain randomization, alternating **A to Z Speedway (reInvent2019_wide)** and **re:Invent 2018 (reinvent_base)**, the same layout in two widths and our best guess for the hidden track's shape. 30-min phases, lr 0.0001, snapshots every 30 min, run prefixes cleaned. Model 14 (10 tracks + DR + 5 m/s) was stopped: completion fell to 0–29%.

## Results

(pending)
