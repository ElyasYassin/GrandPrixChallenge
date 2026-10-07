# Model J31 (jason): J29 wb16-end settled at a very low learning rate

**Why:** portal #67: J29 wb16-end **9.044 / best lap 5.664** (fastest best lap the team has had; leader's score 5.615) with one off-track (~3.4 s). Pace is there; consistency isn't. J30 (E3 reward stack) got worse locally (3–4 off-tracks vs 1) and was stopped. J31 keeps J29's reward and actions and fine-tunes from wb16-end at **lr 0.00003** (J29 used 0.0001) so the policy settles instead of moving; two simulators, A to Z + re:Invent 2018 as in J29, 30-min legs, each leg tested on A to Z (5 trials) for off-tracks first.

## Results

**Stopped after ~35 min (10:30)**: wb7-end scored 5.814 clean on the portal (#68), so training continues from wb7 instead (J32). Snapshot `cedc-m31-jason-stop`.
