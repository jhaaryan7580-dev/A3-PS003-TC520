import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import data as D


def synthetic(T=2000, N=6, seed=0):
    rng = np.random.default_rng(seed)
    t = np.arange(T)
    base = 100 + 80 * np.sin(2 * np.pi * (t % 288) / 288)
    scale = np.linspace(0.5, 2.0, N)
    return base[:, None] * scale[None, :] + 5 * rng.standard_normal((T, N)) + 300  # strictly positive


def test_split_is_chronological_and_complete():
    b = D.split_bounds(17856)
    assert b["train"] == (0, 12499) and b["val"] == (12499, 15177) and b["test"] == (15177, 17856)


def test_windows_never_cross_split_boundaries():
    f = synthetic()
    b = D.split_bounds(len(f))
    for sp in ("train", "val", "test"):
        t, s = D.valid_windows(f, sp, b)
        a, e = b[sp]
        assert t.min() - D.LAGS >= a and t.max() < e


def test_unfiltered_count_matches_formula_when_no_zeros():
    f = synthetic()
    b = D.split_bounds(len(f))
    for sp in ("train", "val", "test"):
        t, s = D.valid_windows(f, sp, b)
        assert len(t) == D.count_windows_unfiltered(b, sp, f.shape[1])


def test_zero_in_input_or_target_drops_window():
    f = synthetic()
    b = D.split_bounds(len(f))
    f[500, 2] = 0.0
    t, s = D.valid_windows(f, "train", b)
    bad = (s == 2) & (t >= 500) & (t <= 512)       # windows whose inputs or target touch index 500
    assert not bad.any()
    assert ((s == 2) & (t == 513)).any()            # first window clear of the zero is kept


def test_scaler_uses_train_only():
    f = synthetic()
    b = D.split_bounds(len(f))
    m1, s1 = D.train_scaler(f, b)
    f2 = f.copy()
    f2[b["test"][0]:] *= 100                        # change the test period massively
    m2, s2 = D.train_scaler(f2, b)
    assert (m1, s1) == (m2, s2)


def test_phase_uses_global_index():
    f = synthetic()
    b = D.split_bounds(len(f))
    t, s = D.valid_windows(f, "val", b)
    X, y = D.build_xy(f, t[:50], s[:50], 0.0, 1.0)
    expect = np.sin(2 * np.pi * (t[:50] % 288) / 288)
    assert np.allclose(X[:, D.LAGS], expect, atol=1e-6)
    assert b["val"][0] % 288 != 0                   # the failure mode this guards against is real


def test_features_contain_no_future_values():
    f = synthetic()
    b = D.split_bounds(len(f))
    t, s = D.valid_windows(f, "train", b)
    X, y = D.build_xy(f, t[:20], s[:20], 0.0, 1.0)
    for i in range(20):
        assert np.allclose(X[i, :D.LAGS], f[t[i] - D.LAGS:t[i], s[i]], atol=1e-4)
        assert np.isclose(y[i], f[t[i], s[i]], atol=1e-4)


def test_partitions_use_train_means_and_are_balanced():
    f = synthetic()
    b = D.split_bounds(len(f))
    cl = D.partition_sensors(f, b, "non_iid", n_clients=3)
    means, _ = D.sensor_train_means(f, b)
    assert all(len(c) == 2 for c in cl)
    assert means[cl[0]].max() <= means[cl[1]].min() <= means[cl[1]].max() <= means[cl[2]].min()
    f2 = f.copy()
    f2[b["test"][0]:, 0] = 1e6                      # change test only; membership must not move
    cl2 = D.partition_sensors(f2, b, "non_iid", n_clients=3)
    assert all((a == c).all() for a, c in zip(cl, cl2))
    iid_a = D.partition_sensors(f, b, "iid", seed=1, n_clients=3)
    iid_b = D.partition_sensors(f, b, "iid", seed=1, n_clients=3)
    assert all((a == c).all() for a, c in zip(iid_a, iid_b))
