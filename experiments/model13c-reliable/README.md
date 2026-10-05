# Model 13c: Model 13 + reliability (goal: beat the leader, 5.615)

**Status (2026-10-05):** best 7.130 (#33). Model 13 (from scratch: straight-line braking, pure-pursuit expert, grip 9 / top 5 m/s) showed the pace: **6.333 s lap** (#39, `m13-w4-end` ckpt 199), but its three uploads scored 19.2 / 10.2 / 13.0: off-tracks (~3 s per bad trial) and inconsistency. The 7.130 line is capped near 6.7–6.8 s/lap (7.130, J17 7.389 / 6.800).

**Strategy (both machines on Model 13):**

| # | Strategy | Where |
|---|---|---|
| R2 | **Speed-scaled off-track penalty**: off-track reward = −2 × speed (was flat −5): leaving at 5 m/s costs 2× leaving at 2.5 m/s | this reward file (both machines) |
| R3 | **Screen before upload**: every snapshot is evaluated on reInvent2019_wide (5 trials); only 0-off-track ones are packaged (`tools/screen_loop.sh`) | Elyas |
| R1 | **Domain randomization + textured floors** (`DR_ENABLE_DOMAIN_RANDOMIZATION=True`, reinvent_carpet / reinvent_wood with the short tracks): Jason's J13 cut held-out textured off-tracks 27 → 4; the secret track is probably custom | Jason |
| R4 | **Two simulators per run** (Jason's J16b: 10 vs 24 off-tracks for the same model) | Jason |
| P1 | More training on Model 13 (pace 6.33 s after only 6.5 h) | both |
| P2/P3 (tonight, if R1–R4 look good) | 30° action 2.5 → 2.8 m/s; racing-line margin 0.30 → 0.20 m on wide tracks | best snapshot |

**Elyas's run:** `bash tools/screen_loop.sh model13c-reliable m13c cedc-m13-w4-end 6 0.0001` (hourly blocks: 2 × 30-min phases, snapshots every 15 min, then screening; disk-limited). Results in `logs/m13c_screen.txt`; packaged bundles `submissions/m13c-*.tar.gz`.

**Proposed for Jason's machine:** import `m13-w4-end-ckpt199.tar.gz` (Elyas sends it), then train this folder's reward + actions with two simulators, DR on, track pairs mixing reInvent2019_wide / reinvent_base / reinvent_carpet / reinvent_wood / rI2024, lr 0.0001, frequent snapshots; screen locally; upload clean, fast ones.

## Results

(pending)
