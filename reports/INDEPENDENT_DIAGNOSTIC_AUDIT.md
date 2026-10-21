# PS-003 — Independent 100-Round Diagnostic Audit

**Team:** Chauraha Sync / A3-PS003-TC520  
**Date:** 19 October 2026  
**Input:** `A3-PS003-TC520_v3.1_with_diagnostic_100rounds.zip`  
**Verdict:** **PASS. Freeze the modelling scope and proceed to final deliverables.**

## Executive conclusion

All six diagnostic files pass the independent audit: **1,408 checks passed, zero failures**. The supplied 25 tests passed again, and the existing condition-filtered checker passed. All six first-30-round history objects exactly match the previously audited runs—not merely their rounded MAEs. All original 15 main-result files, scientific source files, tests and configs are byte-for-byte unchanged.

More rounds improve both FedAvg conditions, but gains are modest relative to the extra accounted communication. IID diagnostic test MAE is **13.873 ± 0.010**, compared with **13.964 ± 0.014** at 30 rounds. Non-IID diagnostic MAE is **14.064 ± 0.043**, versus **14.209 ± 0.066** at 30 rounds. The quietest group improves with the extended budget, but still performs worse than its matched local-only reference in every seed. **H4 remains refuted.**

The primary 30-round comparison remains intact. The 100-round outputs belong in a separately labelled **extended-budget diagnostic**; they must not silently replace the main results or imply equal-budget centralised/federated superiority. No new architecture, dataset or further round extension is required to complete PS-003.

## 1. Independent verification and scope

The independent script checked actual config equality and expected config hash; data hash against the already independently hashed NPZ; unchanged scaler, eligible sample counts, zero policy, horizon, lags, optimiser and checkpoint rule; exactly 100 unique ordered history entries; all complete client counts and pooled metric identities; sample counts used as FedAvg weights; every cumulative payload entry; and exact selected-checkpoint argmin indices and values.

It additionally compared the complete first 30 history objects—including client validation metrics, losses and byte counts—with the earlier archive. All six prefixes are exactly equal. The only diagnostic configuration change is the maximum round count, from 30 to 100.

Expected diagnostic configuration hash:

```text
8a3b7fdf00c7f75d0c33d8e16808b04472b8d02661b71ca6f405a4e264300172
```

The audited dataset remains:

```text
e1d03ce74e9fb79149e6e7c37c680214822c4a285baa2f42278cacabcd25c075
```

This is an artifact/source/data-identity audit, not a new independent reconstruction of all round-31-to-100 neural predictions. No new training was run during this diagnostic audit. The prior main-matrix audit independently reproduced two representative seed-0 neural runs and both deterministic baselines.

## 2. Exact accuracy comparisons

Sample standard deviations use `ddof=1` over seeds 0, 1 and 2. The selected checkpoint for each run is the lowest **validation** MAE in that run, not the final round and not the lowest test error.

| Condition | Maximum rounds | Test MAE: mean ± sample SD | Test RMSE: mean ± sample SD | Completed payload bytes/run |
| --- | --- | --- | --- | --- |
| FedAvg IID | 30 | 13.964 ± 0.014 | 21.211 ± 0.031 | 615,600 |
| FedAvg IID | 100 | 13.873 ± 0.010 | 21.087 ± 0.013 | 2,052,000 |
| FedAvg non-IID | 30 | 14.209 ± 0.066 | 21.373 ± 0.079 | 615,600 |
| FedAvg non-IID | 100 | 14.064 ± 0.043 | 21.218 ± 0.034 | 2,052,000 |

The centralised **30-epoch** reference remains **13.862 ± 0.013 MAE** and **21.074 ± 0.008 RMSE**. IID diagnostic average MAE is **0.077% higher** than that reference, and non-IID is **1.453% higher**. These comparisons are contextual references, not equal-training-budget claims: FedAvg now has 100 local passes per client versus centralised's 30 pooled epochs.

Test-MAE reductions from the original 30-round checkpoints are **0.651%** for IID and **1.024%** for non-IID. Every seed's MAE and RMSE improve relative to its 30-round result. These are validation-selected outcomes, not a reason to choose the schedule using test performance. The main 30-round experiment remains the predefined headline matrix.

The full per-run selections are:

| Condition | Seed | Original best round | 100-run selected round | Original best val MAE | Extended best val MAE | Validation improvement (%) | Extended test MAE | Extended test RMSE |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FedAvg IID | 0 | 30 | 92 | 13.646794 | 13.566287 | 0.590 | 13.883996 | 21.100175 |
| FedAvg IID | 1 | 29 | 97 | 13.619484 | 13.555495 | 0.470 | 13.870905 | 21.086628 |
| FedAvg IID | 2 | 30 | 97 | 13.645933 | 13.562863 | 0.609 | 13.864232 | 21.075098 |
| FedAvg non-IID | 0 | 26 | 96 | 13.936660 | 13.749253 | 1.345 | 14.049761 | 21.201101 |
| FedAvg non-IID | 1 | 30 | 98 | 13.838957 | 13.742018 | 0.700 | 14.029901 | 21.196583 |
| FedAvg non-IID | 2 | 26 | 89 | 13.968431 | 13.806930 | 1.156 | 14.111803 | 21.257161 |

## 3. Validation gains and what they establish

Average improvement in best validation MAE is **0.075855** flow units for IID and **0.148616** for non-IID. All diagnostic best rounds occur after round 30: IID **92, 97, 97** and non-IID **96, 98, 89**.

Therefore “30 rounds was fully converged” is not supported. The correct conclusion is: **30 rounds attained useful near-centralised validation accuracy quickly; continued training produced additional improvements at greater communication cost.**

The 100-round minima also lie late in the budget, so the extended experiment does not prove asymptotic convergence. Do not keep extending to 200 or 300 rounds simply to chase the test score. The finite-budget cost/accuracy comparison already answers the problem statement.

## 4. Communication cost of the extra training

| Quantity | Bytes |
| --- | ---: |
| Model payload | 2,052 |
| Per round across all clients and both directions | 20,520 |
| Completed 30-round run | 615,600 |
| Completed 100-round diagnostic | 2,052,000 |
| Extra 70 rounds | 1,436,400 |
| Training-flow upload reference | 8,499,320 |

The extended budget uses **3.333 times** the original payload. Its total is still **75.857% below** the labelled float32 training-flow upload reference. The payload crossing remains between rounds 414 and 415.

This is **accounted uncompressed model payload**, not observed internet/cellular traffic. It excludes transport headers, retransmissions, serialization metadata, metric/control messages and security overhead. All six completed diagnostics cost 2,052,000 bytes individually even where the selected round is below 100. Retrospective bytes through the selected checkpoint must be labelled separately.

## 5. Client disparity and H4

The relative absolute error remains `sum(abs(error)) / sum(actual)`. It is not MAPE or a formal fairness guarantee. The comparable evaluation groups are the same deterministic quiet-to-busy bands for all models.

| Condition | Common-group gap at 30 rounds (pp) | Common-group gap in 100-round diagnostic (pp) |
| --- | --- | --- |
| FedAvg IID | 2.404 ± 0.040 | 2.396 ± 0.009 |
| FedAvg non-IID | 2.919 ± 0.062 | 2.796 ± 0.040 |

The extended non-IID gap is **16.72% larger** than the extended IID gap on these common groups. Longer training slightly narrows the disparity, but does not remove it.

### Quietest canonical group Q1

| Q1 quietest group | Test MAE: mean ± SD | Test RMSE: mean ± SD | Relative absolute error (%) |
| --- | --- | --- | --- |
| Local non-IID, 30 epochs | 7.230 ± 0.023 | 10.492 ± 0.050 | 7.376 ± 0.024 |
| FedAvg non-IID, 30 rounds | 7.983 ± 0.080 | 11.184 ± 0.085 | 8.145 ± 0.082 |
| FedAvg non-IID, 100-round diagnostic | 7.785 ± 0.049 | 11.027 ± 0.011 | 7.942 ± 0.050 |

At the extended validation-selected checkpoints, non-IID FedAvg is still **7.68% worse in average Q1 MAE** than the original matched local-only model. The per-seed differences are positive for MAE, RMSE and relative error. Thus H4 remains **refuted in the measured setup**, even after giving federation a larger training budget.

Possible explanations such as conflicting local objectives, model capacity or optimiser dynamics are plausible hypotheses, not mechanisms proved by the diagnostic. Do not claim shared training automatically helps smaller/quiet traffic operators.

### All common-group diagnostic outcomes

| Extended condition | Canonical group | MAE: mean ± SD | RMSE: mean ± SD | Relative error (%) |
| --- | --- | --- | --- | --- |
| FedAvg IID | Q1 | 7.285 ± 0.004 | 10.565 ± 0.012 | 7.432 ± 0.004 |
| FedAvg IID | Q2 | 12.245 ± 0.015 | 19.046 ± 0.038 | 6.585 ± 0.008 |
| FedAvg IID | Q3 | 15.063 ± 0.012 | 21.076 ± 0.018 | 6.579 ± 0.005 |
| FedAvg IID | Q4 | 16.052 ± 0.022 | 23.874 ± 0.032 | 5.689 ± 0.008 |
| FedAvg IID | Q5 | 18.402 ± 0.029 | 26.809 ± 0.034 | 5.036 ± 0.008 |
| FedAvg non-IID | Q1 | 7.785 ± 0.049 | 11.027 ± 0.011 | 7.942 ± 0.050 |
| FedAvg non-IID | Q2 | 12.306 ± 0.044 | 19.013 ± 0.036 | 6.617 ± 0.024 |
| FedAvg non-IID | Q3 | 15.034 ± 0.013 | 20.997 ± 0.017 | 6.566 ± 0.006 |
| FedAvg non-IID | Q4 | 16.087 ± 0.024 | 23.888 ± 0.011 | 5.701 ± 0.008 |
| FedAvg non-IID | Q5 | 18.804 ± 0.101 | 27.213 ± 0.090 | 5.146 ± 0.028 |

## 6. Validation target attainment

The target is unchanged: for each seed, **1.05 × that seed's best centralised validation MAE**. Exact original prefixes make the first-hit rounds unchanged.

| Condition | Seed | First 5% target hit | First round remaining below through round 100* | Selected round | Payload through selected round | Actual full-run payload |
| --- | --- | --- | --- | --- | --- | --- |
| FedAvg IID | 0 | 3 | 3 | 92 | 1,887,840 | 2,052,000 |
| FedAvg IID | 1 | 2 | 2 | 97 | 1,990,440 | 2,052,000 |
| FedAvg IID | 2 | 3 | 3 | 97 | 1,990,440 | 2,052,000 |
| FedAvg non-IID | 0 | 9 | 16 | 96 | 1,969,920 | 2,052,000 |
| FedAvg non-IID | 1 | 6 | 17 | 98 | 2,010,960 | 2,052,000 |
| FedAvg non-IID | 2 | 4 | 20 | 89 | 1,826,280 | 2,052,000 |

*Remaining below through round 100 is a retrospective curve summary, not an online early-stop guarantee or proof of future stability.*

IID first hits are **3, 2, 3**, versus **9, 6, 4** for non-IID. IID stays below after its first hit throughout the observed 100-round history. Non-IID stays below for the remainder only from **16, 17, 20**, respectively. This extends the evidence for slower target attainment and intermittent early threshold crossing under non-IID, without changing the original first-hit numbers.

## 7. Updated hypothesis interpretation

| Hypothesis | Status after diagnostic |
| --- | --- |
| H1: IID close to centralised; non-IID larger client disparity | Remains supported descriptively. Do not call numerical closeness statistical equivalence. |
| H2: non-IID larger seed variation and slower convergence | Remains supported within observed finite-budget curves. Non-IID diagnostic MAE SD is 0.042723 versus IID 0.010054; original target-hit contrast persists. |
| H3: learned MLP beats persistence | Remains supported for all main runs and all diagnostic seeds. |
| H4: quietest client benefits from FedAvg over local-only | Remains refuted; Q1 is worse under non-IID federation in every diagnostic seed. |

These are descriptive findings with three seeds and one chronological split. IID seeds also change partition membership, unlike deterministic non-IID. Temporally overlapping windows are not independent experiment replicates. Do not infer statistical significance, causal mechanisms, privacy guarantees, production feasibility or Bengaluru generalisation from this diagnostic.

## 8. Final experiment/reporting decisions

The test set has now been scored for both the main and extended diagnostic checkpoints. This repeated exposure is disclosed; no model or schedule should be chosen by the diagnostic test scores. Retain the predefined 30-round primary analysis and stop further test-informed tuning.

1. **Freeze the 30-round 15-run matrix as the primary experiment.** Never overwrite or re-label it as a 100-round comparison.
2. **Keep the six 100-round files as a separate supplementary diagnostic.** All extended-round figures must show their larger budget and actual total payload.
3. **Stop model development and test-informed exploration now.** Do not add a GRU, new dataset, horizon, partition or learning-rate search for the submission.
4. **Preserve provenance honestly.** Both archives record `code_commit: unavailable (not a git repository)`. A later commit/source hash identifies the packaged code, not the historical run commit. Do not edit the original metadata retroactively.
5. **Finish deliverables rather than chase a winning FedAvg headline.** Prepare one clean reproduction guide, audit/test entry point, report/evidence tables, pseudocode/prototype demonstration and corrected template-based presentation. The user will personally push the final package to GitHub.

## 9. Safe updated wording for AIORI

> The predefined 30-round experiment showed IID FedAvg near centralised accuracy, while non-IID FedAvg had higher error, a larger common-group relative-error gap and slower validation-target attainment. A separately reported 100-round diagnostic reduced IID test MAE from 13.964 to 13.873 and non-IID MAE from 14.209 to 14.064, at 3.33 times the model-payload cost. Longer training did not reverse the quietest group's disadvantage relative to matched local-only training. The findings describe finite-budget accuracy, client disparity and accounted communication trade-offs, not formal privacy or measured network-bandwidth savings.

## 10. Evidence files

`diagnostic_summary.json` preserves full-precision means, sample SDs, paired improvements, client results, hypothesis-relevant contrasts, payload totals and a source hash manifest. `diagnostic_checks.json` records all 1,408 independent check labels. The three CSVs preserve per-run metrics, all per-client outcomes and all 600 round-history entries.

Regenerate the audit using `audit_diagnostic.py`, the diagnostic archive contents, the original main-matrix archive, and the prior independent `audit_summary.json`:

```bash
python3 audit_diagnostic.py \
  --root /path/to/diagnostic-project \
  --original /path/to/original-main-project \
  --primary-summary /path/to/main-audit-summary.json \
  --out /path/to/diagnostic-audit-output
```

No GitHub push, new modelling experiment or presentation edit was performed during this audit.
