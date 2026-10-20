"""Human-readable replay of the audited saved results.

Default mode reads precomputed JSON artifacts and does not train.  ``--train-smoke``
is the explicit exception: it delegates to the existing immutable runner, requires
the local dataset and smoke config, and writes only to ``artifacts/demo_smoke``.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

CONDITIONS = ["centralised", "local_iid", "local_non_iid", "fedavg_iid", "fedavg_non_iid"]
ROOT = Path(__file__).resolve().parent.parent


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def fmt(value):
    return f"{value:.6f}" if isinstance(value, float) else str(value)


def replay(args) -> int:
    results_dir = ROOT / args.results_dir
    audit_path = ROOT / args.dataset_audit
    cfg_path = ROOT / args.config
    cfg = load(cfg_path)
    audit = load(audit_path) if audit_path.is_file() else {}
    selected = []
    for path in sorted(results_dir.glob("*_seed*.json")):
        try:
            result = load(path)
        except Exception as exc:
            print(f"Skipping unreadable saved result {path.name}: {exc}")
            continue
        if result.get("condition") not in CONDITIONS:
            continue
        selected.append((path, result))
    if not selected:
        raise SystemExit(f"No saved result JSON files found in {results_dir}")

    print("AUDITED RESULTS REPLAY (precomputed saved results; no live training)")
    print(f"Results: {results_dir.relative_to(ROOT)}")
    print(f"Config: {cfg_path.relative_to(ROOT)}")
    print(f"Dataset SHA-256 recorded in results: {selected[0][1].get('metadata', {}).get('dataset_sha256', 'n/a')}")
    print("\nDataset split")
    for name, bounds in audit.get("split_bounds", {}).items():
        windows = audit.get("windows", {}).get(name, {}).get("complete_case")
        print(f"  {name:5s}: rows {bounds[0]}:{bounds[1]}, complete-case windows {windows}")
    print("\nClient descriptions")
    partitions = audit.get("partitions", {})
    iid = partitions.get("iid", {}).get("by_seed", {}).get(str(args.seed), {})
    print(f"  IID seed {args.seed}: client sizes {iid.get('sizes', 'not recorded')}")
    print(f"  non-IID: client sizes {partitions.get('non_iid', {}).get('sizes', 'not recorded')}")
    definitions = partitions.get("definitions", {})
    for key, text in definitions.items():
        print(f"  {key}: {text}")

    # Display only the explicitly requested run. Do not rank seeds or compare
    # unweighted local-client validation minima with a pooled global minimum.
    print("\nNo best-seed selection: displaying the explicitly requested saved run.")

    path = results_dir / f"{args.condition}_seed{args.seed}.json"
    if not path.is_file():
        raise SystemExit(f"Saved result not found for {args.condition} seed {args.seed}: {path}")
    result = load(path)
    overall = result.get("test", {}).get("overall", {})
    print(f"\nSelected saved result: {args.condition}, seed {args.seed}")
    print("Main test metrics (saved, not recomputed):")
    for key in ("mae", "rmse", "relative_abs_error", "n"):
        print(f"  {key}: {fmt(overall.get(key))}")
    for partition in ("iid", "non_iid"):
        block = result.get("test", {}).get(f"per_client_{partition}", {})
        print(f"  {partition}: gap_mae={fmt(block.get('gap_mae'))}, gap_relative_error={fmt(block.get('gap_relative_error'))}")
    best = result.get("best_checkpoint", {})
    print(f"Checkpoint selected by saved validation history: {best}")
    history = result.get("history", [])
    if args.rounds_to_show > 0:
        print(f"History preview (first {args.rounds_to_show} rows):")
        for row in history[: args.rounds_to_show]:
            print("  " + json.dumps({k: v for k, v in row.items() if k not in ("val_mae_per_client",)}, sort_keys=True))
    return 0


def run_smoke() -> int:
    data = ROOT / "data" / "PEMS08.npz"
    config = ROOT / "configs" / "smoke.json"
    if not data.is_file():
        print(f"FAIL: --train-smoke requires dataset {data}", file=sys.stderr)
        return 2
    if not config.is_file():
        print(f"FAIL: --train-smoke requires config {config}", file=sys.stderr)
        return 2
    out = ROOT / "artifacts" / "demo_smoke"
    out.mkdir(parents=True, exist_ok=True)
    print("EXPLICIT SMOKE RUN: delegating to immutable src/run_experiments.py; output is not audited full/diagnostic evidence")
    command = [sys.executable, str(ROOT / "src" / "run_experiments.py"), "--config", str(config), "--out", str(out), "--data", str(data)]
    completed = subprocess.run(command, cwd=ROOT)
    return completed.returncode


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--condition", choices=CONDITIONS, default="fedavg_iid")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--rounds-to-show", type=int, default=5)
    ap.add_argument("--results-dir", default="results/full_results")
    ap.add_argument("--config", default="configs/full.json")
    ap.add_argument("--dataset-audit", default="results/dataset_audit.json")
    ap.add_argument("--train-smoke", action="store_true", help="explicitly run the immutable smoke runner; requires local data/PEMS08.npz")
    args = ap.parse_args(argv)
    if args.train_smoke:
        return run_smoke()
    return replay(args)


if __name__ == "__main__":
    raise SystemExit(main())
