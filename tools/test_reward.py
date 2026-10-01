"""Offline checks for a reward function that contains an `expert_action(params)`.

1. Drive a simple kinematic car on real DeepRacer tracks using only the expert's
   commands: does the expert itself finish laps (on tracks it was never tuned for)?
2. Compare rewards: expert actions vs. random actions vs. mirrored steering.

Usage:
    python tools/test_reward.py experiments/model02-imitation/reward_function.py
"""
from __future__ import annotations

import importlib.util
import math
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
TRACKS = ["Vegas_track", "reinvent_base", "reInvent2019_track", "2022_summit_speedway",
          "Spain_track", "Oval_track", "2022_reinvent_champ_ccw", "jyllandsringen_pro_cw",
          "arctic_pro_cw", "2024_reinvent_champ_cw"]
DT, WHEELBASE, CAR_HALF_WIDTH = 1 / 15, 0.165, 0.10


def load_module(path: str):
    spec = importlib.util.spec_from_file_location("rf", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Track:
    def __init__(self, name: str):
        w = np.load(ROOT / "tracks" / f"{name}.npy")
        if np.allclose(w[0, :2], w[-1, :2]):
            w = w[:-1]
        self.center = w[:, 0:2]
        self.width = float(np.median(np.linalg.norm(w[:, 4:6] - w[:, 2:4], axis=1)))
        seg = np.linalg.norm(np.diff(np.vstack([self.center, self.center[:1]]), axis=0), axis=1)
        self.cum = np.concatenate([[0], np.cumsum(seg)])
        self.length = self.cum[-1]
        self.waypoints = [tuple(p) for p in self.center]

    def locate(self, x, y):
        """closest_waypoints [prev, next], distance from centre, arc-length position."""
        p = np.array([x, y])
        n = len(self.center)
        best = (1e9, 0, 0.0)
        for i in range(n):
            a, b = self.center[i], self.center[(i + 1) % n]
            ab = b - a
            t = float(np.clip(np.dot(p - a, ab) / max(np.dot(ab, ab), 1e-9), 0, 1))
            d = float(np.linalg.norm(p - (a + t * ab)))
            if d < best[0]:
                best = (d, i, t)
        d, i, t = best
        s = self.cum[i] + t * (self.cum[i + 1] - self.cum[i])
        return [i, (i + 1) % n], d, s


def make_params(track, x, y, heading, steer, speed, steps, progress, closest, dfc):
    on = dfc + CAR_HALF_WIDTH <= track.width / 2
    return {"x": x, "y": y, "heading": heading, "steering_angle": steer, "speed": speed,
            "waypoints": track.waypoints, "closest_waypoints": closest, "track_width": track.width,
            "distance_from_center": dfc, "all_wheels_on_track": on, "is_offtrack": not on,
            "is_reversed": False, "steps": steps, "progress": progress, "track_length": track.length}


def drive_expert(mod, track: Track, max_laps_time=120.0):
    x, y = track.center[0]
    d = track.center[1] - track.center[0]
    heading = math.degrees(math.atan2(d[1], d[0]))
    s_prev, travelled, steps, rewards = 0.0, 0.0, 0, []
    speed_now, lat_acc = 0.0, []
    while steps * DT < max_laps_time:
        closest, dfc, s = track.locate(x, y)
        ds = s - s_prev
        if ds < -track.length / 2:
            ds += track.length
        travelled += ds
        s_prev = s
        progress = 100 * travelled / track.length
        p = make_params(track, x, y, heading, 0.0, speed_now, steps, progress, closest, dfc)
        extra = {"rewards": rewards, "max_lat_acc": max(lat_acc, default=0.0)}
        if not p["all_wheels_on_track"]:
            return {"result": "OFF TRACK", "progress": progress, "time": steps * DT, **extra}
        if progress >= 100:
            return {"result": "lap", "progress": 100.0, "time": steps * DT, **extra}
        steer, speed = mod.expert_action(p)
        p["steering_angle"], p["speed"] = steer, speed
        rewards.append(mod.reward_function(p))
        yaw_rate = speed / WHEELBASE * math.tan(math.radians(steer))  # rad/s
        lat_acc.append(abs(speed * yaw_rate))                           # m/s^2 the tyres must hold
        speed_now = speed
        heading += math.degrees(yaw_rate * DT)
        x += speed * math.cos(math.radians(heading)) * DT
        y += speed * math.sin(math.radians(heading)) * DT
        steps += 1
    return {"result": "timeout", "progress": progress, "time": steps * DT, "rewards": rewards,
            "max_lat_acc": max(lat_acc, default=0.0)}


def reward_contrast(mod, track: Track, samples=300, seed=0):
    """Mean reward for expert vs random vs mirrored-steering actions at on-track states."""
    rnd = random.Random(seed)
    out = {"expert": [], "random": [], "mirrored": []}
    n = len(track.center)
    for _ in range(samples):
        i = rnd.randrange(n)
        a, b = track.center[i], track.center[(i + 1) % n]
        if np.linalg.norm(b - a) < 1e-6:
            continue
        heading = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) + rnd.uniform(-15, 15)
        nrm = np.array([-(b - a)[1], (b - a)[0]]) / np.linalg.norm(b - a)
        x, y = a + nrm * rnd.uniform(-0.2, 0.2) * track.width
        closest, dfc, _ = track.locate(x, y)
        base = make_params(track, x, y, heading, 0, 0, 50, 15.0, closest, dfc)
        if not base["all_wheels_on_track"]:
            continue
        es, ev = mod.expert_action(base)
        for key, (st, sp) in {"expert": (es, ev), "random": (rnd.uniform(-30, 30), rnd.uniform(0.5, 1.0)),
                              "mirrored": (-es, ev)}.items():
            out[key].append(mod.reward_function(dict(base, steering_angle=st, speed=sp)))
    return {k: float(np.mean(v)) for k, v in out.items()}


def main():
    mod = load_module(sys.argv[1])
    print(f"{'track':28} {'len m':>6} {'width':>5}  expert drive               max lat.acc  reward: expert / random / mirrored")
    for name in TRACKS:
        if not (ROOT / "tracks" / f"{name}.npy").exists():
            continue
        t = Track(name)
        r = drive_expert(mod, t)
        c = reward_contrast(mod, t)
        drive = f"{r['result']:9} {r['progress']:5.1f}% in {r['time']:5.1f}s"
        print(f"{name:28} {t.length:6.1f} {t.width:5.2f}  {drive:26} {r['max_lat_acc']:5.1f} m/s2  "
              f"{c['expert']:.2f} / {c['random']:.2f} / {c['mirrored']:.2f}")


if __name__ == "__main__":
    main()
