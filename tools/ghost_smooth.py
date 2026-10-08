"""tools/ghost_race.py with cleaned traces: same arguments, smoother video.

The simulator's position log sometimes stalls and then jumps (samples implying 8-13 m/s for a car
with a 4 m/s top speed), which ghost_race.py draws as teleports. This drops samples faster than
MAX_SPEED, re-spaces the samples evenly in time (their timestamps jitter), lightly smooths each path
(3-point average) and renders at 30 fps. No torch needed.

Usage: python3 tools/ghost_smooth.py <track> <out.mp4> "<label>=<eval dir>[:trial]" ...
"""
import sys
import types
from pathlib import Path

import numpy as np

for name in ["torch", "torch.utils", "torch.utils.tensorboard"]:   # tb_export imports torch; not needed here
    sys.modules.setdefault(name, types.ModuleType(name))
sys.modules["torch.utils.tensorboard"].SummaryWriter = object
sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib  # noqa: E402

try:
    import imageio_ffmpeg  # bundled ffmpeg when the system has none
    matplotlib.rcParams["animation.ffmpeg_path"] = imageio_ffmpeg.get_ffmpeg_exe()
except ImportError:
    pass

import ghost_race as g  # noqa: E402

MAX_SPEED = 5.0   # m/s between two samples; faster = logging glitch


def retime(t, xy):
    """Time the replay by distance travelled. The log's timestamps jitter and the simulator sometimes skips
    control steps, so raw (or evenly spaced) times make the car speed up, slow down and jump. Instead: take the
    speed between samples, smooth it (moving average over ~0.5 s), and give each segment the time its length
    needs at that smoothed speed; then rescale so each stretch keeps its real duration. Real pauses
    (> 0.5 s, e.g. an off-track reset) are kept."""
    t = np.asarray(t, float); xy = np.asarray(xy, float)
    out = t.copy()
    breaks = [0] + [i for i in range(1, len(t)) if t[i] - t[i - 1] > 0.5] + [len(t)]
    for a_, b_ in zip(breaks[:-1], breaks[1:]):
        if b_ - a_ < 3:
            continue
        ts, ps = t[a_:b_], xy[a_:b_]
        ds = np.linalg.norm(np.diff(ps, axis=0), axis=1)
        dt = np.maximum(np.diff(ts), 1e-3)
        v = np.clip(ds / dt, 0.3, MAX_SPEED)
        k = 7
        vs = np.convolve(np.pad(v, (k // 2, k // 2), mode="edge"), np.ones(k) / k, mode="valid")
        seg_t = ds / np.maximum(vs, 0.3)
        new = np.concatenate([[0.0], np.cumsum(seg_t)])
        if new[-1] > 0:
            new *= (ts[-1] - ts[0]) / new[-1]
        out[a_:b_] = ts[0] + new
    return out, xy


def drop_stale(t, xy):
    """Some logged positions are stale (the car appears slightly behind where it already was), which shows as a
    back-and-forth jerk. Drop any sample where the path reverses (consecutive moves point > 100 deg apart)."""
    t = np.asarray(t, float); xy = np.asarray(xy, float)
    keep = list(range(len(t)))
    changed = True
    while changed and len(keep) > 3:
        changed = False
        for j in range(1, len(keep) - 1):
            a_, b_, c_ = xy[keep[j - 1]], xy[keep[j]], xy[keep[j + 1]]
            u, w = b_ - a_, c_ - b_
            nu, nw = np.linalg.norm(u), np.linalg.norm(w)
            if t[keep[j + 1]] - t[keep[j - 1]] > 0.5:      # don't touch real pauses (off-track resets)
                continue
            if nu > 1e-6 and nw > 1e-6 and np.dot(u, w) / (nu * nw) < -0.17:
                del keep[j]; changed = True; break
    return t[keep], xy[keep]


def clean(t, xy):
    t, xy = drop_stale(t, xy)
    t, xy = retime(t, xy)
    keep = [0]
    for i in range(1, len(t)):
        dt = t[i] - t[keep[-1]]
        if dt <= 0:
            continue
        if np.linalg.norm(xy[i] - xy[keep[-1]]) / dt > MAX_SPEED and i < len(t) - 1:
            continue
        keep.append(i)
    t, xy = t[keep], xy[keep]
    # resample onto an even 1/30 s grid first, then smooth (smoothing by sample index on unevenly spaced
    # samples shifted points and created new jumps)
    grid = np.arange(t[0], t[-1], 1 / 30)
    if t[-1] - grid[-1] > 1 / 60:
        grid = np.append(grid, t[-1])
    else:
        grid[-1] = t[-1]                  # avoid a near-zero last step (a fake speed spike)
    gx = np.interp(grid, t, xy[:, 0]); gy = np.interp(grid, t, xy[:, 1])
    g_xy = np.stack([gx, gy], axis=1)
    sm = g_xy.copy()
    sm[1:-1] = (g_xy[:-2] + g_xy[1:-1] + g_xy[2:]) / 3
    return grid, sm


_load_lap = g.load_lap


def load_lap(*args, **kwargs):
    t, xy, off, done, n, trial = _load_lap(*args, **kwargs)
    t, xy = clean(np.asarray(t), np.asarray(xy))
    return t, xy, off, done, n, trial


g.load_lap = load_lap
g.FPS = 30

if __name__ == "__main__":
    g.main()
