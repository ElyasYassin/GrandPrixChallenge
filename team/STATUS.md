# Status per machine

Edit only your own section. Times are local (Mountain Time).

---

## Elyas: RTX 3090 / Ryzen 5 5600X (DRfC in WSL2)

**Updated:** 2026-10-01 12:30

| | |
|---|---|
| Training now | **Model 07 reliable** (`cedc-m07-reliable`) since ~11:45, from M06 snap 03:39: off-track penalty −20 + edge-safety factor, 1.3–4.0 m/s, lr 0.0001; stops 15:30, then 5-trial eval of 30-min snapshots |
| Last run | Model 06 (speed 1.3–4.0 m/s, lr 0.0001), from M05 snap2 → portal #16: **23.554** (best lap 14.510): faster best lap, but many more off-tracks |
| Best on portal | **Model 05 snap2 (ckpt 125): 17.877**, best lap 14.713 (#15). Leaderboard keeps the best submission |
| Next | Pick the M07 snapshot by fewest off-tracks, then mean time; consider probe uploads (see FINDINGS) |
| Machine notes | 1 simulator only (CPU); simulator leaks memory with GPU rendering → `tools/supervise.sh` restarts it at iteration boundaries |

---

## Teammate: (machine)

**Updated:** —

| | |
|---|---|
| Training now | |
| Last run | |
| Next | |
| Machine notes | |
