import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import baselines as B
import data as D
import metrics as M
from test_data import synthetic


def test_daily_cycle_is_near_noise_floor_on_periodic_series():
    # sensors have very different levels; a pooled-across-sensors baseline would fail here
    f = synthetic(T=3000, N=6)
    b = D.split_bounds(len(f))
    tab = B.daily_cycle_table(f, b)
    for sp in ("val", "test"):
        t, s = D.valid_windows(f, sp, b)
        mae = np.abs(B.daily_cycle_pred(tab, t, s) - f[t, s]).mean()
        assert mae < 6.0          # noise std is 5, so expected MAE is about 4


def test_pooled_baseline_would_fail_the_same_test():
    f = synthetic(T=3000, N=6)
    b = D.split_bounds(len(f))
    tab = B.daily_cycle_table(f, b)
    pooled = tab.mean(axis=1, keepdims=True) * np.ones((1, f.shape[1]))
    t, s = D.valid_windows(f, "test", b)
    assert np.abs(pooled[t % 288, s] - f[t, s]).mean() > 50


def test_metrics_relative_error_and_gap():
    y = np.array([100., 100., 10., 10.]); p = np.array([110., 90., 11., 9.])
    clients = [np.array([0, 1]), np.array([2, 3])]
    s = np.array([0, 1, 2, 3])
    r = M.per_client(y, p, s, clients)
    assert abs(r["clients"][0]["mae"] - 10) < 1e-9 and abs(r["clients"][1]["mae"] - 1) < 1e-9
    assert abs(r["clients"][0]["relative_abs_error"] - 0.1) < 1e-9
    assert abs(r["gap_relative_error"] - 0.0) < 1e-9      # same relative error, different MAE
    assert abs(r["gap_mae"] - 9) < 1e-9
