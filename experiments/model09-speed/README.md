# Model 09: speed push

**Why:** Model 08 vegas2-2147 scored **10.824** on the portal (best lap 10.225) and lost only ~0.6 s to off-tracks, so speed is now the limit (leader: 5.6 s). Overnight at lr 0.0001, Model 08 kept getting *more reliable but ~1 s/lap slower* on every track. Cause: every step on track earned ~4 reward, so a slow lap collected more in total than a fast one; the speed-scaled lap bonus (~85) was too small to compensate, and the −20 off-track penalty pushed toward caution.

**Changes vs Model 08** (same 15 discrete actions, so it fine-tunes):
1. **Distance reward:** 15 × (% of the lap covered this step). Proportional to speed per step; a whole lap is worth the same however long it takes. Replaces the small average-pace term.
2. **Lap bonus** 300 × (average lap speed / 2 m/s)² (was 100 × speed/2): 334 at 2.1 m/s vs 188 at 1.6 m/s.
3. **Off-track penalty −5** (was −20).

Unchanged: expert imitation (racing line, braking-aware speed profile, grip limit), smoothness, edge safety.

| | |
|---|---|
| Starts from | `cedc-m08-vegas2-2147` (portal 10.824) |
| Tracks | 2024_reinvent_champ_cw and 2022_summit_speedway only (the secret track's stand-ins), alternating, both directions |
| Schedule | champ1 60 → summit1 60 → champ2 60 (lr 0.0003) → summit2 60 → champ3 60 (lr 0.0001), 02:11 → ~07:15 |
| Snapshots | every 30 min (`cedc-m09-<leg>-HHMM`) and at each leg's end |

**What to check:** lap times on the stand-ins should drop below Model 08's (~15 s on both) without the completion rate collapsing. Upload the best snapshot; the portal score − best lap shows the off-track cost.

## Results

(pending)
