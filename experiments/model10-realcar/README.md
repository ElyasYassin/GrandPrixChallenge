# Model 10: the real car (measured turning + grip)

**Why:** can we get near the leader (5.54 s)? A theoretical-lap check showed our expert's assumptions (grip 5 m/s², nominal steering geometry) cap a perfect driver far above that. So we measured the simulated car: a model whose 15 actions are all set to one fixed (steering, speed) drives steady circles (`tools/grip_sweep.sh`, `tools/wsl/grip_test.sh`, analysis `tools/grip_test_analyze.py`, results [`grip_test.txt`](grip_test.txt)).

| | Expert assumed (M05–M09) | Measured |
|---|---|---|
| Turn radius | 0.165 m / tan(steer) | **~0.34 m / tan(steer)** (30°: 0.70 m, 15°: 1.25 m, 8°: 2.1 m) |
| Sideways grip | 5 m/s² | **≥ 8.4 m/s²** without the radius growing (no slide seen) |
| Corner speed at full lock | ~1.2 m/s | the car holds **2.0–2.4 m/s** |

Also: commanded 6 m/s on a straight reached ~3.9 m/s and was still accelerating, but our models almost never chose the fast straight actions (Model 08 on Vegas: 2.5 m/s chosen 60×, 3.2/4.0 2× each), because the expert rarely asked for them.

**Changes vs Model 09:** effective wheelbase 0.34 m, grip budget 7 m/s², faster speeds on the **same 15 steering actions in the same order** (30° 1.3→2.0, 20° 1.5→2.4, 12° 1.7/2.1→2.6/3.2, 6° 2.4/3.0→3.2/4.0, 0° 2.5/3.2/4.0→3.0/3.5/4.0), so it fine-tunes from Model 09 instead of starting from scratch.

Closed-loop check (kinematic car with the measured geometry, 7° steering noise, actions snapped to each action set):

| Track | M09 expert | M10 expert |
|---|---|---|
| 2024_reinvent_champ_cw | 11.4 s | **8.3 s** |
| 2022_summit_speedway | 11.2 s | **8.6 s** |
| Vegas | 10.4 s | **7.5 s** |
| reinvent_base | 8.3 s | **6.2 s** |

| | |
|---|---|
| Starts from | `cedc-m09-summit1-0414` (portal **10.167** / 9.985) |
| Schedule | rI2024 / Summit alternating, 60 min each, lr 0.0003 ×4 then 0.0001 ×2, 16:47 → ~23:10 |
| Snapshots | every 30 min (`cedc-m10-<leg>-HHMM`) and each leg's end; upload the fastest |

## Results

(pending)
