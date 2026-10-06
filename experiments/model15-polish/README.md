# Model 15 (E1 "polish"): Model 14b with steadier training settings

Same reward, actions (4 m/s cap) and tracks (A to Z + re:Invent 2018, no DR) as Model 14b; starts from `m14b-w8-end` (portal **6.338** / 6.270, clean). Only the training hyperparameters change, to polish a near-final model instead of wandering around its peak (Model 14b's continuation at lr 0.0001 plateaued: A to Z 62–66%, re:Invent 2018 slipped to 26–30%):

| Setting | Model 14b | Model 15 |
|---|---|---|
| lr | 0.0001 | **0.00005** |
| beta_entropy | 0.01 | **0.002** (more decisive policy) |
| num_episodes_between_training | 20 | **40** (steadier updates) |
| batch_size | 64 | **128** |
| discount_factor | 0.99 | **0.995** (~2-lap horizon) |

Set with `tools/wsl/set_hparams.sh` (custom_files/hyperparameters.json is global: **reset these for other runs**), supervisor run with `EPISODES_PER_ITER=40` so simulator restarts stay on iteration boundaries.

Run: 2026-10-06 13:23 → ~17:30, 8 × 30-min phases alternating reInvent2019_wide / reinvent_base. Plan: upload its 2 best snapshots ~17:30, then E3 "free racing" from the best.

## Results

(pending)
