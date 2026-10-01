def reward_function(params):
    """Model 01 - baseline. Official CEDC starter reward, unchanged."""

    all_wheels_on_track = params["all_wheels_on_track"]
    distance_from_center = params["distance_from_center"]
    track_width = params["track_width"]

    # Very small reward for leaving the track
    if not all_wheels_on_track:
        return 0.001

    reward = 1.0

    # Reward staying reasonably close to the center
    if distance_from_center < 0.10 * track_width:
        reward += 2.0
    elif distance_from_center < 0.25 * track_width:
        reward += 1.0

    return float(reward)
