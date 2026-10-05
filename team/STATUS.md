# Status per machine

Edit only your own section. Times are local (Mountain Time).

---

## Elyas: RTX 3090 / Ryzen 5 5600X (DRfC in WSL2)

**Updated:** 2026-10-04 13:15

| | |
|---|---|
| Training now | Nothing (C: drive ~2.8 GB free) |
| Last run | **J16b** (your 7.130 model + your settings, two simulators, 4.8 h): `ws1-end` 12/12 laps, **10 off-tracks vs 24** for the 7.130 model, **10.01 vs 11.19 s** mean on wide / base / rI2024 / Vegas (same eval settings). Packaged for portal: `submissions/cedc-m16b-jason-ws1-end.tar.gz`, `…-wbo1-end.tar.gz` |
| Best on portal | **Model 10 variety c2-end (ckpt 199): 7.130**, best lap 6.740 (#33). Leaderboard keeps the best submission |
| Next | Evaluate M08 snapshots on held-out tracks (reInvent2019, reinvent_base, 2022_reinvent_champ_ccw); check zig-zag numbers |
| Machine notes | 1 simulator only (CPU); simulator leaks memory with GPU rendering → `tools/supervise.sh` restarts it at iteration boundaries |

---

## Jason: RTX 3090 (DRfC in WSL2, repo inside WSL at ~/GrandPrixChallenge)

**Updated:** 2026-10-05 08:35

| | |
|---|---|
| Training now | **Model J18** (physical race): J16b ws1-end + carpet/wood floors with wide/base, your settings otherwise, 08:35 → ~12:40 |
| Last run | **J16b** (your 7.130 model + your settings, two simulators, 4.8 h): `ws1-end` 12/12 laps, **10 off-tracks vs 24** for the 7.130 model, **10.01 vs 11.19 s** mean on wide / base / rI2024 / Vegas (same eval settings). Packaged for portal: `submissions/cedc-m16b-jason-ws1-end.tar.gz`, `…-wbo1-end.tar.gz` |
| Next | Evaluate Model J15 (~01:30). Then, per Elyas's 7.130 finding: short tracks (reInvent2019_wide, reinvent_base) in every rotation, and textured-floor training on top of the 7.130 model if its checkpoint can be shared (questions below) |
| Machine notes | Two simulators per run (DRfC multi-config, one track each), 16 GB WSL, C: has ~570 GB free (happy to run long jobs). Repo lives inside WSL: tools now find the repo themselves (`tools/env.sh`) and run from Git Bash or WSL |

**Naming:** my experiments are `model11-jason-*` … `model15-jason-*`; in the LOG I call them **J11–J15** so they don't clash with Elyas's Models 11/11b/11c.

### For Elyas (from Jason's machine, updated 2026-10-05 08:40)

**Your finding "pace is settled at ~6.8 s, off-tracks decide the score" matches what my runs improved.** J16b = your 7.130 model (`cedc-m10v-c2-end`, from your bundle) + **your own settings** (M10 reward, no DR, plain floors, short-track mix, lr 0.0001), the only difference being **two simulators** (two tracks per batch). Same local eval for both (4 tracks × 3 trials, DR off, 1 s penalties):

| | off-tracks / 12 laps | mean | reInvent2019_wide | reinvent_base |
|---|---|---|---|---|
| your 7.130 model | 24 | 11.19 s | 8.39 s, 3 off | 11.07 s, 8 off |
| **J16b ws1-end** | **10** | **10.01 s** | 7.65 s, 0 off | 8.89 s, 3 off |

J17 (ws1-end + 4 h more, same recipe): on wide + base **wv1-end 2 off-tracks / 7.74 s mean** (ws1-end 3 / 8.27, your 7.130 model 11 / 9.73), but more off-tracks on rI2024/Vegas; ws1-end stays most reliable over all four. Full table: `experiments/model17-jason-7130-short2/README.md`. Bundles: `submissions/cedc-m16b-jason-ws1-end.tar.gz`, `cedc-m17-jason-wv1-end`, `-br1-end` (+ `cedc-m16b-jason-wbo1-end`); Jason uploads to the portal.

1. ~~Share the 7.130 checkpoint~~ — received, thanks. Note for imports: portal bundles name the checkpoint without `.ckpt` and my MinIO dropped the 47 MB weights in a multipart upload; `tools/wsl/import_bundle.sh` handles both.
2. ~~11c vs my J15 expert~~ — both dropped (yours: slower on the portal; mine: worse in training). Agreed: the expert line is closed.
3. **Want me to keep running your recipe with two simulators** (I have ~570 GB free and a free 3090 most of the time)? Tell me a start checkpoint + tracks and I'll claim it here.
4. **Physical race (Oct 8):** your 7.130 model leaves the carpet floor 4–5× per lap (wide: 1–2). My texture recipe (J13: carpet/wood in training, off-tracks 27 → 4, held-out concrete 12 → 4) could be applied to the final portal pick before the race. Do we know anything about the real track surface?
5. **Shared tools changed** (two simulators via `world A+B`, no hard-coded Windows path via `tools/env.sh`; single-track runs behave as before). Please do one dry `bash tools/supervise.sh` start after pulling.
