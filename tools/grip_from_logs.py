"""Estimate the simulator's physical limits from recorded training laps.

From consecutive SIM_TRACE steps (x, y, yaw, sim time) we get the car's *actual* motion:
  speed        v = distance / dt
  lateral acc  a_lat = v * yaw_rate          (the grip the tyres had to provide)
  longitudinal a_long = dv / dt              (acceleration / braking)
and compare the commanded speed with the speed actually reached.

Steps from completed laps show what the car can hold; the last steps before an off-track show
where it lost it.

Usage: python tools/grip_from_logs.py cedc-m03-speed cedc-m03b-bothdir cedc-m04-fast
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tb_export import LOGS, parse_trace  # noqa: E402

SMOOTH = 3  # steps on each side used for finite differences (reduces sensor/step noise)


def episode_kinematics(ep: list[dict]):
    x = np.array([s["x"] for s in ep]); y = np.array([s["y"] for s in ep])
    t = np.array([s["t"] for s in ep])
    yaw = np.unwrap(np.radians([s.get("yaw", 0.0) for s in ep]))
    cmd = np.array([s["speed"] for s in ep])
    k = SMOOTH
    if len(ep) < 2 * k + 3:
        return None
    dt = t[2 * k:] - t[:-2 * k]
    ok = dt > 1e-3
    dist = np.hypot(x[2 * k:] - x[:-2 * k], y[2 * k:] - y[:-2 * k])
    v = np.where(ok, dist / np.where(ok, dt, 1), np.nan)
    yaw_rate = np.where(ok, (yaw[2 * k:] - yaw[:-2 * k]) / np.where(ok, dt, 1), np.nan)
    a_lat = np.abs(v * yaw_rate)
    a_long = np.full_like(v, np.nan)
    a_long[1:-1] = (v[2:] - v[:-2]) / np.maximum(t[k + 2:len(t) - k] - t[k:len(t) - k - 2], 1e-3)
    return v, a_lat, a_long, cmd[k:len(cmd) - k]


def main() -> None:
    bases = sys.argv[1:]
    runs = [d for b in bases for d in sorted(LOGS.glob(f"{b}*")) if d.is_dir()]
    lap_v, lap_lat, lap_long, lap_cmd, crash_lat, crash_v = [], [], [], [], [], []
    n_laps = n_off = 0
    for d in runs:
        for ep in parse_trace(d).values():
            if not ep:
                continue
            kin = episode_kinematics(ep)
            if kin is None:
                continue
            v, a_lat, a_long, cmd = kin
            status = ep[-1]["status"]
            if status == "lap_complete":
                n_laps += 1
                lap_v.append(v); lap_lat.append(a_lat); lap_long.append(a_long); lap_cmd.append(cmd)
            elif status == "off_track":
                n_off += 1
                crash_lat.append(np.nanmax(a_lat[-6:])); crash_v.append(np.nanmax(v[-6:]))
    cat = lambda xs: np.concatenate(xs) if xs else np.array([])
    v, lat, lon, cmd = cat(lap_v), cat(lap_lat), cat(lap_long), cat(lap_cmd)
    pct = lambda a, q: np.nanpercentile(a, q) if a.size else float("nan")
    print(f"runs: {', '.join(d.name for d in runs)}")
    print(f"completed laps: {n_laps}, off-track episodes: {n_off}")
    print(f"\nactual speed in completed laps: median {pct(v,50):.2f}, p95 {pct(v,95):.2f}, max {pct(v,99.9):.2f} m/s")
    print(f"commanded speed:               median {pct(cmd,50):.2f}, p95 {pct(cmd,95):.2f} m/s  "
          f"-> actual/commanded (median) {np.nanmedian(v / np.maximum(cmd, 1e-3)):.2f}")
    print(f"\nlateral acceleration held in completed laps (grip used):")
    for q in (50, 90, 95, 99, 99.9):
        print(f"   p{q:<5} {pct(lat, q):5.2f} m/s^2")
    print(f"longitudinal: accel p99 {pct(lon, 99):.2f} m/s^2, braking p1 {pct(lon, 1):.2f} m/s^2")
    if crash_lat:
        cl = np.array(crash_lat)
        print(f"\npeak lateral acc in the last steps before an off-track: median {np.nanmedian(cl):.2f}, "
              f"p25 {np.nanpercentile(cl,25):.2f}, p75 {np.nanpercentile(cl,75):.2f} m/s^2 "
              f"(speed there: median {np.nanmedian(crash_v):.2f} m/s)")


if __name__ == "__main__":
    main()
