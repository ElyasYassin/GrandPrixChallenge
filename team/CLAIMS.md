# Experiment claims

Check here before starting a run. Add a row **before** you start; set Status to `done` (with a link to results) or `dropped` when finished.

| Date | Who / machine | Experiment | Starts from | Status | Results |
|---|---|---|---|---|---|
| 2026-10-01 | Elyas / 3090 | **Model 07 reliability**: stronger off-track penalty + edge-distance reward, speed 1.3–3.0, lr 0.0001 | M05 snap2 (`cedc-m05-snap2`) | planned | — |
| — | open | **Discrete action space** model (10–15 actions derived from the expert's choices), trained from scratch with the M05 reward | scratch | **open: good fit for the second machine** | — |
| — | open | **From-scratch control**: M05 reward, continuous actions, from scratch, to test whether the curriculum helps | scratch | **open** | — |
| — | open | **Hyperparameters**: discount 0.999 and/or 40 episodes per update | M05 snap2 | **open** | — |
