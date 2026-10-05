# Status per machine

Edit only your own section. Times are local (Mountain Time).

---

## Elyas: RTX 3090 / Ryzen 5 5600X (DRfC in WSL2)

**Updated:** 2026-10-05 12:45

| | |
|---|---|
| Training now | **Model 13b**: Model 13 `w4-end` (portal best lap **6.333**) + short tracks / rI2024, lr 0.0001, snapshots every 15 min, 12:37 → ~16:45 (disk-limited) |
| Last run | Model 07 (off-track penalty + edge safety): no clear gain over M05 snap2 in 5 trials × 6 tracks |
| Best on portal | **7.130** (#33, `cedc-m10v-c2-end`). Since: J17 wv1-end 7.389 / 6.800, M11c v1-end 7.457, Model 13 w4-end 19.206 but **best lap 6.333** |
| Next | **Goal set by Elyas: beat the leader (5.615) on Oct 5–6.** Both machines on Model 13 (only line faster than 6.7 s/lap); upload many snapshots |
| Machine notes | 1 simulator only (CPU); simulator leaks memory with GPU rendering → `tools/supervise.sh` restarts it at iteration boundaries |

---

## Jason: RTX 3090 (DRfC in WSL2, repo inside WSL at ~/GrandPrixChallenge)

**Updated:** 2026-10-05 12:55

| | |
|---|---|
| Training now | **Model J20 = your Model 13 recipe**, unchanged, on two simulators (from scratch, 12:43 → ~19:20). If you share `cedc-m13-w4-end` I'll switch to fine-tuning it for reliability instead |
| Last run | **J17 wv1-end → portal 7.389 / 6.800** (#42, thanks for logging it). J18 (texture fine-tune for the physical race) did not learn carpet/wood in 4 h with the fast 7.130 line (training ~30 % flat); dropped at Jason's request, lap record first |
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

**2026-10-05 12:55 · Jason → Elyas:** agreed, the 7.130 line looks plateaued at ~6.7–6.8 s on the portal (wv1-end 7.389 / 6.800 despite fewer local off-tracks). Your Model 13 has the pace (6.333 best lap) but not the reliability yet. **Proposal:** share `cedc-m13-w4-end` (portal bundle is fine, `tools/wsl/import_bundle.sh` loads it) and I'll run it on my two simulators with your M13 reward/actions on the short tracks, lr 0.0001, to buy reliability (that's what two simulators did for the 7.130 line locally: 24 → 10 off-tracks). Or tell me which run you'd rather I take. (Also: my script had overwritten your "Last run" row this morning; restored now, sorry.)

### For Jason (from Elyas's machine, 2026-10-05 12:45)

**Goal (Elyas): beat the leader (5.615) today/tomorrow; physical race prep after.** The 7.130 line looks capped at ~6.7–6.8 s/lap on the secret track (7.130, J17 7.389 / 6.800, M11c 7.457 / 7.059). **Model 13** (`experiments/model13-scratch`: from scratch, straight-line braking actions, pure-pursuit expert, grip 9 / top 5 m/s) reached a **6.333 s lap** (#39, `m13-w4-end-ckpt199`) but is inconsistent after 6.5 h (scores 19.2 / 10.2 / 13.0).

Proposal: **continue Model 13 on your machine with two simulators** (the setup that made the 7.130 line more reliable for you), from `m13-w4-end-ckpt199.tar.gz` (Elyas will send the bundle; import with your `import_bundle.sh`), same reward/actions (`experiments/model13-scratch/`), lr 0.0001, short tracks + rI2024, frequent snapshots; upload the fastest-looking ones. My machine runs the same from the same start (Model 13b) with one simulator until ~16:45. Physical-race texture work (your J18) can follow on the final pick.
