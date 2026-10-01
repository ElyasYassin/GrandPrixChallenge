"""Figures for the team catch-up report (report/img/*.png)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "report" / "img"
sys.path.insert(0, str(ROOT / "tools"))
from lap_time_sim import lap_time, load_track, racing_line  # noqa: E402
from tb_export import LOGS, load_metrics, parse_trace, trajectory_figure  # noqa: E402

plt.rcParams.update({"font.family": "Segoe UI", "font.size": 10, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.dpi": 150})
C = {"blue": "#2563eb", "teal": "#0d9488", "orange": "#ea580c", "purple": "#7c3aed", "gray": "#6b7280",
     "red": "#dc2626", "green": "#16a34a", "light": "#f3f4f6", "ink": "#111827"}


def box(ax, x, y, w, h, text, fc, ec=None, fs=9, bold=False, tc="white"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                fc=fc, ec=ec or fc, lw=1.2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=tc,
            fontweight="bold" if bold else "normal", wrap=True)


def arrow(ax, x1, y1, x2, y2, text="", color="#374151", fs=8, off=(0, 0.12), style="-|>", rad=0.0):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style, mutation_scale=12, color=color,
                                 lw=1.3, connectionstyle=f"arc3,rad={rad}"))
    if text:
        ax.text((x1 + x2) / 2 + off[0], (y1 + y2) / 2 + off[1], text, ha="center", va="bottom", fontsize=fs,
                color=color)


def canvas(w, h):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, w); ax.set_ylim(0, h); ax.axis("off")
    return fig, ax


def save(fig, name):
    fig.savefig(IMG / name, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", name)


# ---------------------------------------------------------------- diagrams
def fig_system():
    fig, ax = canvas(10, 5.6)
    ax.add_patch(FancyBboxPatch((0.2, 0.2), 9.6, 5.2, boxstyle="round,pad=0.02,rounding_size=0.1", fc="#f8fafc", ec="#cbd5e1"))
    ax.text(0.45, 5.15, "Windows PC  (RTX 3090, Ryzen 5 5600X, 32 GB)", fontsize=10, fontweight="bold", color=C["ink"])
    ax.add_patch(FancyBboxPatch((0.45, 0.45), 6.4, 4.4, boxstyle="round,pad=0.02,rounding_size=0.1", fc="#eef2ff", ec="#a5b4fc"))
    ax.text(0.7, 4.55, "WSL2 Ubuntu 22.04  (16 GB, 10 threads)  ·  Docker (compose mode)", fontsize=9, color="#3730a3", fontweight="bold")
    box(ax, 0.75, 2.75, 2.7, 1.5, "Simulator  (robomaker)\nGazebo + ROS, Vegas track\ncamera rendered on GPU\n(D3D12), ~7.5 steps/s", C["blue"], fs=8.5)
    box(ax, 3.95, 2.75, 2.65, 1.5, "Trainer  (sagemaker)\nPPO on the RTX 3090\nupdates every 20 episodes\nsaves checkpoints", C["purple"], fs=8.5)
    box(ax, 0.75, 0.75, 2.7, 1.4, "MinIO  (local S3)\nmodels, checkpoints,\nmetrics, reward file", C["teal"], fs=8.5)
    box(ax, 3.95, 0.75, 2.65, 1.4, "rl_coach\nstarts / coordinates\nthe training job", C["gray"], fs=8.5)
    arrow(ax, 3.45, 3.75, 3.95, 3.75, "experience", fs=7.5)
    arrow(ax, 3.95, 3.25, 3.45, 3.25, "new policy", fs=7.5, off=(0, -0.28))
    arrow(ax, 2.1, 2.75, 2.1, 2.15, style="<|-|>")
    arrow(ax, 5.25, 2.75, 3.3, 2.15, style="-|>")
    box(ax, 7.2, 3.35, 2.4, 1.5, "supervise.sh (Git Bash)\nevery 2 min: logs,\nhealth, restarts,\nstop time", C["orange"], fs=8.5)
    box(ax, 7.2, 1.6, 2.4, 1.3, "TensorBoard :6006\ncharts, trajectories,\noff-track maps", C["green"], fs=8.5)
    box(ax, 7.2, 0.45, 2.4, 0.85, "logs/  evals/  tb/\n(project folder)", "#475569", fs=8.5)
    arrow(ax, 7.2, 4.1, 6.6, 3.9, color=C["orange"])
    ax.text(6.95, 3.62, "watch &\nrestart", fontsize=7.5, color=C["orange"], ha="center", va="top")
    arrow(ax, 8.4, 3.35, 8.4, 2.9, color=C["green"])
    arrow(ax, 8.4, 1.6, 8.4, 1.3, color="#475569")
    save(fig, "diag_system.png")


def fig_rl_loop():
    fig, ax = canvas(10, 4.2)
    ax.set_ylim(-1.0, 4.3)
    box(ax, 0.3, 1.4, 2.6, 1.5, "Camera image\n160×120 grayscale\n(observation sₜ)", C["gray"], fs=9)
    box(ax, 3.7, 1.4, 2.6, 1.5, "Policy network\n(CNN → PPO)\nagent", C["purple"], fs=10, bold=True)
    box(ax, 7.1, 2.45, 2.6, 1.15, "Action aₜ\nsteering −30…30°\nspeed 1.3…3.0 m/s", C["blue"], fs=8.5)
    box(ax, 7.1, 0.55, 2.6, 1.3, "Simulator (Gazebo)\ncar moves ~0.066 s\non the Vegas track", C["teal"], fs=8.5)
    box(ax, 3.7, 0.0, 2.6, 0.95, "Reward rₜ  (our Python)\nknows exact position", C["orange"], fs=8.5)
    arrow(ax, 2.9, 2.15, 3.7, 2.15)
    arrow(ax, 6.3, 2.5, 7.1, 3.0)
    arrow(ax, 8.4, 2.45, 8.4, 1.85)
    arrow(ax, 7.1, 0.9, 6.3, 0.5, "params", fs=7.5, off=(0, -0.05))
    arrow(ax, 7.1, 0.75, 1.6, 1.4, rad=-0.45)
    ax.text(4.0, -0.75, "next camera image", fontsize=7.5, color="#374151", ha="center")
    arrow(ax, 5.0, 0.95, 5.0, 1.4, "learn (PPO)", fs=7.5, off=(0.55, -0.1))
    ax.text(5, 4.05, "Only the camera image reaches the network; the reward (training only) sees waypoints & position.",
            ha="center", fontsize=8.5, style="italic", color=C["gray"])
    save(fig, "diag_rl_loop.png")


def fig_network():
    fig, ax = canvas(10, 2.9)
    items = [("Input\n160×120×1\ngrayscale", C["gray"], 1.2),
             ("Conv 1\n5×5, stride 2", C["blue"], 1.25), ("Conv 2\n5×5, stride 2", C["blue"], 1.25),
             ("Conv 3\n3×3", C["blue"], 1.15), ("Dense\nembedding", C["purple"], 1.2)]
    x = 0.2
    for i, (t, c, w) in enumerate(items):
        box(ax, x, 0.9, w, 1.2, t, c, fs=8.5)
        if i:
            arrow(ax, x - 0.25, 1.5, x, 1.5)
        x += w + 0.25
    box(ax, x, 1.75, 1.75, 0.85, "Policy head\nsteer, speed\n(Gaussian μ, σ)", C["orange"], fs=8)
    box(ax, x, 0.35, 1.75, 0.85, "Value head\nexpected return", C["teal"], fs=8)
    arrow(ax, x - 0.25, 1.6, x, 2.1); arrow(ax, x - 0.25, 1.4, x, 0.8)
    ax.text(5, 2.75, "DEEP_CONVOLUTIONAL_NETWORK_SHALLOW  ·  continuous action space  ·  clipped PPO (actor-critic)",
            ha="center", fontsize=8.5, color=C["gray"])
    save(fig, "diag_network.png")


def fig_curriculum():
    fig, ax = canvas(10, 3.6)
    stages = [("M01\nbaseline", "starter reward\n0 laps", C["gray"]),
              ("M02\nimitation", "expert, ≤1 m/s\nportal 34.7", C["blue"]),
              ("M03\nspeed", "≤2.5 m/s\nportal 22.5", C["blue"]),
              ("M03b\nboth dirs", "right turns fixed\nbut slower", C["purple"]),
              ("M04\nfast", "1.3–3.0 m/s\nportal 18.0", C["green"]),
              ("M05\nracing line", "smooth steering\ntraining now", C["orange"])]
    w, gap = 1.42, 0.2
    for i, (t, sub, c) in enumerate(stages):
        x = 0.15 + i * (w + gap)
        box(ax, x, 1.75, w, 1.1, t, c, fs=9.5, bold=True)
        ax.text(x + w / 2, 1.5, sub, ha="center", va="top", fontsize=8, color=C["ink"])
        if i:
            arrow(ax, x - gap, 2.3, x, 2.3)
    ax.text(0.15 + 0.5 * (w + gap) + w / 2, 3.15, "from scratch", ha="center", fontsize=8, color=C["gray"])
    ax.set_ylim(0.85, 3.45)
    ax.text(3.6, 3.15, "each stage continues from the previous model's best checkpoint  →",
            fontsize=8.5, color=C["gray"])
    save(fig, "diag_curriculum.png")


def fig_reward():
    fig, ax = plt.subplots(figsize=(10, 2.6))
    parts = [("base\n(on track)", 1.0, C["gray"]), ("steering ≈ expert\n(up to 2)", 2.0, C["purple"]),
             ("speed ≈ expert\n(up to 1)", 1.0, C["blue"]), ("smooth\nsteering (0.5)", 0.5, C["teal"]),
             ("pace\n(up to 3)", 3.0, C["orange"])]
    left = 0
    for label, v, c in parts:
        ax.barh(0, v, left=left, color=c, height=0.5, edgecolor="white")
        ax.text(left + v / 2, 0, label, ha="center", va="center", color="white", fontsize=8.5)
        left += v
    ax.text(left + 0.15, 0, "per step (max ≈ 7.5)\n+100 × lap speed / 2 m/s on lap completion\n× 0.5 near the edge,  ≈ 0 off track",
            va="center", fontsize=8.5)
    ax.set_xlim(0, 12); ax.set_yticks([]); ax.set_xlabel("reward points per step")
    ax.spines["left"].set_visible(False)
    ax.set_title("Model 05 reward: imitate a track-agnostic expert (racing line + speed planner)", fontsize=10, loc="left")
    save(fig, "diag_reward.png")


# ---------------------------------------------------------------- data charts
def fig_portal():
    fig, ax = plt.subplots(figsize=(7.5, 3.2))
    names = ["M02 imitation\n(#10)", "M03 speed\n(#13)", "M04 fast\n(#14)"]
    score = [34.716, 22.508, 18.008]; best = [34.713, 15.706, 14.710]
    x = np.arange(3)
    ax.bar(x - 0.18, score, 0.36, color=C["blue"], label="score (avg, incl. penalties)")
    ax.bar(x + 0.18, best, 0.36, color=C["teal"], label="best lap")
    for i in range(3):
        ax.text(x[i] - 0.18, score[i] + 0.6, f"{score[i]:.1f}", ha="center", fontsize=9)
        ax.text(x[i] + 0.18, best[i] + 0.6, f"{best[i]:.1f}", ha="center", fontsize=9)
    ax.axhline(5.615, color=C["red"], ls="--", lw=1)
    ax.text(2.45, 6.3, "leader 5.6", color=C["red"], fontsize=8.5, ha="right")
    ax.set_xticks(x, names); ax.set_ylabel("seconds (lower is better)")
    ax.set_title("Portal results on the secret track (all 100% completion)", fontsize=10, loc="left")
    ax.legend(frameon=False, fontsize=8.5)
    save(fig, "chart_portal.png")


EVAL_SETS = [("M02 ckpt 11", "m02-best"), ("M03 ckpt 31", "m03-ckpt31"),
             ("M03b final", "m03b-m03b-final"), ("M04 final", "m04-m04-final")]
TRACKS = ["Vegas_track", "2022_summit_speedway", "reinvent_base", "2024_reinvent_champ_cw"]
TRACK_LABEL = ["Vegas\n(training)", "Summit Speedway\n(unseen)", "re:Invent 2018\n(unseen)", "re:Invent 2024 CW\n(unseen)"]


def eval_mean(prefix, track):
    f = ROOT / "evals" / f"{prefix}-{track}" / "EvaluationMetrics.json"
    if not f.exists():
        return None, None
    m = json.loads(f.read_text())["metrics"]
    return float(np.mean([x["elapsed_time_in_milliseconds"] / 1000 for x in m])), sum(x["off_track_count"] for x in m)


def fig_eval():
    fig, ax = plt.subplots(figsize=(9, 3.6))
    cols = [C["gray"], C["blue"], C["purple"], C["green"]]
    w = 0.2
    for j, ((label, prefix), c) in enumerate(zip(EVAL_SETS, cols)):
        vals = [eval_mean(prefix, t)[0] or 0 for t in TRACKS]
        ax.bar(np.arange(4) + (j - 1.5) * w, vals, w, color=c, label=label)
    ax.set_xticks(np.arange(4), TRACK_LABEL, fontsize=8.5)
    ax.set_ylabel("mean lap time incl. penalties (s)")
    ax.set_title("Local evaluation: 3 trials per track, practice-race rules", fontsize=10, loc="left")
    ax.legend(frameon=False, fontsize=8.5, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.18))
    save(fig, "chart_eval.png")


def fig_efficiency():
    vmax = {"m02-best": 1.0, "m03-ckpt31": 2.5, "m03b-m03b-final": 2.5, "m04-m04-final": 3.0}
    best = {}
    for t in TRACKS:
        center, _ = load_track(t)
        for v in set(vmax.values()):
            best[(t, v)] = lap_time(center, v, 4.0, 3.0, 3.0)[0]
    fig, ax = plt.subplots(figsize=(7.5, 3.2))
    labels, veg, uns = [], [], []
    for label, prefix in EVAL_SETS:
        e = [best[(t, vmax[prefix])] / eval_mean(prefix, t)[0] * 100 for t in TRACKS]
        labels.append(label); veg.append(e[0]); uns.append(np.mean(e[1:]))
    x = np.arange(len(labels))
    ax.bar(x - 0.18, veg, 0.36, color=C["gray"], label="Vegas (trained on)")
    ax.bar(x + 0.18, uns, 0.36, color=C["green"], label="unseen tracks (avg)")
    for i in range(len(x)):
        ax.text(x[i], max(veg[i], uns[i]) + 2, f"gap {veg[i] - uns[i]:+.0f}", ha="center", fontsize=8.5)
    ax.set_xticks(x, labels); ax.set_ylabel("efficiency (%)"); ax.set_ylim(0, 100)
    ax.set_title("Generalization: theoretical best ÷ actual lap (100% = perfect)", fontsize=10, loc="left")
    ax.legend(frameon=False, fontsize=8.5, loc="upper right")
    save(fig, "chart_efficiency.png")


def fig_racing_line():
    w = np.load(ROOT / "tracks" / "Vegas_track.npy")
    w = w[:-1] if np.allclose(w[0, :2], w[-1, :2]) else w
    center, width = w[:, :2], float(np.median(np.linalg.norm(w[:, 4:6] - w[:, 2:4], axis=1)))
    line = racing_line(center, width, 0.30, 2000)
    fig, ax = plt.subplots(figsize=(7.5, 5))
    ax.fill(*np.vstack([w[:, 4:6], w[:1, 4:6]]).T, color="#e5e7eb"); ax.fill(*np.vstack([w[:, 2:4], w[:1, 2:4]]).T, color="white")
    for b in (w[:, 2:4], w[:, 4:6]):
        ax.plot(*np.vstack([b, b[:1]]).T, color="#6b7280", lw=1)
    ax.plot(*np.vstack([center, center[:1]]).T, "--", color="#9ca3af", lw=1.2, label="centre line (M02–M04 expert)")
    ax.plot(*np.vstack([line, line[:1]]).T, color=C["red"], lw=2, label="racing line (M05 expert)")
    ax.set_aspect("equal"); ax.axis("off"); ax.legend(loc="upper left", frameon=False, fontsize=8.5)
    ax.set_title("Vegas: centre line vs. computed racing line (tightest radius 0.58 → ~0.8 m)", fontsize=10, loc="left")
    save(fig, "chart_racing_line.png")


def fig_lap_sim():
    center, width = load_track("Vegas_track")
    line = racing_line(center, width, 0.30, 2000)
    rows = [("centre, 2.5 m/s, 4 m/s²", center, 2.5, 4.0), ("centre, 3.0 m/s, 4 m/s²", center, 3.0, 4.0),
            ("racing line, 3.0, 4 m/s²", line, 3.0, 4.0), ("racing line, 3.0, 6 m/s²", line, 3.0, 6.0),
            ("racing line, 4.0, 6 m/s²", line, 4.0, 6.0)]
    t = [lap_time(p, v, a, 3.0, 3.0)[0] for _, p, v, a in rows]
    fig, ax = plt.subplots(figsize=(8, 3.2))
    y = np.arange(len(rows))
    ax.barh(y, t, color=[C["gray"], C["gray"], C["orange"], C["orange"], C["orange"]])
    for i, v in enumerate(t):
        ax.text(v + 0.15, i, f"{v:.1f} s", va="center", fontsize=9)
    ax.axvline(14.5, color=C["blue"], lw=1.5); ax.text(14.4, 4.35, "our model on Vegas ≈ 14.5 s", color=C["blue"], fontsize=8.5, ha="right")
    ax.set_yticks(y, [r[0] for r in rows], fontsize=8.5); ax.invert_yaxis(); ax.set_xlim(0, 16.5)
    ax.set_xlabel("theoretical best Vegas lap (s)")
    ax.set_title("Lap-time simulation: best possible lap under each set of limits", fontsize=10, loc="left")
    save(fig, "chart_lap_sim.png")


def fig_grip():
    sys.argv = ["x"]
    from grip_from_logs import episode_kinematics
    lat_lap, lat_off = [], []
    for d in sorted(LOGS.glob("cedc-m04-fast*")) + sorted(LOGS.glob("cedc-m03*")):
        for ep in parse_trace(d).values():
            k = episode_kinematics(ep) if ep else None
            if k is None:
                continue
            if ep[-1]["status"] == "lap_complete":
                lat_lap.append(k[1])
            elif ep[-1]["status"] == "off_track":
                lat_off.append(np.nanmax(k[1][-6:]))
    a = np.concatenate(lat_lap); a = a[np.isfinite(a)]
    fig, ax = plt.subplots(figsize=(8, 3.0))
    bins = np.linspace(0, 8, 41)
    ax.hist(a, bins=bins, density=True, color=C["teal"], alpha=0.8, label="all steps of completed laps")
    ax.hist(np.array(lat_off)[np.isfinite(lat_off)], bins=bins, density=True, color=C["red"], alpha=0.55, label="peak just before an off-track")
    ax.axvline(4.0, color=C["ink"], ls="--", lw=1); ax.text(4.08, ax.get_ylim()[1] * 0.55, "expert's grip\nbudget 4 m/s²", fontsize=8.5)
    ax.set_xlabel("lateral acceleration (m/s²)"); ax.set_ylabel("density")
    ax.set_title("Measured from our laps: off-tracks happen at LOW lateral g → steering errors, not grip", fontsize=10, loc="left")
    ax.legend(frameon=False, fontsize=8.5, loc="upper right")
    save(fig, "chart_grip.png")


def fig_m05_traj():
    runs = sorted(LOGS.glob("cedc-m05-racingline*"))
    eps = []
    for d in runs:
        eps += [e for _, e in sorted(parse_trace(d).items()) if e]
    if not eps:
        return
    w = np.load(ROOT / "tracks" / "Vegas_track.npy")
    track = (w[:, :2], w[:, 2:4], w[:, 4:6])
    fig = trajectory_figure(track, eps[-20:], f"Model 05 (racing line): last {min(20, len(eps))} episodes")
    fig.savefig(IMG / "traj_m05_racingline.png", facecolor="white", dpi=100)
    plt.close(fig); print("wrote traj_m05_racingline.png")


if __name__ == "__main__":
    IMG.mkdir(parents=True, exist_ok=True)
    for f in (fig_system, fig_rl_loop, fig_network, fig_curriculum, fig_reward, fig_portal, fig_eval,
              fig_efficiency, fig_racing_line, fig_lap_sim, fig_grip, fig_m05_traj):
        f()
