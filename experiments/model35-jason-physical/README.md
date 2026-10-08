# Model J35 (jason): physical-race candidate from wb7 (carpet floor, random lighting)

**Why (Jason, 2026-10-07 ~22:30):** physical race on Oct 8; "start from wb7, two tracks, the floor is carpet for sure, random lighting".

**Recipe:** start `cedc-m29b-jason-wb7-end` (portal **5.814 / 5.805 clean**); J29's reward + actions unchanged (wb7's own). Two simulators: **reinvent_carpet** (re:Invent 2018 layout on carpet, closest to the real floor) + **reInvent2019_wide** (plain, keeps wb7's driving). **Domain randomization on** (lighting/colours) while training; evaluations without. lr 0.0001 for 2 h (texture adaptation: lower rates did not learn floors in J18), then 0.00005. 30-min legs, snapshots each leg, overnight.

**Judge:** reinvent_carpet off-tracks first (5 trials), reinvent_concrete as a held-out floor, reInvent2019_wide to make sure the virtual skill stays. Baseline: wb7-end on the same tests (below).

## Results

Baseline wb7-end (5 trials, DR off): reinvent_carpet **16 off / 5 laps**, mean 11.10 s; reinvent_concrete 29 off, mean 14.0 s.

**Test 1 (00:00, after ~1.5 h at lr 0.0001; `logs/m35_test1.txt`):** ca3-end carpet 12 off / 9.08 s, A to Z 3/5 clean; **ca4-end carpet 11 off / 8.89 s, A to Z 4/5 clean (mean 6.06)**. Continuing at lr 0.00005 (`m35d-jason-*`).

**Test 2 (02:15, lr 0.00005 since 00:09; `logs/m35_test2.txt`):** ca6-end carpet 8 off / 8.42 s (concrete 50 off — an outlier run), **ca8-end carpet 8 off / 8.40 s (first clean carpet laps), A to Z 3/5 clean / 6.14 s, concrete (held out) 15 off / 10.20 s** (wb7: 29 / 14.0). Packaged `submissions/m35d-jason-ca8-end` as the current physical candidate.

**Test 3 (04:30; `logs/m35_test3.txt`):** **ca10-end carpet 7 off / 8.92 s, A to Z 5/5 clean / 6.06 s, concrete 16 off / 10.06 s** → physical pick (packaged). ca12-end carpet 11 / 9.62, **A to Z 5/5 clean / 5.66 s** (best A to Z result we have), concrete 24 / 13.71 → packaged as a possible portal probe (caveat: local A to Z misled us for J34 / Model 21, but J35 trains on two tracks with DR).

**Test 4 (07:00; `logs/m35_test4.txt`):** ca14-end carpet 8 off / 8.61 s, A to Z 4/5, concrete 15 / 10.35; ca16-end carpet 7 / **8.14 s** (fastest on carpet), A to Z 4/5, concrete 21 / 12.28. Carpet off-tracks have levelled off at ~7–8 per 5 laps since ca8.

**Summary for race day (2026-10-08 07:05):**

| Snapshot | carpet off / mean | concrete (held out) | A to Z clean / mean |
|---|---|---|---|
| wb7-end (start) | 16 / 11.10 | 29 / 14.0 | — |
| ca8-end | 8 / 8.40 | 15 / 10.20 | 3/5 / 6.14 |
| **ca10-end (pick)** | **7 / 8.92** | 16 / 10.06 | **5/5 / 6.06** |
| ca12-end | 11 / 9.62 | 24 / 13.71 | 5/5 / 5.66 |
| ca14-end | 8 / 8.61 | 15 / 10.35 | 4/5 / 5.95 |
| ca16-end | 7 / **8.14** | 21 / 12.28 | 4/5 / 6.30 |

Pick **ca10-end** (`submissions/m35e-jason-ca10-end-ckpt851.tar.gz`): half wb7's carpet off-tracks, held-out concrete roughly halved too, still 5/5 clean on A to Z. Alternative: ca16-end (fastest on carpet, less steady elsewhere). On the real car, start slow (Elyas: ~60–70 % speed) and raise it if it stays on track.
