import math

# Model 04: fast. Model 03's expert (speed profile + grip limit), trained in both
# directions like 03b, but with a higher speed floor/ceiling (1.3-3.0 m/s) and a lap
# bonus that grows with lap speed, because 03b learned to drive too cautiously.

MIN_SPEED, MAX_SPEED = 1.3, 3.0   # must match the action space
MAX_STEER = 30.0
STEER_TOLERANCE_DEG = 10.0
MAX_LAT_ACC = 4.0                 # m/s^2 the expert allows in a turn (tyre grip budget)
MAX_BRAKE = 3.0                   # m/s^2 the expert assumes it can slow down at
PLAN_AHEAD_M = 4.0                # how far ahead the speed profile looks
WHEELBASE = 0.165                 # m, DeepRacer (approx.)


def _lookahead_m(speed):
    return 0.45 + 0.15 * speed     # pure-pursuit target: 0.6 m at 1 m/s, 0.83 m at 2.5 m/s


def _dist(a, b):
    return math.hypot(b[0] - a[0], b[1] - a[1])


def _angle_diff(a, b):
    """Smallest signed difference a - b in degrees, in [-180, 180)."""
    return (a - b + 180.0) % 360.0 - 180.0


def _point_ahead(waypoints, start_idx, start_pos, distance):
    """Walk along the waypoints from start_pos until `distance` metres are covered."""
    n = len(waypoints)
    pos, idx, left = start_pos, start_idx, distance
    for _ in range(n):
        nxt = waypoints[idx % n]
        d = _dist(pos, nxt)
        if d >= left:
            t = left / d if d > 0 else 0.0
            return (pos[0] + t * (nxt[0] - pos[0]), pos[1] + t * (nxt[1] - pos[1]))
        left -= d
        pos, idx = nxt, idx + 1
    return waypoints[start_idx % n]


def _radius(a, b, c):
    """Radius (m) of the circle through three points; inf on a straight."""
    ab, bc, ca = _dist(a, b), _dist(b, c), _dist(c, a)
    cross = abs((b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0]))
    return float("inf") if cross < 1e-9 else ab * bc * ca / (2.0 * cross)


def _speed_limit_ahead(waypoints, start_idx, car):
    """Fastest speed now that still lets the car slow down for every curve within PLAN_AHEAD_M.

    Each point ahead at distance d with centre-line radius R allows v_corner = sqrt(MAX_LAT_ACC * R);
    to arrive there at v_corner the car may be going at most sqrt(v_corner^2 + 2 * MAX_BRAKE * d) now.
    """
    n = len(waypoints)
    limit, travelled, prev, i = MAX_SPEED, 0.0, car, start_idx
    for _ in range(n):
        p = waypoints[i % n]
        travelled += _dist(prev, p)
        if travelled > PLAN_AHEAD_M:
            break
        # use neighbours ~2 waypoints away so the radius isn't dominated by waypoint noise
        r = _radius(waypoints[(i - 2) % n], p, waypoints[(i + 2) % n])
        if r != float("inf"):
            v_corner = math.sqrt(MAX_LAT_ACC * r)
            limit = min(limit, math.sqrt(v_corner ** 2 + 2.0 * MAX_BRAKE * travelled))
        prev, i = p, i + 1
    return limit


def expert_action(params):
    """Return (steering_deg, speed_mps) the expert would choose in this state."""
    waypoints = params["waypoints"]
    car = (params["x"], params["y"])
    next_idx = params["closest_waypoints"][1]
    speed_now = max(MIN_SPEED, params["speed"])

    target = _point_ahead(waypoints, next_idx, car, _lookahead_m(speed_now))
    bearing = math.degrees(math.atan2(target[1] - car[1], target[0] - car[0]))
    steer = max(-MAX_STEER, min(MAX_STEER, _angle_diff(bearing, params["heading"])))

    # speed profile: fast on straights, slow enough to make every curve ahead
    speed = _speed_limit_ahead(waypoints, next_idx, car)

    # grip limit: turning radius R = wheelbase / tan(steer); lateral acc = v^2 / R <= MAX_LAT_ACC
    tan_s = math.tan(math.radians(abs(steer)))
    if tan_s > 1e-3:
        speed = min(speed, math.sqrt(MAX_LAT_ACC * WHEELBASE / tan_s))
    speed = max(MIN_SPEED, speed)
    return steer, speed


def reward_function(params):
    # note: params["is_reversed"] means "driving the track clockwise", not "wrong way", so don't use it here
    if not params["all_wheels_on_track"] or params["is_offtrack"]:
        return 1e-3

    expert_steer, expert_speed = expert_action(params)

    steer_error = abs(params["steering_angle"] - expert_steer)
    steer_score = math.exp(-(steer_error / STEER_TOLERANCE_DEG) ** 2)

    speed_error = abs(params["speed"] - expert_speed)
    speed_score = max(0.0, 1.0 - speed_error / (MAX_SPEED - MIN_SPEED))

    reward = 1.0 + 2.0 * steer_score + 1.0 * speed_score

    # stay away from the edges: the expert can't save a car that is about to leave
    if params["distance_from_center"] > 0.4 * params["track_width"]:
        reward *= 0.5

    # pace: progress per step, relative to ~1 m/s on a 22 m track at 15 steps/s.
    # Model 02 capped this at 1.5 (= 1.5 m/s); now it pays up to ~3 m/s and weighs more.
    if params["steps"] > 0:
        pace = (params["progress"] / params["steps"]) / 0.3
        reward += 1.0 * min(pace, 3.0)

    if params["progress"] >= 100:
        # faster laps pay more: 1.0 at an average of 2 m/s (15 steps/s), 1.5 at 3 m/s
        avg_speed = params["track_length"] * 15.0 / max(params["steps"], 1)
        reward += 100.0 * avg_speed / 2.0

    return float(reward)
