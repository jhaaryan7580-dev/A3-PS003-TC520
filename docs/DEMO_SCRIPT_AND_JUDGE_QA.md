# Prototype demo script and judge Q&A

Aim for **about five minutes**, adjusted to the actual session’s time limit. This is a prepared script, not proof that a mentoring meeting occurred. Aryan can lead the interface walkthrough; Apeksha can explain the evaluation and communication sections. Introduce Dr Monika as the faculty guide; do not invent an official mentoring assignment or her attendance.

## Before the session

Launch `python prototype/launch.py`. Have the exact PEMS08 file ready locally, the final PDF, report and pseudocode open, and a terminal at the scientific project root. Run the release/test checks beforehand. Do not start a full training matrix during a short presentation. Keep manual input and real dataset playback visibly distinct.

## 0:00–0:35 — Aryan: the question

“Hi, I’m Aryan Jha, the team lead of Chauraha Sync. My teammate is Apeksha Benneshiroor, and our faculty guide is Dr Monika Puttaramaiah from BMS College of Engineering.

Our PS-003 question is simple: can five traffic operators train a useful shared forecasting model without exchanging their raw histories in the FedAvg weight-update loop? We compare that with centralised training, and measure accuracy, convergence, communication payload and who benefits—or loses—at client level.

This is a California PEMS08 benchmark simulation, not a live Bengaluru deployment.”

## 0:35–1:45 — Aryan: actual inference

Open **Forecast lab**, load the local dataset, keep the preset sensor/index, and point to the twelve lag values.

“These are twelve previous observations from one eligible held-out window. The model uses those values and a global index-cycle feature. It does not receive the target we’re about to compare against.

I’ll run the non-IID FedAvg checkpoint. This is an actual forward pass through the saved 513-parameter model, not a stored answer. Now we can compare its forecast with the recorded target and persistence, which simply repeats the last observation.

The table also runs the fixed centralised checkpoint on exactly the same inputs. Both are seed zero, chosen before the demonstration—not selected because they look best. I’ll compare twelve consecutive target slots too: each one uses its own previous observations, so this is one-step playback, not an hour-ahead rollout. These slice scores are only an illustration; our conclusions use the full test set and all three seeds.”

If the dataset is unavailable, show the clearly labelled manual mode and say there is **no recorded ground truth**. Do not pretend the manual history is PEMS08.

## 1:45–2:50 — Apeksha: the full evidence

Open **Experiment evidence**; show the main table, all seeds and quiet-group chart.

“We tested centralised, two local-only arrangements, and IID and non-IID FedAvg. The main comparison is fifteen runs: five arrangements across three seeds. We report mean and sample standard deviation on the same eligible test windows.

The IID FedAvg model is close to centralised in this setup, but that does not mean federation always wins. The group analysis matters. Our non-IID FedAvg model did not improve the quietest group over matched local-only; that hypothesis was refuted, so we report it rather than hiding it.

These common quiet-to-busy groups were defined using training sensor means. Relative error is total absolute error divided by total observed flow, not MAPE.”

Use the displayed exact numbers rather than memorising outdated PDF values. Avoid claims of statistical significance or universal superiority.

## 2:50–3:55 — Apeksha: the weight loop and cost

Open **Federation lab**; inspect one client, expand **Mentor walkthrough: how one FedAvg round works**, and play a short saved history. Show the matched-seed IID/non-IID curves and descriptive target.

“Each round broadcasts the global weights, trains each virtual client locally, and averages the returned parameters using client training-sample counts. All five clients participate. The simulator runs this in one NumPy process.

The graph here replays recorded validation convergence—it is not training again. Checkpoint selection uses validation MAE, never the test score.

The compact model has 513 float32 parameters, so its weight payload is 2,052 bytes. Five uploads and five downloads make 20,520 bytes per round. These are analytical model-payload bytes, not measured transport bytes. The raw-flow reference is also a stated lower-bound convention; we exclude serialization, headers, retries and shared-statistic traffic.”

Show the separately labelled 100-round diagnostic, noting that it has a larger budget and is not the original matched comparison.

## 3:55–4:45 — Aryan: reproduce the simulator

Show the scientific pseudocode and fresh-smoke commands. If the session allows execution, run the already rehearsed smoke in a **separate** directory and show its checker output.

“The interface is only a transparent wrapper. The original NumPy code, all twenty-one primary/diagnostic JSONs and saved weights remain unchanged. Anyone with authorised repository access can inspect the configuration, source hashes and exact results.

Fresh smoke training really executes the simulator, but its short-run scores are not final report results. Our release also includes automatic tests, artifact checks, source and compiled prototype files.”

## 4:45–5:00 — close

“Our contribution is a reproducible comparison and an inspectable working prototype, not a new FedAvg algorithm. It makes the accuracy–payload trade-off—and the quiet-client limitation—visible. We’d welcome feedback on these assumptions and the next useful experiment.”

## Questions judges may ask

| Question | Defensible answer |
|---|---|
| Is this Bengaluru traffic? | No. California PEMS08; no Bengaluru validation or geographic equivalence claim. |
| Are the five clients real intersections? | No. Five simulated operators, each with 34 sensor indices. Physical-intersection identity is not established. |
| Is the dashboard training? | The forecast is genuine saved-weight inference; convergence is labelled history replay. Actual training is the separate NumPy command. |
| Why 14 inputs? | Twelve scaled flow lags plus sine/cosine of the global target-index phase mod 288. |
| How do you avoid leakage? | Chronological splits, split-contained windows, train-only scaler/group statistics, validation-selected checkpoints; test scores are final evaluation. |
| Why drop zero windows? | Exact zero as source-missing is a modelling assumption, not a proven fact about every zero. All thirteen flow values must be positive. |
| Is IID truly independent? | It is an IID-style random sensor-membership control. True sample independence is not proven. |
| Why does local-only perform well? | It can specialise to each group and has five models rather than one shared model. We disclose that capacity difference. |
| Are training budgets identical? | No. Equal sample passes are not equal optimiser steps/trajectories. The central/local versus round schedules are stated explicitly. |
| Is privacy guaranteed? | No. The simulated weight-update loop avoids raw-history exchange, but weights can leak information. Shared global scaling is a simulation assumption. No differential privacy or secure aggregation is implemented. |
| Are bytes really measured on a network? | No. Exact float32 parameter sizes and exchange counts; protocol/serialization/scaler/metric overhead excluded. |
| Did FedAvg help quiet clients? | Not in the full-history H4 primary test; it was refuted. A data-scarcity H5 is unrun, not a result. |
| Why did the old PDF show different numbers? | Preliminary implementation/evaluation errors were corrected. The final README, report and PDF explicitly supersede those numbers and retain honest history. |
| Is this an independent external audit? | No. AI-assisted recalculation and reproduction checks are disclosed, not external human certification. |
| Does browser math exactly match NumPy bit-for-bit? | No. A validated numerical port, checked within 0.001 flow units; frozen report scores remain the original NumPy results. |
| What is innovative? | Transparent joint accuracy, cost and common-group analysis plus checksum-verified, usable inference and reproducibility. We do not claim a new FL algorithm. |
| Can evaluators run it without Node? | Yes: the compiled app and standard-library Python launcher are included. Source development uses the pinned Node/pnpm setup. |
| Does this finish mentoring? | No. The real prototype/pseudocode demonstration and attendance must occur under the organisers’ instructions. |
