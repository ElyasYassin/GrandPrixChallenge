# Model 17: k-means action set, from scratch

**Why:** the community "capstone" approach derives the action space by clustering the optimal line's (steering, speed) pairs; the physical-track paper (arXiv 2406.03769) found smaller action spaces do better on real cars. Clustering our expert's commands on the likely hidden layout (A to Z + re:Invent 2018, both directions, measured car, 4 m/s cap; 1,266 commands) gives a smooth curve: the optimal line never uses full lock or slow speeds (steering within ±24°, speed 2.6–4.0).

**Actions (12):** k-means k=9 → (0°, 4.0), (±8°, 3.95), (±12°, 3.5), (±17°, 3.1), (±23°, 2.7); plus two safety actions for an imperfect car: **(0°, 3.0)** straight-line brake and **(±30°, 2.4)** full-lock recovery.

Closed-loop expert (measured car, 5° noise): A to Z 4.82 s (15-action 14b set: 4.78), re:Invent 2018 5.47 s (5.13; 0.3 off-tracks/lap).

**Reward:** Model 14b's (imitation of the pure-pursuit expert on the racing line, braking-aware speeds, grip 9, top 4 m/s, straight bonus / flip penalty, speed-scaled off-track penalty). **From scratch** (new action count): A to Z 60 min, then 30-min phases alternating re:Invent 2018 / A to Z; lr 0.0003 until ~02:30, then 0.0001; **moved to Jason's machine (two simulators) on 2026-10-06 17:30**; Elyas's machine continues E3. Also the base for tomorrow's physical candidate (DR + textured floors, teacher-student idea from "Sim-To-Real Transfer for Miniature Autonomous Car Racing").

## Results

(pending)
