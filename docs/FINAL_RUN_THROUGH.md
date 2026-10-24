# Chauraha Sync — final technical run-through

The revised submission is technically ready under the documented benchmark assumptions. Five bounded read-only reviews covered the scientific implementation, all result artifacts, report/presentation, portability and official compliance. The focused prototype review and actual-browser checks were separate. This is AI-assisted technical verification, not human accreditation, a guarantee against every possible bug, organiser acceptance or a winning prediction.

## Scientific implementation and frozen evidence

Chronological 70/15/15 splits, split-contained 12-lag windows, global index-cycle features, training-only scaling/group means, complete-case zero filtering, the 14–32–1 NumPy MLP, local Adam reset and sample-count-weighted FedAvg were cross-checked. Minimum validation MAE selects checkpoints; final test scores are not per-round tuning inputs. The scientific/package gate passes **55 tests**, both saved-result checkers, and **41 protected source/result entries**. No new learned experiment was introduced.

Independent recalculation of all 15 primary and six diagnostic JSONs matches the exact summary: primary MAE means are 13.862423 centralised, 13.991692 local IID, 13.897819 local non-IID, 13.964017 FedAvg IID and 14.209280 FedAvg non-IID. Sample SD uses ddof=1. Every learned artifact reports 448,533 scored test windows. Canonical group counts are 86,252, 90,550, 90,559, 90,494 and 90,678. The six diagnostic histories have exactly matching first-30-round prefixes. All recorded checkpoint argmins and communication endpoints were consistent.

Reported bytes remain analytical float32 model payloads: 2,052 B/model, 20,520 B/round, 615,600 B/primary federated run and 2,052,000 B/diagnostic run. These are not measured wire bytes. Three seeds are descriptive rather than a statistical equivalence proof. Complete-case filtering, overlapping windows, common-group membership provenance and five-model local-only capacity are explicit limitations. Diagnostics were artifact-checked, not fully independently retrained.

## Working prototype

The compiled app genuinely executes the two fixed seed-0 saved models. It now compares both models and persistence on the same window; manual mode invents no recorded truth. Its optional 12-slot contiguous held-out trace uses each target's preceding observed history, leaves missing windows as gaps and labels its local scores as illustrations, not new experimental results. The frozen evidence view retains all arrangements, both metrics and three-seed sample SD. Both deterministic baselines score the same test cohort.

The browser numerical/data suite passes **22 tests**. Both development and compiled-app runs pass **19 isolated real-browser checks**, including actual local PEMS08 inference, invalid-input recovery, rejected-file retention, trace generation, metric/seed controls, 100-to-30-round switching, clipboard fallback, visible pseudocode, navigation, unloading and narrow-screen layout. No unhandled browser errors or application POST/upload requests were observed in these paths. Forty numerical unit-fixture histories per model retain NumPy parity within 0.001 flow units. A real-browser check also confirms the standalone report's embedded figures load without unresolved relative resources.

Convergence controls replay saved histories; they do not train. Actual fresh smoke training is the separately documented NumPy command. The front end is not live city forecasting, an hour-ahead autoregressive rollout, physical-intersection geography or a privacy guarantee.

The published prototype is [Chauraha Sync](https://chauraha-sync.jhaaryan7580.workers.dev/), deployed on Cloudflare Workers/Pages, corresponding to verified prototype build c63ad641b36095e4c341de1f7634317c3ce3bcb2. Root, standalone report and PDF downloads return HTTP 200. The application passes all 19 real-browser controls. The production deployment omits third-party hosting analytics and telemetry scripts (__manus__ tracking hooks were excluded from the deployment bundle). No app-origin POST or raw NPZ transfer occurs during the tested workflow. The compiled local launcher remains available as the strictly offline alternative. Historical verification receipts remain catalogued under artifacts/PROTOTYPE_V3_LIVE_BROWSER_CHECKS.json. No app code, scientific results or model weights were changed to resolve this deployment migration.

## Report and presentation

All eleven official-template sections were reviewed, including results, formal module diagram and data flow. New test metrics agree with the raw JSONs; primary and diagnostic budgets are distinct. No old mislabelled Level 1 number is a current performance claim. Team contacts, prepared date, links and author metadata remain present.

Two clarity limitations were corrected: slide 8 now defines its target as 1.05 times the seed-matched best centralised validation MAE, and bibliography [4] distinguishes supplied local PDFs from the public guideline URL. The actual QR asset was decoded and matches the user-supplied repository URL. That proves payload correctness, not authenticated redirect/evaluator access.

## Packaging problems found and corrected

The old summary command could overwrite delivered tables/figures. The packaging analysis helper now writes only to a separate new/empty output tree; the root, frozen subtrees and nonempty destinations are rejected. Recalculated summary JSON equals the frozen summary exactly, and all protected table/figure hashes stayed unchanged in the isolated regeneration test. Learning code and raw results were not changed.

A separately downloaded Markdown report had relative links that would not travel with it. The app now provides self-contained HTML report, mentor and reproduction downloads, with embedded figures and explicit full-package source paths instead of broken local links. Canonical Markdown stays in the full repository tree. The submission verifier checks their canonical-source digests and rejects unresolved local resources.

The package includes source, lockfile, compiled app and a Python standard-library launcher. Raw NPZs, virtual environments, dependency directories, secrets, caches, private strategy and local raw trace receipts are excluded. Root Markdown links, compiled asset connections, all 21 original-source references, checkpoint hashes and presentation download hashes are checked by `scripts/verify_submission.py`. Clean extraction and the original scientific gate are checked before sealing the final ZIP.

## AIORI alignment and remaining actions

Current official guidance retains the public-dataset, 3–5-client FedAvg comparison, chronological leakage safeguards, IID/non-IID, accuracy/bytes/convergence, three seeds, report/PDF and prototype/pseudocode demonstration. Chauraha Sync is listed as qualified for Level 2, not selected for a prize. The public Steps 8–10 window ends 31 October; 20 October is the team's early upload target, with no published closing timezone verified. The guideline offers a live-demo link or uploaded final files where live demonstration is unavailable. The confirmed published link is now in the supplied README/index; the portable compiled app remains the file-review backup. User GitHub insertion/upload is still pending.

The public mentoring page supplies no confirmed Smart Cities date/link. Obtain the actual instructions and complete genuine mentoring/prototype interaction. User-reported repository ownership transfer, collaborator invitations and earlier video/PDF uploads are not re-created or independently certified here. Before pushing, confirm that the original repository URL/QR redirects correctly for authorised evaluators, that invited access is accepted, and that the video and final PDF open. Change the link only if the actual transferred canonical URL requires it. Do not rename or transfer the repository again merely because anonymous access is unavailable.

The remaining work is personal GitHub publication, review from the actual repository, a rehearsal and organiser/mentor confirmation. Upload extracted folders rather than only the ZIP; retain the existing `.git`, genuine history and introduction-video link. Publish the corrected current files together rather than manufacturing dated work or postponing an incomplete submission until the deadline.

## Evidence locations and sources

The local check receipts are under `artifacts/`: `PROTOTYPE_V2_NUMERICAL_TESTS.txt`, `PROTOTYPE_V2_BROWSER_CHECKS.json`, `PROTOTYPE_V2_COMPILED_BROWSER_CHECKS.json`, `PROTOTYPE_V2_SCIENTIFIC_RELEASE_CHECK.txt`, `SAFE_SUMMARY_REGENERATION_CHECK.txt`, `QR_PAYLOAD_CHECK.json` and `STANDALONE_REPORT_BROWSER_CHECK.json`. Final archive hashes are in `artifacts/DELIVERY_SHA256.json`. Use the [complete submission index](../SUBMISSION_INDEX.md), [upload order](FINAL_UPLOAD_ORDER.md) and [official requirement memo](OFFICIAL_REQUIREMENTS_VERIFIED.md).

Official sources: [PS-003](PS-003_official.pdf), [supplied presentation template](Proposed-structure-hackathon.pdf), [AIORI guideline](https://portal.aiori.in/aiori-3/hackathon-guideline/), [selected teams](https://portal.aiori.in/aiori-3/selected-teams/) and [mentoring schedule](https://portal.aiori.in/mentoring-schedule/). They were rechecked in the final read-only review on 19 October 2026. Further private organiser instructions, if any, take precedence over assumptions about unpublished steps.
