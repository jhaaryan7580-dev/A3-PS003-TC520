"""Training conditions: centralised, local-only, FedAvg. All NumPy.

Rules enforced here:
  * checkpoint = minimum VALIDATION MAE; the test split is touched only in the final scoring step
  * same architecture, loss, optimiser, learning rate and batch size in every condition
  * same initial weights for a given seed in every condition
  * FedAvg: all clients every round, sample-weighted average, Adam state local and reset each round
  * communication bytes are counted from the tensors actually exchanged
"""
import numpy as np

import data as D
import meta
import metrics as M
import models as Mo

CHECKPOINT_RULE = "minimum validation MAE; test scored once after selection"


# ---------------------------------------------------------------- config validation
REQUIRED = ("epochs", "rounds", "local_epochs", "batch", "lr", "horizon", "lags", "n_clients")


def validate_cfg(cfg):
    """Reject configs the code cannot honour, instead of silently ignoring fields."""
    missing = [k for k in REQUIRED if k not in cfg]
    if missing:
        raise ValueError(f"config is missing {missing}")
    if cfg["horizon"] != 1:
        raise ValueError("only horizon=1 (next 5-minute step) is implemented")
    if cfg["lags"] != D.LAGS or Mo.N_IN != D.LAGS + 2:
        raise ValueError(f"lags must be {D.LAGS}: the 14-32-1 model is tied to 12 lags + 2 cycle features")
    if cfg["n_clients"] != D.N_CLIENTS:
        raise ValueError(f"n_clients must be {D.N_CLIENTS} in the must-have matrix")


# ---------------------------------------------------------------- data preparation
def make_data(flow, cfg):
    validate_cfg(cfg)
    bounds = D.split_bounds(len(flow))
    mean, std = D.train_scaler(flow, bounds)
    sp = {}
    for name in ("train", "val", "test"):
        X, y, t, s = D.build_split(flow, name, bounds, mean, std)
        sp[name] = {"X": X, "y": y, "t": t, "s": s}
    n_sub = cfg.get("subsample_train")
    if n_sub and n_sub < len(sp["train"]["y"]):
        keep = np.sort(np.random.default_rng(0).choice(len(sp["train"]["y"]), n_sub, replace=False))
        sp["train"] = {k: v[keep] for k, v in sp["train"].items()}
    return bounds, mean, std, sp


def client_view(split, sensors):
    m = np.isin(split["s"], sensors)
    return {"X": split["X"][m], "y": split["y"][m], "s": split["s"][m]}


def val_mae(params, view, std):
    """Validation MAE in flow units (the scaling is linear, so MAE scales by std)."""
    return float(std * np.abs(Mo.predict(params, view["X"]) - view["y"]).mean())


def val_loss(params, view):
    return float(((Mo.predict(params, view["X"]).astype(np.float64) - view["y"]) ** 2).mean())


# ---------------------------------------------------------------- FedAvg pieces
def fedavg_aggregate(vectors, counts):
    """Sample-weighted average of flat parameter vectors: sum_k (n_k / n) * w_k."""
    w = np.asarray(counts, dtype=np.float64)
    w = w / w.sum()
    agg = np.zeros_like(vectors[0], dtype=np.float64)
    for wk, v in zip(w, vectors):
        agg += wk * v.astype(np.float64)
    return agg.astype(vectors[0].dtype)


# ---------------------------------------------------------------- conditions
def run_centralised(sp, cfg, seed, std):
    rng = np.random.default_rng([seed, 1])
    p = Mo.init_params(seed)
    opt = Mo.Adam(p, lr=cfg["lr"])
    hist, best = [], {"val_mae": np.inf}
    for ep in range(1, cfg["epochs"] + 1):
        loss = Mo.train_epochs(p, sp["train"]["X"], sp["train"]["y"], 1, cfg["batch"], rng, opt)[0]
        v = val_mae(p, sp["val"], std)
        hist.append({"epoch": ep, "train_loss_scaled": loss, "val_mae": v})
        if v < best["val_mae"]:
            best = {"val_mae": v, "epoch": ep, "params": Mo.copy_params(p)}
    return {"history": hist, "best": best, "predict": lambda X, s: Mo.predict(best["params"], X),
            "communication": {"bytes_per_round": 0, "total_bytes": 0, "note": "no model exchange"}}


def run_local(sp, cfg, seed, std, clients):
    models, hist_all, best_info = [], [], []
    for k, sens in enumerate(clients):
        tr, va = client_view(sp["train"], sens), client_view(sp["val"], sens)
        rng = np.random.default_rng([seed, 2, k])
        p = Mo.init_params(seed)
        opt = Mo.Adam(p, lr=cfg["lr"])
        best = {"val_mae": np.inf}
        for ep in range(1, cfg["epochs"] + 1):
            loss = Mo.train_epochs(p, tr["X"], tr["y"], 1, cfg["batch"], rng, opt)[0]
            v = val_mae(p, va, std)
            hist_all.append({"client": k, "epoch": ep, "train_loss_scaled": loss, "val_mae": v})
            if v < best["val_mae"]:
                best = {"val_mae": v, "epoch": ep, "params": Mo.copy_params(p)}
        models.append(best["params"])
        best_info.append({"client": k, "epoch": best["epoch"], "val_mae": best["val_mae"], "n_train": int(len(tr["y"]))})
    owner = np.empty(sum(len(c) for c in clients), dtype=int)
    for k, c in enumerate(clients):
        owner[c] = k

    def predict(X, s):
        out = np.empty(len(X), dtype=np.float32)
        for k in range(len(clients)):
            m = owner[s] == k
            if m.any():
                out[m] = Mo.predict(models[k], X[m])
        return out

    return {"history": hist_all, "best": {"per_client": best_info}, "predict": predict,
            "communication": {"bytes_per_round": 0, "total_bytes": 0, "note": "no model exchange"}}


def run_fedavg(sp, cfg, seed, std, clients):
    K = len(clients)
    views = [client_view(sp["train"], c) for c in clients]
    val_views = [client_view(sp["val"], c) for c in clients]
    counts = [len(v["y"]) for v in views]
    g = Mo.init_params(seed)
    hist, best = [], {"val_mae": np.inf}
    cum = 0
    for r in range(1, cfg["rounds"] + 1):
        vecs, up_bytes = [], 0
        down_bytes = Mo.payload_bytes(g) * K                     # server -> every client
        for k in range(K):
            loc = Mo.copy_params(g)
            opt = Mo.Adam(loc, lr=cfg["lr"])                      # fresh optimiser state each round
            rng = np.random.default_rng([seed, 3, r, k])
            Mo.train_epochs(loc, views[k]["X"], views[k]["y"], cfg["local_epochs"], cfg["batch"], rng, opt)
            vecs.append(Mo.get_flat(loc))
            up_bytes += Mo.payload_bytes(loc)                     # client -> server
        Mo.set_flat(g, fedavg_aggregate(vecs, counts))
        rb = down_bytes + up_bytes
        cum += rb
        v = val_mae(g, sp["val"], std)
        hist.append({"round": r, "val_mae": v, "val_loss_scaled": val_loss(g, sp["val"]),
                     "val_mae_per_client": [val_mae(g, vv, std) for vv in val_views],
                     "round_bytes": rb, "cumulative_bytes": cum})
        if v < best["val_mae"]:
            best = {"val_mae": v, "round": r, "params": Mo.copy_params(g)}
    return {"history": hist, "best": best, "predict": lambda X, s: Mo.predict(best["params"], X),
            "communication": {"bytes_per_round": hist[0]["round_bytes"], "total_bytes": cum,
                              "model_payload_bytes": Mo.payload_bytes(g), "clients": K, "rounds": cfg["rounds"],
                              "client_train_samples": counts}}


# ---------------------------------------------------------------- final scoring (the only place test is used)
def score_test(run, sp, flow_mean, std, partitions):
    X, y, s = sp["test"]["X"], sp["test"]["y"], sp["test"]["s"]
    p = run["predict"](X, s).astype(np.float64) * std + flow_mean
    yt = y.astype(np.float64) * std + flow_mean
    out = {"overall": M.basic(yt, p)}
    for name, cl in partitions.items():
        out[f"per_client_{name}"] = M.per_client(yt, p, s, cl)
    return out


def run_condition(flow, cfg, condition, seed, prepared=None, dataset_sha="n/a"):
    """condition: centralised | local_iid | local_non_iid | fedavg_iid | fedavg_non_iid"""
    validate_cfg(cfg)
    bounds, mean, std, sp = prepared or make_data(flow, cfg)
    parts = {"iid": D.partition_sensors(flow, bounds, "iid", seed=seed),
             "non_iid": D.partition_sensors(flow, bounds, "non_iid")}
    kind, _, part = condition.partition("_")
    if kind == "centralised":
        run = run_centralised(sp, cfg, seed, std)
    elif kind == "local":
        run = run_local(sp, cfg, seed, std, parts[part])
    elif kind == "fedavg":
        run = run_fedavg(sp, cfg, seed, std, parts[part])
    else:
        raise ValueError(condition)
    test = score_test(run, sp, mean, std, parts)
    best = {k: v for k, v in run["best"].items() if k != "params"}
    return {
        "condition": condition, "seed": seed, "partition_used": part or "n/a",
        "metadata": {
            "dataset_sha256": dataset_sha, "code_commit": meta.code_commit(),
            "config_hash": meta.config_hash(cfg), "config": cfg, "seed": seed,
            "zero_policy": "complete_case_windows", "horizon": 1, "lags": D.LAGS,
            "eligible_samples": {k: int(len(v["y"])) for k, v in sp.items()},
            "checkpoint_rule": CHECKPOINT_RULE,
            "optimizer": f"Adam lr={cfg['lr']} batch={cfg['batch']} MSE on scaled flow",
            "training_schedule": {"centralised/local epochs": cfg["epochs"], "fedavg rounds": cfg["rounds"],
                                 "fedavg local epochs": cfg["local_epochs"]},
            "scaler": {"mean": mean, "std": std}, "model_params": Mo.n_params(),
            "training_flow_upload_reference_bytes": int(bounds["train"][1] * flow.shape[1] * 4),
        },
        "best_checkpoint": best, "history": run["history"], "communication": run["communication"], "test": test,
    }
