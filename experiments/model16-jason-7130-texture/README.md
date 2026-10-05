# Model J16 (jason): the 7.130 model + textured floors

**Why:** Elyas's `cedc-m10v-c2-end` (ckpt 199) is our best portal model (**7.130 / 6.740**, #33), trained on plain floors only. On my side, J13 showed that plain-floor models leave the track 2–7× per lap on textured floors and that a few hours of carpet/wood training fixes it (27 → 4 off-tracks, concrete never trained on 12 → 4) without losing time. The physical race (Oct 8) runs on a real floor, so this adds that robustness to the fast model.

**Changes vs the 7.130 model:** training worlds include `reinvent_carpet` / `reinvent_wood` (re:Invent 2018 layout, 17.7 m: also short), paired with the short tracks Elyas found transfer best (reInvent2019_wide, reinvent_base) and rI2024 / Vegas; domain randomization on (as in J12a–J13). Reward and the 15 actions are Model 10's, unchanged (`model10-realcar`). `reinvent_concrete` stays held out.

Imported from Elyas's bundle `submissions/m10v-c2-end-ckpt199.tar.gz` with `tools/wsl/import_bundle.sh`.

## Run

Two simulators, lr 0.0001 (as the 7.130 run), 45-min legs (21:52 → ~02:40):

```
bash tools/track_rotation.sh model16-jason-7130-texture m16-jason cedc-m10v-c2-end best \
  reInvent2019_wide+reinvent_carpet:wk1:45:0.0001 \
  reinvent_base+2024_reinvent_champ_cw:br1:45:0.0001 \
  reInvent2019_wide+reinvent_wood:ww1:45:0.0001 \
  reinvent_carpet+2024_reinvent_champ_cw:kr1:45:0.0001 \
  reinvent_wood+reInvent2019_wide:ww2:45:0.0001 \
  reinvent_base+Vegas_track:bv1:45:0.0001
```

**Judge:** evaluate the 7.130 model itself and the J16 snapshots on the textured floors (incl. concrete) and the short + standard tracks (off-tracks first, then time); portal uploads to check the secret-track pace is kept.

## Results

(pending)
