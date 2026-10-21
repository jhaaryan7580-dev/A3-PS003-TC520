# Chauraha Sync — verified AIORI requirements

Team **A3-PS003-TC520 · Chauraha Sync**, BMS College of Engineering. Checked against five official sources on **19 October 2026**. The team’s early upload target is **20 October**. The published Level 2 Steps 8–10 window ends **31 October 2026**; no closing time or timezone is stated. Do not wait for the last day.

## The verdict

The scientific core and the prepared technical deliverables satisfy the scope of PS-003: a public-dataset, five-client traffic forecaster and FedAvg simulator with a centralised comparison, chronological splitting, IID/non-IID analysis, three seeds, MAE/RMSE, convergence and communication accounting. The report’s communication results are explicitly analytical float32 model payloads, not measured wire traffic.

This is **technical readiness**, not certification that every external AIORI step is complete. The user reports that the private repository, collaborator invitations, ownership transfer, Level 1 presentation and introduction-video link are already in place. Do not recreate or transfer the repository again. Confirm authorised evaluator access from the user’s logged-in account. The actual upload of the new package and required mentoring interaction remain user actions.

## Requirement-to-evidence map

| Official requirement | Prepared evidence | Status / boundary |
|---|---|---|
| Public traffic dataset; 3–5 simulated clients | PEMS08 provenance, audited hash, five groups of 34 sensor indices | Complete locally; no physical-intersection or Bengaluru mapping claimed |
| One compact forecaster and FedAvg | Original NumPy 14–32–1 MLP, 513 parameters; sample-weighted aggregation | Complete; all five clients participate |
| Centralised versus federated | Five learned arrangements, 15 primary runs | Complete; local-only comparisons added |
| Chronological splits; avoid leakage | Train-only scaler, split-local complete-case windows, global index phase | Complete under documented assumptions |
| IID/non-IID, accuracy, convergence | Three seeds, MAE/RMSE, per-client and common-group metrics, validation histories | Complete; descriptive SD, no significance/equivalence claim |
| Communication-cost analysis | 2,052 B model and 20,520 B/round; primary/diagnostic budgets and raw-flow lower-bound reference | Complete analytical accounting; excludes protocol/serialization/scaler/metric overhead |
| Final report across three seeds | `reports/FINAL_EVALUATION_REPORT.md`, exact tables, figures and frozen JSONs | Complete locally |
| PDF following the prescribed structure | `presentation/A3-PS003-TC520_Chauraha_Sync.pdf`, editable PPTX | Complete locally; original 11-section order and AIORI styling retained |
| Prototype with pseudocode to mentor | NumPy simulator, saved-model inference, portable browser lab, walkthrough/pseudocode | Prepared; actual mentor demonstration not confirmed |
| Private GitHub collaboration and transfer | Existing user-provided repository | User reports done; evaluator access must be checked by the user |
| Team introduction video and repository link | https://www.youtube.com/watch?v=jJh9rvyaiUA | User supplied/published; confirm playback and README insertion, do not re-record unnecessarily |
| Guideline Step 9: all final files in GitHub | One complete source/evidence/prototype submission folder | User uploads personally |
| Guideline Step 10: live demo link, or final deliverable files if live demonstration is unavailable | Published demo: https://chaurahalab-gzh27d5b.manus.space; compiled portable app and source | Manus publication confirmed; user must retain link in actual GitHub README; compiled files remain backup |
| Guideline Step 8: mentoring as scheduled | Track 3 email received 20 Oct: 23 Oct 7:30–8:30 PM IST and 28 Oct 7:30–8:30 PM IST; Meet links and mailing list recorded in `docs/MENTORING_AND_WORK_LOG.md` | Schedule confirmed; attendance, demonstration and feedback remain pending until the team actually participates |

## What the official pages actually say

The [PS-003 brief](PS-003_official.pdf) requires the simulator, baselines, model, IID/non-IID evaluation, communication/convergence analysis, three-seed report, PDF and prototype/pseudocode demonstration. It excludes a requirement for live cameras, city-wide deployment or formal privacy guarantees.

The [official guideline](https://portal.aiori.in/aiori-3/hackathon-guideline/) says:

> Step 9: Complete and submit all the required files, documents, source code and supporting materials to your GitHub repository before the specified deadline.
>
> Step 10: Include a link to a live working demo in your GitHub repository. If your solution cannot be demonstrated live, upload the final deliverable files directly to the repository for evaluator review.

Steps 8–10 are listed for **16–31 October**, with **two sessions for each problem category**. The public guideline links no final-submission Google Form. **Do not invent a form or make an unverified form a mandatory step.** Follow any additional official instructions the organisers send privately.

The [Selected Teams page](https://portal.aiori.in/aiori-3/selected-teams/) explicitly lists **A3-PS003-TC520 | Chauraha Sync | Aryan Jha | BMS College of Engineering | Qualified for Level 2**. This is not final-selection or prize evidence.

The public [mentoring page](https://portal.aiori.in/mentoring-schedule/) did not list the Smart Cities details when checked, but the team subsequently received an organiser email on 20 October 2026 confirming Track 3 sessions for 23 and 28 October, with Google Meet links. Preserve that email and record actual participation after each session. General footer contact: **info@iifon.org**; not a specifically verified mentoring desk.

The problem brief’s generic team-name repository wording differs from the guideline’s explicit team-code convention. The existing **A3-PS003-TC520** name follows the guideline and the already qualified team identity. **Do not rename it during this submission.** Seek clarification only if the organisers request a change.

## Required presentation order

The [supplied official template](Proposed-structure-hackathon.pdf) has eleven sections: cover; Abstract/Problem Description; Background; Literature & RFC Review; Proposed Solution; Solution Optimization; UML Architecture; Data Flow Diagram; Deployment Timeline; Bibliography; Thank You. It requests a before/after optimisation table, architecture/data-flow visuals, deployment milestones and numbered references. The template filename is a reference to its structure, **not a requirement to rename the team’s final presentation to `Proposed-structure-hackathon.pdf`**.

## Remaining external checks

Upload the new complete package and retain its confirmed live-demo link; make the corrected PDF the clearly linked current version; ensure the video plays; confirm authorised AIORI/evaluator access; attend the two confirmed mentoring sessions and demonstrate the prototype/pseudocode as instructed. The live prototype is published, but no attendance, mentor acceptance, GitHub upload, final-form submission or winning outcome is asserted until actually verified. Hosting is not evidence of real-road deployment or a privacy guarantee.

## Sources

1. Supplied official [PS-003 PDF](PS-003_official.pdf), two pages.
2. Supplied [presentation-structure PDF](Proposed-structure-hackathon.pdf), eleven pages.
3. [Official AIORI-3 guideline](https://portal.aiori.in/aiori-3/hackathon-guideline/).
4. [Official selected-team list](https://portal.aiori.in/aiori-3/selected-teams/).
5. [Official mentoring-schedule page](https://portal.aiori.in/mentoring-schedule/) (redirect target of `/aiori-3/mentoring-schedule/`).
