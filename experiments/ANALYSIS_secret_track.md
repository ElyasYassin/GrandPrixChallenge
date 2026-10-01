# What do our portal results say about the secret track? (2026-10-01)

Idea (team): each uploaded model is a *probe* with a known profile; its secret-track result tells us something about the track.

## Raw ratios (best clean local Vegas lap vs portal best lap)

| Model | Profile | Vegas best (local) | Secret best (portal) | Ratio |
|---|---|---|---|---|
| M02 | ≤1 m/s, very consistent (portal score 34.716 vs best 34.713, so clean laps) | 26.98 | 34.713 | **1.29** |
| M03 | ≤2.5 m/s, weak on right turns | 14.52 | 15.706 | 1.08 |
| M04 | ≤3.0 m/s, both directions | 15.64 | 14.710 | 0.94 |
| M05 | ≤3.0 m/s, racing line | 14.78 | 14.713 | 1.00 |
| M06 | ≤4.0 m/s, racing line | 14.00 | 14.510 | 1.04 |

- The near-constant-speed M02 takes 29% longer → the secret track is **~25–29 m** (Vegas 22.6 m).
- The fast models take about the same time as on Vegas despite the extra length → they average **~2 m/s** there (Vegas ~1.45) → **long straights / fast sweepers**: speed pays.

## Track matching ([tools/secret_track_inference.py](../tools/secret_track_inference.py))

For every simulator track: predicted best lap = Vegas best × LapSim(track) / LapSim(Vegas), with each probe's own limits; compared with the 5 portal best laps.

| Track | Length | Width | rms log error |
|---|---|---|---|
| 2024_reinvent_champ (cw/ccw) | 25.1 m | 0.76 m | 0.077 |
| 2022_summit_speedway | 25.2 m | 1.07 m | 0.089 |
| 2022_summit_speedway cw/ccw | 25.1 m | 1.07 m | 0.101 |
| Vegas_track | 22.6 m | 1.07 m | 0.122 |

**No track fits all probes well** (best ≈ 8% rms; none explains M02's 34.7 s together with the fast models' ~14.7 s). The track is likely custom, or the lap-time simulator under-models M02's own curve-slowing logic. The closest shapes are the two tracks already in our eval set; **weight them more** when choosing models.

## Corner direction (left/right)

M03 (one direction only, weak on tight right turns) lost **6.8 s** to penalties (score − best); M04 (trained both directions, right turns fixed) lost **3.3 s** → the secret track likely has **tight right turns** (or tight turns in general). M06 at 4 m/s lost **9.0 s** → off-track risk at speed is high there.

## Next probes (uploads are free: the leaderboard keeps the best)

Upload snapshots with deliberately different profiles (left-strong vs right-strong, very slow but clean, fast but cautious in tight turns) to pin down the track's character with more than 5 data points.
