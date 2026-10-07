"""tools/ghost_race.py with cleaned traces: same arguments, smoother video.

The simulator's position log sometimes stalls and then jumps (samples implying 8-13 m/s for a car
with a 4 m/s top speed), which ghost_race.py draws as teleports. This drops samples faster than
MAX_SPEED, lightly smooths each path (3-point average) and renders at 30 fps. No torch needed.

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


def clean(t, xy):
    keep = [0]
    for i in range(1, len(t)):
        dt = t[i] - t[keep[-1]]
        if dt <= 0:
            continue
        if np.linalg.norm(xy[i] - xy[keep[-1]]) / dt > MAX_SPEED and i < len(t) - 1:
            continue
        keep.append(i)
    t, xy = t[keep], xy[keep]
    s = xy.copy()
    s[1:-1] = (xy[:-2] + xy[1:-1] + xy[2:]) / 3
    return t, s


_load_lap = g.load_lap


def load_lap(*args, **kwargs):
    t, xy, off, done, n, trial = _load_lap(*args, **kwargs)
    t, xy = clean(np.asarray(t), np.asarray(xy))
    return t, xy, off, done, n, trial


g.load_lap = load_lap
g.FPS = 30

if __name__ == "__main__":
    g.main()
