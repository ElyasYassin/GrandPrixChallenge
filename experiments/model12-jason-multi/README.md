# Model 12 (jason): two tracks at once (multi-worker), from Model 11's best

**Why:** the rotation trains on one track at a time and drifts toward whichever track it is on (FINDINGS 2026-10-03: specialising hurt the secret-track score; mixed training gave our best uploads). With two simulators (DRfC multi-config, `DR_WORKERS=2`) every training batch mixes two tracks, and the run collects about twice the episodes per hour on the same machine.

**Changes vs Model 11:** two workers, each on its own track, pairs rotating (`tools/track_rotation.sh` world `A+B`). Reward, 15 actions, domain randomization and alternating direction unchanged. Starts from Model 11's best checkpoint (DRfC's "best" = highest progress in training evaluations).

## Run

**Phase A** (`model12a-jason-slowstart`): Model 11 stalled from scratch with Model 10's fast actions, so Model 12 first trains with Model 09's slower speeds (same 15 actions, same order; reward = Model 10 with `MIN_SPEED` 1.3) from `cedc-m11-jason-vegas1` best, then **phase B** below switches to Model 10's speeds from phase A's end. Both phases run from `logs/m12_chain.sh` (started 00:00, 2026-10-04):

```
bash tools/track_rotation.sh model12a-jason-slowstart m12a-jason cedc-m11-jason-vegas1 best \
  Vegas_track+2024_reinvent_champ_cw:va1:90:0.0003 2024_reinvent_champ_cw+2022_summit_speedway:csa1:60:0.0003
bash tools/track_rotation.sh model12-jason-multi m12-jason cedc-m12a-jason-csa1-end last \
  2024_reinvent_champ_cw+2022_summit_speedway:cs1:90:0.0003 Vegas_track+2022_summit_speedway:vs1:45:0.0003 \
  2024_reinvent_champ_cw+2022_summit_speedway:cs2:75:0.0003 2024_reinvent_champ_cw+2022_summit_speedway:cs3:60:0.0001
```

**Changes during the night (Claude):**
- 00:24 two simulators can't be restarted one at a time (a restarted worker never rejoins; both stop), so `tools/supervise.sh` now does a full resume from the last checkpoint at an iteration boundary for multi-worker runs. Run prefixes count up (`-2`, `-3`, …) at every memory restart (~every 5 min on Vegas pairs; rI2024+Summit barely leaks). Still ~1.5× the driving time per minute of one simulator (25 vs 16 s/min).
- 01:40 phase A learns (Vegas mean 19 → 28 %, first laps 10.8–12.5 s on Vegas, 12.8 s on Summit) but completes few laps, so phase B was replaced by more slow-speed legs (`logs/m12_chain2.sh`): Vegas+rI2024 45, rI2024+Summit 75, Vegas+Summit 45, rI2024+Summit 75, rI2024+Summit 60 @ lr 0.0001 (until ~07:25). Switching to Model 10's speeds is a morning decision after evaluation.

Originally planned (before the slow start was added):

```
bash tools/track_rotation.sh model12-jason-multi m12-jason <m11 prefix> best \
  Vegas_track+2024_reinvent_champ_cw:vc1:60:0.0003 \
  2024_reinvent_champ_cw+2022_summit_speedway:cs1:90:0.0003 \
  Vegas_track+2022_summit_speedway:vs1:45:0.0003 \
  2024_reinvent_champ_cw+2022_summit_speedway:cs2:90:0.0003 \
  2024_reinvent_champ_cw+2022_summit_speedway:cs3:60:0.0001 \
  Vegas_track+2024_reinvent_champ_cw:vc2:45:0.0001
```

Snapshots every 30 min (`cedc-m12-jason-<leg>-HHMM`). Memory: two simulators share WSL's 16 GB, so the supervisor restarts them above 4 GB at an iteration boundary, 6 GB at any time.

**Evaluation:** held-out tracks (reInvent2019_track, reinvent_base, 2022_reinvent_champ_ccw) + the stand-ins, practice-race rules; off-tracks first, then mean time.

## Results

Phase A (slow-start speeds) ran all night (00:00 → 07:33); the switch to Model 10 speeds was not made. Training at the end (csa4, lr 0.0001): Summit 89 % mean progress / 47 laps per 60 episodes, rI2024 CW 73 %.

Evaluation 2026-10-04 08:00 (DR off, practice-race rules: 3 trials, non-continuous, 1 s penalties), 6 tracks: Summit, rI2024 CW + CCW, reInvent2019, reinvent_base, Vegas (`evals/m12a-*`, `logs/m12a_eval.txt`):

| Snapshot | Completion | Off-tracks | Mean lap | Summit | rI2024 CW/CCW | reInvent2019 | reinvent_base | Vegas |
|---|---|---|---|---|---|---|---|---|
| csa4-0702 (ckpt 184) | 18/18 | **2** | 12.98 | 12.62 | 15.06 | 13.19 | 10.91 | 11.70 |
| **csa3-end** (ckpt 175) | 18/18 | 3 | **12.56** | 12.13 | 14.41 | 12.54 | 10.10 | 12.03 |
| vsa1-end (ckpt 153) | 18/18 | 3 | 12.86 | 12.32 | 15.19 | 12.96 | 10.45 | 11.40 |
| csa4-end (ckpt 191) | 18/18 | 5 | 12.85 | 11.83 | 14.14 | 12.74 | 11.57 | 11.81 |

(rI2024 column = mean of CW and CCW.) Reference: Model 08 Vegas eval 13.73 s mean. Packaged + validated: `submissions/cedc-m12a-jason-csa3-end.tar.gz`, `submissions/cedc-m12a-jason-csa4-0702.tar.gz` (not uploaded).

Textured floors (same layout as reinvent_base, csa3-end): carpet 2-3, wood 2-3, concrete 2-7 off-tracks per lap → Model 13.
