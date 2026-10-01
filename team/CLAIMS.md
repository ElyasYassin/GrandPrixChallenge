# Experiment claims

Check here before starting a run. Add a row **before** you start; set Status to `done` (with a link to results) or `dropped` when finished.

| Date | Who / machine | Experiment | Starts from | Status | Results |
|---|---|---|---|---|---|
| 2026-10-01 | Elyas / 3090 | **Model 07 reliability (07b)**: off-track penalty −20 + edge-safety factor, speed 1.3–4.0, lr 0.0001 | M06 snap 03:39 (`cedc-m06-snap0339`) | **running** (until 15:30) | — |
| 2026-10-01 | Elyas / 3090 | **Model 08 stand-in tracks**: fine-tune on 2024_reinvent_champ then 2022_summit_speedway (both directions); held-out eval on reInvent2019, reinvent_base, 2022_reinvent_champ_ccw, Vegas cw. See `SECRET_TRACK.md` | best M07 snapshot | **planned** (after M07, ~16:00) | — |
| — | open | **Discrete action space** model (10–15 actions derived from the expert's choices), trained from scratch with the M05 reward | scratch | **open: good fit for the second machine** | — |
| — | open | **From-scratch control**: M05 reward, continuous actions, from scratch, to test whether the curriculum helps | scratch | **open** | — |
| — | open | **Hyperparameters**: discount 0.999 and/or 40 episodes per update | M05 snap2 | **open** | — |
