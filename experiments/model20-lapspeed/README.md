# Model 20: steeper lap-time bonus (speed push)

**Why (2026-10-07 17:05):** wb7-end is already clean on the portal (5.814); the gap to the leader (5.610) is pace. Faster corner actions beyond J29 make the closed-loop expert worse (half step: A to Z 7.5 s / 1.7 off per lap vs 6.9 / 1.0), so push speed through the reward instead. Model 18's lap bonus 300*(v/2)^2 pays only ~6 % more for a 3 % faster lap; Model 20 pays 1500*(v/3)^6, ~20 % more.

**Recipe:** Model 18 (E3 free racing + J29 actions) with that bonus; from `cedc-m18w-z12-end` (10-trial A to Z: 9/10 clean, median clean 5.41 s); A to Z only, lr 0.0001, 30-min legs; hourly 10-trial A to Z test with wb7-end as baseline (`logs/m20_screen.txt`).

## Results

(pending)
