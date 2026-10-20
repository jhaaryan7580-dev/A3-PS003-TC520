"""Tiny smoke run: does the pipeline run end to end? Validation only; no result claims, test set untouched."""
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import data as D
import models as Mo

base = Path(__file__).resolve().parent.parent
flow = D.load_flow(base / "data" / "PEMS08.npz")
bounds = D.split_bounds(len(flow))
mean, std = D.train_scaler(flow, bounds)

t0 = time.time()
Xtr, ytr, ttr, _ = D.build_split(flow, "train", bounds, mean, std)
Xva, yva, tva, sva = D.build_split(flow, "val", bounds, mean, std)
t_build = time.time() - t0

rng = np.random.default_rng(0)
sub = rng.choice(len(ytr), 200_000, replace=False)           # smoke subset only
p = Mo.init_params(0)
opt = Mo.Adam(p, lr=1e-3)
t0 = time.time()
losses = Mo.train_epochs(p, Xtr[sub], ytr[sub], 2, 1024, rng, opt)
t_train = time.time() - t0

pred = Mo.predict(p, Xva) * std + mean
yv = yva * std + mean
val_mae = float(np.abs(pred - yv).mean())
out = {"purpose": "smoke test only, validation split, 200k-window subset, 2 epochs; not a result",
       "train_windows": int(len(ytr)), "val_windows": int(len(yva)),
       "train_loss_per_epoch_scaled": losses, "val_mae_flow_units": val_mae,
       "seconds_build": t_build, "seconds_train_200k_x2epochs": t_train,
       "est_seconds_full_epoch": t_train / 2 * len(ytr) / 200_000}
(base / "results" / "smoke_results.json").write_text(json.dumps(out, indent=2))
print(json.dumps(out, indent=2))
