# Model J16b (jason): the 7.130 model, Elyas's settings, two tracks at once

**Why (Jason, 2026-10-04):** "use his settings, he got the high score on the hidden track". Portal focus: continue Elyas's recipe that broke the 10 s wall (Model 10 variety, `cedc-m10v-c2-end`, **7.130 / 6.740**), with the one machine-level difference that my DRfC runs **two simulators** (two tracks per batch, ~1.5-2× the episodes per hour).

**Settings = Elyas's Model 10 variety run:** Model 10 reward and actions unchanged, plain floors, no domain randomization, lr 0.0001, ~40-min phases on short tracks (reInvent2019_wide 16.6 m, reinvent_base 17.7 m) plus rI2024 / Vegas / Bowtie / Summit. Start: `cedc-m10v-c2-end` (ckpt 199) from Elyas's bundle, imported with `tools/wsl/import_bundle.sh`.

Direct check of the imported model (DR off, 3 trials, 1 s penalties): reInvent2019_wide 3/3, 9.2-10.1 s, 2/2/1 off-tracks; reinvent_carpet 3/3, 13.0-13.4 s, 5/4/4 off-tracks (`evals/e7130-c2-end-*`).

## Run (22:30 → ~03:20)

```
bash tools/track_rotation.sh model16b-jason-7130-short m16b-jason cedc-m10v-c2-end best \
  reInvent2019_wide+reinvent_base:wb1:40:0.0001  2024_reinvent_champ_cw+reInvent2019_wide:rw1:40:0.0001 \
  Vegas_track+reinvent_base:vb1:40:0.0001  reInvent2019_wide+Bowtie_track:wbo1:40:0.0001 \
  reinvent_base+2024_reinvent_champ_cw:br1:40:0.0001  reInvent2019_wide+2022_summit_speedway:ws1:40:0.0001 \
  reinvent_base+reInvent2019_wide:bw2:40:0.0001
```

**Judge:** off-tracks then lap time on the short tracks vs the 7.130 model itself (same eval settings); best snapshots → portal probes (Jason uploads).

## Results

Trained 22:30 → 03:17 (7 legs × 40 min). Training on reInvent2019_wide rose 39 → 74 % mean progress (3 → 25 laps / 60 episodes, ~6.4-7.0 s laps); rI2024 / Vegas / Bowtie stayed hard (20-30 %), as in Elyas's runs.

Evaluation (DR off, 3 trials, non-continuous, 1 s penalties, same settings for all; `logs/m16b_eval.txt`, `evals/m16b-*`):

| Model | Laps | Off-tracks | Mean | reInvent2019_wide | reinvent_base | rI2024 CW | Vegas |
|---|---|---|---|---|---|---|---|
| 7.130 model (`cedc-m10v-c2-end`) | 12/12 | 24 | 11.19 s | 8.39 s / 3 off | 11.07 / 8 | 13.58 / 7 | 11.73 / 6 |
| **ws1-end** (ckpt 332) | 12/12 | **10** | **10.01 s** | 7.65 / **0** | **8.89** / 3 | 13.02 / 5 | 10.46 / 2 |
| wbo1-end (ckpt 287) | 12/12 | 16 | 10.68 s | **6.80** / **0** | 9.55 / 5 | 12.73 / 4 | 13.64 / 7 |
| bw2-end (final) | 12/12 | 16 | 10.75 s | 9.12 / 3 | 9.79 / 6 | 13.59 / 6 | 10.51 / 1 |
| ws1-0225 | 12/12 | 18 | 11.06 s | 7.92 / 2 | 10.24 / 4 | 14.54 / 9 | 11.52 / 3 |

`ws1-end`: less than half the off-tracks and ~1.2 s faster per lap than the 7.130 model. Packaged + validated: `submissions/cedc-m16b-jason-ws1-end.tar.gz`, `submissions/cedc-m16b-jason-wbo1-end.tar.gz` (portal upload: Jason's decision). Ghost race on reinvent_base: `videos/base_7130_vs_j16b.mp4`.
