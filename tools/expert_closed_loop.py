"""How does a reward's expert behave when the car only imitates it imperfectly?

The real policy is not the expert: it reacts a step late and its steering is off by ~12 deg (measured
on evaluation logs). The expert then sees a car that is off the line / pointing the wrong way and asks
for a correction. A twitchy expert turns those corrections into full-lock zig-zags and (through a
steering-based speed cap) low speed; the policy learns exactly that. This drives a kinematic car with
the expert's command delayed by DELAY steps plus Gaussian noise and reports what the expert asked for.

Usage: python tools/expert_closed_loop.py <reward_function.py> [variant] [tracks...]
  variant: m07 (as is) | look (longer lookahead) | nocap (no steering-based speed cap) | both
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_reward import DT, WHEELBASE, Track, load_module, make_params  # noqa: E402

import os
DELAY, SPEED_NOISE, SEEDS = int(os.environ.get("DELAY", 1)), 0.25, 3
STEER_NOISE = float(os.environ.get("STEER_NOISE", 10.0))
TRACKS = ["Vegas_track", "2022_summit_speedway", "2024_reinvent_champ_cw", "reInvent2019_track", "reinvent_base"]


def apply_variant(mod, variant: str):
    if variant in ("look", "both"):
        mod._lookahead_m = lambda speed: 0.8 + 0.2 * speed
    if variant in ("nocap", "both"):
        def expert_action(params, mod=mod):
            line = mod.racing_line(params["waypoints"], params["track_width"])
            car = (params["x"], params["y"])
            nxt = params["closest_waypoints"][1]
            target = mod._point_ahead(line, nxt, car, mod._lookahead_m(max(mod.MIN_SPEED, params["speed"])))
            bearing = math.degrees(math.atan2(target[1] - car[1], target[0] - car[0]))
            steer = max(-mod.MAX_STEER, min(mod.MAX_STEER, mod._angle_diff(bearing, params["heading"])))
            # speed from the racing line's curves ahead only, not from the corrective steering angle
            return steer, max(mod.MIN_SPEED, mod._speed_limit_ahead(line, nxt, car))
        mod.expert_action = expert_action


def drive(mod, track: Track, seed: int, max_time=90.0):
    rng = np.random.default_rng(seed)
    x, y = track.center[0]
    d = track.center[1] - track.center[0]
    heading = math.degrees(math.atan2(d[1], d[0]))
    s_prev, travelled, steps, speed_now = 0.0, 0.0, 0, 0.0
    queue, cmds, acts, offs = [], [], [], 0
    while steps * DT < max_time:
        closest, dfc, s = track.locate(x, y)
        ds = s - s_prev
        if ds < -track.length / 2:
            ds += track.length
        travelled += ds
        s_prev = s
        progress = 100 * travelled / track.length
        p = make_params(track, x, y, heading, 0.0, speed_now, steps, progress, closest, dfc)
        if not p["all_wheels_on_track"]:
            offs += 1  # put the car back on the centre line (like the simulator's reset)
            i = closest[1]
            x, y = track.center[i]
            d = track.center[(i + 1) % len(track.center)] - track.center[i]
            heading = math.degrees(math.atan2(d[1], d[0]))
            queue.clear()
            steps += 15  # ~1 s penalty
            continue
        if progress >= 100:
            break
        steer_e, speed_e = mod.expert_action(p)
        cmds.append((steer_e, speed_e))
        queue.append((steer_e, speed_e))
        steer, speed = queue.pop(0) if len(queue) > DELAY else (0.0, mod.MIN_SPEED)
        steer = float(np.clip(steer + rng.normal(0, STEER_NOISE), -mod.MAX_STEER, mod.MAX_STEER))
        speed = float(np.clip(speed + rng.normal(0, SPEED_NOISE), mod.MIN_SPEED, mod.MAX_SPEED))
        acts.append(steer)
        speed_now = speed
        yaw_rate = speed / WHEELBASE * math.tan(math.radians(steer))
        heading += math.degrees(yaw_rate * DT)
        x += speed * math.cos(math.radians(heading)) * DT
        y += speed * math.sin(math.radians(heading)) * DT
        steps += 1
    c = np.array(cmds)
    sg = np.sign(c[np.abs(c[:, 0]) > 3, 0])
    return dict(time=steps * DT, done=progress >= 100, offs=offs, lock=np.mean(np.abs(c[:, 0]) >= 29.9),
                minv=np.mean(c[:, 1] <= mod.MIN_SPEED + 0.01), v=c[:, 1].mean(),
                flips=(np.diff(sg) != 0).sum() / (len(c) * DT))


def main():
    path = sys.argv[1]
    variant = sys.argv[2] if len(sys.argv) > 2 else "m07"
    tracks = sys.argv[3:] or TRACKS
    mod = load_module(path)
    apply_variant(mod, variant)
    print(f"variant {variant}: delay {DELAY} step, steering noise {STEER_NOISE} deg, {SEEDS} seeds")
    print(f"{'track':26} {'lap s':>6} {'offs':>5} {'full lock':>9} {'v=min':>6} {'v mean':>6} {'flips/s':>7}")
    for name in tracks:
        rs = [drive(mod, Track(name), s) for s in range(SEEDS)]
        m = lambda k: np.mean([r[k] for r in rs])  # noqa: E731
        print(f"{name:26} {m('time'):6.1f} {m('offs'):5.1f} {m('lock'):9.0%} {m('minv'):6.0%} {m('v'):6.2f} {m('flips'):7.2f}")


if __name__ == "__main__":
    main()
