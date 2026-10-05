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

**Updated:** 2026-10-05 04:00

| | |
|---|---|
| Training now | **Model J17**: J16b ws1-end + your recipe again (short tracks weighted more), two simulators, 04:00 → ~08:00 |
| Last run | **J16b** (your 7.130 model + your settings, two simulators, 4.8 h): `ws1-end` 12/12 laps, **10 off-tracks vs 24** for the 7.130 model, **10.01 vs 11.19 s** mean on wide / base / rI2024 / Vegas (same eval settings). Packaged for portal: `submissions/cedc-m16b-jason-ws1-end.tar.gz`, `…-wbo1-end.tar.gz` |
| Next | Evaluate Model J15 (~01:30). Then, per Elyas's 7.130 finding: short tracks (reInvent2019_wide, reinvent_base) in every rotation, and textured-floor training on top of the 7.130 model if its checkpoint can be shared (questions below) |
| Machine notes | Two simulators per run (DRfC multi-config, one track each), 16 GB WSL, C: has ~570 GB free (happy to run long jobs). Repo lives inside WSL: tools now find the repo themselves (`tools/env.sh`) and run from Git Bash or WSL |

**Naming:** my experiments are `model11-jason-*` … `model15-jason-*`; in the LOG I call them **J11–J15** so they don't clash with Elyas's Models 11/11b/11c.

### Questions for Elyas (from Jason's machine, 2026-10-04 20:15)

1. ~~**Can you share the 7.130 checkpoint?**~~ Received (all bundles), thanks — J16 is training on it. e.g. `tools/wsl/fetchmodel.sh cedc-m10v-c2-end` → zip `models/cedc-m10v-c2-end/model` (~60 MB) via OneDrive. I'd fine-tune it with the textured-floor recipe (J13: off-tracks on carpet/wood/concrete 27 → 4, see FINDINGS) for the **physical race**, keeping your short tracks in the mix.
2. **Our expert fixes overlap.** Your 11c (pure pursuit, measured geometry) and my J15 (Stanley tracker on the racing line, `experiments/model15-jason-path`) attack the same twitchy expert. Closed loop (8° noise, 5 tracks, measured 0.34 m geometry) mine went 40.8 → 36.9 s lap total, off-tracks 3.0 → 1.0. Suggest: whichever evaluates better on the short tracks, we both use. Can you post 11c's eval / portal numbers when you have them?
3. **Your C: drive is at ~2.8 GB.** Want me to take some training load? I can run two tracks at once (two simulators) and have ~570 GB free. Tell me a run (start checkpoint + tracks) and I'll claim it here.
4. **Shared tools changed** (commit "Jason's machine: …"): scripts no longer hard-code your Windows path (`tools/env.sh`; Git Bash path /c/Users/… is converted to /mnt/c/… for WSL), and `track_rotation.sh` accepts `A+B` worlds for two simulators. Single-track runs behave as before, but please pull and do one `bash tools/supervise.sh` dry start to confirm on your side. Your crash-dump cleanup is merged.
5. **Physical race (Oct 8):** do we know anything about the real track (surface, colour, width, lighting)? My textured-floor results suggest the floor look matters a lot.
6. **Portal:** my best (J13 `wooc1-end`, 0 off-tracks on 6 tracks locally, but ~11-12 s laps on 17-25 m tracks) is much slower than the 7.130 line. Worth uploading as a *reliability probe*, or not worth the slot?

