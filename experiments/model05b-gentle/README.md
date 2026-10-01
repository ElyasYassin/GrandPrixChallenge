# Model 05b: Gentler racing line

**Why:** Model 05's full racing line + smoothness bonus made the car *less* reliable in training (laps per 60 episodes fell from 33 to ~20 while M04 climbed to ~38), without faster laps.
**Starts from:** Model 05 snap2 (ckpt 125), our best model (eval mean 16.51 s), so 05b keeps its racing-line skill while the gentler reward targets the reliability drift seen after it. (Planned: M04 final; changed after snap2 won the evaluation.) Same action space (1.3–3.0 m/s), both directions, Vegas only.

## Change vs Model 05 (one idea: "less aggressive")

| | Model 05 | **Model 05b** |
|---|---|---|
| Expert path | full racing line (≤0.30 m from the edges) | **racing line blended 50% toward the centre** (`LINE_BLEND = 0.5`) |
| Smoothness bonus | up to +0.5 per step | **up to +0.25** |

Everything else is identical (grip 4 m/s², braking 3 m/s², speed-scaled lap bonus).

## Offline validation (kinematic car)

All 10 tracks lapped. Vegas 8.6 s (centre line 9.1, full racing line 8.2), Summit 9.1 s (9.7 / 8.7). Peak lateral acc 4.0–5.9 m/s².

Also raised `term_cond_max_episodes` 1000 → 100000 (stop condition only), so long runs can't silently stop learning.

## Results

_To fill in._
