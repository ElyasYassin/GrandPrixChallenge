# Experiment claims

Check here before starting a run. Add a row **before** you start; set Status to `done` (with a link to results) or `dropped` when finished.

| Date | Who / machine | Experiment | Starts from | Status | Results |
|---|---|---|---|---|---|
| 2026-10-01 | Elyas / 3090 | **Model 07 reliability (07b)**: off-track penalty −20 + edge-safety factor, speed 1.3–4.0, lr 0.0001 | M06 snap 03:39 (`cedc-m06-snap0339`) | **done** (stopped early 14:03: training plateaued) | no clear gain over M05 snap2 (see LOG) |
| 2026-10-01 | Elyas / 3090 | **Model 08 discrete actions** (15 actions), from scratch, M07 reward; track rotation Vegas → 2024_reinvent_champ_cw → 2022_summit_speedway (×3). Takes over the open discrete-action item. See `experiments/model08-discrete` | scratch | **done** (stopped 01:44: C: drive full) | portal 16.693 (17:53), **10.824** (21:47) |
| 2026-10-02 | Elyas / 3090 | **Model 09 speed push**: distance reward, lap bonus ∝ speed², off-track −5; stand-in tracks only. See `experiments/model09-speed` | M08 vegas2-2147 | **done** 07:21 (trained only on rI2024: track switches failed) | not faster than M08; ~70% laps; candidates packaged |
| — | open | **From-scratch control**: M05 reward, continuous actions, from scratch, to test whether the curriculum helps | scratch | **open** | — |
| — | open | **Hyperparameters**: discount 0.999 and/or 40 episodes per update | M05 snap2 | **open** | — |
