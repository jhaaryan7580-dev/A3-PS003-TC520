"""Gate A: audit the PEMS08 tensor and the split/partition decisions; write results/dataset_audit.json."""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import data as D


def main(npz_path, out_path):
    raw = np.load(npz_path)["data"]
    flow = raw[:, :, 0].astype(np.float64)
    T, N = flow.shape
    bounds = D.split_bounds(T)

    # zero runs per sensor (consecutive zeros)
    runs = []
    for s in range(N):
        z = np.concatenate([[0], (flow[:, s] == 0).astype(np.int8), [0]])
        d = np.diff(z)
        st, en = np.where(d == 1)[0], np.where(d == -1)[0]
        runs.extend((en - st).tolist())
    runs = np.array(runs) if runs else np.array([0])

    x = flow - flow.mean(axis=0)
    ac288 = float((x[:-288] * x[288:]).sum() / (x * x).sum())

    win = {}
    for sp in ("train", "val", "test"):
        t, s = D.valid_windows(flow, sp, bounds)
        win[sp] = {"unfiltered": int(D.count_windows_unfiltered(bounds, sp, N)),
                   "complete_case": int(len(t)),
                   "dropped_fraction": float(1 - len(t) / D.count_windows_unfiltered(bounds, sp, N))}

    mean, std = D.train_scaler(flow, bounds)
    part = {"iid": {"by_seed": {}}, "non_iid": {}}
    for sd in (0, 1, 2):
        cl = D.partition_sensors(flow, bounds, "iid", seed=sd)
        part["iid"]["by_seed"][str(sd)] = {"sizes": [len(c) for c in cl],
                                           "sensor_mean_w1": D.sensor_mean_w1(flow, bounds, cl),
                                           "pooled_value_w1": D.pooled_value_w1(flow, bounds, cl)}
    cl = D.partition_sensors(flow, bounds, "non_iid")
    part["non_iid"] = {"sizes": [len(c) for c in cl],
                       "sensor_mean_w1": D.sensor_mean_w1(flow, bounds, cl),
                       "pooled_value_w1": D.pooled_value_w1(flow, bounds, cl)}
    part["definitions"] = {"sensor_mean_w1": "primary: W1 between client distributions of per-sensor valid training means",
                           "pooled_value_w1": "secondary: W1 between clients' pooled valid training flow values"}
    means, cnt = D.sensor_train_means(flow, bounds)
    zero_frac = (flow[bounds["train"][0]:bounds["train"][1]] == 0).mean(axis=0)

    audit = {
        "source_file": str(npz_path),
        "sha256": D.sha256(npz_path),
        "shape": list(raw.shape),
        "target_channel": 0,
        "channel_means": raw.reshape(-1, 3).mean(0).tolist(),
        "nan": int(np.isnan(raw).sum()), "inf": int(np.isinf(raw).sum()),
        "zero_flow_entries": int((flow == 0).sum()),
        "zero_flow_fraction": float((flow == 0).mean()),
        "max_zero_run": int(runs.max()), "mean_zero_run": float(runs.mean()),
        "sensors_with_any_zero": int((flow == 0).any(axis=0).sum()),
        "worst_sensor_zero_fraction_train": float(zero_frac.max()),
        "lag288_autocorr": ac288,
        "split_bounds": {k: list(v) for k, v in bounds.items()},
        "phase_offsets_global_t_mod_288": {k: int(v[0] % D.PERIOD) for k, v in bounds.items()},
        "windows": win,
        "scaler_train_valid_only": {"mean": mean, "std": std},
        "training_flow_upload_reference_bytes": int(bounds["train"][1] * N * 4),   # primary reference
        "full_stream_flow_reference_bytes": int(T * N * 4),                        # all time steps, not used for the main comparison
        "partitions": part,
        "sensor_train_mean_flow": {"min": float(means.min()), "max": float(means.max())},
    }
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(json.dumps(audit, indent=2))
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    base = Path(__file__).resolve().parent.parent
    main(base / "data" / "PEMS08.npz", base / "results" / "dataset_audit.json")
