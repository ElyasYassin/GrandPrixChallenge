# Model 13 (jason): textured floors (sim-to-real), from Model 12a csa3-end

**Why:** Model 12a `csa3-end` completes every lap on 6 tracks (18/18, 3 off-tracks, mean 12.56 s), 0 off-tracks on reinvent_base, but on the **same layout with textured floors** it leaves the track 2-7 times per lap (`evals/m12a-tex-csa3-end-*`):

| World (re:Invent 2018 layout) | Lap times | Off-tracks per lap |
|---|---|---|
| reinvent_base (plain) | 9.8-10.3 s | 0, 0, 0 |
| reinvent_carpet | 12.6-13.3 s | 3, 3, 2 |
| reinvent_wood | 12.3-13.3 s | 2, 2, 3 |
| reinvent_concrete | 12.1-19.3 s | 7, 3, 2 |

Domain randomization (lighting/colours) did not cover floor texture. A real track looks more like these worlds, so this is the physical-race risk.

**Change vs Model 12a:** training worlds now pair a textured floor with a stand-in track (two workers). `reinvent_concrete` stays held out to measure generalization to an unseen texture. Reward, actions (slow-start speeds), DR and alternating direction unchanged.

## Run

```
bash tools/track_rotation.sh model13-jason-texture m13-jason cedc-m12a-jason-csa3-end best \
  reinvent_carpet+2024_reinvent_champ_cw:carc1:50:0.0001 \
  reinvent_wood+2022_summit_speedway:woos1:50:0.0001 \
  reinvent_carpet+2022_summit_speedway:cars1:50:0.0001 \
  reinvent_wood+2024_reinvent_champ_cw:wooc1:50:0.0001
```

lr 0.0001 (fine-tuning a model that already drives; FINDINGS: runs at 0.0003 peak after ~1 h and slip).

## Results

Trained 08:27 → 11:53 (4 legs × 50 min, lr 0.0001, 2 workers, DR on). Training progress on carpet rose 38 → 67 %; Summit reached 91 % (47 laps / 60 episodes); the last leg (wood + rI2024, both 0.76 m wide) dipped mid-way and recovered to ~63 %.

Evaluation (DR off, 3 trials, non-continuous, 1 s penalties; `logs/m13_eval.txt`, `evals/m13-*`):

| Snapshot | Textured (carpet, wood, concrete*) | 6 standard tracks |
|---|---|---|
| Model 12a csa3-end (start) | 9/9, **27 off**, mean 13.61 s (concrete 12 off) | 18/18, 3 off, 12.56 s |
| cars1-end (ckpt 226) | 9/9, 6 off, 11.41 s | 18/18, 3 off, 13.07 s |
| **wooc1-end** (ckpt 246) | 9/9, **4 off**, 11.16 s (concrete 4 off) | 18/18, **0 off**, 12.53 s |

\* concrete never trained on. `wooc1-end`: first candidate with 0 off-tracks on all 6 standard tracks; per track Summit 12.67, rI2024 CW 13.38 / CCW 14.44, reInvent2019 12.65, reinvent_base 10.86, Vegas 11.16 s. Packaged + validated: `submissions/cedc-m13-jason-wooc1-end.tar.gz` (not uploaded). Model 14 starts from it.
