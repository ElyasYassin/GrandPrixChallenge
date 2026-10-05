# Status per machine

Edit only your own section. Times are local (Mountain Time).

---

## Elyas: RTX 3090 / Ryzen 5 5600X (DRfC in WSL2)

**Updated:** 2026-10-04 13:15

| | |
|---|---|
| Training now | Nothing (C: drive ~2.8 GB free) |
| Last run | Model 07 (off-track penalty + edge safety): no clear gain over M05 snap2 in 5 trials × 6 tracks |
| Best on portal | **Model 10 variety c2-end (ckpt 199): 7.130**, best lap 6.740 (#33). Leaderboard keeps the best submission |
| Next | Evaluate M08 snapshots on held-out tracks (reInvent2019, reinvent_base, 2022_reinvent_champ_ccw); check zig-zag numbers |
| Machine notes | 1 simulator only (CPU); simulator leaks memory with GPU rendering → `tools/supervise.sh` restarts it at iteration boundaries |

---

## Jason: RTX 3090 (DRfC in WSL2, repo inside WSL at ~/GrandPrixChallenge)

**Updated:** 2026-10-04 19:50

| | |
|---|---|
| Training now | **Model 15** (Stanley path-tracking expert on the racing line + Model 14b reward) from M13 wooc1-end, 19:45 → ~00:40 |
| Last run | Model 14b (smooth/completion-first reward): all evals 100 % but not better than **Model 13 wooc1-end**, which stays our best (0 off on 6 tracks, 12.53 s; `submissions/cedc-m13-jason-wooc1-end.tar.gz`) |
| Next | Evaluate M11 snapshots under practice-race rules + a textured world; if DR learns too slowly from scratch, fine-tune M10's best with DR (needs `cedc-m10-summit1-end` from Elyas) |
| Machine notes | 1 simulator, 16 GB WSL. Repo lives inside WSL: tools now find the repo themselves (`tools/env.sh`) and run from Git Bash or WSL |
