# Model 11 (jason): Model 10 from scratch with domain randomization

**Why:** the physical race (Oct 8) runs the same model on a real car, under real lighting and track colours. Our models have only ever seen the simulator's default look. Domain randomization (`DR_ENABLE_DOMAIN_RANDOMIZATION=True`) varies lighting and colours during training, so the policy has to rely on the track shape instead. This run also brings the second machine (Jason, RTX 3090) into the pipeline.

**Changes vs Model 10:** reward and 15-action space unchanged (`model10-realcar`). Two differences:
1. **Domain randomization on** (the idea under test).
2. **From scratch**, because Model 10's checkpoints live on the other machine. Same from-scratch rotation recipe as Model 08 (Vegas first, then the stand-ins), with shorter legs (FINDINGS 2026-10-03: no long single-track phases).

`DR_TRAIN_ALTERNATE_DRIVING_DIRECTION=True`, hyperparameters at DRfC defaults (lr as below, 20 episodes per update).

## Run

```
bash tools/track_rotation.sh model11-jason-dr m11-jason none best \
  Vegas_track:vegas1:90:0.0003 2024_reinvent_champ_cw:champ1:60:0.0003 2022_summit_speedway:summit1:60:0.0003 \
  Vegas_track:vegas2:45:0.0003 2024_reinvent_champ_cw:champ2:60:0.0003 2022_summit_speedway:summit2:60:0.0003 \
  2024_reinvent_champ_cw:champ3:45:0.0001 2022_summit_speedway:summit3:45:0.0001
```

Snapshots every 30 min (`cedc-m11-jason-<leg>-HHMM`) and at each leg's end.

**Compare with:** Model 08 (from scratch, same rotation idea, no DR: portal 10.824 after ~5 h). If Model 11 learns far slower, DR is costing too much from scratch; then fine-tune Model 10's best with DR instead (needs `cedc-m10-summit1-end` copied over from Elyas's machine).

**Evaluation:** practice-race rules (3 trials, non-continuous, 1 s penalties), off-tracks first, then mean time; also evaluate on a textured world (`reinvent_carpet` / `reinvent_wood`) as a sim-to-real check.

## Results

**Stopped early at 00:00 (2026-10-04), after only the first leg (vegas1, 85 min, ~1,040 episodes, ckpt 52).** Progress per iteration rose from ~6% to ~15% (11–21%) and then flattened; no real lap (one "3.2 s lap" is a progress glitch). From scratch, Model 10's fast actions (slowest 2.0 m/s) leave the track ~1.5 s into most episodes, so the car rarely reaches the big distance and lap rewards; domain randomization may slow it further. Not separable from this run alone.

Snapshots: `cedc-m11-jason-vegas1-2307` (ckpt 24), `-2337` (ckpt 42), `-end` (ckpt 52 = DRfC best). Continued as Model 12 (slow-start curriculum, two tracks at once).
