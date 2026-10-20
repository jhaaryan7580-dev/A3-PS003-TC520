"""Non-learned baselines.

persistence : predict the previous 5-minute flow of the same sensor
daily cycle : per-(sensor, slot) mean of valid TRAIN flow, slot = global target index mod 288
              (one mean per sensor and slot, NOT one pooled mean across sensors)
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import data as D
import meta
import metrics as M


def persistence_pred(flow, t, s):
    return flow[t - 1, s]


def daily_cycle_table(flow, bounds):
    a, b = bounds["train"]
    x = flow[a:b]
    slots = np.arange(a, b) % D.PERIOD
    n = flow.shape[1]
    tab = np.zeros((D.PERIOD, n))
    cnt = np.zeros((D.PERIOD, n))
    valid = x != 0
    np.add.at(tab, slots, np.where(valid, x, 0.0))
    np.add.at(cnt, slots, valid.astype(float))
    sensor_mean = x.sum(axis=0) / np.maximum(valid.sum(axis=0), 1)
    return np.where(cnt > 0, tab / np.maximum(cnt, 1), sensor_mean[None, :])


def daily_cycle_pred(table, t, s):
    return table[t % D.PERIOD, s]


def run(npz_path, out_path):
    flow = D.load_flow(npz_path)
    T, N = flow.shape
    bounds = D.split_bounds(T)
    table = daily_cycle_table(flow, bounds)
    res = {"metadata": {"dataset_sha256": D.sha256(npz_path), "code_commit": meta.code_commit(),
                        "command": "python src/baselines.py", "zero_policy": "complete_case_windows",
                        "horizon": 1, "lags": D.LAGS,
                        "eligible_windows": {sp: int(len(D.valid_windows(flow, sp, bounds)[0])) for sp in ("train", "val", "test")}},
           "policy": "complete_case_windows",
           "note": "scored on the shared complete-case windows of each split"}
    for sp in ("val", "test"):
        t, s = D.valid_windows(flow, sp, bounds)
        y = flow[t, s]
        res[sp] = {}
        for name, p in (("persistence", persistence_pred(flow, t, s)),
                       ("daily_cycle_per_sensor", daily_cycle_pred(table, t, s))):
            r = M.basic(y, p)
            for mode in ("iid", "non_iid"):
                cl = D.partition_sensors(flow, bounds, mode, seed=0)
                r[f"per_client_{mode}"] = M.per_client(y, p, s, cl)
            res[sp][name] = r
    Path(out_path).write_text(json.dumps(res, indent=2))
    return res


if __name__ == "__main__":
    base = Path(__file__).resolve().parent.parent
    r = run(base / "data" / "PEMS08.npz", base / "results" / "baselines.json")
    for sp in ("val", "test"):
        for k, v in r[sp].items():
            nc = v["per_client_non_iid"]
            print(f"{sp:4s} {k:24s} MAE {v['mae']:.3f} RMSE {v['rmse']:.3f} rel {v['relative_abs_error']:.4f} "
                  f"n {v['n']}  non-IID gap(rel) {nc['gap_relative_error']:.4f} gap(MAE) {nc['gap_mae']:.3f}")
