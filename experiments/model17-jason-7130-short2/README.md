# Model J17 (jason): J16b ws1-end, same recipe, short tracks weighted more

Continues the best J16b snapshot (`ws1-end`: 10 off-tracks vs 24 for the 7.130 model, 10.01 vs 11.19 s) with Elyas's settings unchanged (M10 reward, no DR, plain floors, lr 0.0001), two simulators. Pairs lean on the short tracks that transfer to the secret track (reInvent2019_wide, reinvent_base) and keep rI2024 / Vegas in the mix.

```
bash tools/track_rotation.sh model17-jason-7130-short2 m17-jason cedc-m16b-jason-ws1-end best \
  reInvent2019_wide+reinvent_base:wb1:40:0.0001  reInvent2019_wide+2024_reinvent_champ_cw:wr1:40:0.0001 \
  reinvent_base+Vegas_track:bv1:40:0.0001  reInvent2019_wide+reinvent_base:wb2:40:0.0001 \
  reinvent_base+2024_reinvent_champ_cw:br1:40:0.0001  reInvent2019_wide+Vegas_track:wv1:40:0.0001
```

Judge against `ws1-end` and the 7.130 model with the J16b eval (4 tracks × 3 trials, DR off).

## Results

Trained 03:55 → 08:01. Training on reInvent2019_wide up to 76 % mean progress (31 laps / 60), reinvent_base 52–53 %.

Evaluation (same as J16b: 4 tracks × 3 trials, DR off, 1 s penalties; `logs/m17_eval.txt`):

| Model | all 4 tracks: off / mean | short tracks (wide + base): off / mean | wide | base | rI2024 CW | Vegas |
|---|---|---|---|---|---|---|
| 7.130 model | 24 / 11.19 s | 11 / 9.73 s | 8.39 / 3 | 11.07 / 8 | 13.58 / 7 | 11.73 / 6 |
| J16b ws1-end | **10** / **10.01 s** | 3 / 8.27 s | 7.65 / 0 | 8.89 / 3 | 13.02 / 5 | 10.46 / 2 |
| **wv1-end** (ckpt 438) | 16 / 10.38 s | **2 / 7.74 s** | **6.66 / 0** | 8.82 / 2 | 14.69 / 9 | 11.36 / 5 |
| **br1-end** (ckpt 429) | 15 / 10.12 s | 3 / 7.82 s | 7.21 / 0 | **8.43 / 3** | **11.77 / 3** | 13.07 / 9 |
| wb2-end | 14 / 10.55 s | 4 / 8.43 s | 6.93 / 0 | 9.93 / 4 | 13.20 / 5 | 12.12 / 5 |
| wb1-end | 18 / 11.50 s | 5 / 8.98 s | 8.34 / 2 | 9.63 / 3 | 18.12 / 12 | 9.91 / 1 |

J17 is the fastest and cleanest on the short tracks; ws1-end stays the most reliable over all four. Packaged: `submissions/cedc-m17-jason-wv1-end.tar.gz`, `…-br1-end.tar.gz`.
