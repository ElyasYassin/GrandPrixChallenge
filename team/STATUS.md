# Status per machine

Edit only your own section. Times are local (Mountain Time).

---

## Elyas: RTX 3090 / Ryzen 5 5600X (DRfC in WSL2)

**Updated:** 2026-10-01 14:20

| | |
|---|---|
| Training now | Nothing; evaluating Model 07 snapshots (5 trials × 6 tracks, done ~15:25). Model 07 stopped early (14:03): training metrics flat for 2 h |
| Last run | Model 06 (speed 1.3–4.0 m/s, lr 0.0001), from M05 snap2 → portal #16: **23.554** (best lap 14.510): faster best lap, but many more off-tracks |
| Best on portal | **Model 05 snap2 (ckpt 125): 17.877**, best lap 14.713 (#15). Leaderboard keeps the best submission |
| Next | Model 08 from the best M07 snapshot, trained on the secret-track stand-ins (2024_reinvent_champ → 2022_summit_speedway → Vegas), see `SECRET_TRACK.md` |
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
