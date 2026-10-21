# Chauraha Sync — portable traffic forecasting lab

This is the demonstration interface around the unchanged PS-003 NumPy scientific core. It performs actual saved-weight inference, displays frozen experimental evidence and explains FedAvg with explicitly labelled replay.

## Review the included compiled app

From the scientific root:

```bash
python prototype/launch.py
```

Or, from this folder: `python launch.py`. Use `--port 8081` if the default local port is occupied. No Node, login, database, GPU or cloud service is required for this compiled route. Open the printed localhost URL; direct `file://` opening is unsupported.

Manual example mode works immediately and has no recorded truth. Select the exact local PEMS08 NPZ for real held-out playback. The file is checked and decoded inside the browser; the application has no dataset-upload endpoint. Raw NPZs and local receipts are excluded from the package.

## Develop or rebuild from source

Node **20.19+ / 22.12+**, pnpm **10.18.0**:

```bash
npx --yes pnpm@10.18.0 install --frozen-lockfile
npx --yes pnpm@10.18.0 test
npx --yes pnpm@10.18.0 check
npx --yes pnpm@10.18.0 build:static
npx --yes pnpm@10.18.0 dev:static
```

`client/src/components/lab/` contains the four views. `lib/engine.ts` performs checksum-verified 14–32–1 inference; `lib/dataset.ts` parses the local hashed NPZ and rejects invalid test windows. `client/public/data/` contains exact copied checkpoint JSONs, a read-only evidence export and original-source hashes, not raw sensor streams.

The exported evidence derives from the unchanged results. Scientific source lives one folder above in `src/`, with its own tests/reproduction guide. The browser port is tolerance-checked against NumPy; the full report’s scores are never recalculated using browser inference.

See [full operating and scope guide](../docs/PROTOTYPE_GUIDE.md), [demo script](../docs/DEMO_SCRIPT_AND_JUDGE_QA.md) and [submission index](../SUBMISSION_INDEX.md).

The published counterpart is [Chauraha Sync](https://chaurahalab-gzh27d5b.manus.space), initially audited as Manus version `c63ad641b36095e4c341de1f7634317c3ce3bcb2`. The later documentation-only refresh preserves inference code, models and evidence; publication receipts are under the scientific root's `artifacts/`. The hosted page includes platform analytics; the local compiled launcher remains available for strictly local operation. Neither publication nor this local app implies mentoring attendance, real-city deployment or a model privacy guarantee. Keep source-code licensing and dataset-usage rights separate.

## Requirement-focused revision

One run now compares centralised, non-IID FedAvg and persistence on the same input. With locally selected PEMS08, a 12-slot consecutive one-step trace displays observed flow, both models and persistence; gap-preserving slice scores are illustrative only. The evidence table includes both non-learned baselines for MAE/RMSE. Federation lab displays matched-seed IID/non-IID histories and an expandable mentor pseudocode explanation. The frontend numerical/data suite passes 22 tests; isolated real-browser checks are recorded under the scientific root's `artifacts/`.

The Submission desk downloads standalone HTML report/mentor/reproduction documents. Figures are embedded and package-only references are shown as labelled paths, so downloading one document does not create broken relative links. Canonical Markdown files remain in the full package. If these documents are edited, regenerate the app downloads from the scientific root before rebuilding:

```bash
python -m pip install Markdown
python scripts/export_standalone_documents.py --out prototype/client/public/downloads
cd prototype
npx --yes pnpm@10.18.0 build:static
```

Python Markdown is optional build-time document tooling, not a runtime dependency for the compiled app. Summary/figure regeneration uses the separate safe output tree described in `docs/REPRODUCE.md`; never overwrite the delivered evidence for a rehearsal.
