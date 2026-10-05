# Model J21 (jason): the 7.130 model + Elyas's Model 13c plan (two simulators, DR + textured floors, screening)

Elyas's proposal for Jason's machine (`experiments/model13c-reliable/README.md`, strategies R1 + R4 + R3), accepted by Jason 2026-10-05:
- start: **the 7.130 model** (`cedc-m10v-c2-end`, ckpt 199; Jason 2026-10-05: "just use the one that reached 7.13" instead of waiting for Model 13 w4-end)
- reward + actions: the 7.130 model's own (Model 10) with **one change from Model 13c: speed-scaled off-track penalty (−2 × speed, was −5)**
- **two simulators**, **domain randomization on while training**, textured floors (reinvent_carpet / reinvent_wood) paired with the short tracks and rI2024; lr 0.0001
- **screening** (Elyas's `tools/screen_loop.sh`, now portable + two-track legs + DR on/off): hourly blocks of 2 × 30-min two-track legs, snapshots every 15 min, each screened on reInvent2019_wide with 5 trials **without DR**; clean ones packaged to `submissions/`

```
TRAIN_DR=True PAIRS_SPEC="reInvent2019_wide+reinvent_carpet:wk reinvent_base+reinvent_wood:bo;2024_reinvent_champ_cw+reInvent2019_wide:cw reinvent_base+reinvent_carpet:bk;reInvent2019_wide+reinvent_wood:wo reinvent_base+Bowtie_track:bt" \
  bash tools/screen_loop.sh model21-jason-m13c-robust m21-jason cedc-m10v-c2-end 8 0.0001
```

## Results

(pending)

Note: J18 (7.130 line + carpet/wood, no DR, flat penalty) did not learn the textured floors in 4 h; J21 adds DR (as in J13, which did) and the speed-scaled penalty.
