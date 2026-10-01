# Model 03: Speed

**Why:** Model 02 (our submission "Slowcedes") scored **100% completion** on the secret track, but a **34.7 s** lap vs 5.5 s for #1. Completion is secured, so speed is now the lever.
**Change vs Model 02:** the car and the expert are faster. Same imitation idea, same track, same hyperparameters.
**Starts from:** Model 02 checkpoint 11 (`cedc-m02-imitation-5`, best), so it keeps its driving skills and learns to go faster. This is stage 2 of our curriculum.

## Changes

| | Model 02 | Model 03 |
|---|---|---|
| Speed action range | 0.5–1.0 m/s | **1.0–2.5 m/s** |
| Expert speed | 1.0 on straights, 0.5 when ≥60° of turn within 1.5 m | **Speed profile:** each curve ahead allows √(4 m/s² × radius); the car must be able to brake (3 m/s²) in time. So 2.5 m/s on straights, braking late to about 1.1 m/s for corners |
| Grip limit | none needed at ≤1 m/s | Expert speed capped so lateral acc. = v²·tan(steer)/wheelbase ≤ 4 m/s² |
| Pure-pursuit look-ahead | 0.8 m | 0.45 + 0.15·speed (0.6–0.83 m). Longer look-ahead cut corners on narrow tracks at speed |
| Pace reward | 0.5 × min(pace, 1.5) | **1.0 × min(pace, 3.0)** |

Still track-agnostic: everything comes from the current track's `waypoints` and physics, with no hard-coded positions.

## Offline validation ([tools/test_reward.py](../../tools/test_reward.py), kinematic car model)

| Track | Model 02 expert | Model 03 expert |
|---|---|---|
| Vegas_track | 33.9 s | **9.6 s** |
| reinvent_base (0.76 m wide) | 24.6 s | 7.3 s |
| 2024_reinvent_champ_cw (0.76 m) | 32.9 s | 10.4 s |
| all 10 test tracks | laps | **laps on all 10**, max lateral acc. 4.0 m/s² |

Iterations that failed and were fixed during design:
1. A fixed "curve window" made the expert brake for corners 3 m early, so it drove 1.2 m/s everywhere. Replaced by the braking-distance speed profile.
2. Without a grip limit, the expert asked for up to 10.5 m/s² in corners. Capped at 4.
3. A 1.35 m look-ahead at 2.5 m/s went off 3 narrow tracks. Shortened to 0.83 m.

The kinematic model has no tyre slip: the real test is the DRfC evaluation.

## Run

| Setting | Value |
|---|---|
| Prefix | `cedc-m03-speed` (auto-resumes → `-2`, `-3`, ...) |
| Pretrained | `cedc-m02-imitation-5`, checkpoint `best` (= 11) |
| Workers | 1 |
| Start / planned stop | 2026-09-29 21:14 → 23:45 |

## Success criteria (before any submission)

1. Local evaluation on Vegas: **3/3 clean laps**, lap time well under 27 s (Model 02).
2. Unseen tracks: at least as good as Model 02 (Summit Speedway 3/3 clean).
3. Only then package and upload. A faster model with lower completion would rank *below* Slowcedes.

## Results

### Training (21:14–23:46; runs `cedc-m03-speed` → `-2` → `-3`)

Interrupted by the Windows memory freeze (21:47), WSL idle shutdown (21:54), and the simulator memory leak. From 22:45 on, the memory guard restarted the simulator 5× with no full restarts needed.

| | 21:36 | 22:50 | **23:46** |
|---|---|---|---|
| Episodes | 104 | 280 | 405 |
| Mean progress, last 20 episodes | 35% | 36% | **70%** |
| Laps, last 20 episodes | 1 | 1 | **9** |
| Total laps / best | 1 / 13.8 s | 13 / 13.7 s | **42 / 13.7 s** |

### Evaluation (practice-race rules, 3 trials)

| Track | Model 02 ckpt 11 | **Model 03 ckpt 31** | Model 03 ckpt 30 |
|---|---|---|---|
| Vegas | 3/3 clean, 27.0–27.5 s | **3/3 clean, 14.5–15.2 s** | 3/3 clean, 15.3–15.8 s |
| Summit Speedway (unseen) | **3/3 clean**, 28.3–29.2 s | ❌ 4–7 off/lap, 20.8–22.8 s | — |
| re:Invent 2018 (unseen) | 0/3 clean (4 off/lap) | 1/3 clean (0–2 off/lap), 12.9–15.0 s | — |
| re:Invent 2024 CW (unseen) | 0/3 clean (5 off/lap) | 0/3 clean (2–4 off/lap), 18.0–22.4 s | — |

On Summit Speedway, **10 of 16 off-tracks were in right-hand turns** (T6, T8, T9), at about 1.9 m/s. The right-turn weakness from Model 02 now costs laps at speed.

**Decision:** not uploaded. It could drop below 100% completion on the secret track and rank below Slowcedes. Packaged anyway (`submissions/cedc-m03-speed-ckpt31.tar.gz`, validated).
**Next:** Model 03b, same model trained in both directions.
