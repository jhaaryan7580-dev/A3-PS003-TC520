# A3-PS003-TC520 — Chauraha Sync

**Federated Traffic-Flow Prediction with Communication-Cost Evaluation**  
AIORI-3 · Smart Cities · BMS College of Engineering

**Current submission:** [complete deliverable index](SUBMISSION_INDEX.md) · [corrected PDF](presentation/A3-PS003-TC520_Chauraha_Sync.pdf) · [editable PPTX](presentation/A3-PS003-TC520_Chauraha_Sync.pptx) · [final evaluation report](reports/FINAL_EVALUATION_REPORT.md).

## Working prototype — launch without Node or retraining

**Published live demo:** [Open Chauraha Sync](https://chaurahalab-gzh27d5b.manus.space). Initial audited Manus version: `c63ad641b36095e4c341de1f7634317c3ce3bcb2`; a documentation-only refresh does not change its inference code, models or evidence. Publication receipts are under `artifacts/`. Manual forecasting works immediately; select your local exact PEMS08 NPZ for held-out playback. The application reads it in-browser and has no dataset-upload endpoint. The hosted page includes platform analytics; use the compiled local launcher below for strictly local operation. This is a scientific prototype, not a deployed city traffic system.

```bash
python prototype/launch.py
```

The included compiled **Forecast / Evidence / Federation / Submission** lab performs real saved-weight inference and compares centralised, non-IID FedAvg and persistence on the same input. Selecting the exact local PEMS08 file enables a gap-preserving 12-slot held-out trace with explicitly local MAE/RMSE. Manual input never invents ground truth. Experimental tables and matched-seed convergence remain labelled frozen evidence/replay, not live training. No dataset-upload endpoint, cloud account or GPU is needed. [Operation and scope guide](docs/PROTOTYPE_GUIDE.md) · [prototype source/build instructions](prototype/README.md) · [demo script and judge Q&A](docs/DEMO_SCRIPT_AND_JUDGE_QA.md).

The revised browser numerical/data suite passes **22 tests** plus **19 isolated real-browser UI checks**, separate from the **55 scientific/package tests**. Forty manual numerical fixtures per checkpoint agree with original NumPy inference within **0.001 flow units**; report scores remain the original NumPy values. The source, compiled app, lockfile and a local Python launcher are all supplied. The published live link supports Step 10; compiled files remain the direct-review backup. Hosted browser checks and their observed platform-telemetry boundary are recorded under `artifacts/`.

Prepared October 19 for the team's October 20 early upload target. See [official requirements and remaining external actions](docs/OFFICIAL_REQUIREMENTS_VERIFIED.md) and [upload order](docs/FINAL_UPLOAD_ORDER.md). No GitHub changes were performed while preparing this package.
The [final technical run-through](docs/FINAL_RUN_THROUGH.md) covers the scientific core, all artifacts, prototype, presentation, packaging corrections and remaining account/mentor checks.

## Team and contributions

**Aryan Jha — Team Lead and Primary Technical Contributor**  
Led the PS-003 problem interpretation, leakage-safe data pipeline,
NumPy simulator, centralised/local/FedAvg implementation, experiment
execution, three-seed audit, evaluation, browser prototype, packaging
and final submission integration.

**Apeksha Benneshiroor — Team Member**  
Participated in team orientation and project communication. Her role is
listed accurately without attributing technical implementation that is
not claimed in this repository.

**Dr. Monika Puttaramaiah — Faculty Mentor**  
Faculty mentor and academic guide. This README does not claim mentor
review or attendance unless separately recorded after the sessions.


This is a reproducible measurement study, not a new federated-learning algorithm. A compact NumPy MLP is compared under centralised, local-only and sample-weighted FedAvg training on public PEMS08 traffic flow. Five virtual clients represent sensor groups; they are not verified physical intersections. California results are not Bengaluru results. No formal privacy guarantee or production cellular-bandwidth measurement is claimed.

## AI assistance and validation status

Claude assisted with technical code/document review and checked the existing numerical scripts. A separate-process numerical reproduction reran two fixed seed-0 cases (centralised and non-IID FedAvg) to numerical tolerance. This is an **AI-assisted technical cross-check and numerical reproduction**, not an independent human, professional, or accredited audit or certification. The team must validate commands, claims and external submission obligations; no faculty review is implied. The core source and 21 original result JSONs were preserved; the enhanced package passes 55 tests and retains 41 preserved original entries. See [AI assistance and reproducibility details](docs/AI_ASSISTANCE_AND_REPRODUCIBILITY.md).

## Team introduction video

[Watch our AIORI team introduction](https://www.youtube.com/watch?v=jJh9rvyaiUA). This is the original orientation video, separate from the prototype demonstration.

## Primary results and validation status

The 30-round/30-epoch matrix is the primary experiment. Values are means ± sample standard deviations over seeds 0, 1 and 2.

| Training arrangement | Test MAE | Test RMSE |
| --- | ---: | ---: |
| Centralised | 13.862 ± 0.013 | 21.074 ± 0.008 |
| Local IID | 13.992 ± 0.031 | 21.221 ± 0.048 |
| Local non-IID | 13.898 ± 0.005 | 21.096 ± 0.012 |
| FedAvg IID | 13.964 ± 0.014 | 21.211 ± 0.031 |
| FedAvg non-IID | 14.209 ± 0.066 | 21.373 ± 0.079 |

Persistence test MAE is 16.078; per-sensor index-based daily-cycle MAE is 34.776. Every learned main run beats persistence in MAE and RMSE. FedAvg IID is less accurate than centralised in all three seeds, but is slightly lower than matched Local IID by seed differences of -0.030604554687744923, -0.008634277335549001 and -0.043784769237481314 (FedAvg minus Local; mean -0.02767453). This small difference is not a statistical tie or an equivalence claim. Under non-IID membership, FedAvg is worse than matched local-only by 0.3114613 MAE on average and in every seed. The quietest group's disadvantage relative to matched local-only training refutes H4.

FedAvg is therefore a conditional systems choice, not a demonstrated accuracy win. It may be considered when raw data must remain at clients or one shared model is required, but this study provides no privacy guarantee. Local-only's zero model-exchange count is not zero compute or raw-data governance cost: it uses five 513-parameter models (2,565 parameters total) versus one shared 513-parameter model. No scarcity or low-resource benefit was run or proven. On accuracy alone, the current history does not justify choosing non-IID FedAvg over local-only.

The separately labelled 100-round diagnostic gives MAE 13.873 ± 0.010 for IID and 14.064 ± 0.043 for non-IID, at 3.33 times the payload cost. Do not silently replace the primary matrix with these extended-budget results; observations through round 100 are not proof of a plateau. See [the final evaluation report](reports/FINAL_EVALUATION_REPORT.md) and generated [exact tables](reports/tables/).

> The earlier Level 1 presentation contains superseded preliminary numbers. The pooled daily-cycle baseline (about 89.7 MAE) was replaced by the per-sensor baseline (34.776 MAE), and the zero/preprocessing protocol also changed, so this is not a clean single-fix ablation. Earlier FedAvg validation metrics were mislabeled as test metrics; current labels, leakage handling, preprocessing and checkpoint provenance are consistent. The core optimizer is fixed, so no isolated optimizer change is claimed. Keep the artifact historical; the original run has no Git commit and must not be retrofilled.

## Quick start — no dataset or retraining needed for saved-result review

Use Python 3.10 or newer. A Python 3.12 environment was used for package validation. See [the reproduction guide](docs/REPRODUCE.md) and the recorded environment under `artifacts/`.

```bash
python -m pip install -r requirements.txt
python -m pytest -q tests
python src/check_results.py --dir results/full_results --config configs/full.json
python src/check_results.py --dir results/diagnostic_100rounds \
  --config configs/diagnostic_100rounds.json \
  --conditions fedavg_iid fedavg_non_iid
python src/summarize_results.py --out artifacts/reproduced_summary
python src/demo.py
```

The default demo is explicitly labelled **saved-results replay**. It does not pretend to retrain live or to measure live network traffic. The working simulator can also run a fresh smoke demonstration once the exact dataset is supplied; see [the mentor walkthrough and pseudocode](docs/MENTOR_DEMO_AND_PSEUDOCODE.md). Smoke scores are plumbing evidence, not final performance claims.

## Dataset and full reproduction

The enhanced package also includes **actual inference from verified saved checkpoints**, not only JSON replay. Follow [the saved-model demonstration](docs/SAVED_MODEL_DEMO.md) to run a real forward pass without training and view preset [held-out forecast examples](figures/heldout_forecast_examples.png). The examples are illustrative seed-0 segments, not replacements for three-seed test statistics. The separate [validation-payload frontier](reports/VALIDATION_PAYLOAD_FRONTIER.md) derives budget-to-target findings from existing histories; it does not invent test errors by round. The enhanced suite passes 55 tests, with 41 preserved original entries.

Follow [data/README.md](data/README.md) to obtain `PEMS08.npz` and verify SHA-256. The raw benchmark is intentionally excluded from the GitHub package. Do not infer redistribution permission from a public download URL.

The protocol uses channel 0, 17,856 five-minute time steps, 170 sensors, a chronological 70/15/15 split, 12 lags plus global index-cycle sine/cosine features, and complete-case windows. Exact-zero exclusion is an explicit modelling assumption. Eligible windows are 2,098,136 train, 448,263 validation and 448,533 test. The MLP has 513 parameters. FedAvg resets local Adam state each round; the shared scaler uses valid training values only. Checkpoints are validation-selected, with one final test scoring per run.

Full training commands and instructions for writing independent outputs without overwriting the frozen results are in [docs/REPRODUCE.md](docs/REPRODUCE.md). No full retraining is necessary just to inspect this submission.

## Submission materials

The final package includes an evaluation report, exact CSV/JSON tables, evidence plots, executable simulator, tests, validation scripts, mentor pseudocode/walkthrough, and the prescribed AIORI presentation in PDF plus editable PPTX. [The compliance check](docs/AIORI_REQUIREMENTS_CHECK.md) separates scientific completion from external account/attendance/upload actions.

Current presentation: [corrected final PDF](presentation/A3-PS003-TC520_Chauraha_Sync.pdf) · [editable PPTX](presentation/A3-PS003-TC520_Chauraha_Sync.pptx). Upload the corrected PDF again; the earlier Level 1 figures are superseded.

The official team page listed Chauraha Sync as **Qualified for Level 2** when checked on October 19. Final uploads, evaluator access, mentoring attendance and the mentor prototype demonstration remain actions the team must verify in its actual accounts. No remote GitHub changes were made while preparing this package.

Use [the item-by-item submission checklist](docs/SUBMISSION_CHECKLIST.md) for completion. It does not guarantee regional or final selection.

## Contacts

**Aryan Jha · Team lead:** aryanjha.ad26@bmsce.ac.in
**Apeksha Benneshiroor:** apekshabenneshiroor.ec26@bmsce.ac.in  
**Dr. Monika Puttaramaiah · Faculty mentor:** monika.mel@bmsce.ac.in

## Sources

[AIORI official guideline](https://portal.aiori.in/aiori-3/hackathon-guideline/) and [team qualification list](https://portal.aiori.in/aiori-3/selected-teams/); [McMahan et al. — FedAvg](https://proceedings.mlr.press/v54/mcmahan17a.html); [ASTGNN benchmark package](https://github.com/guoshnBJTU/ASTGNN); [Caltrans PeMS provenance](https://dot.ca.gov/programs/traffic-operations/mpr/pems-source).
