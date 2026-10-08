# Model 23: physical-race candidate (Oct 8)

**Why:** the physical race rewards robustness (real lighting, floor textures, camera noise), not portal pace. Plan from Oct 6 (teacher-student / sim-to-real idea): best reliable virtual model + domain randomization + textured floors, low lr.

**Recipe:** J29 reward + actions unchanged (`experiments/model29-jason-fastcorners`, portal-proven), from **wb7-end** (portal 5.814 clean), **DR on** (lighting / colours), two simulators: `reinvent_carpet+reinvent_wood` alternating with `reInvent2019_wide+reinvent_base`, lr 0.00005, 60-min legs. **`reinvent_concrete` held out** as the unseen-floor test (10 trials, DR off), every ~2 h, vs wb7-end and wb16-mid-corners baselines (`logs/m23_check.txt`).

On race day: start the car at ~60-70 % speed, raise it if clean.

## Results

**Unseen concrete floor (reinvent_concrete, 10 trials, DR off; `logs/m23_check.txt`):** wb7-end 0/10 (avg 15.6 s with penalties), wb16-mid 0/10 (14.8), **p2-end 1/10 (14.0)**, p1-end 0/10 (18.6), p3-end stuck, p4-end 0/10 (24.8). Snapshots that ended on a carpet/wood leg were worse; more training made it worse, so training stopped at 07:05. 80 % speed did not help on concrete (wb7 21.4, p2 21.1): the simulated concrete is a vision problem for every model (Jason's M13 saw the same), so it is a poor proxy for a real mat.

**p2-end on plain tracks (10 trials):** A to Z 8/10 clean (median 5.67), re:Invent 2018 6/10 (median 7.05) vs wb7-end 2/5 there. **Physical pick: `submissions/m23-physical-p2-end-ckpt686.tar.gz`** (wb7-end + 2 h DR/textures); fallback wb7-end.
