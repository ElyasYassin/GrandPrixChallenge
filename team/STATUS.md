# Status per machine

Edit only your own section. Times are local (Mountain Time).

---

## Elyas: RTX 3090 / Ryzen 5 5600X (DRfC in WSL2)

**Updated:** 2026-10-01 10:00

| | |
|---|---|
| Training now | nothing (idle since 05:02) |
| Last run | Model 06 (speed 1.3–4.0 m/s, lr 0.0001), from M05 snap2 → portal #16: **23.554** (best lap 14.510): faster best lap, but many more off-tracks |
| Best on portal | **Model 05 snap2 (ckpt 125): 17.877**, best lap 14.713 (#15). Leaderboard keeps the best submission |
| Next (planned, waiting for go-ahead) | Model 07 "reliability": from M05 snap2, speed 1.3–3.0, lr 0.0001, much stronger off-track penalty + reward for distance from the edges; pick snapshots by fewest off-tracks |
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
