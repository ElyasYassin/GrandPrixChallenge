# Model 18: stack E3 + J29 + A to Z

**Why (2026-10-07 03:00):** the three things that worked, together. E3's free-racing reward (portal 6.197, #57), Jason's J29 faster corners (A to Z test: wb7-end 1 off / 5.93 s mean, clean laps 5.56-5.82), A to Z only (the layout closest to the secret track).

**Recipe:** `experiments/model16-freeracing` reward with MIN_SPEED 2.8 / MAX_LAT_ACC 10.5; actions = `experiments/model29-jason-fastcorners` (same 15 in the same order, so it fine-tunes from the E3 line); reInvent2019_wide only, no DR, lr 0.0001, 30-min legs; from `cedc-m16z-z5-end`.

A to Z E3 checkpoint before the switch (5 trials): z5-end 1 off, clean 5.73/6.21/6.34/7.57; z8-end 2 off in one trial, clean 6.00/6.01/6.53/7.19 (w3-end: 1 off, clean 6.00/6.21/6.40/7.90) → plateaued, no clear gain.

## Results

(pending)
