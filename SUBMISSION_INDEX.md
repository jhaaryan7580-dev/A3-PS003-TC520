# Chauraha Sync — Complete Submission & Deliverable Index

**Team Code:** `A3-PS003-TC520`  
**Problem Statement:** PS-003 (Traffic-Flow Prediction: Centralised vs. Federated Learning)  
**Track:** AIORI-3 · Track 3: Smart Cities  
**Institution:** BMS College of Engineering  

**Live Prototype Lab:** [https://chauraha-sync.jhaaryan7580.workers.dev/](https://chauraha-sync.jhaaryan7580.workers.dev/)

---

## 1. Executive Summary & Boundaries

* **Core Scope:** A reproducible measurement study on the California PEMS08 benchmark evaluating the predictive accuracy vs. analytical communication trade-off between Centralised Learning and Federated Learning (FedAvg).
* **Architecture:** 14–32–1 multilayer perceptron (513 parameters) implemented from scratch in pure NumPy.
* **Key Finding:** Centralised learning serves as the strongest predictive baseline (MAE ≈ 13.86). FedAvg IID achieves near-centralised performance (MAE ≈ 13.96). FedAvg non-IID exhibits degraded convergence and accuracy (MAE ≈ 14.21) due to client distribution heterogeneity.
* **Communication Accounting:** Analytical float32 model-payload accounting (2,052 bytes per model transfer; 20,520 bytes per 5-client round). Real wire network overhead is explicitly excluded.
* **Non-Claims:** No live city traffic deployment, no physical intersection hardware, and no formal cryptographic privacy guarantees (differential privacy / secure aggregation) are claimed.

---

## 2. Deliverable Directory Map

### Root Package
- `README.md` — Complete technical overview, quick start, and test reproduction guide.
- `SUBMISSION_INDEX.md` — This deliverable navigation map.
- `requirements.txt` — Standard installation dependencies (Python 3.10+).
- `requirements-tested.txt` — Exact pinned reproduction dependencies.
- `.gitignore` — Excludes raw datasets, caches, and telemetry scripts.

### Source Code (`src/`)
- `src/model.py` — 513-parameter plain NumPy MLP with explicit forward/backward Adam updates.
- `src/train.py` — Centralised and local-only training routines.
- `src/federated.py` — FedAvg aggregation simulator with IID and non-IID client partition splits.
- `src/demo.py` — Saved-result numerical replay script.
- `src/check_results.py` — Integrity verification checking result JSONs against target configs.
- `src/summarize_results.py` — Aggregate multi-seed metrics calculator.

### Prototype (`prototype/`)
- `prototype/launch.py` — Offline zero-dependency Python static launcher for evaluators.
- `prototype/dist/public/` — Compiled static web bundle deployed to Cloudflare.
- `prototype/client/` — Editable TypeScript / React (Vite) frontend application source.
  - `ForecastView.tsx` — Real browser-side forward-pass inference using saved weights.
  - `EvidenceView.tsx` — Frozen 3-seed experimental results and convergence replay.
  - `FederationView.tsx` — Analytical model payload and round-accounting explainer.
  - `SubmissionView.tsx` — Documentation downloads and evaluation report viewer.

### Presentation (`presentation/`)
- `presentation/A3-PS003-TC520_Chauraha_Sync.pptx` — Prescribed editable pitch deck.
- `presentation/A3-PS003-TC520_Chauraha_Sync.pdf` — Presentation PDF for evaluator upload.

### Documentation (`docs/`)
- `docs/PROTOTYPE_GUIDE.md` — Guide for running the web prototype offline and online.
- `docs/REPRODUCE.md` — Complete instructions for reproducing experiments from scratch.
- `docs/DEMO_SCRIPT_AND_JUDGE_QA.md` — Walkthrough script and expected technical Q&A.
- `docs/MENTOR_DEMO_AND_PSEUDOCODE.md` — Walkthrough documentation for mentor review.
- `docs/FINAL_RUN_THROUGH.md` — Full pre-submission validation checklist.
- `docs/SUBMISSION_CHECKLIST.md` — Final submission audit list.
- `docs/PS-003_official.pdf` — Official problem statement specification.

### Data & Checkpoints
- `data/README.md` — Acquisition guide and SHA-256 verification hash for PEMS08.
- `checkpoints/` — Pre-trained float weight checkpoints (`centralised_seed0.json`, `fedavg_non_iid_seed0.json`).
- `results/` — Primary 30-round/30-epoch results (seeds 0, 1, 2) and 100-round diagnostic JSONs.
- `artifacts/` — Checkpoint exports, audit hashes, test logs, and build receipts.
