# Model J35 (jason): physical-race candidate from wb7 (carpet floor, random lighting)

**Why (Jason, 2026-10-07 ~22:30):** physical race on Oct 8; "start from wb7, two tracks, the floor is carpet for sure, random lighting".

**Recipe:** start `cedc-m29b-jason-wb7-end` (portal **5.814 / 5.805 clean**); J29's reward + actions unchanged (wb7's own). Two simulators: **reinvent_carpet** (re:Invent 2018 layout on carpet, closest to the real floor) + **reInvent2019_wide** (plain, keeps wb7's driving). **Domain randomization on** (lighting/colours) while training; evaluations without. lr 0.0001 for 2 h (texture adaptation: lower rates did not learn floors in J18), then 0.00005. 30-min legs, snapshots each leg, overnight.

**Judge:** reinvent_carpet off-tracks first (5 trials), reinvent_concrete as a held-out floor, reInvent2019_wide to make sure the virtual skill stays. Baseline: wb7-end on the same tests (below).

## Results

Baseline wb7-end (5 trials, DR off): reinvent_carpet **16 off / 5 laps**, mean 11.10 s; reinvent_concrete 29 off, mean 14.0 s.

**Test 1 (00:00, after ~1.5 h at lr 0.0001; `logs/m35_test1.txt`):** ca3-end carpet 12 off / 9.08 s, A to Z 3/5 clean; **ca4-end carpet 11 off / 8.89 s, A to Z 4/5 clean (mean 6.06)**. Continuing at lr 0.00005 (`m35d-jason-*`).

**Test 2 (02:15, lr 0.00005 since 00:09; `logs/m35_test2.txt`):** ca6-end carpet 8 off / 8.42 s (concrete 50 off — an outlier run), **ca8-end carpet 8 off / 8.40 s (first clean carpet laps), A to Z 3/5 clean / 6.14 s, concrete (held out) 15 off / 10.20 s** (wb7: 29 / 14.0). Packaged `submissions/m35d-jason-ca8-end` as the current physical candidate.
