# Model J22 (jason): the 7.130 model, AWS re:Invent 2018 track only

**Why (Jason, 2026-10-05):** "use Elyas's best model and just train on the AWS re:Invent 2018 track, I believe that might be the hidden track". In DRfC that track is `reinvent_base` (17.7 m), in the 17–20 m range Elyas estimated for the secret track (`team/SECRET_TRACK.md`).

**Settings = the 7.130 run's (Elyas):** start `cedc-m10v-c2-end` (ckpt 199), Model 10 reward + actions unchanged, no domain randomization, lr 0.0001, alternating driving direction. **Both simulators on reinvent_base.** 6 × 40-min legs, snapshots every 30 min.

Risk noted: single-track specialisation hurt before (Model 10, 2.5 h Summit only: secret-track best lap 9.90 → 13.27). If the secret track *is* re:Invent 2018-like, this should show on the portal quickly; upload snapshots early.

```
bash tools/track_rotation.sh model22-jason-reinvent2018 m22-jason cedc-m10v-c2-end best \
  reinvent_base+reinvent_base:b1:40:0.0001 ... (6 legs)
```

## Results

(pending)
