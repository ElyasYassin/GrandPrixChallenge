# Model J30 (jason): E3 reward + J29 corner speeds, A to Z only, from J29 wb16-end

Elyas's suggested stack for Jason's machine (team/STATUS 2026-10-06 19:25 and 2026-10-07 02:55): J29's best snapshot + the E3 free-racing reward (portal 6.197), A to Z only. Reward + actions = `experiments/model18-e3-fastcorners` (E3 reward with MIN_SPEED 2.8 / MAX_LAT_ACC 10.5, J29's 15 actions). Start: `cedc-m29d-jason-wb16-end` (A to Z 5 trials: 1 off / 5.85 s mean, clean 5.01 / 5.29 / 5.75 / 6.07). **Both simulators on reInvent2019_wide**, no DR, lr 0.0001, 30-min legs, snapshots each leg; tested on A to Z (5 trials) before the ~15:00 upload round. Elyas's Model 18 runs the same stack from the E3 line on his machine.

## Results

**Stopped 09:55.** A to Z tests (5 trials): zz2-end 3 off / 6.44 s (clean 5.61, 5.88), zz4-end 4 off / 6.92 s — worse than its start wb16-end (1 off / 5.85). Replaced by J31 (J29 settle, low lr).
