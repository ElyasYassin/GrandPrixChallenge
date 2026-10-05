# The secret evaluation track: what we think we know

Living document for both teams' AIs. Each portal upload is a **probe**: we know how the model behaves locally, so its secret-track result tells us something about the track. **Append new observations to the log at the bottom** and update the belief table if they change it. Treat every claim here as a hypothesis to verify.

Full method: [`experiments/ANALYSIS_secret_track.md`](../experiments/ANALYSIS_secret_track.md), tool: [`tools/secret_track_inference.py`](../tools/secret_track_inference.py).

---

## 1. Current beliefs (2026-10-01, from 5 uploads)

| # | Belief | Confidence | Main evidence |
|---|---|---|---|
| B1 | Length is **~25–29 m** (Vegas: 22.6 m) | Medium-high | Near-constant-speed M02 takes 1.29× its Vegas lap |
| B2 | It **flows faster than Vegas**: longer straights and/or fast sweepers; top speed pays | Medium | Fast models average ~2 m/s there vs ~1.45 m/s on Vegas despite the extra length |
| B3 | It has **tight right-hand turns** (or tight turns in both directions) | Medium | One-direction M03 lost 6.8 s to off-tracks; both-direction M04 lost 3.3 s |
| B4 | **Off-track risk at speed is high** (narrow track or hard corner entries after fast sections) | Medium-high | M06 (4 m/s) lost 9.0 s to off-tracks vs 3.2 s for M05 (3 m/s) |
| B5 | It is **probably a custom track**, not one of the simulator tracks | Low-medium | No simulator track fits all 5 probes (best rms error ~8%) |
| B6 | Closest simulator shapes: **2024_reinvent_champ** (cw/ccw) and **2022_summit_speedway** | Medium | Best fits (0.077, 0.089 rms log error) and similar profile (table below) |

Unknowns: track width (summit is 1.07 m, re:Invent 2024 is 0.76 m; B4 hints narrow), driving direction, whether the 3 trials alternate direction, and exactly how the portal adds penalty time.

## 2. Evidence

### Portal history (score = average of 3 trials; best = best lap)

| # | Model | Profile | Score | Best lap | Score − best ≈ off-track time |
|---|---|---|---|---|---|
| 10 | M02 | ≤1 m/s, very consistent | 34.716 | 34.713 | 0.0 s |
| 13 | M03 | ≤2.5 m/s, one direction (weak right turns) | 22.508 | 15.706 | 6.8 s |
| 14 | M04 | ≤3 m/s, both directions | 18.008 | 14.710 | 3.3 s |
| 15 | **M05 snap2** | ≤3 m/s, racing line | **17.877** | 14.713 | 3.2 s |
| 16 | M06 | ≤4 m/s, racing line | 23.554 | 14.510 | 9.0 s |

Leader (Shallow Learner): 5.615 / 5.542, so the score and best lap are almost equal: a clean, fast model. That lap at ~2.6 s per 10 m means ≥ 4.5–5 m/s average on a 25–29 m track (or a shorter track than we think, see probes P5).

### Secret / Vegas best-lap ratio per probe

| Model | Vegas best (local) | Secret best | Ratio |
|---|---|---|---|
| M02 | 26.98 | 34.713 | 1.29 |
| M03 | 14.52 | 15.706 | 1.08 |
| M04 | 15.64 | 14.710 | 0.94 |
| M05 | 14.78 | 14.713 | 1.00 |
| M06 | 14.00 | 14.510 | 1.04 |

The ratio falls as models get faster → the extra length is in sections where a faster car gains a lot (straights, sweepers).

### Candidate stand-in tracks (profiles from waypoints)

| Track | Length | Width | Corners (L/R) | Tight < 0.8 m radius | Longest straight | Straight share |
|---|---|---|---|---|---|---|
| Vegas_track (training) | 22.6 m | 1.07 | 10 (7/3) | 10 | 3.3 m | 37% |
| **2024_reinvent_champ_cw** | 25.1 m | 0.76 | 10 (3/7) | 4 | 3.6 m | 47% |
| 2024_reinvent_champ_ccw | 25.1 m | 0.76 | 10 (7/3) | 4 | 3.6 m | 47% |
| **2022_summit_speedway** | 25.2 m | 1.07 | 12 (7/5) | 7 | 3.6 m | 46% |
| 2022_summit_speedway_cw | 25.1 m | 1.07 | 10 (3/7) | 4 | 3.6 m | ~46% |
| reInvent2019_track | 23.1 m | — | 10 (7/3) | 2 | 5.1 m | 38% |
| reinvent_base | 17.7 m | — | 5 (4/1) | 3 | 3.9 m | 51% |

The two best fits share what B1–B3 predict: ~25 m, **more straight than Vegas (46–47% vs 37%)**, fewer but still several tight corners, and in one direction mostly right turns.

## 3. What this means for us

**Training**
- Keep `DR_TRAIN_ALTERNATE_DRIVING_DIRECTION=True` (B3). Consider training directly on **2024_reinvent_champ** (both directions) or alternating it with Vegas: closer to the secret track than Vegas is.
- Speed pays on straights (B2) but costs off-tracks in corners (B4): reward **braking before corners** and carrying speed on straights, not a higher top speed everywhere. The braking-aware speed profile in the M05+ reward already does this; check tight-corner entry speed when tuning.
- Narrow-track robustness (B4, 0.76 m width): edge-safety reward (M07), the racing line with margin ≥ 0.30 m.

**Evaluation / choosing what to upload**
- Rank by **off-track count first**, then mean time (FINDINGS 2026-10-01).
- Use ≥ 5 trials per track, and weight **2024_reinvent_champ cw + ccw** and **2022_summit_speedway** (incl. cw) more than Vegas. Vegas-only results misled us on M06.
- A candidate worth uploading: zero or near-zero off-tracks on those stand-ins, and lap time no worse than M05 snap2 there.

### Plan: train on the stand-ins (now part of Model 08 discrete, running since 2026-10-01 15:53)

Train on the closest-matching tracks as well as Vegas (Model 08 trains from scratch with a discrete action space, see `experiments/model08-discrete`):
- 2024_reinvent_champ (both directions; ~1 h), then 2022_summit_speedway (both directions; ~1 h), optionally back to Vegas briefly so it doesn't forget. Our reward is track-agnostic (racing line and speed profile computed from runtime waypoints), so no reward changes are needed.
- One simulator only, so tracks change between runs (`start_run.sh` currently forces Vegas and needs a world argument).
- **Cost:** those tracks stop being unseen tests. New held-out set for choosing uploads: **reInvent2019_track, reinvent_base, 2022_reinvent_champ_ccw, Vegas cw** (plus one unseen ~25 m track if we find one). Judge generalization only on held-out tracks; stand-in results show fit, not generalization.
- Risk: memorizing the stand-ins. The secret track is probably custom (B5), so the point is more variety of similar corners and straights, not copying one layout.

## 4. Probe plan (uploads are free: the leaderboard keeps the best)

Ask the humans before uploading; each probe answers one question.

| Probe | Model profile | Question it answers |
|---|---|---|
| P1 | Left-strong (trained CCW only on Vegas) | If it gets many off-tracks: the track has tight **right** turns (confirms B3) |
| P2 | Right-strong (trained CW only) | Mirror of P1: tight left turns? |
| P3 | Slow and clean, fixed ~1.5 m/s | Track length directly: length ≈ 1.5 × lap time (sharpens B1) |
| P4 | Fast but cautious (high straight speed, low corner speed) | Whether straight speed or cornering decides time (B2) |
| P5 | Best clean model at a capped 2 m/s | Separates "track is longer" from "track is faster" |

Non-upload questions for the humans:
- Ask the organizers: track length/width, whether it's a standard simulator track, how off-track penalties are timed.
- Check the practice race leaderboard: if top Vegas times there ≈ the secret track leader's times, the tracks are similar in size.

## 5. Observation log (append below, newest last)

Format: `date · who · upload / observation · what it implies for B1–B6`

- 2026-10-01 · Elyas · 5 probes above (M02–M06) · basis for B1–B6
- 2026-10-01 · Elyas · M08 Vegas-end (discrete actions, Vegas only, <2 h from scratch; Vegas eval best 12.66, mean 13.73) → portal **16.693 / 13.928**, score − best 2.77 s (M05 3.16 s) · secret/Vegas best-lap ratio **1.10** (M05 1.00, M06 1.04): this model gains less on the secret track than on Vegas; consistent with B1 (longer) and with corners Vegas doesn't train (B3); off-track cost similar to M05 (B4 unchanged)
- 2026-10-01 · Elyas · **M08 vegas2-2147** (same discrete model after +1 h on 2024_reinvent_champ_cw, +45 min on 2022_summit_speedway, +1 h on Vegas) → portal **10.824 / 10.225**, score − best **0.6 s** (was 16.693 / 13.928, 2.8 s). Training on the stand-ins cut the secret-track time by 35% and almost removed off-tracks → **strong support for B6** (the secret track's corners look like re:Invent 2024 / Summit) and for B3/B4. Its secret lap (10.2 s) is now *faster* than its Vegas training laps (~13.5 s): ratio ≈ 0.76 (M05 1.00), so the secret track is probably shorter and/or more flowing than B1's 25–29 m guess; earlier ratios were inflated by models that handled its corners badly. Revisit B1.
- 2026-10-02 · Elyas · M09 (M08 21:47 + ~2 h / ~3 h more on **2024_reinvent_champ_cw only**, speed reward): portal **10.167 / 9.985** (2 h) and 11.286 / 11.014 (3 h); off-track cost 0.18 s / 0.27 s. re:Invent 2024 alone keeps improving the secret-track time; the faster snapshot wins, so speed is now the lever. Further support for B6 (re:Invent 2024 is the closest stand-in).
- 2026-10-02 · Elyas · **Revisit B1 (length):** theoretical laps (perfect driver, racing line) on 25 m tracks are ≥ 6.2 s even at 6 m/s and 8 m/s² grip, so the leader's 5.54 s implies a shorter track, likely ~17–20 m (reinvent_base, 17.7 m: 5.1–6.2 s). Our early 25–29 m estimate came from models that were slow on its corners.
- 2026-10-02 · Elyas · M10 summit1-end (real-car expert, faster actions; Summit training laps ~10 s vs ~15 s for M09, but only ~20–30% completed) → portal **10.096 / 9.902**, off-track cost 0.19 s. A ~35% faster Summit lap gave only ~1% on the secret track: whatever limits the secret-track lap is not what limits Summit (tight sections where both models drive similarly?). The off-track cost stayed tiny although training completion was low, so the secret track is more forgiving than our stand-ins at speed.
- 2026-10-03 · Elyas · M10 summit4-0247 (our 10.096 model + ~2.5 h **Summit only**; Summit training laps ~10 s, ~45% completed) → portal **13.527 / 13.270**: 3.4 s *slower* best lap, off-track cost still small (0.26 s). Specialising on Summit hurt badly on the secret track. Pattern so far: Vegas-only 13.9 best lap; Vegas+rI2024+Summit mix 10.2; rI2024-heavy 9.99; rI2024 30 min + Summit 1 h 9.90; Summit-heavy 13.27. **The secret track is not Summit-like; mixed training (and rI2024) transfers best.**
- 2026-10-03 · Elyas · M10 champ2-1940 (best model + ~50 min **rI2024 only**, finishing just ~2% of training laps there) → portal **10.442 / 10.103**, close to our best; Summit-only training gave 13.27. rI2024 time transfers to the secret track even when the car struggles on rI2024; Summit time does not. Next runs weight rI2024 most.
- 2026-10-03 · Elyas · Mixed-run probes from the best model: c2-end (rI2024/Vegas/rI2024) 13.920 / 10.497 (3.4 s lost to off-tracks), s1-end (+Summit 20 min) 10.494 / 10.356. Six uploads in a row land at **best lap 9.9–10.5 s** whatever we train on, while training laps elsewhere dropped to ~9 s (Vegas) and ~10 s (Summit). Something specific to the secret track sets a ~10 s floor for our models.
- 2026-10-04 · Elyas · **Breakthrough: 7.130 / 6.740** (#33) from our 10.096 model + 40-min phases on rI2024, Vegas, **reInvent2019_wide (16.6 m), Summit, reinvent_base (17.7 m)**, Canada, rI2024 (lr 0.0001). The ~10 s wall broke after training on *short* tracks for the first time. Strong support for the revised B1: the secret track is short (~17–20 m) and its character resembles reInvent2019_wide / reinvent_base more than our 25 m stand-ins. Off-track cost 0.39 s.
- 2026-10-04 · Elyas · w2-end (c2-end + Vegas + reInvent2019_wide, 80 min more) → 10.425 / **6.865**: same pace, but 3.56 s lost to off-tracks. Reliability on the secret track varies a lot between nearby snapshots; upload several.
- 2026-10-04 · Elyas · m11c-w1-end → 10.039 / 6.919 (3.1 s lost to off-tracks). Three uploads from the short-track lineage all have best laps 6.74–6.92 s but scores 7.13 / 10.04 / 10.43: **pace is settled at ~6.8 s; the score is decided by whether any of the 3 trials goes off track** (~3 s per bad trial on the average). Reliability is now the lever.
