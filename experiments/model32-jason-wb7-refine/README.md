# Model J32 (jason): refine J29 wb7-end (portal 5.814, clean)

**Why (Jason, 2026-10-07):** wb7-end scored **5.814 / 5.805, clean (#68)**: new team best, 0.20 s behind the leader (5.610). wb16-end was faster at its best (5.664) but went off on the portal (9.044). So keep wb7's reliability and look for a little pace: J29's reward + actions, two simulators A to Z + re:Invent 2018 (as wb7 was trained), **lr 0.00005**, 30-min legs, every leg tested on A to Z (5 trials, 0 off-tracks first, then mean < wb7's 5.93 s locally). Replaces J31 (wb16 settle, 35 min).

## Results

**Test 1 (11:10, A to Z 5 trials, DR off; `logs/m32_test1.txt`):** rf1-end 7 off / 7.74 s, rf2-end 5 off / 6.94 s (best 5.21) vs **wb7-end re-tested 2 off / 6.31 s** (yesterday 1 off / 5.93; portal clean 5.814). The first hour of continued training disturbed wb7 even at lr 0.00005. Continued one more hour (`m32b-jason-*`); stop if not at least as clean as wb7 by ~12:15. Note: a 5-trial local test of the same model varies (wb7: 1 vs 2 off), so the portal remains the judge.
