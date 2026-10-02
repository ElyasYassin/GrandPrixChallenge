"""Ghost race: replay several models' evaluation laps on one track at the same time (top-down MP4).

Each car is one logged evaluation trial (default: the trial with the median lap time, so it's a
typical lap, not a lucky one), played back in real time from SIM_TRACE_LOG timestamps. Off-track
resets show as a red x where the car left the track; the penalty time is in the playback.

Training laps: "<label>=<training robomaker log>#<fwd|rev>[:n][@HH:MM]" uses the median of the last n (default 8)
completed laps in that direction (fwd = the track's waypoint order, like evaluations). Training
episodes start anywhere on the track, so each lap is re-phased to start at the start/finish line.
Training actions are sampled (exploration), so these laps are a bit noisier than evaluation laps.

Usage:
  python tools/ghost_race.py <track> <out.mp4> "<label>=<eval dir>[:trial]" ...
  e.g. python tools/ghost_race.py Vegas_track videos/vegas.mp4 "M02=evals/m02-best-Vegas_track" "M05=evals/m05-m05-snap2-Vegas_track"
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.animation import FFMpegWriter  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tb_export import _parse_trace_file, load_track  # noqa: E402

FPS, TRAIL_S, SPEEDUP = 20, 1.5, 1.0
COLORS = ["#e6194b", "#3cb44b", "#4363d8", "#f58231", "#911eb4", "#42d4f4", "#f032e6", "#9a6324"]


def load_lap(eval_dir: str, trial: int | None):
    eps = [e for _, e in sorted(_parse_trace_file(Path(eval_dir) / "robomaker.log").items()) if len(e) > 5]
    durs = [e[-1]["t"] - e[0]["t"] for e in eps]
    if trial is None:
        trial = int(np.argsort(durs)[len(durs) // 2])
    e = eps[trial]
    t = np.array([s["t"] for s in e]) - e[0]["t"]
    xy = np.array([[s["x"], s["y"]] for s in e])
    off = [(t[i], xy[i]) for i, s in enumerate(e) if s["status"] == "off_track"]
    done = e[-1]["status"] == "lap_complete"
    return t, xy, off, done, len(eps), trial


def _turn(e) -> float:
    yaw = np.unwrap(np.radians([s["yaw"] for s in e]))
    return yaw[-1] - yaw[0]


def load_training_lap(log: str, direction: str, n: int, center: np.ndarray, fwd_sign: float, before: float | None = None):
    """Median of the last n completed laps driven in `direction`, re-phased to start at waypoint 0."""
    eps = [e for _, e in sorted(_parse_trace_file(Path(log)).items())]
    laps = [[s for s in e if s["status"] != "prepare"] for e in eps if e[-1]["status"] == "lap_complete"
            and (before is None or e[-1]["t"] <= before)]
    want = fwd_sign if direction == "fwd" else -fwd_sign
    laps = [e for e in laps if np.sign(_turn(e)) == np.sign(want)][-n:]
    if not laps:
        raise SystemExit(f"no completed {direction} laps in {log}")
    e = sorted(laps, key=lambda e: e[-1]["t"] - e[0]["t"])[len(laps) // 2]
    t = np.array([s["t"] for s in e]) - e[0]["t"]
    xy = np.array([[s["x"], s["y"]] for s in e])
    k = int(np.argmin(((xy - center[0]) ** 2).sum(1)))           # closest point to the start line
    dt = np.diff(t, append=t[-1] + np.median(np.diff(t)))
    xy = np.vstack([xy[k:], xy[:k]])
    t = np.concatenate([[0.0], np.cumsum(np.concatenate([dt[k:], dt[:k]]))[:-1]])
    return t, xy, [], True, len(laps)


def main() -> None:
    track_name, out = sys.argv[1], Path(sys.argv[2])
    cars = []
    center = load_track(track_name)[0]
    fwd_sign = np.sign(_turn([{"yaw": float(np.degrees(np.arctan2(*(np.roll(center, -1, 0) - center)[i][::-1])))}
                              for i in range(len(center))]))
    for k, spec in enumerate(sys.argv[3:]):
        label, rest = spec.split("=", 1)
        if "#" in rest:
            log, _, sel = rest.partition("#")
            sel, _, cutoff = sel.partition("@")            # optional @HH:MM: only laps finished before then (today)
            direction, _, n = sel.partition(":")
            before = None
            if cutoff:
                import datetime as _dt
                h, m = map(int, cutoff.split(":"))
                day = _dt.datetime.fromtimestamp(Path(log).stat().st_mtime).replace(hour=h, minute=m, second=0)
                before = day.timestamp()
            t, xy, off, done, cnt = load_training_lap(log, direction, int(n or 8), center, fwd_sign, before)
            print(f"{label}: training lap ({direction}, median of last {cnt}), {t[-1]:.2f}s")
        else:
            d, _, tr = rest.partition(":")
            t, xy, off, done, cnt, trial = load_lap(d, int(tr) if tr else None)
            print(f"{label}: trial {trial + 1}/{cnt}, {t[-1]:.2f}s, {len(off)} off-track")
        cars.append(dict(label=label, t=t, xy=xy, off=off, done=done, color=COLORS[k % len(COLORS)]))
    t_end = max(c["t"][-1] for c in cars) + 1.5
    width = max(len(c["label"]) for c in cars)

    fig, ax = plt.subplots(figsize=(11, 7.2), dpi=100)
    fig.patch.set_facecolor("#1d1f24")
    ax.set_facecolor("#1d1f24")
    center, inner, outer = load_track(track_name)
    ax.fill(*outer.T, color="#3a3d44")
    ax.fill(*inner.T, color="#1d1f24")
    for b in (inner, outer):
        ax.plot(*b.T, color="#d8d8d8", lw=1.2)
    ax.plot(*center.T, color="#777", lw=0.6, ls=(0, (4, 4)))
    ax.plot([inner[0, 0], outer[0, 0]], [inner[0, 1], outer[0, 1]], color="white", lw=3)  # start/finish
    ax.set_aspect("equal")
    ax.axis("off")
    title = fig.text(0.015, 0.955, "", color="white", fontsize=13)
    for c in cars:
        c["trail"], = ax.plot([], [], color=c["color"], lw=2.5, alpha=0.7)
        c["dot"], = ax.plot([], [], "o", color=c["color"], ms=10, mec="white", mew=1.2)
        c["xs"] = ax.scatter([], [], marker="X", color=c["color"], edgecolors="#ff3b3b", s=110, linewidths=1.2, zorder=5)
    board = [fig.text(0.725, 0.90 - 0.045 * i, "", color=c["color"], fontsize=11, family="monospace",
                      fontweight="bold") for i, c in enumerate(cars)]
    fig.subplots_adjust(left=0.01, right=0.72, top=0.93, bottom=0.01)

    def pos(c, tau):
        tau = min(tau, c["t"][-1])
        return np.array([np.interp(tau, c["t"], c["xy"][:, 0]), np.interp(tau, c["t"], c["xy"][:, 1])])

    out.parent.mkdir(parents=True, exist_ok=True)
    writer = FFMpegWriter(fps=FPS, bitrate=2400)
    with writer.saving(fig, str(out), dpi=100):
        for frame in range(int(t_end * FPS / SPEEDUP) + 1):
            tau = frame * SPEEDUP / FPS
            title.set_text(f"{track_name}   t = {tau:5.1f} s")
            for c, txt in zip(cars, board):
                p = pos(c, tau)
                c["dot"].set_data([p[0]], [p[1]])
                m = (c["t"] >= tau - TRAIL_S) & (c["t"] <= tau)
                c["trail"].set_data(c["xy"][m, 0], c["xy"][m, 1])
                offs = [xy for t, xy in c["off"] if t <= tau]
                c["xs"].set_offsets(np.array(offs) if offs else np.empty((0, 2)))
                finished = tau >= c["t"][-1]
                state = (f"{c['t'][-1]:5.2f}s" + ("" if c["done"] else " DNF")) if finished else f"{tau:5.1f}s"
                txt.set_text(f"{c['label']:<{width}} {state}  off {len(offs)}")
            writer.grab_frame(facecolor=fig.get_facecolor())
    print("wrote", out)


if __name__ == "__main__":
    main()
