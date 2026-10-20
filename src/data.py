"""Data layer for the PS-003 federated traffic-flow study.

Design rules (see docs/DECISIONS.md):
  * channel 0 of PEMS08 is the flow target
  * one chronological 70/15/15 split shared by all sensors
  * windows are built inside each split and never cross a boundary
  * the daily-cycle phase always uses the GLOBAL time index t mod 288
    (a split-local index would shift validation/test by 115 and 201 slots)
  * exact zero flow is treated as a missing marker; any window with a zero
    in its 12 inputs or its target is dropped (complete-case policy)
  * scaling statistics, sensor rankings and client membership use training data only
"""
import hashlib
import numpy as np

LAGS = 12
PERIOD = 288
N_CLIENTS = 5


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_flow(path):
    """Return flow array of shape (T, N) from the PEMS08 npz (channel 0)."""
    d = np.load(path)["data"]
    return d[:, :, 0].astype(np.float64)


def split_bounds(T, train_frac=0.70, val_frac=0.15):
    n_train = int(train_frac * T)
    n_val = int(val_frac * T)
    return {"train": (0, n_train), "val": (n_train, n_train + n_val), "test": (n_train + n_val, T)}


def valid_windows(flow, split, bounds, lags=LAGS, horizon=1):
    """Indices (t, sensor) of complete-case windows of one split.

    The target is at global index t (+ horizon - 1 for longer horizons);
    inputs are t-lags .. t-1 (for horizon 1). Everything lies inside the split.
    Returns int arrays (t_target, sensor).
    """
    a, b = bounds[split]
    first = a + lags + horizon - 1          # first target index that keeps all inputs in the split
    ts = np.arange(first, b)
    nz = flow != 0                           # (T, N) valid marker
    # input block validity: all of t-lags-horizon+1 .. t-horizon must be valid, plus the target at t
    csum = np.vstack([np.zeros((1, flow.shape[1]), dtype=np.int64), np.cumsum(nz, axis=0)])
    lo = ts - lags - horizon + 1
    hi = ts - horizon + 1                    # exclusive end of the input block
    block_ok = (csum[hi] - csum[lo]) == lags
    target_ok = nz[ts]
    ok = block_ok & target_ok                # (len(ts), N)
    ti, si = np.nonzero(ok)
    return ts[ti], si


def count_windows_unfiltered(bounds, split, n_sensors, lags=LAGS, horizon=1):
    a, b = bounds[split]
    return (b - (a + lags + horizon - 1)) * n_sensors


def train_scaler(flow, bounds):
    """Mean/std over valid (non-zero) TRAIN entries only."""
    a, b = bounds["train"]
    x = flow[a:b]
    x = x[x != 0]
    return float(x.mean()), float(x.std())


def build_xy(flow, t, s, mean, std, lags=LAGS, horizon=1):
    """Features and target for windows (t, s). Features: 12 scaled lags + sin/cos of GLOBAL phase."""
    idx = (t - horizon + 1)[:, None] - np.arange(lags, 0, -1)[None, :]   # (n, lags) input indices
    lagv = (flow[idx, s[:, None]] - mean) / std
    phase = 2 * np.pi * (t % PERIOD) / PERIOD
    X = np.concatenate([lagv, np.sin(phase)[:, None], np.cos(phase)[:, None]], axis=1).astype(np.float32)
    y = ((flow[t, s] - mean) / std).astype(np.float32)
    return X, y


def build_split(flow, split, bounds, mean, std, chunk=400_000):
    """All complete-case windows of one split: X (n,14) float32, y (n,) float32, t, s."""
    t, s = valid_windows(flow, split, bounds)
    X = np.empty((len(t), LAGS + 2), dtype=np.float32)
    y = np.empty(len(t), dtype=np.float32)
    for i in range(0, len(t), chunk):
        X[i:i + chunk], y[i:i + chunk] = build_xy(flow, t[i:i + chunk], s[i:i + chunk], mean, std)
    return X, y, t, s


def sensor_train_means(flow, bounds):
    """Per-sensor mean over valid (non-zero) training steps."""
    a, b = bounds["train"]
    x = flow[a:b]
    cnt = (x != 0).sum(axis=0)
    return x.sum(axis=0) / np.maximum(cnt, 1), cnt


def partition_sensors(flow, bounds, mode, seed=0, n_clients=N_CLIENTS):
    """Assign sensors to clients. Uses training data only.

    iid     : seeded random permutation, equal-size chunks
    non_iid : sort sensors by valid training mean flow, cut into contiguous quiet-to-busy bands
    """
    n = flow.shape[1]
    if mode == "iid":
        order = np.random.default_rng(seed).permutation(n)
    elif mode == "non_iid":
        means, cnt = sensor_train_means(flow, bounds)
        if (cnt == 0).any():
            raise ValueError("sensor with no valid training flow")
        order = np.argsort(means, kind="stable")
    else:
        raise ValueError(mode)
    return [np.sort(c) for c in np.array_split(order, n_clients)]


def sensor_mean_w1(flow, bounds, clients):
    """PRIMARY heterogeneity statistic (locked definition).

    One valid (non-zero) training mean per sensor; each client contributes its 34 sensor means;
    return the mean pairwise 1-D Wasserstein-1 distance between those client distributions.
    """
    from scipy.stats import wasserstein_distance
    means, _ = sensor_train_means(flow, bounds)
    d = [wasserstein_distance(means[clients[i]], means[clients[j]])
         for i in range(len(clients)) for j in range(i + 1, len(clients))]
    return float(np.mean(d))


def pooled_value_w1(flow, bounds, clients, max_per_client=200_000, seed=0):
    """SECONDARY statistic: W1 between clients' pooled valid training flow VALUES (not sensor means).
    Not comparable with sensor_mean_w1."""
    from scipy.stats import wasserstein_distance
    a, b = bounds["train"]
    rng = np.random.default_rng(seed)
    samples = []
    for c in clients:
        v = flow[a:b][:, c].ravel()
        v = v[v != 0]
        if len(v) > max_per_client:
            v = rng.choice(v, max_per_client, replace=False)
        samples.append(v)
    d = [wasserstein_distance(samples[i], samples[j])
         for i in range(len(samples)) for j in range(i + 1, len(samples))]
    return float(np.mean(d))
