# Model 14: the generalist

**Why:** the secret track is unknown/probably custom, and no local track predicts portal off-tracks (proxy study so far: the reInvent2019_wide variants predict *backwards*, AUC 0.25–0.42). Our best portal result (7.130) came from our most varied training (6 tracks). Jason's domain randomization + textured floors cut held-out off-tracks 27 → 4. Each portal off-track costs ~9.5 s in a trial (~3.2 s on the score), so general reliability is worth more than a few tenths of pace.

**Recipe:** Model 13c's reward (Model 13 + speed-scaled off-track penalty) and Model 13's 15 actions, starting from `m13-w4-end` (portal best lap 6.333).
- **10 training tracks**, 20-min phases, 3 cycles (~10 h): 2024_reinvent_champ_cw, reInvent2019_wide, reinvent_base, Vegas, 2022_summit_speedway, Bowtie, reInvent2019_track, reinvent_carpet, reinvent_wood, 2022_reinvent_champ_ccw (alternating direction).
- **Domain randomization on** for training (lighting/colours); always off for evaluations (`tools/wsl/evalrun.sh` forces it).
- lr 0.0001. `CLEAN_RUNS=1`: each phase continues from its `-end` snapshot and its ~280 MB run prefix is deleted (disk).
- **Held out for judging** (never trained on): Oval_track, Mexico_track, New_York_Track, Canada_Training, reinvent_concrete. Snapshots are ranked by their average over these, not by one track.

Run: `DR=True CLEAN_RUNS=1 SNAP_MIN=60 bash tools/track_rotation.sh model14-general m14 cedc-m13-w4-end last <30 legs>` (2026-10-05 17:06 → ~03:30).

## Results

(pending)
