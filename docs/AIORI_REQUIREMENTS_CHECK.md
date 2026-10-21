# AIORI PS-003 requirement and submission check

Checked on **19 October 2026** against the supplied PS-003 brief and the live official guideline. Scientific completion is distinct from upload completion and mentor attendance.

## Published team status

The official selected-teams page lists **A3-PS003-TC520 — Chauraha Sync — Aryan Jha — BMS College of Engineering — Qualified for Level 2**. This independently confirms the published qualification status; it does not prove future Level 2 submission or mentoring attendance. [1]

## PS-003 scientific requirements

**One public dataset and 3–5 simulated clients — complete.** PEMS08 channel 0, 170 sensors, five clients of 34 sensors. These are virtual sensor groups, not verified real intersections. California benchmark results are not Bengaluru results. Evidence: `results/dataset_audit.json`, `src/data.py`, `configs/full.json`.

**One compact forecasting model and FedAvg — complete.** A NumPy 14–32–1 ReLU MLP with 513 float32 parameters, five-client participation, sample-count-weighted averaging and locally reset Adam state each round. Evidence: `src/models.py`, `src/train.py`, tests.

**Chronological splitting without test leakage — complete for the reviewed protocol.** Fixed 70/15/15 chronology, windows confined within each split, train-only valid-value scaler and partition statistics, global index-cycle features. Checkpoints use minimum validation MAE; chosen models are then scored on test. Evidence: `src/data.py`, `src/train.py`, boundary/leakage tests and independent audits. Shared scaler computation is a simulator assumption, not a distributed privacy mechanism.

**IID and non-IID comparison — complete.** Seeded random sensor membership for IID-style assignments; deterministic valid-training-mean quiet-to-busy bands for non-IID. Both partitions have matched local-only references. Models are also evaluated on the same canonical groups so membership differences do not masquerade as fairness effects.

**MAE/RMSE, accounted bytes and convergence — complete.** Raw JSONs contain test MAE/RMSE, per-client relative-error diagnostics, validation histories and payload counts. Float32 payload is 2,052 bytes/model and 20,520 bytes/round. Counts are simulation accounting, not measured mobile-network traffic. Evidence: `results/full_results/`, `results/diagnostic_100rounds/`, generated tables/figures.

**Three random seeds — complete.** Five primary conditions × seeds 0, 1, 2 = 15 main results. Two federated diagnostic conditions × three seeds = six supplementary results. Mean and sample SD are computed from full-precision values, not rounded console output.

**Centralised and federated baselines / simulator / report — complete in the local release package.** Source implements the simulator and matched comparisons; deterministic persistence and per-sensor daily-cycle baselines are included. The evaluation report and the updated AIORI-template presentation are supplied for upload. Their existence here is not proof they have been pushed to GitHub.

**No live cameras, city-wide deployment or formal privacy guarantees — respected.** No such feature or claim is required by PS-003. A dashboard, GRU, new dataset, longer horizon, differential privacy or secure aggregation is not a missing must-have.

## Official repository and submission steps

**Steps 1–4: template repository, team-code name, collaborators, ownership transfer.** The user reports completion. Qualification is publicly confirmed, but the repository remains inaccessible to the Manus GitHub session. A private repository or transfer redirect can explain that; this is not proof the user's link is broken. The team should inspect the repository's actual owner, access list and evaluator access while logged in. Retain the existing repository and organiser ownership; do not create a replacement or rename it merely because the PS PDF's general naming wording differs from the guideline. The live guideline specifically uses the team code. [2]

**Step 5: PDF in the prescribed structure.** A preliminary Level 1 PDF was previously submitted. Its numbers are superseded. Upload the corrected final PDF from `presentation/` after team review, retain the preliminary PDF as an explicitly labelled historical artifact, and do not imply the corrected results existed at the earlier upload date. PPTX is an editable convenience; PDF is the official required format. [2]

**Steps 6–7: introduction video and repository link.** The team supplied [the actual introduction URL](https://www.youtube.com/watch?v=jJh9rvyaiUA), now included in the final README and presentation. The fetched page metadata matches “AIORI 3 | Team Chauraha Sync | PS-003 Federated Traffic-Flow Prediction,” dated October 14. The extractor also showed a player-unavailable message, so this is not a successful playback test; check that mentors can actually play it in an independent browser/account. The private GitHub README was inaccessible to this session, so its current link insertion remains user-reported rather than independently verified. The prototype demonstration is separate from the original orientation video. [2]

**Step 8: mentoring sessions.** Attendance is not established by the experiment files or by Level 2 qualification. Attend the official sessions when scheduled and record genuine dates, feedback and changes in `docs/MENTORING_AND_WORK_LOG.md`. The guideline window is October 16–31, with two sessions for each problem category; follow the organiser's actual schedule rather than our suggested work days. [2]

**Step 9: code and supporting material in GitHub.** The package is prepared here for the user to upload. This step remains an external action until the team has pushed and checked the repository files. Keep source, tests, configs, data instructions, raw result JSONs, tables, figures, evaluation report, pseudocode and presentation. Do not push credentials, environments or the large raw benchmark file. [2]

**Step 10: working demonstration.** The confirmed published working demo is [Chauraha Sync](https://chaurahalab-gzh27d5b.manus.space). Retain this link in the actual GitHub README. The compiled portable app, source and Python launcher remain direct-review backups under the guideline's final-files alternative. Actual saved-weight inference is distinct from the labelled experimental-history replay; fresh NumPy smoke training remains a separate command. Demonstrate the prototype and pseudocode to the mentor as instructed. Hosting does not substitute for required mentor interaction or imply real-city deployment. [2]

## What cannot be confirmed from this workspace

We cannot attest that the final package is uploaded, that all collaborators accepted access, that organiser ownership is still correct, that the video URL is accessible, that mentoring sessions were attended, or that the mentor has seen the prototype. These need checks/actions in the team's actual accounts. We also cannot verify a historical pre-training Git commit: the original runs say `code_commit: unavailable (not a git repository)`. Preserve that truth and use new manifests only to identify the current source snapshot.

## Completion rule

The technical project passes. Final submission is complete only after the team verifies external access, attends required mentoring, demonstrates the prototype, uploads the final files and checks their GitHub rendering/downloads. The public guideline's Level 2 work window ends October 31; the early upload target is **October 20**, with **October 30** reserved for the final access/check buffer. No submission time-of-day or timezone is specified on the checked page, so do not invent one. [2]

## References

[1]: https://portal.aiori.in/aiori-3/selected-teams/ "AIORI official team qualification list"
[2]: https://portal.aiori.in/aiori-3/hackathon-guideline/ "AIORI official hackathon steps and milestones"

The attached `docs/PS-003_official.pdf` is the problem-specific requirement source. `docs/Proposed-structure-hackathon.pdf` is the supplied presentation template.
