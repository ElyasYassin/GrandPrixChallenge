# Model J21 (jason): Elyas's Model 13c plan on two simulators, with DR + textured floors

Elyas's proposal for Jason's machine (`experiments/model13c-reliable/README.md`, strategies R1 + R4 + R3), accepted by Jason 2026-10-05:
- start: Elyas's Model 13 `w4-end` (ckpt 199, portal best lap **6.333**), imported with `tools/wsl/import_bundle.sh`
- reward + actions: Model 13c unchanged (speed-scaled off-track penalty −2 × speed)
- **two simulators**, **domain randomization on while training**, textured floors (reinvent_carpet / reinvent_wood) paired with the short tracks and rI2024; lr 0.0001
- **screening** (Elyas's `tools/screen_loop.sh`, now portable + two-track legs + DR on/off): hourly blocks of 2 × 30-min two-track legs, snapshots every 15 min, each screened on reInvent2019_wide with 5 trials **without DR**; clean ones packaged to `submissions/`

```
TRAIN_DR=True PAIRS_SPEC="reInvent2019_wide+reinvent_carpet:wk reinvent_base+reinvent_wood:bo;2024_reinvent_champ_cw+reInvent2019_wide:cw reinvent_base+reinvent_carpet:bk;reInvent2019_wide+reinvent_wood:wo reinvent_base+Bowtie_track:bt" \
  bash tools/screen_loop.sh model21-jason-m13c-robust m21-jason cedc-m13-w4-end 8 0.0001
```

## Results

(pending)
