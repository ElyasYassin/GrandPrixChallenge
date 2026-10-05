import math

# Model 13: everything we learned, from scratch, so the wiggle never becomes a habit.
# Model 11/11b/11c could not train the wiggle out of the 7.130 model's line (wheels straight on ~2% of
# straight steps after 7 h of fixes). This model starts from random weights with:
#  - Model 12's limits: grip 9 m/s^2, top speed 5 m/s (expert ~8-13% faster than the 7.130 line)
#  - Model 11c's pure-pursuit expert with the measured car geometry (calmer steering)
#  - straight-line braking (straight at 2.5), and only "straight" reaches 5.0 m/s
#  - Model 11b's straight bonus and steering-flip penalty
#  - trained on the short tracks + re:Invent 2024 from the start (what produced the 7.130 model)
#
# Model 11c: a calmer expert. Replaying Model 11b's laps showed the expert asked for a median of 30 deg
# (full lock) on straights and said "straight" only 7% of the time: it set steering = heading error to
# the target point, which over-steers ~2x for this car. Now it uses pure pursuit with the measured
# geometry: steer = atan(2 * WHEELBASE * sin(alpha) / distance). Closed-loop check (measured car,
# 5 deg noise): same lap times, steering flips about halved, full lock 15-19% -> 3-10%.
# Keeps Model 11b's straight bonus and flip penalty.
#
# Model 11b: make "straight" actually pay. After 1.5 h, Model 11 still had its wheels straight on only
# 1-2% of straight-section steps (3-4 left/right flips per second) and braked while turning 99% of
# the time: the imitation reward scores 6 deg about as well as 0 deg when the expert asks for a small
# correction. Changes vs Model 11 (same actions):
#  1. STRAIGHT_BONUS when the expert's steering is small and the car's wheels are straight.
#  2. FLIP_PENALTY when the steering changes side (left <-> right) between consecutive steps.
#  3. Trained at lr 0.0003 for the first phases so the habit can change.
#
# Model 11: brake in a straight line, stop wiggling. Model 10's best snapshot (portal 7.130) still
# wiggled: on straights the wheels were off-centre on 98% of steps with ~3-4 left/right flips per
# second, and 100% of its braking happened while steering >= 12 deg. Cause: its action set had no
# slow straight action (slowest straight was 3.0 m/s), and "6 deg at 4.0" was as fast as "straight at
# 4.0". Changes vs Model 10 (same 15 actions, so it fine-tunes from the 7.130 model):
#  1. Actions: straight 3.0 -> 2.0 and straight 3.5 -> 3.0 (straight-line braking), 6 deg at 4.0 -> 3.5
#     (only straight reaches 4.0).
#  2. Smoothness bonus weight 0.5 -> 1.0.
#
# Model 10: the real car. A grip test (tools/grip_sweep.sh: fixed steering + speed circles) showed the
# simulated car turns about twice as wide as our expert assumed (radius ~0.34 m / tan(steer), not
# 0.165 m / tan(steer)) and holds at least 8 m/s^2 sideways without sliding (we assumed 5). The expert
# therefore capped corner speed far too low (~1.2 m/s at full lock; the car holds 2.0-2.4).
# Changes vs Model 09: effective wheelbase 0.34 m, grip budget 7 m/s^2, and faster speeds on the same
# 15 steering actions (same order, so it fine-tunes from Model 09).
#
# Model 09: speed push (fine-tuned from Model 08 vegas2-2147, portal 10.824 with only 0.6 s lost to
# off-tracks: speed is now the limit). Model 08 got slower overnight because every step on track
# earned ~4 reward, so a slow lap collected more in total than a fast one. Changes vs Model 08:
#  1. Distance reward: PROGRESS_WEIGHT per % of lap covered in this step (replaces the small
#     average-pace term). Per step it is proportional to speed, so within the discount horizon
#     covering more track pays more; a whole lap is worth the same however long it takes.
#  2. Lap bonus grows with the square of the lap's average speed (was linear and small).
#  3. Off-track penalty -5 (Model 07/08: -20), so the car is less timid near the limit.
#
# Model 07: reliable. Model 06 had our fastest portal best lap (14.51 s) but lost ~9 s to off-tracks
# (score 23.554). Changes vs Model 06: a large penalty when the car leaves the track (instead of ~0)
# and an edge-safety factor that scales the reward down as the wheels approach an edge.
#
# Model 06: faster. Model 05 (our best, portal 17.877) hit the same best lap as Model 04 on the
# secret track (14.71 s), so top speed looks like the limit. Changes vs Model 05: speed range
# 1.3-4.0 m/s (was 1.3-3.0), expert grip budget 5 m/s^2 (was 4; we measured >= 5-6 in the
# simulator), pace reward capped at ~4 m/s (was ~3). Trained with learning rate 0.0001.
#
# Model 05: racing line + smooth steering. Model 04's expert (speed profile + grip limit,
# both directions, 1.3-3.0 m/s, speed-scaled lap bonus), plus two racing-driver principles:
#  1. Racing line: instead of the centre line, the expert follows a minimum-curvature line
#     (outside -> apex -> outside), computed from the current track's waypoints and cached.
#     Wider curves allow more speed at the same grip.
#  2. Smooth hands: a small bonus for small steering changes between steps.
# Everything is derived from params at runtime, so it works on any track (no hard-coded positions).

MIN_SPEED, MAX_SPEED = 2.5, 5.0   # must match the action space (slowest: 2.5, fastest: straight at 5.0)
MAX_STEER = 30.0
STEER_TOLERANCE_DEG = 10.0
MAX_LAT_ACC = 9.0                 # m/s^2 the expert allows in a turn (grip test: >= 8.4 without sliding; Model 05-09: 5.0)
MAX_BRAKE = 3.0                   # m/s^2 the expert assumes it can slow down at
PLAN_AHEAD_M = 4.0                # how far ahead the speed profile looks
WHEELBASE = 0.34                  # m, effective: measured turn radius ~0.34 / tan(steer) (nominal 0.165)

LINE_MARGIN_M = 0.30              # racing line stays this far inside each edge (0.22 went off 6 of 10 test tracks)
LINE_ITERATIONS = 2000            # curvature-averaging passes when building the racing line
SMOOTH_STEER_DEG = 15.0           # steering change per step that earns no smoothness bonus
STRAIGHT_EXPERT_DEG = 5.0         # expert steering below this counts as "go straight"
STRAIGHT_BONUS = 1.0              # reward for straight wheels when the expert says straight
FLIP_PENALTY = 0.5                # penalty for steering left <-> right between consecutive steps
SMOOTH_WEIGHT = 1.0                 # Model 05-10: 0.5
OFFTRACK_PENALTY = -5.0           # reward on the step the car leaves the track (Model 07/08: -20)
PROGRESS_WEIGHT = 15.0            # reward per % of the lap covered in one step (~0.3 %/step at 1.5 m/s on 25 m)
LAP_BONUS = 300.0                 # times (average lap speed / 2 m/s)^2
SAFE_EDGE_M = 0.25                # full reward while the car centre is >= this far from an edge
MIN_EDGE_M = 0.10                 # car half-width: at this distance a wheel touches the edge

_line_cache = {}                  # track signature -> racing line points
_last = {"steps": None, "steer": None}
_prog = {"steps": None, "progress": 0.0}
_flip = {"steps": None, "steer": None}


def _lookahead_m(speed):
    return 0.45 + 0.15 * speed     # pure-pursuit target: 0.6 m at 1 m/s, 0.83 m at 2.5 m/s


def _dist(a, b):
    return math.hypot(b[0] - a[0], b[1] - a[1])


def _angle_diff(a, b):
    """Smallest signed difference a - b in degrees, in [-180, 180)."""
    return (a - b + 180.0) % 360.0 - 180.0


def _signed_curvature(a, b, c):
    """Signed curvature (1/m) of the circle through a, b, c: positive = turning left."""
    ab, bc, ca = _dist(a, b), _dist(b, c), _dist(c, a)
    if ab * bc * ca < 1e-12:
        return 0.0
    cross = (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])
    return 2.0 * cross / (ab * bc * ca)


def racing_line(waypoints, track_width):
    """Racing line in the spirit of the K1999 algorithm: repeatedly move each point sideways so
    its curvature becomes the average of its neighbours' curvatures. That spreads every turn over
    a longer arc (outside -> apex -> outside) without shrinking the whole loop, then each point is
    clamped to stay LINE_MARGIN_M inside the edges. Point i stays paired with centre-line waypoint
    i (it only moves along i's normal), so closest_waypoints indexes both."""
    # drop a duplicated closing point, if any
    pts_in = [(float(p[0]), float(p[1])) for p in waypoints]
    n = len(pts_in)
    key = (n, round(pts_in[0][0], 3), round(pts_in[0][1], 3),
           round(pts_in[1][0], 3), round(pts_in[1][1], 3), round(track_width, 3))
    if key in _line_cache:
        return _line_cache[key]
    center = pts_in
    normals = []  # unit LEFT normal at each centre-line point
    for i in range(n):
        a, b = center[(i - 1) % n], center[(i + 1) % n]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1.0
        normals.append((-dy / L, dx / L))
    max_off = max(0.0, track_width / 2.0 - LINE_MARGIN_M)
    off = [0.0] * n  # signed lateral offset along the left normal
    for _ in range(LINE_ITERATIONS):
        pts = [(center[i][0] + off[i] * normals[i][0], center[i][1] + off[i] * normals[i][1]) for i in range(n)]
        k = [_signed_curvature(pts[(i - 1) % n], pts[i], pts[(i + 1) % n]) for i in range(n)]
        for i in range(n):
            target = 0.5 * (k[(i - 1) % n] + k[(i + 1) % n])
            chord = _dist(pts[(i - 1) % n], pts[(i + 1) % n])
            # moving a point by delta toward its left changes its curvature by about -8*delta/chord^2
            delta = (k[i] - target) * chord * chord / 8.0
            off[i] = max(-max_off, min(max_off, off[i] + 0.5 * delta))
    line = [(center[i][0] + off[i] * normals[i][0], center[i][1] + off[i] * normals[i][1]) for i in range(n)]
    _line_cache[key] = line
    return line


def _point_ahead(path, start_idx, start_pos, distance):
    """Walk along the path from start_pos until `distance` metres are covered."""
    n = len(path)
    pos, idx, left = start_pos, start_idx, distance
    for _ in range(n):
        nxt = path[idx % n]
        d = _dist(pos, nxt)
        if d >= left:
            t = left / d if d > 0 else 0.0
            return (pos[0] + t * (nxt[0] - pos[0]), pos[1] + t * (nxt[1] - pos[1]))
        left -= d
        pos, idx = nxt, idx + 1
    return path[start_idx % n]


def _radius(a, b, c):
    """Radius (m) of the circle through three points; inf on a straight."""
    ab, bc, ca = _dist(a, b), _dist(b, c), _dist(c, a)
    cross = abs((b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0]))
    return float("inf") if cross < 1e-9 else ab * bc * ca / (2.0 * cross)


def _speed_limit_ahead(path, start_idx, car):
    """Fastest speed now that still lets the car slow down for every curve of the path within
    PLAN_AHEAD_M: a point at distance d with radius R allows v_corner = sqrt(MAX_LAT_ACC * R),
    so the car may be going at most sqrt(v_corner^2 + 2 * MAX_BRAKE * d) now."""
    n = len(path)
    limit, travelled, prev, i = MAX_SPEED, 0.0, car, start_idx
    for _ in range(n):
        p = path[i % n]
        travelled += _dist(prev, p)
        if travelled > PLAN_AHEAD_M:
            break
        r = _radius(path[(i - 2) % n], p, path[(i + 2) % n])
        if r != float("inf"):
            v_corner = math.sqrt(MAX_LAT_ACC * r)
            limit = min(limit, math.sqrt(v_corner ** 2 + 2.0 * MAX_BRAKE * travelled))
        prev, i = p, i + 1
    return limit


def expert_action(params):
    """Return (steering_deg, speed_mps) the expert would choose in this state."""
    line = racing_line(params["waypoints"], params["track_width"])
    car = (params["x"], params["y"])
    next_idx = params["closest_waypoints"][1]
    speed_now = max(MIN_SPEED, params["speed"])

    # pure pursuit: the arc through the target point needs curvature 2 sin(alpha) / distance;
    # the car's steering angle for curvature k is atan(WHEELBASE * k)
    target = _point_ahead(line, next_idx, car, _lookahead_m(speed_now))
    bearing = math.degrees(math.atan2(target[1] - car[1], target[0] - car[0]))
    alpha = math.radians(_angle_diff(bearing, params["heading"]))
    distance = max(_dist(car, target), 0.05)
    steer = math.degrees(math.atan(2.0 * WHEELBASE * math.sin(alpha) / distance))
    steer = max(-MAX_STEER, min(MAX_STEER, steer))

    # speed profile on the racing line's (wider) curves
    speed = _speed_limit_ahead(line, next_idx, car)

    # grip limit: turning radius R = wheelbase / tan(steer); lateral acc = v^2 / R <= MAX_LAT_ACC
    tan_s = math.tan(math.radians(abs(steer)))
    if tan_s > 1e-3:
        speed = min(speed, math.sqrt(MAX_LAT_ACC * WHEELBASE / tan_s))
    speed = max(MIN_SPEED, speed)
    return steer, speed


def _smoothness(params):
    """1.0 for no steering change since the previous step, 0 at SMOOTH_STEER_DEG or more.
    Remembers the previous step's steering (reset when a new episode starts)."""
    steps, steer = params["steps"], params["steering_angle"]
    prev_steps, prev_steer = _last["steps"], _last["steer"]
    _last["steps"], _last["steer"] = steps, steer
    if prev_steps is None or steps != prev_steps + 1:   # first step of an episode (or a gap)
        return 0.0
    return max(0.0, 1.0 - abs(steer - prev_steer) / SMOOTH_STEER_DEG)


def _progress_delta(params):
    """% of the lap covered since the previous step (0 on an episode's first step or after a gap)."""
    steps, progress = params["steps"], params["progress"]
    prev_steps, prev_progress = _prog["steps"], _prog["progress"]
    _prog["steps"], _prog["progress"] = steps, progress
    if prev_steps is None or steps != prev_steps + 1:
        return 0.0
    return max(0.0, min(2.0, progress - prev_progress))   # clip: resets/glitches never pay


def _flipped(params):
    """True when the steering changed side (left <-> right) since the previous step."""
    steps, steer = params["steps"], params["steering_angle"]
    prev_steps, prev_steer = _flip["steps"], _flip["steer"]
    _flip["steps"], _flip["steer"] = steps, steer
    if prev_steps is None or steps != prev_steps + 1:
        return False
    return steer * prev_steer < 0


def reward_function(params):
    smooth = _smoothness(params)
    flipped = _flipped(params)     # update the steering memory on every step, even off track
    # note: params["is_reversed"] means "driving the track clockwise", not "wrong way", so don't use it here
    if params["is_offtrack"]:
        return OFFTRACK_PENALTY
    if not params["all_wheels_on_track"]:
        return 1e-3

    expert_steer, expert_speed = expert_action(params)

    steer_error = abs(params["steering_angle"] - expert_steer)
    steer_score = math.exp(-(steer_error / STEER_TOLERANCE_DEG) ** 2)

    speed_error = abs(params["speed"] - expert_speed)
    speed_score = max(0.0, 1.0 - speed_error / (MAX_SPEED - MIN_SPEED))

    reward = 1.0 + 2.0 * steer_score + 1.0 * speed_score + SMOOTH_WEIGHT * smooth
    if abs(expert_steer) < STRAIGHT_EXPERT_DEG and params["steering_angle"] == 0:
        reward += STRAIGHT_BONUS
    if flipped:
        reward -= FLIP_PENALTY

    # edge safety: scale the reward down as the car gets close to an edge (1 at >= SAFE_EDGE_M, 0 at MIN_EDGE_M)
    edge = params["track_width"] / 2.0 - params["distance_from_center"]
    reward *= max(0.0, min(1.0, (edge - MIN_EDGE_M) / (SAFE_EDGE_M - MIN_EDGE_M)))

    # distance covered this step (progress is % of the lap since the episode started)
    reward += PROGRESS_WEIGHT * _progress_delta(params)

    if params["progress"] >= 100:
        # faster laps pay much more: 300 at an average of 2 m/s (15 steps/s), 675 at 3 m/s
        avg_speed = params["track_length"] * 15.0 / max(params["steps"], 1)
        reward += LAP_BONUS * (avg_speed / 2.0) ** 2

    return float(reward)
