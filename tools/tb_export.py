"""Convert saved DeepRacer training logs into TensorBoard runs.

Reads logs/<model-prefix>/ (written by the savelogs step):
    TrainingMetrics.json   per-episode results (always present, from S3)
    sagemaker.log          PPO update stats (loss, KL, entropy)
    robomaker.log          per-step SIM_TRACE_LOG (actions, positions, rewards)
    run.env                track name + pre-trained parent (for continued runs)

Usage:
    python tools/tb_export.py            # export every run in logs/
    tensorboard --logdir tb              # then open http://localhost:6006
"""
from __future__ import annotations

import json
import re

from collections import Counter, defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from torch.utils.tensorboard import SummaryWriter

ROOT = Path(__file__).resolve().parent.parent
LOGS, TB, TRACKS = ROOT / "logs", ROOT / "tb", ROOT / "tracks"
EPISODES_PER_ITER = 20
STATUSES = {"in_progress", "off_track", "lap_complete", "reversed", "crashed", "immobilized", "time_up", "prepare"}
POLICY_RE = re.compile(r"Surrogate loss=([-\d.e]+), KL divergence=([-\d.e]+), Entropy=([-\d.e]+), training epoch=(\d+), learning_rate=([-\d.e]+)")


def read_env(run_dir: Path) -> dict[str, str]:
    env = {}
    f = run_dir / "run.env"
    if f.exists():
        for line in f.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def load_metrics(run_dir: Path) -> list[dict]:
    """All per-episode metrics of a run, merged across simulator workers.

    DRfC writes one file per worker (TrainingMetrics.json, TrainingMetrics_1.json, ...).
    Training episodes are interleaved like the trace: worker w's i-th episode -> i * W + w.
    """
    files = sorted(run_dir.glob("TrainingMetrics*.json"), key=lambda f: (len(f.name), f.name))

    def worker_history(f: Path) -> list[dict]:
        # a simulator restarted mid-run (memory-leak guard) starts a fresh metrics file; the saved
        # earlier pieces part1_<name>, part2_<name>, ... come first
        parts = sorted(run_dir.glob(f"part*_{f.name}"), key=lambda p: int(p.name[4:p.name.index("_")]))
        return [m for p in parts + [f] for m in json.loads(p.read_text())["metrics"]]

    per_worker = [worker_history(f) for f in files]
    train = [[m for m in ms if m["phase"] == "training"] for ms in per_worker]
    merged: list[dict] = []
    for i in range(max((len(t) for t in train), default=0)):
        merged.extend(t[i] for t in train if i < len(t))
    evals = [m for ms in per_worker for m in ms if m["phase"] == "evaluation"]
    return merged + evals


def parse_trace(run_dir: Path) -> dict[int, list[dict]]:
    """Episode -> list of steps from SIM_TRACE_LOG lines.

    One log per simulator worker (robomaker_<w>.log; older runs: robomaker.log).
    Each worker numbers its episodes from 0, so worker w's episode e becomes e * W + w:
    with W workers each doing 20/W episodes per iteration, that keeps iterations in
    consecutive blocks of 20.
    """
    files = sorted(run_dir.glob("robomaker_*.log")) or [f for f in [run_dir / "robomaker.log"] if f.exists()]
    eps: dict[int, list[dict]] = defaultdict(list)
    for w, f in enumerate(files):
        for e, steps in _parse_trace_file(f).items():
            eps[e * len(files) + w] = steps
    return dict(sorted(eps.items()))


def _parse_trace_file(f: Path) -> dict[int, list[dict]]:
    """A restarted simulator (memory-leak guard) keeps writing to the same container log and
    numbers its episodes from 0 again: each time the episode number drops, start a new session
    so steps of different laps aren't merged."""
    eps: dict[int, list[dict]] = defaultdict(list)
    session, last_ep, offset = 0, -1, 0
    for line in f.open(errors="replace"):
        if "SIM_TRACE_LOG:" not in line:
            continue
        f_ = line.split("SIM_TRACE_LOG:", 1)[1].strip().split(",")
        try:
            i = next(k for k, x in enumerate(f_) if x in STATUSES)
            ep = int(f_[0])
            if ep < last_ep:  # simulator restarted
                session += 1
                offset = max(eps) + 1 if eps else 0
            last_ep = ep
            eps[offset + ep].append({
                "step": int(f_[1]), "x": float(f_[2]), "y": float(f_[3]), "yaw": float(f_[4]),
                "steer": float(f_[5]), "speed": float(f_[6]), "reward": float(f_[i - 7]),
                "progress": float(f_[i - 4]), "wp": int(f_[i - 3]), "t": float(f_[i - 1]), "status": f_[i],
            })
        except (StopIteration, ValueError, IndexError):
            continue
    return eps


def parse_policy(run_dir: Path) -> list[tuple[float, ...]]:
    f = run_dir / "sagemaker.log"
    if not f.exists():
        return []
    return [tuple(float(x) for x in m.groups()) for m in POLICY_RE.finditer(f.read_text(errors="replace"))]


def load_track(name: str):
    f = TRACKS / f"{name}.npy"
    if not f.exists():
        return None
    w = np.load(f)
    return w[:, 0:2], w[:, 2:4], w[:, 4:6]


def trajectory_figure(track, episodes: list[list[dict]], title: str):
    fig, ax = plt.subplots(figsize=(8, 6))
    if track is not None:
        c, inner, outer = track
        ax.fill(*outer.T, color="0.9")
        ax.fill(*inner.T, color="white")
        for b in (inner, outer):
            ax.plot(*b.T, color="0.4", lw=1)
    sc = None
    for ep in episodes:
        xs, ys, sp = [s["x"] for s in ep], [s["y"] for s in ep], [s["speed"] for s in ep]
        ax.plot(xs, ys, color="0.6", lw=0.4, alpha=0.5)
        sc = ax.scatter(xs, ys, c=sp, s=4, cmap="viridis", vmin=0.5, vmax=max(1.0, max(sp)))
        if ep[-1]["status"] in ("off_track", "reversed", "crashed"):
            ax.plot(xs[-1], ys[-1], "x", color="crimson", ms=7, mew=2)
    if sc is not None:
        fig.colorbar(sc, ax=ax, shrink=0.7, label="speed action (m/s)")
    ax.set_title(title + "   (x = off track)")
    ax.set_aspect("equal")
    return fig


def offtrack_figure(track, counts: Counter, title: str):
    fig, ax = plt.subplots(figsize=(8, 6))
    if track is not None:
        c, inner, outer = track
        ax.fill(*outer.T, color="0.9")
        ax.fill(*inner.T, color="white")
        for b in (inner, outer):
            ax.plot(*b.T, color="0.4", lw=1)
        if counts:
            wps = np.array(list(counts.keys()))
            n = np.array(list(counts.values()))
            sc = ax.scatter(*c[np.clip(wps, 0, len(c) - 1)].T, s=40 + 60 * n, c=n, cmap="Reds", edgecolors="k", zorder=3)
            fig.colorbar(sc, ax=ax, shrink=0.7, label="off-track count")
            for i in range(0, len(c), 10):
                ax.annotate(str(i), c[i], fontsize=7, color="0.3")
    ax.set_title(title)
    ax.set_aspect("equal")
    return fig


def export_run(run_dir: Path, parent_offsets: dict[str, tuple[int, int, int]]) -> tuple[int, int, int]:
    """Write one run. Returns (episodes, iterations, policy_updates) for chaining children."""
    env = read_env(run_dir)
    parent = env.get("DR_LOCAL_S3_PRETRAINED_PREFIX") if env.get("DR_LOCAL_S3_PRETRAINED") == "True" else None
    ep_off, it_off, pol_off = parent_offsets.get(parent, (0, 0, 0))
    track_name = env.get("DR_WORLD_NAME", "Vegas_track")
    track = load_track(track_name)

    out = TB / run_dir.name
    # Don't delete the folder while TensorBoard is watching it: drop only the old event
    # file and write a new one. TensorBoard sees steps restart from 0 and replaces the
    # old points (its "purge orphaned data" behaviour for restarted jobs).
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("events.out.tfevents.*"):
        old.unlink(missing_ok=True)
    w = SummaryWriter(str(out))
    w.add_text("run/info", f"track: `{track_name}`  \ncontinues from: `{parent or '-'}` (episode offset {ep_off})")
    for name in ("reward_function.py", "model_metadata.json"):
        if (run_dir / name).exists():
            w.add_text(f"config/{name}", "```\n" + (run_dir / name).read_text() + "\n```")

    # 1) per-episode results (TrainingMetrics.json)
    metrics = load_metrics(run_dir)
    train = [m for m in metrics if m["phase"] == "training"]
    evals = [m for m in metrics if m["phase"] == "evaluation"]
    for i, m in enumerate(train):
        g = ep_off + i + 1
        w.add_scalar("episode/reward", m["reward_score"], g)
        w.add_scalar("episode/progress_pct", m["completion_percentage"], g)
        w.add_scalar("episode/lap_complete", float(m["episode_status"] == "Lap complete"), g)
        w.add_scalar("episode/duration_s", m["elapsed_time_in_milliseconds"] / 1000, g)
    n_iters = (len(train) + EPISODES_PER_ITER - 1) // EPISODES_PER_ITER
    for it in range(n_iters):
        chunk = train[it * EPISODES_PER_ITER:(it + 1) * EPISODES_PER_ITER]
        if len(chunk) < EPISODES_PER_ITER // 2:
            continue
        g = it_off + it
        r = [m["reward_score"] for m in chunk]
        p = [m["completion_percentage"] for m in chunk]
        w.add_scalar("iteration/mean_reward", np.mean(r), g)
        w.add_scalar("iteration/mean_progress_pct", np.mean(p), g)
        w.add_scalar("iteration/max_progress_pct", np.max(p), g)
        w.add_scalar("iteration/lap_completion_rate", np.mean([m["episode_status"] == "Lap complete" for m in chunk]), g)
    # evaluation episodes DRfC runs between iterations (used to pick the "best" checkpoint)
    by_ev = defaultdict(list)
    for m in evals:
        by_ev[m["episode"]].append(m["completion_percentage"])
    for k, (ep, ps) in enumerate(sorted(by_ev.items())):
        w.add_scalar("eval_between_iterations/progress_pct", np.mean(ps), it_off + k)

    # 2) PPO update statistics
    pol = parse_policy(run_dir)
    for k, (loss, kl, ent, _epoch, lr) in enumerate(pol):
        g = pol_off + k
        w.add_scalar("ppo/surrogate_loss", loss, g)
        w.add_scalar("ppo/kl_divergence", kl, g)
        w.add_scalar("ppo/entropy", ent, g)
        w.add_scalar("ppo/learning_rate", lr, g)

    # 3) per-step detail from the simulator trace
    trace = parse_trace(run_dir)
    if trace:
        ep_ids = sorted(trace)
        for e in ep_ids:
            steps = trace[e]
            g = ep_off + e + 1
            w.add_scalar("episode_detail/mean_speed_action", np.mean([s["speed"] for s in steps]), g)
            w.add_scalar("episode_detail/mean_abs_steering", np.mean([abs(s["steer"]) for s in steps]), g)
            steer = np.array([s["steer"] for s in steps])
            if len(steer) > 1:
                w.add_scalar("episode_detail/steering_change_per_step", np.mean(np.abs(np.diff(steer))), g)
            if steps[-1]["status"] == "lap_complete":
                w.add_scalar("episode_detail/lap_time_s", steps[-1]["t"] - steps[0]["t"], g)
        for it in range((len(ep_ids) + EPISODES_PER_ITER - 1) // EPISODES_PER_ITER):
            ids = ep_ids[it * EPISODES_PER_ITER:(it + 1) * EPISODES_PER_ITER]
            eps = [trace[e] for e in ids]
            g = it_off + it
            allsteps = [s for ep in eps for s in ep]
            w.add_histogram("actions/steering_deg", np.array([s["steer"] for s in allsteps]), g)
            w.add_histogram("actions/speed_mps", np.array([s["speed"] for s in allsteps]), g)
            w.add_histogram("actions/step_reward", np.array([s["reward"] for s in allsteps]), g)
            w.add_figure("track/trajectories", trajectory_figure(track, eps, f"iteration {g}: {len(eps)} episodes"), g)
            off = Counter(ep[-1]["wp"] for ep in eps if ep[-1]["status"] in ("off_track", "reversed", "crashed"))
            w.add_figure("track/off_track_locations", offtrack_figure(track, off, f"iteration {g}: where the car left the track"), g)
            plt.close("all")
    w.close()
    print(f"{run_dir.name}: {len(train)} episodes, {len(pol)} PPO updates, {len(trace)} traced episodes -> tb/{run_dir.name}")
    return ep_off + len(train), it_off + n_iters, pol_off + len(pol)


def source_signature(run_dir: Path) -> str:
    return ";".join(f"{f.name}:{f.stat().st_size}:{int(f.stat().st_mtime)}" for f in sorted(run_dir.iterdir()) if f.is_file())


def main() -> None:
    runs = sorted(d for d in LOGS.iterdir() if (d / "TrainingMetrics.json").exists())
    offsets: dict[str, tuple[int, int, int]] = {}

    def export_if_changed(d: Path) -> tuple[int, int, int]:
        sig_file = TB / d.name / ".source_signature"
        sig = source_signature(d)
        cached = TB / d.name / ".offsets.json"
        if sig_file.exists() and sig_file.read_text() == sig and cached.exists():
            return tuple(json.loads(cached.read_text()))  # unchanged: keep the existing export
        result = export_run(d, offsets)
        sig_file.write_text(sig)
        cached.write_text(json.dumps(result))
        return result
    # parents before children so continued runs line up on the same x axis
    pending = list(runs)
    while pending:
        progressed = False
        for d in list(pending):
            env = read_env(d)
            parent = env.get("DR_LOCAL_S3_PRETRAINED_PREFIX") if env.get("DR_LOCAL_S3_PRETRAINED") == "True" else None
            if parent is None or parent in offsets or not (LOGS / parent).exists():
                try:
                    offsets[d.name] = export_if_changed(d)
                except Exception as exc:  # e.g. a log file caught mid-copy; retried on the next refresh
                    print(f"{d.name}: skipped ({type(exc).__name__}: {exc})")
                    offsets[d.name] = (0, 0, 0)
                pending.remove(d)
                progressed = True
        if not progressed:
            break


if __name__ == "__main__":
    main()
