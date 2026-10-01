import math

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

MIN_SPEED, MAX_SPEED = 1.3, 4.0   # must match the action space (Model 05: 1.3, 3.0); a 1.5 floor demanded up to 7 m/s^2 on tight tracks
MAX_STEER = 30.0
STEER_TOLERANCE_DEG = 10.0
MAX_LAT_ACC = 5.0                 # m/s^2 the expert allows in a turn (Model 05: 4.0; measured >= 5-6)
MAX_BRAKE = 3.0                   # m/s^2 the expert assumes it can slow down at
PLAN_AHEAD_M = 4.0                # how far ahead the speed profile looks
WHEELBASE = 0.165                 # m, DeepRacer (approx.)

LINE_MARGIN_M = 0.30              # racing line stays this far inside each edge (0.22 went off 6 of 10 test tracks)
LINE_ITERATIONS = 2000            # curvature-averaging passes when building the racing line
SMOOTH_STEER_DEG = 15.0           # steering change per step that earns no smoothness bonus
SMOOTH_WEIGHT = 0.5
OFFTRACK_PENALTY = -20.0          # reward on the step the car leaves the track (Model 06: 0.001)
SAFE_EDGE_M = 0.25                # full reward while the car centre is >= this far from an edge
MIN_EDGE_M = 0.10                 # car half-width: at this distance a wheel touches the edge

_line_cache = {}                  # track signature -> racing line points
_last = {"steps": None, "steer": None}


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

    target = _point_ahead(line, next_idx, car, _lookahead_m(speed_now))
    bearing = math.degrees(math.atan2(target[1] - car[1], target[0] - car[0]))
    steer = max(-MAX_STEER, min(MAX_STEER, _angle_diff(bearing, params["heading"])))

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


def reward_function(params):
    smooth = _smoothness(params)  # update the steering memory on every step, even off track
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

    # edge safety: scale the reward down as the car gets close to an edge (1 at >= SAFE_EDGE_M, 0 at MIN_EDGE_M)
    edge = params["track_width"] / 2.0 - params["distance_from_center"]
    reward *= max(0.0, min(1.0, (edge - MIN_EDGE_M) / (SAFE_EDGE_M - MIN_EDGE_M)))

    # pace: progress per step (1.0 = ~1 m/s on a 22 m track at 15 steps/s), capped at ~3 m/s
    if params["steps"] > 0:
        pace = (params["progress"] / params["steps"]) / 0.3
        reward += 1.0 * min(pace, 4.0)

    if params["progress"] >= 100:
        # faster laps pay more: 1.0 at an average of 2 m/s (15 steps/s), 1.5 at 3 m/s
        avg_speed = params["track_length"] * 15.0 / max(params["steps"], 1)
        reward += 100.0 * avg_speed / 2.0

    return float(reward)
