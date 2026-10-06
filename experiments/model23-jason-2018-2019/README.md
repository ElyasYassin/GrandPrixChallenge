# Model J23 (jason): re:Invent 2018 + re:Invent 2019 (wide) together, from J22

**Why (Jason, 2026-10-05):** "do both re:Invent 2018 and re:Invent 2019, they are similar tracks but one is wider". `reinvent_base` (2018: 17.7 m, 0.76 m wide) on one simulator and `reInvent2019_wide` (16.6 m, 1.07 m wide) on the other, every batch. Both are in Elyas's estimated 17–20 m range for the secret track; reInvent2019_wide transferred best to the portal in the 7.130 run.

**Settings = the 7.130 run's** (Model 10 reward + actions, no DR, lr 0.0001, alternating direction, changing start positions). Start: J22's final snapshot (7.130 model + ~4 h on reinvent_base). 8 × 45-min legs, snapshots every 30 min (~22:15 → ~04:30). Snapshots packaged for portal uploads.

## Results

Trained 22:09 → 04:21 (8 × 45 min). Training (last 120 episodes per leg): reinvent_base 45–57 % (best leg 6: 57 %, ~20 % laps), reInvent2019_wide 67–80 % (leg 6: 80 %, 74/120 laps). Plateau from leg 2.

Comparison eval 04:25 (5 trials per track, DR off, 1 s penalties; `logs/m23_eval.txt`):

| Model | reinvent_base off / mean | reInvent2019_wide off / mean | total off |
|---|---|---|---|
| 7.130 model (portal 7.130) | 5 / 8.63 s | 4 / 7.92 s | 9 |
| J17 wv1-end (portal 7.389) | 1 / 7.53 s | **0** / 7.30 s | **1** |
| J22 b5-end (2018 only) | 4 / 8.16 s | 4 / 8.57 s | 8 |
| J23 bw2-end | 2 / 7.88 s | 2 / 7.69 s | 4 |
| J23 bw6-end | 3 / 8.24 s | **0 / 6.95 s** | 3 |
| **J23 bw8-end** | **1 / 7.37 s** | 1 / 7.09 s | 2 |

Packaged for portal (Jason uploads): `m23-jason-bw8-end-ckpt584`, `m23-jason-bw6-end-ckpt535`, `m23-jason-bw2-end-ckpt429`. Continued as J24 (same recipe from bw8-end).
