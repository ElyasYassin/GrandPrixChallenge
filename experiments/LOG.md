# Experiment Log

One row per trained model. Change **one idea** per model.

| # | Model name | Change vs. previous | Train time | Train progress % | Eval laps | Best lap (s) | Portal score | Notes |
|---|---|---|---|---|---|---|---|---|
| 01 | cedc-m01-baseline-gpu(-2) | — (starter reward, defaults), local DRfC | ~48 min effective (crash at 15:24, resumed) | 26% mean / 65% max | not run | — | — | 0 laps in 225 episodes; crashes mostly in the S-section (wp 35–55) and T9/T10 |
| 02 | cedc-m02-imitation(-2..-5), ckpt 11 | reward: imitate a pure-pursuit expert + slow before curves | ~2 h (crashes, auto-resumed) | 47% mean, 13 laps | Vegas 3/3 clean; unseen: Summit 3/3 clean, re:Invent2018 0/3 clean (4 off/lap), 2024 champ CW 0/3 clean (5 off/lap) | 26.98 (Vegas) | 34.716 (uploaded, #10) | all unseen-track off-tracks are in tight RIGHT turns → Model 03: both directions |
| — | **Portal submission** | Model 02 ckpt 11 = team "Slowcedes" | — | — | secret track: **100% completion** | 34.713 | 34.716 (#2 of 2 on 2026-09-29) | #1 Shallow Learner: 100%, 5.615 |
| 03 | cedc-m03-speed(-2,-3), ckpt 31 | speed 1.0–2.5 m/s; expert with speed profile (grip 4 m/s², braking 3 m/s²) + grip limit; from M02 ckpt 11 | ~2.5 h (crashes, then memory-leak guard) | 70% mean, 9/20 laps at end, 42 laps | Vegas 3/3 clean **14.5–15.2 s**; Summit 4–7 off/lap (regressed); re:Invent2018 1/3 clean; 2024 CW 0/3 | 14.52 (Vegas) | **22.508** (uploaded) | off-tracks at speed in RIGHT turns → Model 03b: both directions |
| — | **Portal submission** | Model 03 ckpt 31 (`cedc-m03-speed-ckpt31.tar.gz`) | — | — | secret track: **100% completion** | **15.706** | **22.508** (was 34.716) | best lap about 2.2× faster. Score ≫ best lap → some trials much slower (likely off-track resets + penalties), but completion stayed 100% |
| 03b | cedc-m03b-bothdir (snapshots 04:00 ckpt 56, 05:00 ckpt 63, final ckpt 69) | alternate driving direction each episode; from M03 ckpt 31 | 00:05–06:31 (0 crashes) | 81–87% mean, ~15/20 laps; clockwise 26% → 77% | all 12 trials complete; mean over 4 tracks: 04:00 20.1 s, final 20.3 s, 05:00 20.8 s (M03: 17.7 s). Final has fewest off-tracks (11 vs 30) | 16.96 (Vegas, 04:00) | not uploaded | right turns fixed, but the car got slower (1.46 → 1.28 m/s). Keep final as physical-race candidate; next: push speed explicitly |
| 04 | cedc-m04-fast(-2,-3), final ckpt 108 | speed 1.3–3.0 m/s + lap bonus scaled by lap speed; both directions; from 03b final | 11:30–17:00 | ~87% mean, ~15/20 laps | all complete; **mean 17.04 s** (Vegas 15.8, Summit 19.0, re:Invent2018 13.0, 2024 CW 20.3); 15 off-tracks; unseen efficiency 55%, gap +10 | 15.64 (Vegas) | **18.008** (uploaded #14, best lap 14.710) | best model so far: faster than M03 on all unseen tracks, half the off-tracks |
| 05 | cedc-m05-racingline, **snap2 = ckpt 125** | racing line (K1999-style, 0.30 m margin) + smooth-steering bonus; from M04 final | 17:50–21:00 (stopped early) | strong start (33/60 laps), then fell to ~20/60 after ckpt 125 | snap2: all complete; **mean 16.51 s** (Vegas 15.6, Summit 18.2, re:Invent2018 13.9, 2024 CW 18.4); 14 off-tracks; unseen efficiency **57%**, gap **+9** | 14.78 (Vegas) | packaged (`cedc-m05-snap2-ckpt125.tar.gz`), recommended upload | new best: the racing line helps on unseen right-turn tracks; training degraded after this snapshot, so snapshots matter |


## Portal history

| # | Uploaded | Model | Completion | Score | Best lap |
|---|---|---|---|---|---|
| 10 | 2026-09-29 18:36 | Model 02 ckpt 11 | 100% | 34.716 | 34.713 |
| 13 | 2026-09-30 00:57 | Model 03 ckpt 31 | 100% | 22.508 | 15.706 |
| 14 | 2026-09-30 17:46 | **Model 04 final ckpt 108** | 100% | **18.008** | **14.710** |

Leader (2026-09-30): Shallow Learner, 100%, 5.615 / 5.542.
