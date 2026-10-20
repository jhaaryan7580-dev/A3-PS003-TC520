"""Run conditions x seeds and write one JSON per run.

    python src/run_experiments.py --config configs/smoke.json --out results/smoke
    python src/run_experiments.py --config configs/full.json  --out results/full_results
"""
import argparse
import json
from pathlib import Path

import data as D
import train as T

CONDITIONS = ["centralised", "local_iid", "local_non_iid", "fedavg_iid", "fedavg_non_iid"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--data", default=str(Path(__file__).resolve().parent.parent / "data" / "PEMS08.npz"))
    ap.add_argument("--conditions", nargs="*", default=CONDITIONS)
    ap.add_argument("--seeds", nargs="*", type=int, default=None)
    a = ap.parse_args()
    cfg = json.loads(Path(a.config).read_text())
    seeds = a.seeds if a.seeds is not None else cfg["seeds"]
    flow = D.load_flow(a.data)
    sha = D.sha256(a.data)
    prepared = T.make_data(flow, cfg)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    for cond in a.conditions:
        for seed in seeds:
            res = T.run_condition(flow, cfg, cond, seed, prepared=prepared, dataset_sha=sha)
            (out / f"{cond}_seed{seed}.json").write_text(json.dumps(res, indent=2))
            o = res["test"]["overall"]
            print(f"{cond:14s} seed {seed}  test MAE {o['mae']:.3f}  RMSE {o['rmse']:.3f}")


if __name__ == "__main__":
    main()
