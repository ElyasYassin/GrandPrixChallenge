# Model J29: Model 14b with faster corners (speed first, for Jason's two simulators)

**Why (Elyas, 2026-10-06 18:00):** speed first, reliability after. Portal evidence: J27 slowed the sharp turns to stay within the measured grip and its best lap got **slower** (wb3-end 6.407 vs m14b-w8-end 6.270, both clean). In this simulator a car that slides a little but carries speed through the corner is quicker, so go the other way.

**Change vs Model 14b (`experiments/model14b-cap4`):**

| Action | 14b | J29 |
|---|---|---|
| ±30° | 2.5 | **2.8** |
| ±20° | 2.9 | **3.2** |
| ±12° (slow) | 3.1 | **3.4** |
| 0° brake | 2.5 | **2.8** |
| ±12° fast, ±6°, 0° 3.6 / 4.0 | unchanged | unchanged |

Same 15 actions in the same order, so it **fine-tunes from `m14b-w8-end`** (like J27). Expert: `MIN_SPEED` 2.5 → 2.8, `MAX_LAT_ACC` 9.0 → 10.5. Everything else is Model 14b.

**Closed-loop expert check** (`tools/expert_closed_loop.py`, kinematic car, 1-step delay, 5° steering noise, 3 seeds):

| | A to Z lap / offs | re:Invent 2018 lap / offs |
|---|---|---|
| 14b | 7.3 s / 1.3 | 10.4 s / 4.7 |
| J29 | **6.9 s / 1.0** | 12.6 s / 7.3 |

Faster on A to Z (the layout closest to the secret track), worse in re:Invent 2018's tight hairpins: expected for a speed-first bet.

**Run:** two simulators `reInvent2019_wide+reinvent_base`, no DR, lr 0.0001, snapshots every 30 min, overnight, from `m14b-w8-end` (last). Judge on A to Z lap time first (5 trials); reliability work tomorrow (clean-snapshot screening, short low-lr fine-tune).

## Results

**Test 1 (20:36, Jason's machine, A to Z 5 trials, DR off; `logs/m29_test.txt`):**

| Snapshot | off | mean | best lap |
|---|---|---|---|
| m14b-w8-end (portal 6.338), same test earlier | 3 | 7.70 | 6.20 |
| J27 wb3-end (portal 6.531) | 1 | 6.63 | 5.93 |
| J29 wb1-end | 3 | 7.09 | 5.82 |
| J29 wb2-end | 6 | 7.55 | **5.62** |
| **J29 wb3-end** | **2** | **6.41** | 5.81 (clean laps 5.81–5.96) |

Training (A to Z median training lap 5.8–6.1 s vs ~6.7 for J27; re:Invent 2018 ~25 % progress, almost no laps). Packaged: `m29-jason-wb3-end-ckpt462`, `m29-jason-wb2-end-ckpt428`. Resumed as `m29b-jason-*`.

**Test 2 (23:50, A to Z 5 trials, DR off; `logs/m29_test2.txt`):**

| Snapshot | off | mean | best | clean laps |
|---|---|---|---|---|
| m29b wb4-end | 2 | 6.09 | **5.35** | 5.35, 5.55, 5.74 |
| m29b wb5-end | 3 | 6.55 | 5.88 | 5.88, 5.94 |
| m29b wb6-end | 6 | 7.50 | 5.88 | 5.88 |
| **m29b wb7-end** | **1** | **5.93** | 5.56 | **5.56, 5.68, 5.81, 5.82** |

wb7-end: 4 of 5 laps clean at 5.56–5.82 s (leader's portal score 5.615). Packaged: `m29b-jason-wb7-end-ckpt590` (pick), `m29b-jason-wb4-end-ckpt495` (fastest lap). Resumed as `m29c-jason-*`.
