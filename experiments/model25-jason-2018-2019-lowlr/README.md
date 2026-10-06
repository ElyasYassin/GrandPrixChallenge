# Model J25 (jason): J23 bw8-end, re:Invent 2019 focus, half the learning rate

**Why:** J23 bw8-end is the best model in local tests (re:Invent 2018 1 off / 7.37 s, 2019 wide 1 off / 7.09 s in 5 trials each). J24 continued it at lr 0.0001 and peaked after ~1.5 h, then declined (eval of its peak: 9 off-tracks in 10 trials). Jason chose: continue from J23 bw8 with a lower learning rate (0.00005) to refine rather than drift.

**Tracks (Jason 09:15: "focus on 2019"): reInvent2019_wide (16.6 m) + reInvent2019_track (23.1 m) on the two simulators**, Model 10 reward + actions, no DR, alternating direction. 6 × 40-min legs, snapshots every 30 min; snapshots evaluated (5 trials, both tracks) at the end.

## Results

(pending)
