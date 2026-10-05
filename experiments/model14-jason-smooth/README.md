# Model 14 (jason): smooth, fast, completion first

**Why (Jason, 2026-10-04):** the car weaves left/right on straights; also "max out the speed, use the racing line in the reward, completion is the priority, then speed/time".

Measured weaving (`tools/zigzag.py` on Model 12a csa3-end evals; straight = centre line turns < 15 deg within 1.5 m): 54-94 % of straight steps at >= 12 deg steering, ~3 left/right flips per second, mean |steering| 11-14 deg. Replaying those states through the reward's expert: it asks for 18-20 deg there itself (2-3 flips/s), i.e. the policy copies a twitchy expert.

**Changes vs Model 12a** (details at the top of `reward_function.py`):
1. Model 10's faster actions (same 15 actions/order, 2.0-4.0 m/s; 4.0 = physical car's top speed), expert floor 2.0 m/s.
2. Racing-line term: up to +1 for being within 0.10 m of the racing line (0 beyond 0.40 m).
3. Smoothness 0.5 -> 1.0, no smoothness credit for a left/right flip, straight bonus (up to +1 for steering < ~12 deg while the track ahead is straight and the car points along it).
4. Lap reward = fixed 400 for finishing + 200 x (avg speed / 2 m/s)^2 (was 300 x (...)^2 only): completion first, then time.
5. Multi-scale racing line (Jason: "on S / snake roads the best route is often straight through the middle"): the old single-scale line had a sawtooth on straights (the expert chased it) and followed S-bends closely. Coarse-to-fine curvature passes (neighbour distance 16 → 1) + 2 light smoothing passes: ideal-lap model (`tools/lap_time_sim.py`, 4 m/s, 7 m/s²) over Vegas, Summit, rI2024, reInvent2019, reinvent_base 34.02 → 33.49 s; line wobbles 18/48/18/62/46 → 15/33/17/13/17. A plain moving average was tried first: fewer wobbles but slower (35.80 s), dropped.

Tried and dropped: a 1.5x longer expert lookahead on straights; in `tools/test_reward.py` the expert then cut corners and left the track on 4 more test tracks.

Offline check (`tools/test_reward.py` with the measured car geometry, wheelbase 0.34 m; the tool's default 0.165 m turns twice too sharply): the expert completes all 10 test tracks like Model 10's, faster on Vegas (5.9 vs 6.2 s) and reInvent2019 (5.9 vs 6.3 s), within ±0.4 s elsewhere. Reward expert / random / mirrored ~4.6 / 2.4 / 2.9.

## Run

Starts after Model 13 (~11:50) from the better of Model 13's best snapshot and Model 12a csa3-end (evaluation decides), two workers; Vegas in 4 of 6 legs (Jason: "use the Vegas track next time"), textured floors and stand-ins mixed in:

```
bash tools/track_rotation.sh model14-jason-smooth m14-jason <start snapshot> best \
  Vegas_track+2024_reinvent_champ_cw:vc1:45:0.0003 \
  Vegas_track+reinvent_carpet:vk1:45:0.0003 \
  2024_reinvent_champ_cw+2022_summit_speedway:rs1:60:0.0003 \
  Vegas_track+reinvent_wood:vw1:45:0.0001 \
  Vegas_track+2022_summit_speedway:vs1:45:0.0001 \
  2024_reinvent_champ_cw+2022_summit_speedway:rs2:45:0.0001
```

**Success =** completion stays 100 % in evals (off-tracks not worse than the start), weaving down (`tools/zigzag.py`: >= 12 deg share and flips/s), then lap time.

## Results

**Stopped 13:44 after 75 min (legs vc1 + part of vk1), from `cedc-m13-jason-wooc1-end`.** Much faster laps (Vegas 7.1–9.2 s vs ~11 s for Model 13; rI2024 ~10 s vs 13–14 s; carpet layout ~7 s) but training progress stayed flat at 30–37 % (Model 13 ended at 60–90 %), about 1 finished lap per 15 episodes. Completion is the priority, so the same reward continues with the slower speeds as **Model 14b** (`experiments/model14b-jason-smooth-slow`). Snapshots kept for a possible fast probe: `cedc-m14-jason-vc1-1257`, `-vc1-end`, `-vk1-end`.
