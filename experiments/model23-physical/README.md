# Model 23: physical-race candidate (Oct 8)

**Why:** the physical race rewards robustness (real lighting, floor textures, camera noise), not portal pace. Plan from Oct 6 (teacher-student / sim-to-real idea): best reliable virtual model + domain randomization + textured floors, low lr.

**Recipe:** J29 reward + actions unchanged (`experiments/model29-jason-fastcorners`, portal-proven), from **wb7-end** (portal 5.814 clean), **DR on** (lighting / colours), two simulators: `reinvent_carpet+reinvent_wood` alternating with `reInvent2019_wide+reinvent_base`, lr 0.00005, 60-min legs. **`reinvent_concrete` held out** as the unseen-floor test (10 trials, DR off), every ~2 h, vs wb7-end and wb16-mid-corners baselines (`logs/m23_check.txt`).

On race day: start the car at ~60-70 % speed, raise it if clean.

## Results

(pending)
