# CEDC DeepRacer Challenge 2026 — Our Playbook

This is our team's guide to the competition: what the challenge is, how it's scored, the full workflow from training to submission, and our strategy.

> The kit's original instructions are in [README.md](README.md). This file is our own overview.

---

## 1. The challenge in one paragraph

We train an autonomous racing car with **reinforcement learning (RL)** on AWS DeepRacer's cloud simulator. The car learns to drive from a single front camera. We control its behaviour by writing a **reward function**, a Python function that scores every action the car takes. We submit the trained model to the CU Denver competition portal, which runs it on a **hidden track**. The best teams then race the **same model** on a **physical DeepRacer car** on a real track.

You only need a browser. No GPU, Docker, ROS or local ML setup is required.

---

## 1b. Official rules (organizer email, Sep 2026)

| Rule | Our status |
|---|---|
| **Single camera only** | ✅ `"sensor": ["FRONT_FACING_CAMERA"]` |
| **PPO only** | ✅ `"training_algorithm": "clipped_ppo"` |
| Train/experiment on the public **Vegas_track** (AWS Summit Raceway) | ✅ Models 01–07 trained on `Vegas_track` only; from Model 08 also on other public simulator tracks (allowed, see below) |
| Local infrastructure allowed (e.g. DeepRacer-for-Cloud) | ✅ Explicitly allowed |
| **Generalize; avoid hard-coding waypoints**, don't memorize one track | ✅ The reward reads `params["waypoints"]` of whatever track it runs on; no fixed indices or coordinates |
| Keep notes, change one or two things at a time | ✅ `experiments/LOG.md` + per-model READMEs |
| Generative AI welcome as an assistant; the engineering decisions are the team's | ⚠️ The team should understand and own each design choice |
| **Physical race: Thursday, October 8, 2026** | Details to come |

**Training on other simulator tracks:** allowed (confirmed by the team on 2026-10-01). Models 01–07 used Vegas only; Model 08 onward also trains on the public tracks closest to the secret track (see `team/SECRET_TRACK.md`).

## 2. Key links

| What | Where |
|---|---|
| Competition portal (register, upload, leaderboard) | https://deepracer.ashiskb.info |
| Training simulator | CU Denver DeepRacer on AWS (via invitation email; no personal AWS account needed) |
| Practice race | DeepRacer dashboard → **Races → CEDC-deepracer-practice-race1** |
| Official docs | AWS DeepRacer developer guide (reward function input parameters) |

---

## 3. The stages

```
 Virtual training ──► Portal submission ──► Hidden-track evaluation ──► Physical race
 (AWS cloud sim)      (compact .tar.gz)     (3 trials, scored)          (selected teams)
```

### Stage 1: Virtual training
- Train on a **public practice track** (AWS Summit Raceway / Vegas).
- Optionally submit to the **practice race** to test. Its results are for development only and don't count.

**Practice race: `CEDC-deepracer-practice-race1`** (our racer name: `Charles_LeCrash`)

| | |
|---|---|
| Open | Sep 29 – **Oct 7, 2026 23:59** (Mountain Time) |
| Track | AWS Summit Raceway: 22.57 m, 91 cm wide, **counterclockwise** (DRfC: `Vegas_track`, default direction) |
| Race type | Time trial, community race |
| Ranking | **Best lap time**, individual lap |
| Entry | 1 consecutive lap; 3 laps total |
| Resets | Unlimited |
| Penalties | Off-track **+1 s**, collision +1 s |

Our local DRfC evaluation mirrors these rules (`run.env`: 3 trials, non-continuous, 1 s penalties).

### Stage 2: Official virtual evaluation
- Upload the packaged model to the portal.
- Status goes **QUEUED → EVALUATING → SCORED**.
- The evaluator runs **3 trials** with **organizer-controlled settings**, on a track we don't see.
- Recorded: **completion rate**, **public score**, **best completed lap**.
- If the evaluation itself fails (an infrastructure problem), contact the organizers with our team name and submission number.

**How the portal ranks teams:** first by **higher completion rate**, then by **lower public score** (time-based, from the official trials).

| Snapshot 2026-09-29 | Completion | Score | Best lap |
|---|---|---|---|
| #1 Shallow Learner | 100.00% | 5.6150 | 5.5420 |

What this tells us:
- **Completion rate comes first.** A 99% model ranks below *every* 100% model, however fast it is. Non-negotiable target: 3 of 3 trials finished.
- **Score ≈ average lap across trials** (5.615 vs a best of 5.542). Consistency matters, not just one fast lap.
- **The hidden track is short or fast:** a lap takes about 5.5 s. With our baseline speed (≤ 1 m/s), we'd need about 20+ s on a Vegas-length track. We'll have to raise the speed range once reliability is there.

### Stage 3: Physical race (selected teams)
- The organizers load our **same model** onto a real DeepRacer car.
- The physical track **may differ** from the training, practice and hidden tracks.
- We get **two chances to make adjustments** after the first run.
- The big question: does what works in simulation also work in the real world?

---

## 4. Step-by-step workflow

### Step 0: Setup (once)
1. Register the team on the portal and sign in.
2. Accept the organizer's invitation email and create the racer account on the DeepRacer training environment.

### Step 1: Create a model
**Learning & Models → Your Models → Create Model**

| Setting | Value |
|---|---|
| Race type | Time Trial |
| Track | AWS Summit Raceway / Vegas |
| Algorithm | PPO |
| Sensor | Single Camera |
| Action space / hyperparameters | Defaults to start, then tuned deliberately |

Paste in the reward function from the experiment folder and start training.

### Step 2: Evaluate and observe
Don't look only at the score. Watch the video and ask:
- Does it stay on the track?
- Does it zig-zag?
- Can it handle turns?
- Is it unnecessarily slow?
- Where does it usually fail?

### Step 3: Iterate, changing one idea at a time
```
Model 1: stay on track  →  Model 2: smoother steering  →  Model 3: steering + speed  →  ...
```
Log every model in [experiments/LOG.md](experiments/LOG.md).

### Step 4: Download the model
**Your Models → select model → Actions → Download Virtual Model** gives a model archive.

### Step 5: Package and validate locally (Windows)
The portal wants a **compact bundle** with a single checkpoint, not the raw download.

```bash
mkdir my_model && tar -xzf downloaded_model.tar.gz -C my_model
python cedc_package_model.py my_model/model cedc_submission.tar.gz
python validate_cedc_bundle.py cedc_submission.tar.gz
```

- Point the script at the folder containing `model_metadata.json` and `deepracer_checkpoints.json`.
- Checkpoint choice: `--checkpoint auto` (default: best, then last, then highest), `best`, `latest`, or an iteration number such as `--checkpoint 50`.
- The archive must be **≤ 90 MB**.
- Upload **only** `cedc_submission.tar.gz`. **Do not** upload the raw `model/` folder or a physical-car `model.tar.gz` that contains only `agent/model.pb`.

### Step 6: Submit
Upload `cedc_submission.tar.gz` on the portal, then wait for **SCORED**.

---

## 5. What the bundle contains

```
cedc_submission.tar.gz
├── cedc_submission_manifest.json   # selected checkpoint + file hashes
└── model/
    ├── model_metadata.json         # action space, sensor, algorithm
    ├── deepracer_checkpoints.json  # normalized to the selected checkpoint
    ├── <N>_Step-<S>.ckpt.data-*    # weights
    ├── <N>_Step-<S>.ckpt.index
    ├── <N>_Step-<S>.ckpt.meta
    ├── model_<N>.pb                # frozen graph
    ├── .coach_checkpoint
    └── .ready
```

---

## 6. Strategy

1. **Generalize, don't memorize.** We're scored on a hidden track and a different physical track. Avoid rewards tied to the practice track's waypoint indexes or a hard-coded racing line. Reward behaviour that works on any track: staying on track, heading aligned with the track direction, smooth steering, and progress per step.
2. **Finishing beats speed.** Completion rate across 3 trials is recorded. A consistent car that finishes every trial should beat a fast car that crashes in one of three.
3. **Build for sim-to-real.** Real cars punish jerky control. Keep the action space tight (a modest top speed, limited steering range) and reward smooth steering.
4. **Change one variable per model** and write it down. The goal is to learn *which* changes help, not to write the most complicated reward.
5. **Pick the checkpoint deliberately.** The "best" checkpoint from training isn't always the most stable. Compare checkpoints in evaluation or the practice race before submitting.
6. **Submit early.** Push the baseline through the portal to check the whole pipeline end to end.

---

## 7. Project layout

```
GrandPrixChallenge/
├── README.md                  # official kit instructions
├── README_CHALLENGE.md        # this file
├── cedc_package_model.py      # builds the compact submission
├── cedc_package_model.sh      # bash wrapper (use python directly on Windows)
├── validate_cedc_bundle.py    # checks the bundle before upload
└── experiments/
    ├── LOG.md                 # one row per model
    └── model01-baseline/
        ├── README.md          # config, results, observations
        └── reward_function.py
```

**Adding a new experiment:** copy `model01-baseline/` to `modelNN-<short-name>/`, change one thing, and fill in its README and a row in `LOG.md`.

---

## 7b. Future ideas (sim-to-real)

- **Isaac Lab / Isaac Sim** for photorealistic, massively parallel training, later or as a side project. Blockers: the result must become DeepRacer's exact TF1 `model.pb` (convert PyTorch weights into the DeepRacer graph, same input/output names and action scaling); we'd need to rebuild the car (public DeepRacer URDF, Ackermann steering, matching motor dynamics), the track meshes and the camera (FOV, mounting, 160×120 grayscale, 15 Hz). Realistically 1–2+ weeks. First milestone: a PyTorch copy of the DeepRacer network that reproduces a `model.pb`'s outputs.
- **Before the physical race (Oct 8), cheaper:** `DR_ENABLE_DOMAIN_RANDOMIZATION` (lighting and colours); test on the textured re:Invent worlds (`reinvent_carpet`, `reinvent_concrete`, `reinvent_wood`); an offline check of our `model.pb` on real photos or video of a DeepRacer track; pick the most reliable checkpoint, not the fastest.

## 8. Status

- [ ] Team registered on the portal
- [ ] DeepRacer invitation accepted
- [ ] Model 01 (baseline) trained and evaluated
- [ ] Baseline packaged, validated and submitted (pipeline check)
- [ ] Model 02+ iterations
- [ ] Final model selected
- [ ] Physical race
