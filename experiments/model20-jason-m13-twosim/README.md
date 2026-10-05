# Model J20 (jason): Elyas's Model 13 recipe on two simulators

**Why (2026-10-05):** the 7.130 line plateaued at ~6.7-6.8 s per lap on the portal (J17 wv1-end 7.389 / 6.800 despite fewer local off-tracks). Elyas's Model 13 (from scratch: grip 9 / top 5 m/s, pure-pursuit expert, straight-line braking, straight bonus + flip penalty; `experiments/model13-scratch`) reached the fastest secret-track lap so far (**6.333 s**) after 6.5 h, but not the reliability (19.206 score). Jason: "stick with what he had". Two simulators give ~2× the episodes per hour, which is what Model 13 lacked.

**Settings = Elyas's Model 13, unchanged:** reward + 15 actions copied from `experiments/model13-scratch` (0° at 2.5 / 3.6 / 5.0; ±6° 3.8 / 4.3; ±12° 3.1 / 3.7; ±20° 2.9; ±30° 2.5), from scratch, no domain randomization, short tracks + rI2024 + Bowtie, lr 0.0003 then 0.0001. Only difference: two tracks per batch.

```
bash tools/track_rotation.sh model20-jason-m13-twosim m20-jason none best \
  reInvent2019_wide+reinvent_base:wb1:60:0.0003  2024_reinvent_champ_cw+reInvent2019_wide:rw1:40:0.0003 \
  reinvent_base+Bowtie_track:bbo1:40:0.0003  reInvent2019_wide+2024_reinvent_champ_cw:wr1:40:0.0003 \
  reinvent_base+reInvent2019_wide:bw1:40:0.0003  Bowtie_track+2024_reinvent_champ_cw:bor1:40:0.0003 \
  reInvent2019_wide+reinvent_base:wb2:40:0.0001  2024_reinvent_champ_cw+reinvent_base:rb1:40:0.0001 \
  reInvent2019_wide+Bowtie_track:wbo1:40:0.0001
```

12:43 → ~19:20. If Elyas shares `cedc-m13-w4-end`, a fine-tune from it is the faster path to reliability.

**Judge:** 5-trial evals on wide / base (off-tracks first, then time) vs J17 wv1-end and the 7.130 model; portal uploads.

## Results

**Stopped 13:48 after ~65 min** (Jason: run Elyas's 13c plan from the 7.130 model instead of waiting for Model 13 w4-end → J21). From scratch it reached 24–28 % mean progress and its first laps (5.68 s on wide, 6.17 s on base). Snapshot `cedc-m20-jason-stop` (ckpt 74).
