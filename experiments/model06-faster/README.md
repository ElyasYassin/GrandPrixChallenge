# Model 06: Faster

**Why:** Model 05 snap2 (portal **17.877**) has the *same best lap* on the secret track as Model 04 (14.713 vs 14.710 s). Better lines and reliability only trimmed the average; **top speed looks like the binding limit**. The leader (5.5 s) is far faster, not just more consistent. Also: both racing-line runs peaked after about 1–1.5 h and then degraded, which suggests the learning rate is too high for fine-tuning.
**Starts from:** Model 05 snap2 (ckpt 125). Vegas only, both directions.

## Changes vs Model 05

| | Model 05 | **Model 06** |
|---|---|---|
| Speed action range | 1.3–3.0 m/s | **1.3–4.0 m/s** |
| Expert grip budget | 4 m/s² | **5 m/s²** (measured: the simulator holds ≥ 5–6) |
| Pace reward cap | ~3 m/s | ~4 m/s |
| Learning rate | 0.0003 | **0.0001** (fine-tuning without forgetting) |
| term_cond_max_episodes | 1000 | 100000 (stop condition only) |

Speed floor: 1.5 m/s was tried first; offline it asked for up to 7.1 m/s² on tight tracks (above what the simulator holds). **1.3** gives the same lap times with ≤ 5.0 m/s² on 9/10 tracks.

## Offline validation

Expert laps all 10 tracks; Vegas **7.3 s** (M05 expert 8.2 s), Summit 7.5 s (8.7). Lap-time simulation, racing line, Vegas: best possible 8.65 s (3.0 m/s, 4 m/s²) → **7.65 s** (4.0 m/s, 5 m/s²).

In the simulator: reward median 4.4 per step, 11 laps in the first 3,700 steps.

## Run

`cedc-m06-faster`, started ~02:05 on 2026-10-01, supervised until 05:00 (`tools/supervise.sh`, memory thresholds 4/8.5 GB), snapshots every 30 min, then automatic 4-track evaluation of every snapshot (`tools/overnight_run.sh` → `logs/m06_overnight_summary.txt`).

## Results

Training 02:05–05:02 (28 simulator restarts, 0 crashes, 0 full resumes). Laps got faster (13.6–14.4 s vs M05 ≈14.7) but fewer completed (5–9 / 20 episodes).

Evaluation (3 trials per track, penalties included, all trials complete):

| Candidate | Vegas | Summit | re:Inv 2018 | re:Inv 2024 CW | **Mean** | Off-tracks | Trial spread |
|---|---|---|---|---|---|---|---|
| snap 04:09 (ckpt 146) | 15.39 | 16.76 | 14.01 | 18.02 | 16.05 | 18 | 1.32 s |
| snap 02:38 | 14.28 | 17.10 | 13.53 | 19.46 | 16.09 | 19 | 1.27 s |
| **snap 03:39 (ckpt 141)** | 14.67 | 17.47 | 14.12 | **18.21** | **16.12** | 18 | **0.76 s** |
| final | 14.12 | 16.44 | 14.54 | 20.98 | 16.52 | 25 | 0.84 s |
| snap 03:09 | 15.51 | 16.57 | 14.41 | 19.65 | 16.53 | 25 | 0.87 s |
| snap 04:40 | 15.01 | 18.09 | 14.34 | 19.07 | 16.63 | 23 | 0.93 s |
| *M05 snap2 (portal 17.877)* | *15.61* | *18.16* | *13.94* | *18.35* | *16.51* | *14* | *0.70 s* |

(snap 04:09's re:Invent 2018 eval failed in the overnight batch and was re-run at 06:05.)

**Speed helped:** the top three snapshots are about 0.4 s faster on average than M05 snap2, at the cost of ~4 more off-tracks. They are tied within noise; **snap 03:39 chosen** for its consistency (trial spread 0.76 s, close to M05's 0.70). Packaged: `submissions/cedc-m06-snap0339-ckpt141.tar.gz`. Reminder: locally M05 looked 0.53 s better than M04 but gained 0.13 s on the portal, so expect a smaller real gain.

The lower learning rate did not stop the late decline entirely (final and 04:40 are worse), but the run stayed competitive for longer (02:38–04:09 all ≈16.1).


## Portal result (#16, 2026-10-01 09:43)

**Score 23.554, best lap 14.510** (M05 snap2: 17.877 / 14.713). The best lap improved by 0.2 s, but the average got much worse: 9.0 s above the best lap (M05: 3.2 s), so the faster car lost far more time to off-tracks on the secret track. Our 4-track × 3-trial evaluation ranked it better than M05 (16.12 vs 16.51), the wrong direction. **Lessons:** on the secret track reliability matters more than speed; select candidates by off-track count first, use more trials and more unseen tracks.
