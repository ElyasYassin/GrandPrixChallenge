# Overnight log: 2026-09-30

**Goal:** a model by morning that is faster than Slowcedes (34.7 s on the secret track, 100% completion) **without** losing completion, i.e. clean on Vegas **and** on the unseen tracks, especially right-turn-heavy ones.

## Plan

| Time | Step |
|---|---|
| 00:05 → 06:30 | Train **Model 03b** (Model 03 checkpoint 31 + alternating driving direction on Vegas). The supervisor restarts the simulator when its memory leak passes 9 GB and recovers from crashes |
| every hour | Check-in: overall + **clockwise vs counterclockwise** progress, health. Results appended below |
| ~03:00 | **Decision point:** if clockwise progress is still < 35% and not rising, start **Model 03c** from the latest 03b checkpoint with gentler cornering (expert grip limit 4 → 3 m/s², brake 3 → 2.5 m/s²) |
| 06:30 → 07:30 | Stop training; evaluate the 2 most promising checkpoints on Vegas, Summit Speedway, re:Invent 2018, re:Invent 2024 CW (3 trials each, practice-race rules); package the best |
| morning | **You decide** whether to upload. Rule: clean 3/3 on Vegas **and** Summit Speedway, and faster than Model 02 |

Nothing is uploaded to the portal overnight.

## Update ~01:00: Model 03 uploaded by the team

Portal: **Slowcedes 100.00%, score 22.508, best lap 15.706** (before: 34.716 / 34.713).

What it tells us:
- **Off-tracks don't cost completion on the secret track, they cost time.** Model 03 goes off track on right-handers in our local tests, yet completion stayed 100%: the evaluator evidently resets the car (like the practice race), and the time lost shows in the **score (22.5, the average) vs best lap (15.7)**. One or two of the trials were about 25 s or more.
- So the lever is now **fewer off-tracks** (average → best lap) and then **more top speed**.

**Revised upload rule for the morning:** a new model is worth uploading if its **average local evaluation time across Vegas + the 3 unseen tracks (including off-track penalties)** beats Model 03 ckpt 31's, with every trial completed. Reference, Model 03 ckpt 31: Vegas 14.7 s, Summit 21.6 s, re:Invent 2018 14.0 s, 2024 CW 20.5 s → **mean 17.7 s**.

## Check-ins

**00:58.** 03b, 162 episodes. Counterclockwise: 75% mean progress, 14 laps in the last 30 (15.5 s). **Clockwise: 26%, 0 laps** (up from 21% at 00:57). Simulator restarts: 4, crashes: 0.

**02:00.** 328 episodes (~16 iterations). **Clockwise jumped: 26% → 63% mean progress, 7 laps in the last 30 (15.3 s).** Counterclockwise: 80%, 19 laps (16.0 s). Overall last 20: 73%, 12/20 laps; 107 laps in total, best 14.0 s. Steering change 17.5°/step (lowest yet). Health: 6 routine simulator restarts since 01:00 (memory guard), 0 crashes, Windows 6.1 GB available. → Right-turn training is working, so the 03:00 fallback (Model 03c) looks unnecessary.

**03:01. Decision point: continue 03b, no 03c.** 480 episodes (~24 iterations). **Clockwise now matches counterclockwise: 75% vs 76% mean progress, 15 vs 17 laps in the last 30** (clockwise laps 15.0 s, counterclockwise 16.4 s). Overall last 20: 77%, 10/20 laps; 182 laps total, best 14.0 s. Steering change 16.1°/step (still falling). Health: 12 routine simulator restarts, 0 crashes; Windows 4.1 GB available (WSL 10.8 GB, capped at 16).

**04:02. Plateau; snapshot taken.** 617 episodes (~30 iterations). Last 20: 74%, 11/20 laps; 265 laps total, best 14.0 s, mean 15.8 s. Counterclockwise 83% / 19 laps, clockwise 62% / 11 laps (last 30 each; noisy). Progress has been flat at 73–77% for about 2 h, and mean speed is drifting down (1.42 → 1.39 m/s) as the model trades speed for safety. → Saved **checkpoint 56 as `cedc-m03b-snap0400`**, so the morning evaluation can compare it against the final checkpoint. Memory was tightening (Windows 3.5 GB available, 91% commit, WSL 11.6 GB), so I lowered the simulator restart threshold from 9 GB to **7 GB**.

**05:03. More reliable, slower.** 768 episodes (~38 iterations). **Last 20: 87% mean progress, 16/20 laps** (best so far); 358 laps total. But mean speed dropped to **1.31 m/s** and lap times rose (counterclockwise 17.5 s, clockwise 16.2 s; best still 14.0 s). Both directions balanced (77% / 72%). → Saved this checkpoint as `cedc-m03b-snap0500` too. The morning evaluation decides between 04:00, 05:00 and final using time including off-track penalties. Health: 8 simulator restarts since 04:05, 0 crashes, Windows 4.9 GB available.

**06:31.** Training stopped as planned: 990 episodes, 516 laps, 19 routine simulator restarts, **0 crashes, 0 full resumes all night**. Final checkpoint 69 saved as `cedc-m03b-final`.

## Morning result (07:13): no better model, keep the uploaded one

Evaluation, practice-race rules, 3 trials per track, all trials completed. Time includes off-track penalties/resets.

| Model | Vegas | Summit Speedway | re:Invent 2018 | re:Invent 2024 CW | **Mean** | Off-tracks (12 trials) |
|---|---|---|---|---|---|---|
| **Model 03 ckpt 31 (uploaded, portal 22.5)** | **14.7** | **21.6** | **14.0** | **20.5** | **17.7 s** | 30 |
| 03b @ 04:00 (ckpt 56) | 17.0 | 24.5 | 16.6 | 22.2 | 20.1 s | 28 |
| 03b final (ckpt 69) | 18.3 | 23.4 | 16.9 | 22.8 | 20.3 s | **11** |
| 03b @ 05:00 (ckpt 63) | 18.5 | 24.8 | 17.9 | 21.9 | 20.8 s | 26 |

**Conclusion:** both-direction training did fix right turns (the final checkpoint has **about a third of the off-tracks** of Model 03 (11 vs 30), and only 1–2 per lap on Summit), but the model also got **much slower** (average speed 1.46 → 1.28 m/s; clean Vegas lap 14.7 → 18 s). Overall that loses more time than the fewer off-tracks save. **Recommendation: don't upload; Model 03 ckpt 31 stays our entry.**

**But for the physical race (Oct 8):** `cedc-m03b-final` is the most *reliable* model we have (fewest off-tracks, right turns handled). On a real track, where an off-track may cost more than a few seconds, it may be the better choice. Keep it as the physical-race candidate.

**Why it slowed down (hypothesis):** once laps complete reliably, the reward's pace term (capped at about 3 m/s-equivalent) and speed-matching don't reward going faster *enough* compared to the risk of crashing, so the policy drifts toward caution. Next model should keep the right-turn skill but **push speed explicitly**, e.g. continue from 03b-final with a higher speed floor (min 1.5 m/s) and/or a lap-time bonus that grows as laps get faster.

## Check-in log

**05:59. Stable plateau.** 907 episodes (~45 iterations). Last 20: 86%, 15/20 laps; 450 laps total. Counterclockwise 89% / 22 laps (17.6 s), clockwise 77% / 17 laps (16.7 s). Mean speed 1.29 m/s. 15 simulator restarts since 04:05, 0 crashes, Windows 3.8 GB available.
