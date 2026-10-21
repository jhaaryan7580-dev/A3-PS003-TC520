# AI assistance and reproducibility

## Purpose and scope

This note documents how AI assistance was used in preparing the public package and what was actually checked. It is a disclosure and reproducibility aid, not a certification.

## AI assistance disclosure

Claude assisted with technical code review, numerical-script review, document editing and consistency checking. The assistance used the existing repository code and preserved artifacts; it did not add a new learning algorithm, change the core optimizer, conduct new neural-model training, or create a new experimental condition. The team remains responsible for validating the commands, interpreting the results, and completing external submission, account and attendance obligations.

The terms **independent audit** in the historical filenames are provenance labels only. `reports/INDEPENDENT_MAIN_AUDIT.md` and `reports/INDEPENDENT_DIAGNOSTIC_AUDIT.md` should be understood as historical **AI-assisted audit records**, not as an independent human, professional, faculty, accredited or regulatory audit. No faculty review or mentoring attendance is asserted by this disclosure.

## What was checked

- The existing numerical scripts were checked, and a separate-process numerical reproduction reran two fixed seed-0 cases: centralised training and non-IID FedAvg. Their reported outputs matched to numerical tolerance.
- The historical main audit record reports 793 checks. The historical diagnostic record reports 1,408 checks and exact first-30-round prefixes for all six diagnostic runs. These counts describe artifact/checker review, not human certification or a fresh reimplementation of every run.
- The enhanced package passes **55 tests** and retains **41 preserved original entries**. The core source and **21 original result JSONs** remain unchanged.
- The primary experiment remains the frozen 30-round/30-epoch matrix. The 100-round files are a separately labelled diagnostic: observations through round 100 do not prove a plateau, eventual convergence, or an operational stopping point.

## Numerical interpretation that must be preserved

- For matched IID conditions, FedAvg minus Local IID MAE is **-0.030604554687744923**, **-0.008634277335549001**, and **-0.043784769237481314** for seeds 0, 1 and 2, with mean **-0.02767453**. FedAvg is lower in each of these three saved comparisons, but the small difference is not a statistical tie or an equivalence claim; no significance or equivalence test was run.
- For matched non-IID conditions, FedAvg is worse than local-only by **0.3114613 MAE on average**, and is worse in every seed. Therefore the current large history does not justify choosing non-IID FedAvg over local-only for accuracy alone.
- FedAvg can still be a conditional systems choice when raw data must remain at clients or one shared model is required. This study makes **no privacy guarantee**. Local-only's zero model-exchange count is not zero compute or raw-data governance cost: it uses five 513-parameter models (2,565 parameters total) instead of one shared 513-parameter model. No scarcity or low-resource benefit was run or proven.
- The Level 1 correction is not a clean single-fix ablation: the pooled daily-cycle baseline (about 89.7 MAE) was replaced by the per-sensor 34.776 MAE baseline, and zero handling/preprocessing also changed. Earlier FedAvg validation metrics were mislabeled as test metrics; leakage handling, preprocessing and checkpoint provenance are now consistent. The original run has no Git commit, and that provenance must not be retroactively filled in.

## Reproduction and validation

For saved-result review, use the commands in [`REPRODUCE.md`](REPRODUCE.md) and the exact result files under `results/`. A reviewer should, at minimum:

```bash
python -m pip install -r requirements.txt
python -m pytest -q tests
python src/check_results.py --dir results/full_results --config configs/full.json
python src/check_results.py --dir results/diagnostic_100rounds \
  --config configs/diagnostic_100rounds.json \
  --conditions fedavg_iid fedavg_non_iid
python src/summarize_results.py
```

The raw PEMS08 file is intentionally excluded. A full rerun requires obtaining the dataset as described in [`data/README.md`](../data/README.md), verifying its SHA-256, and writing fresh outputs rather than overwriting frozen results. Result replay and saved-checkpoint inference do not constitute live retraining or a measurement of cellular traffic.

Before public submission, the team should inspect the exact JSON/CSV tables, verify the dataset hash and test commands, confirm that current claims match the frozen artifacts, and separately verify account/upload/mentor obligations. AI assistance is not a substitute for those validations, a human scientific review, or any required professional/accredited certification.
