# Code packaging changelog

This file records the packaging changes made for the release candidate. **No historical result JSON, source training code, configuration bytes, audit output, or result metadata was modified.**

## Changes

- Strengthened `src/check_results.py` while preserving `check_dir(path, cfg, conditions)` compatibility:
  - optional condition subsets and optional expected dataset SHA-256;
  - safe FAIL reporting for malformed JSON, missing files/keys, non-finite values, and wrong filename identity;
  - supplied-config hash and full metadata-config equality checks;
  - complete histories, unique epochs/rounds, local five-client coverage, checkpoint argmin and checkpoint value checks;
  - test counts, pooled MAE/RMSE, client gaps, and FedAvg communication-byte identities.
- Added `src/demo.py`. Its default mode is explicitly labelled **precomputed saved-results replay**; `--train-smoke` delegates the immutable runner and writes isolated `artifacts/demo_smoke/` output only.
- Added `scripts/verify_release.py` for tests, full 15-result validation, diagnostic six-result validation, and tolerant optional audited-source manifest checks.
- Added `tests/test_result_validation.py` covering wrong config, malformed JSON, missing files, incomplete local histories, bad checkpoint values, pooled RMSE corruption, and subset conditions.
- Updated `.gitignore` to exclude raw NPZ files and smoke-demo artifacts.
- Kept `requirements.txt` as minimum-supported dependency ranges; added `requirements-tested.txt` and `artifacts/environment.json` for the actual validation environment.

## Scope limits

No new algorithm, dashboard, live-network claim, neural-training result, or historical-results metadata was introduced.

## Final parent-side preparation — October 19, 2026

The replay no longer ranks validation minima across different seeds or unweighted local ensembles; it displays only the explicitly requested saved run. Three focused demo tests bring the final suite to **35 passing tests**. A fresh smoke demonstration actually ran the unchanged training code in `artifacts/demo_smoke/` and passed the checker; its scores are plumbing evidence only. A separate data/baseline wrapper reproduced the dataset audit and deterministic metrics without overwriting `results/`.

The preservation manifest now includes the original `src/meta.py`, for **41 unchanged entries**. Original scientific routines, configs, raw JSONs and frozen decisions remain byte-identical. New helpers, documents and release manifests identify present packaging work, not a fabricated historical training commit.

The final report distinguishes gap changes from overall relative-error changes, explains local-only ensemble capacity, and states exact validation targets and byte crossing. Pseudocode filters sensor-time windows independently and preserves central/local Adam state while resetting it each FedAvg round. Convergence figures show the full range with a labelled log axis. The introduction link is included; GitHub calls were read-only and no remote change was made.

## Enhanced release — October 19, 2026

Added genuine saved-model inference, two verified fixed seed-0 checkpoints, an isolated exporter and preset held-out forecast illustrations. Both original runs reproduce before export; no frozen learning routine, config or result file changed. Added a posthoc validation-only payload frontier from existing histories, with explicit target censoring and exact cumulative-byte fields. It does not infer test accuracy by round or relabel retrospective hit cost as the completed-run cost.

The suite now passes **55 tests**, including feature parity, input guards, parameter shape/checksum checks, exported-model provenance and frontier semantics. Locally generated raw trace CSVs are excluded from the ZIP/GitHub; model weights, figures and metric summaries are included. Original source/result hashes remain unchanged. The original 35-test log is historical preparation evidence; enhanced logs record the later gate.
