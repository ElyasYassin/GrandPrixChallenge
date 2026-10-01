# Model 08: discrete actions, from scratch, on Vegas + the secret track's stand-ins

## Why

Models 04–07 zig-zag and crawl: on Vegas evaluations ~50% of steps are at full steering lock (±30°) and ~55% at the minimum speed (1.3 m/s); M06 averages 1.7 m/s on straights although it may drive 4.0. Replaying their logged states through the reward's expert shows the **expert asks for the same thing**: a car that is off the racing line gets a sharp correction, and the expert's grip limit (speed from the steering angle) then caps the speed. The cause is **imprecise imitation**, not a bad expert ([`tools/expert_closed_loop.py`](../../tools/expert_closed_loop.py): kinematic car following the expert with a 1-step delay + steering noise):

| Steering error vs expert | Vegas lap | Full lock | Off-tracks |
|---|---|---|---|
| 0° | 9.4 s | 4% | 0 |
| 5° | 10.1 s | 13% | 0 |
| 10° | 11.7 s | 26% | 0.3 |
| 15° | 14.3 s | 37% | 1.7 |

Our continuous policies are at ~12–15° error (their entropy implies ~±9° of sampling noise alone) → ~14.5 s laps, matching the portal. Removing the steering-based speed cap or lengthening the lookahead made it worse in the same test; a sweep of grip / braking / lookahead ([`tools/expert_sweep.py`](../../tools/expert_sweep.py), `logs/expert_sweep.txt`) found the current settings within ~2% of the best. So the lever is **policy precision**.

## The change: discrete action space (15 actions)

A categorical policy picks "straight, 4 m/s" exactly instead of sampling around it; no clipping at ±30°; much less to explore. Actions are the bands the expert actually commands (closed-loop, 6 tracks, mirrored), speed falling with steering angle as the grip limit requires:

| Steering | Speeds (m/s) |
|---|---|
| 0° | 4.0, 3.2, 2.5 |
| ±6° | 3.0, 2.4 |
| ±12° | 2.1, 1.7 |
| ±20° | 1.5 |
| ±30° | 1.3 |

The expert restricted to these 15 actions loses ≤ 4% (Vegas 9.7 vs 9.3 s; Summit 10.6 vs 10.6 s; 0 off-tracks).

Reward: unchanged from Model 07 (expert imitation on the racing line, braking-aware speed profile, off-track −20, edge safety, pace + lap bonus). A new action space changes the network's output layer, so this trains **from scratch** (lr 0.0003, then 0.0001).

Also new: training on the public tracks closest to the secret track (allowed; `team/SECRET_TRACK.md`): **2024_reinvent_champ_cw** and **2022_summit_speedway**, alternating direction, rotating with Vegas.

## Run

```
bash tools/track_rotation.sh model08-discrete m08 none best \
  Vegas_track:vegas1:120:0.0003 2024_reinvent_champ_cw:champ1:90:0.0003 2022_summit_speedway:summit1:90:0.0003 \
  Vegas_track:vegas2:90:0.0003 2024_reinvent_champ_cw:champ2:90:0.0001 2022_summit_speedway:summit2:90:0.0001 \
  Vegas_track:vegas3:90:0.0001 2024_reinvent_champ_cw:champ3:90:0.0001 2022_summit_speedway:summit3:90:0.0001
```

Snapshots every 30 min (`cedc-m08-<leg>-HHMM`) and at each leg's end.

**Evaluation:** held-out tracks (reInvent2019_track, reinvent_base, 2022_reinvent_champ_ccw) judge generalization; the stand-ins and Vegas now only show fit. Rank by off-tracks, then mean time; compare with M05 snap2 / M07 under the same 5-trial setup. Also check the zig-zag numbers (full-lock share, speed on straights).

## Results

(pending)
