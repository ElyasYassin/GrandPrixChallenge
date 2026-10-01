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
