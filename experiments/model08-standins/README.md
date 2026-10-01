# Model 08: train on the secret track's stand-ins

**Idea:** our portal results suggest the secret track is ~25–29 m, flows faster than Vegas and has tight right turns ([`team/SECRET_TRACK.md`](../../team/SECRET_TRACK.md)). The closest public tracks are **2024_reinvent_champ** and **2022_summit_speedway** (both 25 m, ~47% straights vs 37% on Vegas). Training on them, in both directions, should teach the corner/straight mix the secret track has. Training on other public tracks is allowed (team confirmation, 2026-10-01).

**One change from Model 07:** the training tracks. Reward and action space are the same as Model 07 (off-track penalty −20, edge-safety factor, racing line, braking-aware speed, 1.3–4.0 m/s); the reward computes its line from the runtime waypoints, so it works unchanged on any track.

| | |
|---|---|
| Starts from | best Model 07 snapshot (fewest off-tracks, then mean time) |
| Legs | `2024_reinvent_champ_cw` 75 min → `2022_summit_speedway` 75 min → `Vegas_track` 30 min (so it doesn't forget Vegas), all with alternating direction |
| Hyperparameters | lr 0.0001, discount 0.99, 20 episodes per update (unchanged) |
| Snapshots | every 30 min: `cedc-m08-<leg>-HHMM`, and `cedc-m08-<leg>-end` |
| Run | `bash tools/track_rotation.sh model08-standins m08 <M07 snapshot> best 2024_reinvent_champ_cw:champ:75 2022_summit_speedway:summit:75 Vegas_track:vegas:30` |

**Evaluation:** the stand-ins are now training tracks, so they only show fit. Generalization is judged on **held-out** tracks: reInvent2019_track, reinvent_base, 2022_reinvent_champ_ccw (Vegas is trained on briefly, so it counts as seen). Choose by off-tracks first, then mean time; compare with M05 snap2 and the best M07 snapshot under the same 5-trial setup.

**Risk:** memorizing two layouts. The secret track is probably custom, so watch the held-out tracks: if they get worse while the stand-ins improve, it's memorizing.

## Results

(pending)
