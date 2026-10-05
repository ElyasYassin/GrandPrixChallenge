# Model J18 (jason): physical-race robustness for the 7.130 line (textured floors)

**Why:** the physical race (Oct 8) runs on a real floor. The 7.130 model leaves `reinvent_carpet` 4–5× per lap (`evals/e7130-c2-end-*`); my J13 showed carpet/wood training fixes this (off-tracks on three floors 27 → 4, held-out concrete 12 → 4) without losing time. The portal candidates (J16b ws1-end, J17 wv1-end / br1-end) stay as they are; this is a separate model for the race.

**Changes vs J16b ws1-end (Elyas's settings otherwise unchanged):** `reinvent_carpet` and `reinvent_wood` (re:Invent 2018 layout, 17.7 m) paired with the short tracks; no domain randomization (to change one thing); `reinvent_concrete` held out. Two simulators, lr 0.0001.

```
bash tools/track_rotation.sh model18-jason-texture-race m18-jason cedc-m16b-jason-ws1-end best \
  reinvent_carpet+reInvent2019_wide:kw1:40:0.0001  reinvent_wood+reinvent_base:ob1:40:0.0001 \
  reinvent_carpet+reinvent_base:kb1:40:0.0001  reinvent_wood+reInvent2019_wide:ow1:40:0.0001 \
  reinvent_carpet+reInvent2019_wide:kw2:40:0.0001  reinvent_wood+reinvent_base:ob2:40:0.0001
```

**Judge:** carpet / wood / concrete off-tracks (7.130: 4–5 per lap on carpet) while keeping wide / base pace (ws1-end: 7.65 s / 8.89 s).

## Results

**Dropped 12:37** (Jason: lap record first, not carpet/wood). Training on carpet/wood stayed flat at ~27-36 % mean progress for all 6 legs (4 h) while wide/base kept 55-70 %: the fast 7.130 line did not adapt to texture at lr 0.0001 without DR (J13 did, from a slower, DR-trained model). Not evaluated.
