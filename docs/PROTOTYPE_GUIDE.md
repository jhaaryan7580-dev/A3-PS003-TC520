# Working prototype guide

The scientific engine is still the original NumPy simulator. The new interface is a **portable scientific demonstration**, not a production traffic-control system or a new federated-learning algorithm. It reads the frozen results and computes actual forecasts from the exported validation-selected weights.

## Fastest launch — no Node installation

From the extracted project root:

```bash
python prototype/launch.py
```

Open the localhost address printed by the launcher. It serves the included compiled static app on the team computer. Python does not retrain a model or upload the dataset. Keep this terminal open during the demonstration; Ctrl+C stops it.

For source development, use Node **20.19+ or 22.12+**, and the pinned pnpm **10.18.0**:

```bash
cd prototype
npx --yes pnpm@10.18.0 install --frozen-lockfile
npx --yes pnpm@10.18.0 dev:static
```

The local launcher is the simplest review route; do not open `index.html` directly with `file://`, since relative data fetches require HTTP. No login, database, cloud account, model API key or GPU is needed.

## 1. Show a real forecast

The initial manual example is deliberately labelled **manual input**, not PEMS08 observations. Press **Run forward pass**. Both the non-IID FedAvg and centralised options are fixed **seed 0** models, not the best-looking seed. Manual mode has no recorded truth, so its truth/error cells remain empty.

For a real held-out dataset example, obtain the exact PEMS08 file using `data/README.md`. The required SHA-256 is:

```text
e1d03ce74e9fb79149e6e7c37c680214822c4a285baa2f42278cacabcd25c075
```

Press **Load local PEMS08** and select the NPZ from the team computer. The application validates its hash before decompressing, checks the `[17856,170,3]` C-order array and reads flow channel 0. The application has no dataset-upload endpoint. For strict local operation, use the included launcher rather than a hosted Preview.

The default sensor index is **156** and target index **15189**, the first split-contained test target after 12 lags. Preset sensors **156/Q1, 31/Q3 and 3/Q5** were selected from training-defined groups, not from test errors. Sensor indices are positional indices, not authenticated physical-intersection IDs. You can inspect other sensors and move to the next eligible window; that button uses the positive complete-case rule, not model error.

The chart shows 12 prior observations, then computes the forecast from those observations and the global index-cycle features. Recorded target truth is displayed only for comparison after inference, not used in the predictor. A point’s absolute error is **not** a full-test MAE. Empty/zero-containing windows, out-of-range indices, malformed/wrong NPZs and unsafe integer indices are rejected.

## 2. Inspect the full experimental evidence

Open **Experiment evidence**. The five learned arrangements, all three seeds, mean and **sample SD** come from the frozen raw JSONs. Select MAE/RMSE and individual seeds. Common quiet-to-busy evaluation groups are fixed from training means; they are not changed to match a convenient IID seed’s training membership. Relative error is sum absolute error divided by sum observed flow, not MAPE.

The quiet-group penalty is retained even though it is unfavourable to FedAvg. H4 was refuted in this full-history primary experiment. No unrun data-scarcity study is used as evidence.

## 3. Explain the federation honestly

Open **Federation lab**. Inspect seeded IID/non-IID training memberships, local training counts and sample-weighted aggregation. The client/server topology is conceptual: all clients were simulated sequentially in one NumPy process.

Play a saved validation history. This is explicitly **replay**, not fresh training or per-round test evaluation. The fixed final test score belongs to the validation-selected checkpoint. Primary 30-round and diagnostic 100-round runs remain separately labelled.

The cost slider is arithmetic: 513 float32 parameters = 2,052 B; five uploads plus five downloads = **20,520 B/round**. It is not a network benchmark. JSON encoding, transport headers, retries, scaler and metric traffic are excluded; the training-flow reference is a lower-bound convention, not an end-to-end system saving.

## 4. Execute fresh training separately

From the scientific root, after installing `requirements.txt` and placing the exact dataset:

```bash
python src/run_experiments.py --config configs/smoke.json --out results/my_smoke
python src/check_results.py --dir results/my_smoke --config configs/smoke.json
```

This is actual NumPy training. Its outputs are separate from frozen evidence and must not be quoted as final performance or used for tuning. The repository already includes the complete original matrices; rerunning the full matrix is not necessary to view or demonstrate them.

## Integrity and arithmetic scope

The browser checks the evidence file against its packaged manifest, each checkpoint’s full-file hash, its condition/seed identity, binary little-endian Float32 parameter hash, dataset provenance and feature/scaler settings. These checks are **integrity checks, not a signed external certification**.

The JavaScript forward pass uses the same saved parameters, ReLU architecture, training scaler and global phase features. Floating-point accumulation can differ slightly from NumPy/BLAS. Forty deterministic **manual numerical diagnostic histories per model** were checked against original NumPy inference; these are unit fixtures, not benchmark performance samples. Measured maximum absolute differences were **0.0000693744** flow units for centralised and **0.0000433590** for non-IID FedAvg, below the **0.001** tolerance. Original three-seed report metrics come from NumPy, never from the browser port.

Raw NPZs, local forecast receipts and temporary raw trace CSVs are excluded from the submission. Keep data usage/redistribution rights separate from source-code licensing. Public availability is not, by itself, permission to redistribute a dataset.

## External completion

The public working demo is **[Chauraha Sync](https://chauraha-sync.jhaaryan7580.workers.dev/)**. It is deployed on Cloudflare Workers/Pages, corresponding to audited build c63ad641b36095e4c341de1f7634317c3ce3bcb2; the documentation-only refresh keeps application inference, models, and evidence unchanged, with original publication receipts under artifacts/. This live URL is referenced in the GitHub README.md and SUBMISSION_INDEX.md. The compiled executable/static files remain a file-review backup. This is a stable production deployment, not a temporary Preview URL.

The Cloudflare static deployment excludes third-party hosting analytics and telemetry scripts (__manus__ tracking scripts were omitted from the production bundle). No scientific application-origin POST or raw NPZ transfer occurs in the hosted workflow. For strictly offline operation, use the compiled Python launcher; the app still checks and decodes the selected NPZ entirely in-browser. 

The prepared prototype and pseudocode do **not** certify that the required mentor interaction occurred. Demonstrate them at the actual instructed session and record genuine feedback.

## Requirement-focused revision: direct comparison and mentor walkthrough

A single **Run forward pass** now computes centralised, non-IID FedAvg and persistence from the exact same lag values and target index. The comparison table displays each prediction and its point absolute error only when recorded truth exists. The original selected-model receipt remains available, with both fixed-checkpoint predictions added; neither model is selected using the displayed error.

With verified local PEMS08 loaded, press **Compare 12 target slots**. The app takes 12 consecutive index positions from the selected start (shorter only at the dataset end). Each target uses its own preceding observed history. This is causal one-step playback, **not** a recursive hour-ahead forecast from one origin. Invalid zero-containing windows stay as visible gaps and are excluded equally from all three local-score calculations. It does not jump to lower-error examples. The displayed slice MAE/RMSE and downloaded local trace are illustrations, never replacements for the frozen full-test three-seed evidence. Do not commit raw local trace receipts.

The primary evidence table includes deterministic persistence and per-sensor daily-cycle rows for the selected MAE/RMSE metric, on the same 448,533 test windows. These baselines do not acquire a seed SD or change when a learned-model seed is selected.

Federation lab now overlays IID/non-IID validation curves from the **same seed and round budget**. The descriptive target is 1.05 times that seed's best centralised validation MAE, matching the report; it is not a stopping rule, equivalence margin or per-round test score. Expand **Mentor walkthrough: how one FedAvg round works** to explain train-count weights, one local epoch, resetting local Adam, weighted parameter aggregation and validation-only checkpoint selection. Replay remains replay; the separate NumPy command remains actual training. If clipboard permission/API is absent, the control gives manual-copy instructions rather than crashing.

The unused browser training-boundary constant was corrected to 12,499 and tested for agreement with the locked split; it did not drive the original scientific training or inference. Rejected replacement files now explicitly keep the previous verified dataset usable instead of silently blocking inference.

## Revision verification

The revised frontend has **22 passing numerical/data tests**, retaining the original NumPy parity measurements. An isolated system-Chromium run passes **19 real UI checks**, including real PEMS08 file selection and fixed-reference inference, both-model comparison, trace generation, invalid-sensor recovery, rejected-file retention, MAE/RMSE baseline display, 100-to-30-round switching, visible pseudocode, clipboard fallback, dataset retention, unloading and narrow-screen layout. No unhandled browser exception or application POST/upload request was observed in those checks. The 55 scientific/package tests and protected core hashes remain separate verification gates.

Optional browser checks can be repeated after launching the compiled app, with Playwright and an installed Chromium browser:

```bash
python prototype/scripts/check_prototype_ui.py --url http://127.0.0.1:8080 --dataset data/PEMS08.npz --chromium /path/to/chromium --out artifacts/my_ui_check.json
```

Playwright is optional test tooling, not a runtime dependency. Choose the real browser executable path on your OS. Test checks are AI-assisted technical evidence, not external certification or a claim that no bug can ever exist.
