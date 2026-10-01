"""Build the team catch-up report: report/Slowcedes_DeepRacer_Catchup.pdf"""
from __future__ import annotations

from pathlib import Path

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

ROOT = Path(__file__).resolve().parent
IMG = ROOT / "img"
OUT = ROOT / "Slowcedes_DeepRacer_Catchup.pdf"

FONT_DIR = Path("C:/Windows/Fonts")
pdfmetrics.registerFont(TTFont("Segoe", str(FONT_DIR / "segoeui.ttf")))
pdfmetrics.registerFont(TTFont("Segoe-Bold", str(FONT_DIR / "segoeuib.ttf")))
pdfmetrics.registerFont(TTFont("Segoe-Italic", str(FONT_DIR / "segoeuii.ttf")))
pdfmetrics.registerFontFamily("Segoe", normal="Segoe", bold="Segoe-Bold", italic="Segoe-Italic", boldItalic="Segoe-Bold")

INK = colors.HexColor("#111827"); MUTED = colors.HexColor("#6b7280"); ACCENT = colors.HexColor("#2563eb")
LIGHT = colors.HexColor("#f3f4f6"); LINE = colors.HexColor("#d1d5db"); GOOD = colors.HexColor("#dcfce7")
WARN = colors.HexColor("#fef3c7")

ss = getSampleStyleSheet()
S = {
    "title": ParagraphStyle("t", fontName="Segoe-Bold", fontSize=24, leading=29, textColor=INK, spaceAfter=6),
    "subtitle": ParagraphStyle("st", fontName="Segoe", fontSize=12, leading=16, textColor=MUTED, spaceAfter=18),
    "h1": ParagraphStyle("h1", fontName="Segoe-Bold", fontSize=16, leading=20, textColor=ACCENT, spaceBefore=14, spaceAfter=8),
    "h2": ParagraphStyle("h2", fontName="Segoe-Bold", fontSize=12, leading=15, textColor=INK, spaceBefore=10, spaceAfter=5),
    "body": ParagraphStyle("b", fontName="Segoe", fontSize=9.5, leading=13.5, textColor=INK, spaceAfter=5),
    "bullet": ParagraphStyle("bl", fontName="Segoe", fontSize=9.5, leading=13.5, textColor=INK, leftIndent=12, bulletIndent=2, spaceAfter=2),
    "caption": ParagraphStyle("c", fontName="Segoe-Italic", fontSize=8.5, leading=11, textColor=MUTED, alignment=TA_CENTER, spaceAfter=10),
    "cell": ParagraphStyle("cell", fontName="Segoe", fontSize=8.3, leading=10.5, textColor=INK),
    "cellb": ParagraphStyle("cellb", fontName="Segoe-Bold", fontSize=8.3, leading=10.5, textColor=INK),
    "box": ParagraphStyle("box", fontName="Segoe", fontSize=9.5, leading=13.5, textColor=INK),
}
W = letter[0] - 1.5 * inch  # usable width


def P(text, style="body"):
    return Paragraph(text, S[style])


def bullets(items):
    return [Paragraph(t, S["bullet"], bulletText="•") for t in items]


def img(name, width=W, caption=None, max_h=None):
    path = IMG / name
    w, h = PILImage.open(path).size
    width = min(width, W)
    height = width * h / w
    if max_h and height > max_h:
        height = max_h; width = height * w / h
    out = [Image(str(path), width=width, height=height)]
    if caption:
        out.append(P(caption, "caption"))
    return KeepTogether(out)


def table(rows, widths, header=True, highlight=None, zebra=True):
    data = [[Paragraph(str(c), S["cellb" if (header and r == 0) else "cell"]) for c in row] for r, row in enumerate(rows)]
    t = Table(data, colWidths=[W * f for f in widths], repeatRows=1 if header else 0)
    style = [("GRID", (0, 0), (-1, -1), 0.4, LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"),
             ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
             ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
    if header:
        style.append(("BACKGROUND", (0, 0), (-1, 0), LIGHT))
    if highlight is not None:
        for r in ([highlight] if isinstance(highlight, int) else highlight):
            style.append(("BACKGROUND", (0, r), (-1, r), GOOD))
    t.setStyle(TableStyle(style))
    return t


def callout(text, bg=WARN):
    t = Table([[Paragraph(text, S["box"])]], colWidths=[W])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), bg), ("BOX", (0, 0), (-1, -1), 0.5, LINE),
                           ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                           ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    return t


def side_by_side(names, captions, height=2.0 * inch):
    cells = []
    for n in names:
        w, h = PILImage.open(IMG / n).size
        cells.append(Image(str(IMG / n), width=height * w / h, height=height))
    t = Table([cells, [P(c, "caption") for c in captions]], colWidths=[W / len(names)] * len(names))
    t.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    return t


def grid2x2(names, captions):
    cell_w = W / 2 - 6
    cells = []
    for n, c in zip(names, captions):
        w, h = PILImage.open(IMG / n).size
        cells.append([Image(str(IMG / n), width=cell_w, height=cell_w * h / w), P(c, "caption")])
    t = Table([[cells[0], cells[1]], [cells[2], cells[3]]], colWidths=[W / 2, W / 2])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    return t


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Segoe", 7.5); canvas.setFillColor(MUTED)
    canvas.drawString(0.75 * inch, 0.5 * inch, "Slowcedes · CEDC AI Grand Prix 2026 · team catch-up · 2026-09-30")
    canvas.drawRightString(letter[0] - 0.75 * inch, 0.5 * inch, f"page {doc.page}")
    canvas.restoreState()


def build():
    s = []
    # ------------------------------------------------------------------ cover / TL;DR
    s += [P("Slowcedes: DeepRacer Challenge catch-up", "title"),
          P("Everything we built, learned and changed from the first baseline to Model 05 · status as of 2026-09-30 evening", "subtitle")]
    s.append(callout(
        "<b>Where we stand.</b> Team <b>Slowcedes</b> has <b>100% completion</b> on the secret evaluation track with a "
        "<b>score of 18.008</b> (best lap 14.710 s), down from 34.7 → 22.5 → 18.0 over three uploads. The leader "
        "(Shallow Learner) is at 5.615. Our best model is <b>Model 04 final</b> (uploaded). <b>Model 05</b> (racing line + "
        "smooth steering) is training now on the local RTX 3090.", GOOD))
    s.append(Spacer(1, 8))
    s.append(P("The five things to know", "h2"))
    s += bullets([
        "<b>We train locally</b> with DeepRacer-for-Cloud (DRfC) on the 3090 in WSL2 (allowed by the organizers' email), "
        "with heavy automation because the simulator is fragile on Windows.",
        "<b>The car only sees one camera image.</b> Our reward teaches it by imitating a track-agnostic <b>expert driver</b> "
        "that we compute from the track's waypoints (pure pursuit + braking-aware speed profile + grip limit). No hard-coded "
        "positions, so it follows the rules and generalizes.",
        "<b>Curriculum:</b> each model continues from the previous one's best checkpoint and makes the task harder "
        "(slow laps → speed → both directions → faster → racing line).",
        "<b>We judge models on unseen tracks,</b> not on Vegas: 4-track evaluation, time including off-track penalties, "
        "and a <b>generalization efficiency</b> metric (theoretical best ÷ actual lap).",
        "<b>The portal counts off-tracks as time, not as failure:</b> completion stayed 100% even when our model went off; "
        "fewer off-tracks is what cut our score from 22.5 to 18.0.",
    ])
    s.append(Spacer(1, 6))
    s.append(img("chart_portal.png", width=W * 0.8, caption="Fig. 1: Our three portal submissions vs. the leader."))

    # ------------------------------------------------------------------ challenge
    s.append(PageBreak())
    s.append(P("1. The challenge in one page", "h1"))
    s.append(P("We train an AWS DeepRacer car (1/18 scale) with reinforcement learning. Models are uploaded to the "
               "CU Denver portal (deepracer.ashiskb.info) and evaluated on a <b>secret track</b> (3 trials). The "
               "leaderboard ranks <b>completion rate first, then the lower score</b> (time-based). Selected teams race the "
               "same model on a <b>physical car on October 8</b>; the practice race (Vegas) closes October 7."))
    s.append(table([
        ["Rule (organizers' email)", "How we comply"],
        ["Single camera only", "<font name='Segoe-Bold'>FRONT_FACING_CAMERA</font>"],
        ["PPO only", "clipped PPO, continuous action space"],
        ["Train on the public Vegas track (AWS Summit Raceway)", "All training is on Vegas_track (both directions). Other tracks are only used to <i>evaluate</i>."],
        ["Generalize, avoid hard-coding waypoints", "The reward computes everything from runtime <i>waypoints</i> of whatever track it is on"],
        ["Local infrastructure allowed (e.g. DRfC)", "Yes, DRfC on our own RTX 3090"],
        ["Keep notes, change one or two things at a time", "experiments/LOG.md + a README per model"],
    ], [0.42, 0.58]))
    s.append(Spacer(1, 6))
    s.append(callout("<b>Open question for the organizers</b> (still to send): is training on simulator tracks other than "
                     "Vegas allowed, and is evaluating on them locally OK? Until answered we train on Vegas only."))

    # ------------------------------------------------------------------ setup
    s.append(P("2. How we train: local setup", "h1"))
    s.append(img("diag_system.png", caption="Fig. 2: Local training system. Simulator and trainer run in Docker inside WSL2; "
                 "a supervisor script on Windows keeps everything alive and logs to the project folder."))
    s.append(P("Getting DRfC stable on a Windows desktop took most of the first day. Every problem below happened to us and "
               "is now handled automatically (details in docs/DRFC_SETUP.md):"))
    s.append(table([
        ["Problem we hit", "Symptom", "Fix now in place"],
        ["MinIO image removed from Docker Hub (Sep 2026)", "storage would not start", "Chainguard MinIO image, re-tagged"],
        ["Simulator rendered on CPU", "2.8 steps/s", "GPU rendering via WSL D3D12 (GALLIUM_DRIVER=d3d12) → ~9.8 steps/s"],
        ["Docker swarm manager timeouts", "simulators silently shut down", "switched to compose mode"],
        ["2 simulators + Windows apps", "CPU load 12/12, physics timeouts", "1 simulator"],
        ["WSL given 24 GB + 8 GB swap", "Windows at 0.8 GB free, WSL froze", ".wslconfig: 16 GB, 10 threads, 4 GB swap, autoMemoryReclaim"],
        ["WSL idles its VM when no Windows process attached", "training killed after terminal closed", "supervisor holds a keep-alive connection"],
        ["<b>Simulator memory leak</b> with GPU rendering", "~1 GB/min until the PC chokes", "restart <i>only</i> the simulator; the trainer keeps its state"],
        ["Simulator restarted mid-iteration", "trainer waits forever (silent stall)", "restart only at iteration boundaries + stuck-trainer detection (8 min → full resume)"],
        ["DRfC auto-increment bug", "resumed runs pointed at nonexistent parents", "own resume script names runs <i>-2, -3…</i>"],
        ["Several metrics files with 2 workers", "episode counts halved", "exporter merges them"],
        ["<i>is_reversed</i> means 'clockwise', not 'wrong way'", "clockwise episodes got 0 reward", "removed from all rewards"],
        ["Interrupted evaluation left another track in run.env", "trained 1 min on the wrong track", "start script always forces Vegas"],
    ], [0.3, 0.27, 0.43]))

    # ------------------------------------------------------------------ RL problem
    s.append(PageBreak())
    s.append(P("3. The RL problem", "h1"))
    s.append(img("diag_rl_loop.png", caption="Fig. 3: The reinforcement-learning loop (~15 decisions per simulated second)."))
    s.append(table([
        ["RL concept", "In our setup"],
        ["Agent", "Policy network (CNN), clipped PPO actor-critic"],
        ["Observation", "<b>Only</b> the front camera: 160×120 grayscale, 1 frame (stack_size 1)"],
        ["Action", "Continuous: steering −30…+30°, speed 1.3…3.0 m/s (Model 04/05)"],
        ["Reward", "Our Python function, sees exact position, waypoints, heading, speed… (training only)"],
        ["Episode", "Random start point; ends on lap complete or off track. Direction alternates every episode"],
    ], [0.22, 0.78]))
    s.append(Spacer(1, 6))
    s.append(side_by_side(["car_camera.jpg", "model_input_160x120_zoomed.png", "broadcast.jpg"],
                          ["Car's camera", "What the network actually gets (160×120 gray)", "Simulator broadcast view"],
                          height=1.55 * inch))
    s.append(img("diag_network.png", caption="Fig. 4: Network architecture (DeepRacer's shallow CNN)."))
    s.append(P("Hyperparameters & throughput", "h2"))
    s.append(table([
        ["Hyperparameter", "Value", "Meaning"],
        ["learning rate", "0.0003", "step size of each update"],
        ["discount γ", "0.99", "looks ~100 steps (≈ 6.6 s, a third of a lap) ahead"],
        ["episodes between training", "20", "one <b>iteration</b> = 20 episodes, then an update"],
        ["epochs / batch size", "5 / 64", "≈ 230 gradient steps per update"],
        ["entropy β", "0.01", "exploration bonus"],
        ["term_cond_max_episodes", "1000", "<b>Note:</b> a single run may stop learning after 1000 episodes; raise it for overnight runs"],
    ], [0.3, 0.13, 0.57]))
    s.append(Spacer(1, 4))
    s.append(P("Measured: 15 decisions per simulated second; the simulation runs at about <b>half real time</b> "
               "(≈7.5 steps/s); ~2.5–3 episodes/min; one iteration ≈ 8–10 min; <b>≈150–180 episodes and ~6–7 updates per hour</b>. "
               "The GPU is mostly idle: the simulator (CPU) is the bottleneck. All hyperparameters are still DRfC defaults."))

    # ------------------------------------------------------------------ reward
    s.append(PageBreak())
    s.append(P("4. Reward design: imitate an expert driver", "h1"))
    s.append(P("Instead of rewarding 'stay near the centre' (the starter reward), every step the reward computes what a "
               "simple expert would do <b>on this track</b> and rewards the car for doing something similar. The network never "
               "sees the expert; it must learn the behaviour from pixels, which is what transfers to unseen and physical tracks."))
    s += bullets([
        "<b>Steering:</b> pure pursuit, aiming at a point 0.6–0.83 m ahead (further at higher speed) on the path.",
        "<b>Speed:</b> a braking-aware speed profile. Every curve ahead allows √(grip × radius); the car must be able to "
        "brake (3 m/s²) in time for it. Plus a grip cap from the steering angle (≤ 4 m/s² lateral).",
        "<b>Model 05 additions:</b> the path is a <b>racing line</b> (K1999-style curvature averaging, 0.30 m from the edges), "
        "and a <b>smooth-steering bonus</b> for small steering changes.",
        "<b>Lap bonus:</b> +100 × (average lap speed / 2 m/s), so faster laps pay more.",
    ])
    s.append(img("diag_reward.png", caption="Fig. 5: Reward per step (Model 05)."))
    s.append(img("chart_racing_line.png", width=W * 0.8, caption="Fig. 6: Centre line vs. computed racing line on Vegas. Same algorithm runs on any track."))
    s.append(P("Every reward is first tested offline (tools/test_reward.py): a simple car model drives each track using "
               "only the expert's commands. Model 05's expert laps all 10 test tracks and is ~10% faster than the centre-line "
               "expert (Vegas 8.2 vs 9.1 s). Two earlier versions failed this test and were fixed before training."))

    # ------------------------------------------------------------------ history
    s.append(PageBreak())
    s.append(P("5. Model history (curriculum)", "h1"))
    s.append(img("diag_curriculum.png", caption="Fig. 7: Each stage continues from the previous model's best checkpoint."))
    s.append(table([
        ["Model", "What changed", "Started from", "Outcome"],
        ["M01 baseline", "Organizers' starter reward (stay near centre), 0.5–1.0 m/s", "scratch", "0 laps in 225 episodes; heavy zig-zag (23°/step)"],
        ["M02 imitation", "Expert reward (pure pursuit + slow before curves)", "scratch", "First laps; Vegas 3/3 clean, 27 s; <b>portal 34.7</b>. Off-tracks only in right turns"],
        ["M03 speed", "1.0–2.5 m/s, braking speed profile + grip limit", "M02 ckpt 11", "Vegas 14.7 s; <b>portal 22.5</b>; more off-tracks on unseen right-handers"],
        ["M03b both dirs", "Alternate driving direction each episode", "M03 ckpt 31", "Right turns fixed (11 vs 30 off-tracks) but slower (1.46 → 1.28 m/s); not uploaded"],
        ["M04 fast", "1.3–3.0 m/s + lap bonus scaled by lap speed", "M03b final", "Mean 17.0 s on 4 tracks, half the off-tracks; <b>portal 18.0</b>"],
        ["M05 racing line", "Racing line + smooth-steering bonus", "M04 final", "Training now (best lap 13.1 s so far)"],
    ], [0.14, 0.33, 0.13, 0.40], highlight=5))
    s.append(Spacer(1, 8))
    traj = [P("Trajectories during training", "h2"), P("Each plot shows the paths of one training iteration on Vegas, coloured by commanded speed, with × where the "
               "car left the track. Note the speed scales differ (0.5–1.0 m/s for M01/M02, up to 3.0 m/s for M04/M05).")]
    s.append(PageBreak())
    s.append(KeepTogether(traj + [grid2x2(["traj_m01_baseline.png", "traj_m02_imitation.png", "traj_m04_fast.png", "traj_m05_racingline.png"],
                     ["M01 baseline: scattered paths, off-tracks everywhere, slow",
                      "M02 imitation (early): follows the road, crashes cluster in the S-section",
                      "M04 fast: consistent laps at 1.3–3.0 m/s, 1 off-track in 6 episodes",
                      "M05 racing line (now): fast laps, both directions, few off-tracks"])]))

    # ------------------------------------------------------------------ evaluation
    s.append(PageBreak())
    s.append(P("6. How we evaluate (and why Vegas alone lies)", "h1"))
    s.append(P("Every candidate checkpoint is evaluated locally under practice-race rules (3 trials, individual lap, "
               "resets allowed, 1 s off-track penalty) on <b>4 tracks</b>: Vegas plus three it never trained on (Summit "
               "Speedway, re:Invent 2018, re:Invent 2024 clockwise). We save hourly snapshots and evaluate several, because "
               "the last checkpoint is not always the best (overnight, 03b got slower the longer it trained)."))
    s.append(img("chart_eval.png", caption="Fig. 8: Mean time per track including penalties (lower is better)."))
    s.append(table([
        ["Model", "Vegas", "Summit", "re:Inv 2018", "re:Inv 2024 CW", "Mean", "Off-tracks /12", "Portal"],
        ["M02 ckpt 11", "27.2", "28.8", "27.5", "39.2", "30.7", "27", "34.716"],
        ["M03 ckpt 31", "14.7", "21.6", "14.0", "20.5", "17.7", "30", "22.508"],
        ["M03b final", "18.3", "23.4", "16.9", "22.8", "20.3", "11", "—"],
        ["<b>M04 final</b>", "15.8", "<b>19.0</b>", "<b>13.0</b>", "<b>20.3</b>", "<b>17.0</b>", "15", "<b>18.008</b>"],
    ], [0.17, 0.09, 0.1, 0.12, 0.14, 0.09, 0.14, 0.15], highlight=4))
    s.append(Spacer(1, 8))
    s.append(img("chart_efficiency.png", width=W * 0.82, caption="Fig. 9: Generalization efficiency. A model that memorized Vegas "
                 "scores much higher there than on unseen tracks (large gap). Both-direction training cut the gap from 18 to 10 points."))

    # ------------------------------------------------------------------ analysis
    s.append(PageBreak())
    s.append(P("7. What limits us: lap-time simulation & measured physics", "h1"))
    s.append(img("chart_lap_sim.png", caption="Fig. 10: Theoretical best Vegas lap under each set of limits (quasi-steady-state lap simulation, tools/lap_time_sim.py)."))
    s += bullets([
        "Our model drives at <b>~60% of what its own limits allow</b> (≈14.5 s vs 8.65 s theoretical): execution, not limits, is the main gap.",
        "A racing line is worth ~1.6 s per Vegas lap; more top speed barely helps (grip-limited, short straights).",
        "<b>The leader's 5.54 s</b> is below even the 4 m/s / 6 m/s² bound (7.1 s) for a Vegas-length track. Either the secret "
        "track is much shorter, they use a top speed above 4 m/s (DRfC allows it), or the timing differs. Worth asking.",
    ])
    s.append(img("chart_grip.png", caption="Fig. 11: Lateral acceleration measured from 994 completed laps vs. the moment before 1,246 off-tracks."))
    s += bullets([
        "The simulator holds <b>at least 5–6 m/s²</b> lateral (p99 4.8, p99.9 6.0): the expert's 4 m/s² is conservative.",
        "<b>Off-tracks happen at low lateral g</b> (median 2 m/s²): the car isn't sliding off, it steers wrong or late. That is a skill problem.",
        "Top-speed test: commanded 6 m/s on a 5.7 m straight, the car accelerated at ~4.5 m/s² and reached 3.89 m/s with no "
        "visible cap; inconclusive (track too short), and our tracks never let it pass ~3.4 m/s anyway.",
    ])

    # ------------------------------------------------------------------ now & next
    s.append(PageBreak())
    s.append(P("8. Current state & next steps", "h1"))
    s.append(table([
        ["Model 05 (racing line), live at 18:50", "Value"],
        ["Episodes / laps", "154 / 83"],
        ["Last 20 episodes", "13 laps, 77% mean progress"],
        ["Best / mean lap (Vegas training)", "13.1 s (record) / 14.8 s"],
        ["Clockwise / counterclockwise lap", "14.2 s / 15.2 s"],
        ["Steering change", "15.3°/step (M01: 23.3°)"],
    ], [0.5, 0.5]))
    s.append(Spacer(1, 6))
    s.append(P("Plan", "h2"))
    s += bullets([
        "Finish Model 05 (hourly snapshots), evaluate on the 4 tracks with efficiency; upload if it beats M04's 17.0 s mean.",
        "Raise the expert's grip budget to ~5 m/s² (measured), and make the line use more of the track.",
        "Hyperparameter experiments (one at a time): lower learning rate for fine-tuning, more episodes per iteration, lower entropy.",
        "<b>Control experiment (good for the second PC):</b> train Model 05's reward <i>from scratch</i> to check whether the curriculum helps or carries old habits.",
        "Physical race (Oct 8): pick the most reliable model (fewest off-tracks, both directions); real cameras punish zig-zag steering.",
    ])
    s.append(P("How you can help", "h2"))
    s += bullets([
        "Set up DRfC on your PC with <b>docs/DRFC_SETUP.md</b> (copy our .wslconfig, compose mode, GPU-rendering fix, MinIO fix).",
        "Run the from-scratch control or a hyperparameter experiment in parallel; use <b>tools/supervise.sh</b> to babysit it.",
        "Send the organizers the open question (other tracks for training/evaluation; how 'best lap' is measured).",
    ])

    # ------------------------------------------------------------------ cheat sheet
    s.append(P("9. Cheat sheet: files & tools", "h1"))
    s.append(table([
        ["Path", "What it is"],
        ["README_CHALLENGE.md", "Challenge overview, rules, practice race details"],
        ["experiments/LOG.md", "One row per model + portal history"],
        ["experiments/modelNN-*/", "reward_function.py, model_metadata.json, README with results"],
        ["experiments/ANALYSIS_limits.md", "Lap-time simulation, measured grip, generalization efficiency"],
        ["experiments/OVERNIGHT_2026-09-30.md", "Overnight log of Model 03b"],
        ["docs/DRFC_SETUP.md, docs/RL_FORMULATION.md", "Setup guide (all fixes) and RL explanation"],
        ["tools/supervise.sh HH:MM", "Babysits a run: logs, TensorBoard, memory-leak restarts, stall detection, stop time"],
        ["tools/wsl/*.sh", "WSL helpers: start_run, autoresume, simrestart, evalrun, eval_candidates, snapshot, …"],
        ["tools/test_reward.py", "Offline test of a reward's expert on 10 tracks"],
        ["tools/run_summary.py, direction_summary.py, checkin.sh", "Progress summaries (overall and per direction)"],
        ["tools/tb_export.py → tensorboard --logdir tb", "TensorBoard: scalars, PPO stats, trajectories, off-track maps"],
        ["tools/lap_time_sim.py, grip_from_logs.py, efficiency.py", "Analysis tools from section 6–7"],
        ["submissions/*.tar.gz", "Validated portal bundles (made with cedc_package_model.py)"],
    ], [0.42, 0.58]))

    doc = SimpleDocTemplate(str(OUT), pagesize=letter, leftMargin=0.75 * inch, rightMargin=0.75 * inch,
                            topMargin=0.7 * inch, bottomMargin=0.75 * inch,
                            title="Slowcedes DeepRacer catch-up", author="Slowcedes")
    doc.build(s, onFirstPage=footer, onLaterPages=footer)
    print("wrote", OUT)


if __name__ == "__main__":
    build()
