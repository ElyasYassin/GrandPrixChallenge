# Limits & generalization analysis (2026-09-30)

## 1. Theoretical best lap ([tools/lap_time_sim.py](../tools/lap_time_sim.py))

Quasi-steady-state lap simulation: corner limit √(grip/curvature), capped at top speed, forward pass (accelerate), backward pass (brake late). Accel = brake = 3 m/s².

| Vegas | top speed | grip 4 m/s² | grip 6 m/s² |
|---|---|---|---|
| centre line | 2.5 m/s | 10.7 s | 9.5 s |
| centre line | 3.0 m/s | 10.3 s | 8.9 s |
| **racing line** | **3.0 m/s** | **8.65 s** | 7.7 s |
| racing line | 4.0 m/s | 8.4 s | 7.1 s |

Summit Speedway, racing line, 3.0 m/s, 4 m/s²: 9.0 s (4.0 m/s, 6 m/s²: 7.1 s).

- **Our model drives at about 60% of what its own limits allow** (about 14.5 s vs 8.65 s on Vegas). Execution is the biggest lever.
- Racing line ≈ −1.6 s on Vegas. More top speed barely helps at 4 m/s² grip (grip-limited, short straights).
- **#1 on the secret track: 5.54 s.** On a Vegas-length track that is below the 4 m/s / 6 m/s² bound (7.1 s). Either the secret track is much shorter than ours suggests (our secret lap 15.7 s ≈ our Vegas lap), or they use a top speed above 4 m/s (DRfC lets the action space exceed the console's 4 m/s), or "best lap" is measured differently. **To test: does the simulator accept speed actions above 4 m/s?**

## 2. Simulator grip, measured ([tools/grip_from_logs.py](../tools/grip_from_logs.py))

994 completed laps and 1,246 off-track episodes (Models 03, 03b, 04):

| | |
|---|---|
| lateral acc held in completed laps | p95 3.8, **p99 4.8, p99.9 6.0 m/s²** |
| lateral acc just before off-tracks | median **2.0 m/s²** (p75 2.9) |
| actual speed | median 1.42, max 2.26 m/s (commanded up to 2.5–3.0) |
| accel / braking seen | 2.9 / 2.75 m/s² |

- **Grip is at least about 5–6 m/s²**; the expert's 4 m/s² is conservative.
- **Off-tracks are not grip-limited.** They happen at low lateral acceleration, so they're steering or line errors, not slides.
- Top speed is never reached on these short straights.

## 3. Generalization efficiency ([tools/efficiency.py](../tools/efficiency.py))

efficiency = theoretical best lap (centre line, model's top speed, 4 m/s²) / actual mean eval time (penalties included). A model that learned *driving* scores similarly on Vegas and on unseen tracks; one that memorized Vegas drops.

| Model | Vegas | Summit | re:Invent 2018 | 2024 CW | unseen avg | gap |
|---|---|---|---|---|---|---|
| Model 02 ckpt 11 | 83% | 87% | 64% | 64% | 72% | +11 |
| Model 03 ckpt 31 (uploaded) | 72% | 53% | 56% | 54% | 54% | **+18** |
| 03b 04:00 | 63% | 47% | 48% | 50% | 48% | +15 |
| 03b final | 58% | 49% | 47% | 49% | 48% | **+10** |
| 03b 05:00 | 57% | 46% | 44% | 50% | 47% | +11 |

- Both-direction training cut the Vegas-vs-unseen gap from 18 to 10 points (less memorization), at the cost of speed.
- **Target for every new model: higher unseen efficiency with a small gap.** That, not the Vegas time, predicts the secret track and the physical race.
