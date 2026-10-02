# Findings (append-only)

Add new entries at the bottom, dated, with who wrote them and links to evidence. Don't edit old entries; add corrections as new entries.

---

**2026-09-29 · Elyas** · The organizers' starter reward (stay near centre) learned 0 laps in 225 episodes. Rewarding the car for imitating a track-agnostic expert (pure pursuit + slow before curves) gave reliable laps. → `experiments/model01-baseline`, `model02-imitation`

**2026-09-29 · Elyas** · Vegas counterclockwise is mostly left turns; models trained one way fail on unseen tracks in tight **right** turns. Training with `DR_TRAIN_ALTERNATE_DRIVING_DIRECTION=True` fixes it (11 vs 30 off-tracks) and shrinks the Vegas-vs-unseen generalization gap (18 → 10 points). → `model03b-bothdir`

**2026-09-30 · Elyas** · In DeepRacer, `params["is_reversed"]` means "driving the track clockwise", **not** "wrong way". Using it as a penalty gave every clockwise episode ~0 reward.

**2026-09-30 · Elyas** · The portal counts off-tracks as **time** (resets + penalty), not as failed completion: completion stays 100% even with off-tracks. Score (average of 3 trials) − best lap ≈ time lost to off-tracks.

**2026-09-30 · Elyas** · Measured from ~1,000 laps: the simulator holds ≥ 5–6 m/s² lateral; off-tracks happen at low lateral g (median 2 m/s²) → steering/line errors, not grip. Theoretical best Vegas lap ~8.65 s at 3 m/s / 4 m/s²; our models drive ~14.5 s. → `experiments/ANALYSIS_limits.md`, `tools/lap_time_sim.py`, `tools/grip_from_logs.py`

**2026-09-30 · Elyas** · Fine-tuning runs peak after ~1–1.5 h and then degrade (at lr 0.0003). **Always snapshot every 30–60 min and evaluate snapshots**; the last checkpoint is often not the best. lr 0.0001 extended the good window but didn't remove the decline.

**2026-09-30 · Elyas** · The racing line (K1999-style, computed from runtime waypoints) helped most on tight right-turn tracks (re:Invent 2024 CW −2 s). Portal: M05 snap2 17.877 vs M04 18.008. → `model05-racingline`

**2026-10-01 · Elyas** · **Speed vs reliability on the secret track:** Model 06 (top speed 3 → 4 m/s) improved the portal best lap (14.71 → 14.51) but the score got much worse (17.877 → 23.554; score − best lap 3.2 → 9.0 s). Our 4-track × 3-trial local eval ranked it *better* (16.12 vs 16.51), the wrong direction. → **Select candidates by off-track count first, then mean time; use more trials / more unseen tracks.** Local eval predicts direction poorly when off-track risk differs. → `model06-faster`

**2026-10-01 · Elyas** · Infra gotchas on Windows/WSL2 (all handled by `tools/supervise.sh`; details in `docs/DRFC_SETUP.md`): MinIO image gone from Docker Hub (use Chainguard); GPU rendering needs `GALLIUM_DRIVER=d3d12`; use compose not swarm; the simulator leaks ~1 GB/min with GPU rendering, so restart **only the simulator and only at iteration boundaries** (mid-iteration restarts freeze the trainer); WSL shuts down when no Windows process is attached (keep-alive); `dr-increment-training` misnames prefixes without a trailing number.

**2026-10-01 · Elyas** · **Secret-track inference** from our 5 portal results (each model as a probe): the track is likely **~25–29 m** (Vegas 22.6) with **fast sections** (fast models average ~2 m/s there vs ~1.45 on Vegas) and **tight right turns** (one-direction M03 lost 6.8 s to penalties vs 3.3 s after both-direction training). No simulator track fits all probes well (best: re:Invent 2024 Champ, Summit Speedway ≈ 8% error), so it may be custom. Weight those two tracks more in evaluation. Uploads are free (leaderboard keeps the best), so use deliberate probe models to learn more. → `experiments/ANALYSIS_secret_track.md`, `tools/secret_track_inference.py`

**2026-10-01 · Elyas** · **Bug:** our `tools/wsl/evalrun.sh` stopped every evaluation after **3** finished trials (hard-coded), whatever `DR_EVAL_NUMBER_OF_TRIALS` said. So all local evals before 14:10 today were 3 trials per track, including the ones we called "5-trial". Fixed: it now reads the trial count from `run.env`. If you copied our scripts, pull again.

**2026-10-01 · Elyas** · Training on other public simulator tracks is **allowed** (team confirmation). Model 08 trains on the secret track's closest stand-ins (2024_reinvent_champ, 2022_summit_speedway). → `team/SECRET_TRACK.md`, `experiments/model08-standins`

**2026-10-01 · Elyas** · **Why our continuous models zig-zag and crawl:** on Vegas evals, M04–M07 spend ~50% of steps at full steering lock and ~55% at the 1.3 m/s minimum (M06 averages 1.7 m/s on straights with a 4.0 cap). Replaying their logged states through our expert shows the expert asks for the same: imprecise imitation (~12–15° steering error) pulls the car off the line → sharp corrections → the steering-based grip cap lowers the speed. A closed-loop test (`tools/expert_closed_loop.py`) gives 9.4 s on Vegas for a perfect follower, 14.3 s at 15° error. Removing the cap / longer lookahead made it worse; a parameter sweep (`tools/expert_sweep.py`) found our expert settings near-optimal. → **The lever is policy precision**: Model 08 uses a **discrete action space** (15 actions from the expert's command bands; the restricted expert loses ≤ 4%). → `experiments/model08-discrete`

**2026-10-01 · Elyas** · Model 07 (off-track penalty + edge safety) did not clearly beat M05 snap2 in a 5-trial × 6-track eval (best snapshot: same off-tracks, 0.5 s faster on average). Snapshots of one run differ a lot by track: 13:32 was best on Vegas (0 off-tracks) and worst on the stand-ins (54). Never select on Vegas alone.

**2026-10-01 · Elyas** · **Don't run an evaluation while training on the same machine** (DRfC, one host): the two Gazebo simulators cross-talk. The eval car never spawned ("model [racecar] does not exist") and the *training* episodes got garbage (elapsed times ±630 s, negative progress) for ~2 iterations, so the trainer learned from bad data. We rolled back to a snapshot taken just before. `tools/wsl/evalrun.sh` now refuses to run while a training simulator is up; status/restart/log helpers only touch the training containers.

**2026-10-01 · Elyas** · **Discrete actions + training on the stand-in tracks = big jump on the secret track.** Model 08 (15 discrete actions, from scratch): after Vegas only (<2 h) → portal 16.693 (best 13.928); after Vegas → 2024_reinvent_champ_cw → 2022_summit_speedway → Vegas (~5 h total) → **10.824** (best 10.225, only 0.6 s lost to off-tracks). The stand-in tracks matter more than anything we changed in the reward. Also: at lr 0.0003 each phase peaks after ~1 h and then slips; upload snapshots from the peak, not the end of a phase. → `experiments/model08-discrete`, `team/SECRET_TRACK.md`

**2026-10-02 · Elyas** · Two infra lessons from tonight. (1) **Keep ≥ 10–20 GB free on the Windows drive that holds WSL's virtual disk**: when C: hit 0 GB, Linux got I/O errors and WSL crashed (twice); `tools/supervise.sh` now stops training cleanly below 2 GB free. (2) **Per-step rewards bias toward slow driving**: if every step on track pays about the same, a slow lap earns more in total. Model 08 got ~1 s/lap slower overnight; Model 09 pays per distance covered instead.

**2026-10-02 · Elyas** · **WSL shuts down between runs if nothing keeps it attached**, and that wipes /tmp. Our overnight track rotation lost its helper scripts at every phase switch, so it never changed track: all of Model 09 trained on 2024_reinvent_champ_cw (snapshots named `summit…` are re:Invent-trained). `tools/track_rotation.sh` now holds its own keep-alive and reinstalls helpers before each phase. Model 09's speed reward stopped Model 08's slow drift and raised completion to ~70% on rI2024, but lap times stayed ~15.5–15.9 s.

**2026-10-02 · Elyas** · **Grip test: the simulated car is not the car our expert assumed.** Driving fixed (steering, speed) circles: turn radius ≈ 0.34 m / tan(steer) (we assumed the 0.165 m wheelbase: 2× too tight), and ≥ 8.4 m/s² sideways without sliding (we assumed 5). Our expert therefore capped full-lock corners at ~1.2 m/s where the car holds 2.0–2.4, and the policies rarely chose fast straight actions. A closed-loop check with the measured car puts a corrected expert ~25–30% faster. Also: the secret track must be shorter than our 25 m stand-ins (a 5.5 s lap is impossible on 25 m even at 6 m/s); likely ~17–20 m. → `experiments/model10-realcar`
