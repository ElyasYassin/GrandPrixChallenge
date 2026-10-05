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

(pending)
