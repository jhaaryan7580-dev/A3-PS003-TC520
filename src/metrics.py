"""Metrics on the original flow scale. All methods are scored on the same complete-case windows."""
import numpy as np


def basic(y, p):
    e = p - y
    return {"mae": float(np.abs(e).mean()),
            "rmse": float(np.sqrt((e ** 2).mean())),
            "relative_abs_error": float(np.abs(e).sum() / y.sum()),   # sum |err| / sum actual
            "n": int(len(y))}


def per_client(y, p, sensors, clients):
    """Metrics per client plus the worst-minus-best gaps (relative error is the headline gap)."""
    owner = np.empty(max(int(c.max()) for c in clients) + 1, dtype=int)
    for k, c in enumerate(clients):
        owner[c] = k
    which = owner[sensors]
    out = [basic(y[which == k], p[which == k]) for k in range(len(clients))]
    rel = [o["relative_abs_error"] for o in out]
    mae = [o["mae"] for o in out]
    return {"clients": out,
            "gap_relative_error": float(max(rel) - min(rel)),
            "gap_mae": float(max(mae) - min(mae))}
