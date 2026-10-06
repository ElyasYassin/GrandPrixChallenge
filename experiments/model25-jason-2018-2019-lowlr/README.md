# Model J25 (jason): J23 bw8-end, re:Invent 2019 focus, half the learning rate

**Why:** J23 bw8-end is the best model in local tests (re:Invent 2018 1 off / 7.37 s, 2019 wide 1 off / 7.09 s in 5 trials each). J24 continued it at lr 0.0001 and peaked after ~1.5 h, then declined (eval of its peak: 9 off-tracks in 10 trials). Jason chose: continue from J23 bw8 with a lower learning rate (0.00005) to refine rather than drift.

**Tracks (Jason 09:15: "focus on 2019"): reInvent2019_wide (16.6 m) + reInvent2019_track (23.1 m) on the two simulators**, Model 10 reward + actions, no DR, alternating direction. 6 × 40-min legs, snapshots every 30 min; snapshots evaluated (5 trials, both tracks) at the end.

## Results

**1-hour test (10:25, 5 trials, DR off; `logs/m25_test.txt`):**

| Model | reInvent2019_wide off / mean | reInvent2019_track off / mean |
|---|---|---|
| J23 bw8-end (start) | **0 / 7.26 s** | 8 / 12.30 s |
| J25 wt2-1023 (lr 0.00005, 1 h) | 1 / 7.80 s | **5 / 10.82 s** |

Mixed (better on the regular 2019 track it now trains on, slightly worse on 2019 wide) → as agreed with Jason: continue from wt2-1023 at **lr 0.0001** (`m25c-jason-*`, 10:35 →), test again after an hour.

**2-hour test (11:46, after 1 h at lr 0.0001; `logs/m25_test2.txt`):** `m25c wt4-1145` reInvent2019_wide **0 off / 6.77 s** (6.47–7.07 s, 5 clean laps), reInvent2019_track **3 off / 10.59 s** — better than J23 bw8-end on both (0 / 7.26, 8 / 12.30). Packaged: `submissions/m25c-jason-wt4-1145-ckpt651.tar.gz`. Continued from it at lr 0.0001 (`m25d-jason-*`, 11:55 →).
