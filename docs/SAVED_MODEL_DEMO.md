# Actual saved-model demonstration

The enhanced release adds a genuinely runnable predictor. `src/demo.py` still replays result JSONs; **`src/inference.py` executes the MLP forward pass from saved validation-selected parameters**. No learning occurs during inference. This is a benchmark demonstration, not a hosted traffic service or a Bengaluru model.

## What is supplied

`checkpoints/centralised_seed0.json` and `checkpoints/fedavg_non_iid_seed0.json` contain all 513 float32 parameters, the training scaler, index-cycle settings, source hashes and original result references. Seed 0 and these two conditions were fixed before the export, not picked as the best-looking seed. Both reproduce the unchanged 30-pass primary schedule.

The exporter verified each complete validation history, selected checkpoint, final test block (including client metrics) and communication block against its original JSON before saving weights. Maximum absolute floating-field differences were **3.2867397692371014e-10** for centralised and **5.547988735088438e-10** for non-IID FedAvg. JSON round-tripping recovers the exact float32 parameter bits. No original result, config or scientific routine was changed.

Centralised seed 0 selects **epoch 29**, validation MAE **13.56922721862793**; non-IID FedAvg seed 0 selects **round 26**, validation MAE **13.936659812927246**. Their test MAEs are **13.877108369** and **14.218150408**, respectively. These are individual seed values—not the report's three-seed means.

Metadata checks and parameter checksums detect malformed tensors, altered weights, invalid scalers and unsupported feature settings. Use the release manifest for full-file integrity; a checksum is not a signed authenticity or privacy guarantee.

## Run an actual benchmark forward pass

Install the normal requirements and obtain the exact NPZ through `data/README.md`. From the project root:

```bash
python src/inference.py \
  --checkpoint checkpoints/fedavg_non_iid_seed0.json \
  --data data/PEMS08.npz \
  --sensor-index 156 --global-index 15189
```

The command verifies the dataset SHA-256, takes that sensor's preceding 12 flows, builds the original global index-cycle features and executes the saved MLP. The recorded output is:

```text
forecast_flow:              186.37592180221702
observed_flow_if_dataset:   193.0
persistence_reference:     179.0
```

This one point illustrates the software only. It is not evidence that FedAvg generally beats centralised or persistence, nor an uncertainty interval. Full test results remain governed by the original JSONs. The observed target is read for display, not included in the feature vector or used to update the model.

For the centralised control, change only the checkpoint path:

```bash
python src/inference.py \
  --checkpoint checkpoints/centralised_seed0.json \
  --data data/PEMS08.npz \
  --sensor-index 156 --global-index 15189
```

The command also accepts `--history` instead of `--data`, with exactly 12 comma-separated positive flow values, oldest to newest, plus a valid `--global-index`. This performs inference without an NPZ. Do not treat arbitrary manual inputs as calibrated city forecasts: the model/scaler and cycle convention were learned for this benchmark. Calendar alignment outside it is not established. Predictions are not clipped or post-processed.

## Show actual held-out forecast traces

The supplied [forecast figure](../figures/heldout_forecast_examples.png) compares observed flow with centralised, non-IID FedAvg and persistence over preset segments. Selection is deterministic: use the upper-median valid-training-mean sensor from canonical Q1, Q3 and Q5, and the first 288 target-index slots after the test split's lag boundary. No sensor, period or checkpoint is chosen by test error.

The resulting zero-based sensor indices are **156, 31 and 3**, with **288 eligible windows each** in global span `[15189,15477)`. The index axis does not claim verified calendar timestamps. Segment MAEs are displayed on the figure and in `reports/tables/heldout_example_summary.json`; they are illustrations, not population estimates or three-seed results. A middle-group segment happens to favour FedAvg slightly, but that does not override the main aggregate comparison or H4's refutation.

Regenerate locally with:

```bash
python scripts/render_heldout_forecasts.py
```

The script writes a local trace CSV under `artifacts/heldout_trace_data/`; that raw excerpt is excluded from the release ZIP and GitHub staging. The full NPZ is also excluded. Figures, model weights and metric summaries are included, with provenance and the existing dataset-rights caution retained.

## A short mentor demonstration

Begin with `python scripts/verify_release.py` and explain that it checks the supplied evidence without retraining. Open the forecast figure and identify the observed and predicted curves. Run the actual inference command above and say: “This is the saved validation-selected model executing a forward pass, not a console replay.” Then show the primary three-seed results and canonical client errors; do not draw general conclusions from one point or one plotted day.

Finish with the separate [validation-payload frontier](../reports/VALIDATION_PAYLOAD_FRONTIER.md). At a 2%-above-centralised validation target, IID reaches the target by seed-0/1/2 rounds **8/5/9**, while non-IID requires **57/50/46** in the diagnostic and fails within the 30-round primary budget. Those are retrospective validation target crossings, not test-by-round accuracy or completed-run stopping savings.

A fresh smoke execution remains available with `python src/demo.py --train-smoke`. Label it as new learning execution on the short smoke schedule, not the final model's accuracy.

## Re-export only when necessary

The shipped checkpoints already work. Re-exporting is optional and repeats the two full primary runs:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
python scripts/export_verified_checkpoints.py
```

On Windows, set those environment variables using the shell's syntax, or run the Python command directly. The exporter refuses wrong data or changed audited routines. It writes only `checkpoints/` and its new verification report/log, never the original result files. It does not add a new hypothesis or replace the primary matrix.

## Files to publish

Publish `checkpoints/`, `src/inference.py`, its tests, the exporter and forecast renderer, this guide, the forecast figure and metric summary, and `artifacts/VERIFIED_CHECKPOINT_EXPORT.json`. The frontier's source, tests, report, CSV and figure should be published as supplementary analysis. The enhanced release passes **55 tests**; all **41 original preserved entries** still match.

Suggested placement in the existing upload plan: include the inference module/models with the October 20 source bundle; show the working example during October 24's prototype walkthrough; publish the frontier alongside October 25–26 analysis. Preparation remains October 19 and all publication/mentoring dates must be genuine.
