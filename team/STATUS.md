# Status per machine

Edit only your own section. Times are local (Mountain Time).

---

## Elyas: RTX 3090 / Ryzen 5 5600X (DRfC in WSL2)

**Updated:** 2026-10-06 11:50

| | |
|---|---|
| Training now | **Model 13c screening loop** from Model 13 `w4-end` (portal best lap 6.333): speed-scaled off-track penalty, hourly train + screen on reInvent2019_wide, clean snapshots packaged; since 12:47 |
| Last run | Model 07 (off-track penalty + edge safety): no clear gain over M05 snap2 in 5 trials × 6 tracks |
| Best on portal | **Model 14b w8-end (ckpt 357): 6.338**, best lap 6.270, clean (#51). Jason J23 bw8-end 6.989 (#50). Leader 5.615 |
| Next | **Goal set by Elyas: beat the leader (5.615) on Oct 5–6.** Both machines on Model 13 (only line faster than 6.7 s/lap); upload many snapshots |
| Machine notes | 1 simulator only (CPU); simulator leaks memory with GPU rendering → `tools/supervise.sh` restarts it at iteration boundaries |

---

## Jason: RTX 3090 (DRfC in WSL2, repo inside WSL at ~/GrandPrixChallenge)

**Updated:** 2026-10-06 16:25

| | |
|---|---|
| Training now | **J27** (your m14b-w8-end with 30° 2.2 / 20° 2.7 m/s, two simulators A to Z + re:Invent 2018). After 2.25 h, 5-trial A to Z test **1 off / 6.63 s mean, best 5.93 s** (your m14b-w8-end on the same test: 3 / 7.70); re:Invent 2018 8 / 9.48 (11 / 9.92). Bundles for Oct 7: `m27b-jason-wb3-end-ckpt447` (best), `m27-jason-wb1-end-ckpt388`. Training continues, tested every leg |
| Last run | **J23** (2018 + 2019 wide, 6 h): local 5-trial eval bw8-end 2018 1 off / 7.37 s, 2019 wide 1 off / 7.09 s vs your 7.130 model 5 / 8.63 and 4 / 7.92. J22 (2018 only) did not get cleaner on 2018 (4 off). Portal probes waiting for Jason's uploads in the morning |
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

**Update 12:50:** the plan is now strategies R1–R4 + P1–P3 in `experiments/model13c-reliable/README.md`. Proposed for your machine: Model 13c (that folder's reward/actions) with **two simulators + domain randomization + carpet/wood floors**, from `m13-w4-end-ckpt199.tar.gz`.

**2026-10-05 13:50 · Jason → Elyas:** thanks for the 13c plan, going with all of it. Your `tools/screen_loop.sh` now runs on both machines (`env.sh` instead of your Windows path), takes two-track legs (`PAIRS_SPEC="A+B:tag C+D:tag;..."`) and `TRAIN_DR=True` (DR while training, off while screening); your defaults are unchanged — please pull before the next block.

### For Jason (from Elyas's machine, 2026-10-06 12:05)

**New best: 6.338 / 6.270, clean (#51) = Model 14b `w8-end` (ckpt 357)**, ahead of J23 (6.989, #50). Gap to the leader: 0.72 s. Recipe: `experiments/model14b-cap4/` (Model 13c reward = M13 + speed-scaled off-track penalty; M13 actions **capped at 4.0 m/s**; expert grip 9, top 4), **no DR**, only **reInvent2019_wide (A to Z) + reinvent_base (re:Invent 2018)**, lr 0.0001, from `m13-w4-end`. It was still improving at the end (A to Z 62 → 70 % laps, re:Invent 2018 39 → 45 %, avg 6.2 / 6.5 s, best 5.28 s).

**Proposal for your machine (disk + two simulators):** import `m14b-w8-end-ckpt357.tar.gz` (Elyas sends it) and continue the same recipe with **two simulators: `reInvent2019_wide+reinvent_base`**, lr 0.0001, no DR, snapshots every 30 min, as long as possible (tonight). Upload your best-looking snapshots tomorrow (we have 5 uploads on Oct 7). My machine is disk-limited: Model 14b single-simulator continuation now, then a "free racing" fine-tune (pure lap-time reward + lower entropy) from the same model.

### Plan for the last two days (Elyas, 2026-10-06 14:40)

"Two chances to make adjustments" suggests the **physical race (Oct 8) counts**, so:

**Today (Oct 6): best virtual model.** Elyas's machine: E1 polish (Model 15, from m14b-w8-end) → E3 "free racing" (lap-time reward, decisive policy) → best of the two overnight. Jason's machine: J26 (m14b-w8-end, two simulators) as planned. Today's remaining uploads: the best snapshots of E1/E3/J26.

**Tomorrow (Oct 7): best physical candidate, both machines.** Start from the best virtual model (portal-proven, 4 m/s), fine-tune for real-world robustness: **domain randomization on** (lighting/colours), re:Invent 2018 in **carpet / wood / concrete** + A to Z, 4 m/s cap, low lr (0.00005), several hours. Judge locally under different textures/lighting (fewest off-tracks, least variation), not by peak pace. Upload 1–2 physical candidates to the portal too (in case the organizers load a submitted model), keep the best virtual one on the leaderboard. On race day: start ~60–70 % speed, raise with the adjustments if clean.

Open questions for the professor (Elyas asks): does the physical race decide the winner; which submission goes on the car; what are the "adjustments"; what is the physical track/surface?

### For Jason (from Elyas's machine, 2026-10-06 17:30): please run Model 17 tonight

Portal today: **#54 your J27 wb3-end 6.531 / 6.407, clean** (wb1-end #53 10.032 / 6.727, 1 off). Nice reliability gain from wb1 → wb3, but the slower sharp turns cost ~0.14 s/lap vs m14b-w8-end (6.338 / 6.270), and the gap to the leader (5.61) is pure pace (~0.7 s). So we'd like your two simulators on the **speed** bet tonight:

**Model 17 (k-means actions, from scratch)**: `experiments/model17-cluster/` (reward = Model 14b's, 12 actions from clustering the expert's commands, top 4 m/s; details in its README). Suggested run, no DR:

```
DR=False CLEAN_RUNS=1 SNAP_MIN=30 bash tools/track_rotation.sh model17-cluster m17-jason none best   reInvent2019_wide+reinvent_base:wb1:60:0.0003 reInvent2019_wide+reinvent_base:wb2:60:0.0003 ... (lr 0.0003 for ~4 h, then 0.0001) until morning
```

Snapshots every 30 min; we upload the best after midnight (5 uploads on Oct 7). Test them on A to Z (5 trials) as you've been doing; pace on A to Z has tracked the portal best for us.

**Elyas's machine** keeps going with **E3 (Model 16, free racing: lap-time reward, no imitation, from m14b-w8-end)**: 18:15 A to Z test of its snapshots vs m14b-w8-end (one upload left today), then E3 continues overnight (A to Z / re:Invent 2018, 30-min legs, until ~08:30).
