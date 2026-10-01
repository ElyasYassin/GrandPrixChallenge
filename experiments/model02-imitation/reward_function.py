import math

# Model 02: imitation through the reward.
# Each step we compute what a simple track-agnostic "expert" would do
# (pure pursuit on the centre line + slow down before curves) and reward
# the car for choosing a similar steering angle and speed.

LOOKAHEAD_M = 0.8        # pure-pursuit target distance ahead
CURVE_WINDOW_M = 1.5     # how far ahead to look for curves when choosing speed
MIN_SPEED, MAX_SPEED = 0.5, 1.0   # must match the action space
MAX_STEER = 30.0
STEER_TOLERANCE_DEG = 10.0


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
            return (pos[0] + t * (nxt[0] - pos[0]), pos[1] + t * (nxt[1] - pos[1])), idx % n
        left -= d
        pos, idx = nxt, idx + 1
    return waypoints[start_idx % n], start_idx % n


def _max_turn_ahead(waypoints, start_idx, window_m):
    """Largest heading change (deg) of the centre line over the next window_m metres."""
    n = len(waypoints)
    headings, travelled, i = [], 0.0, start_idx
    while travelled < window_m and len(headings) < n:
        a, b = waypoints[i % n], waypoints[(i + 1) % n]
        i += 1
        d = _dist(a, b)
        if d < 1e-6:  # some tracks repeat a waypoint; a zero-length segment has no heading
            if i - start_idx > n:
                break
            continue
        headings.append(math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])))
        travelled += d
    if len(headings) < 2:
        return 0.0
    return max(abs(_angle_diff(h, headings[0])) for h in headings)


def expert_action(params):
    """Return (steering_deg, speed_mps) the expert would choose in this state."""
    waypoints = params["waypoints"]
    car = (params["x"], params["y"])
    next_idx = params["closest_waypoints"][1]

    target, _ = _point_ahead(waypoints, next_idx, car, LOOKAHEAD_M)
    bearing = math.degrees(math.atan2(target[1] - car[1], target[0] - car[0]))
    steer = max(-MAX_STEER, min(MAX_STEER, _angle_diff(bearing, params["heading"])))

    turn = _max_turn_ahead(waypoints, next_idx, CURVE_WINDOW_M)
    # 0-10 deg of turn ahead = straight (full speed), 60+ deg = sharp corner (min speed)
    t = max(0.0, min(1.0, (turn - 10.0) / 50.0))
    speed = MAX_SPEED - t * (MAX_SPEED - MIN_SPEED)
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

    # pace: progress per step, relative to ~1 m/s on a 22 m track at 15 steps/s
    if params["steps"] > 0:
        pace = (params["progress"] / params["steps"]) / 0.3
        reward += 0.5 * min(pace, 1.5)

    if params["progress"] >= 100:
        reward += 50.0

    return float(reward)
