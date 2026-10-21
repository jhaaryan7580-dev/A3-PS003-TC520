# Reproduce and verify PS-003

This guide separates verification of supplied evidence from fresh computation. The original 15 main and six diagnostic JSONs are frozen. Never overwrite them merely to repeat an experiment. New reproduction runs may have a different actual Git commit/environment, which should be recorded honestly in their own files.

## 1. Environment

Use Python 3.10 or newer, preferably an isolated environment. Package validation used Python 3.12.3; library versions are recorded in `artifacts/environment.json` and `requirements-tested.txt`. The normal requirements allow supported library versions. Exact float32 neural histories can differ slightly across environments; do not change claims or fabricate matches when that happens.

From the project root on Linux/macOS:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows, activate with `.venv\Scripts\Activate.ps1` in PowerShell, or `.venv\Scripts\activate.bat` in Command Prompt. The Python entry points below are the same. Dataset download can be done through the direct link in `data/README.md`; `sha256sum` is a Linux utility, not a Python dependency.

## 2. Review supplied evidence without a dataset

```bash
python -m pytest -q tests
python scripts/verify_release.py
python src/summarize_results.py --out artifacts/reproduced_summary
python src/demo.py --condition fedavg_non_iid --seed 0 --rounds-to-show 3
```

`verify_release.py` runs tests, checks all 15 main files and six diagnostic files, and verifies the preserved source/result manifest. The default demo explicitly replays saved results; it does not retrain or select a best seed. Summarisation writes full-precision CSV/JSON tables and four evidence figures **only into the new isolated output folder**. It rejects the release root, frozen subdirectories and nonempty output folders. Use a different fresh output name when repeating it. No NPZ is needed for this review, and the supplied reports/tables and figures must not be overwritten.

Equivalent direct hash-gated checks are:

```bash
python src/check_results.py \
  --dir results/full_results --config configs/full.json \
  --dataset-sha256 e1d03ce74e9fb79149e6e7c37c680214822c4a285baa2f42278cacabcd25c075

python src/check_results.py \
  --dir results/diagnostic_100rounds \
  --config configs/diagnostic_100rounds.json \
  --conditions fedavg_iid fedavg_non_iid \
  --dataset-sha256 e1d03ce74e9fb79149e6e7c37c680214822c4a285baa2f42278cacabcd25c075
```

The diagnostic contains only the two federated conditions, so its `--conditions` selection is necessary. Passing the main config to diagnostic files must fail. A checker PASS establishes artifact consistency, not independent reconstruction of all saved neural predictions.

## 3. Obtain the exact public dataset

```bash
curl -L --fail --output data/PEMS08.npz \
  https://raw.githubusercontent.com/guoshnBJTU/ASTGNN/main/data/PEMS08/PEMS08.npz
sha256sum data/PEMS08.npz
```

Expected SHA-256 is `e1d03ce74e9fb79149e6e7c37c680214822c4a285baa2f42278cacabcd25c075`. The source URL and hash were rechecked on October 19. Download availability does not establish redistribution/commercial-use rights. Do not commit the raw NPZ, virtual environment or secrets.

## 4. Recompute data audit and non-learned baselines safely

```bash
python scripts/reproduce_data.py
```

This wrapper invokes the unchanged audit and baseline functions but writes to `artifacts/reproduced_data/`, verifies the hash/window counts and compares baseline metrics to the supplied evidence. The original standalone `src/audit_dataset.py` and `src/baselines.py` overwrite their fixed `results/` filenames when run directly; use the wrapper in a frozen release.

Persistence uses the last observation of the same sensor. The daily-cycle baseline uses training-only means for each `(sensor, global slot modulo 288)`; it is neither pooled across sensors nor a verified timestamp-aware predictor.

## 5. Fresh working-prototype smoke demonstration

```bash
python src/demo.py --train-smoke
python src/check_results.py --dir artifacts/demo_smoke --config configs/smoke.json
```

This really runs the scientific training code on the smoke schedule and writes isolated outputs. The smoke uses restricted training windows and short schedules. Its errors are not final results and must not be used for tuning or performance claims. `artifacts/live_smoke_validation.txt` records the package-preparation smoke that passed on October 19.

## 6. Optional representative main reproduction

If a mentor asks for fresh learned-model reproduction, start with one fixed seed and write new outputs:

```bash
python src/run_experiments.py --data data/PEMS08.npz \
  --config configs/full.json --out artifacts/reproduced_main_seed0 \
  --conditions centralised fedavg_non_iid --seeds 0
```

The selected conditions/config schedule must remain unchanged. The raw primary JSONs retain their original metadata. A new run's genuine commit/environment identifies that new run, not the historical run. Two representative seed-0 main runs were independently reproduced during the original audit; all extended runs were artifact-audited rather than independently retrained.

## 7. Full fresh matrix, only if genuinely required

```bash
python src/run_experiments.py --data data/PEMS08.npz \
  --config configs/full.json --out artifacts/reproduced_full
python src/check_results.py --dir artifacts/reproduced_full --config configs/full.json
```

The five conditions × three seeds produce 15 files. Centralised and local-only use 30 epochs; FedAvg uses 30 rounds × one local epoch. Equal nominal sample passes are not identical optimisation-step or total-capacity budgets. Full retraining is unnecessary merely to inspect the release.

## 8. Separate extended-round diagnostic

```bash
python src/run_experiments.py --data data/PEMS08.npz \
  --config configs/diagnostic_100rounds.json \
  --out artifacts/reproduced_diagnostic \
  --conditions fedavg_iid fedavg_non_iid
python src/check_results.py --dir artifacts/reproduced_diagnostic \
  --config configs/diagnostic_100rounds.json \
  --conditions fedavg_iid fedavg_non_iid
```

These six 100-round files are supplementary. Keep the 30-round comparison primary. The independent diagnostic audit checked all six exact first-30-round prefixes and selected checkpoints but did not independently reconstruct round-31-to-100 predictions.

## Interpretation boundaries

The raw result JSONs, rather than rounded slides, govern numerical claims. Test is scored after validation selection, once per run. Sample SD is descriptive over three fixed seeds; no p-values, confidence intervals or statistical equivalence are claimed. Common evaluation groups are necessary for comparing proportional client disparities. A “noise floor” wording in the preserved decisions is interpreted as a descriptive random-partition reference, not statistical noise.

Bytes are tensor payload accounting: 513 × 4 × 5 × 2 = 20,520 per round. Shared train-derived scaling, virtual clients, omitted transport overhead and zero handling are stated assumptions. No formal privacy, Bengaluru validation or production deployment is demonstrated.

## Actual-account checks

The user personally uploads. Check organiser ownership, accepted collaborator/evaluator access, PDF download, the introduction video, mentoring participation and prototype demonstration in the real accounts. No GitHub push or settings change was made when preparing this package. The staged review/upload plan ends October 30; the official Level 2 window ends October 31 without a published time-of-day in the checked guideline.
