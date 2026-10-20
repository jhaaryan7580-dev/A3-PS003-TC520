"""Compact MLP (14 -> 32 ReLU -> 1) in plain NumPy, with explicit backprop and Adam.

Parameters (513 total):  W1 (14,32)=448, b1 (32)=32, W2 (32,)=32, b2 ()=1.
Loss: mean squared error on the scaled flow. Model payload for communication = 513 x 4 bytes.
"""
import numpy as np

N_IN, N_HID = 14, 32
ORDER = ("W1", "b1", "W2", "b2")
SHAPES = {"W1": (N_IN, N_HID), "b1": (N_HID,), "W2": (N_HID,), "b2": (1,)}


def n_params():
    return sum(int(np.prod(s)) for s in SHAPES.values())


def init_params(seed, dtype=np.float32):
    rng = np.random.default_rng(seed)
    return {"W1": (rng.standard_normal(SHAPES["W1"]) * np.sqrt(2.0 / N_IN)).astype(dtype),
            "b1": np.zeros(SHAPES["b1"], dtype=dtype),
            "W2": (rng.standard_normal(SHAPES["W2"]) * np.sqrt(1.0 / N_HID)).astype(dtype),
            "b2": np.zeros(SHAPES["b2"], dtype=dtype)}


def payload_bytes(params):
    """Bytes of the model as exchanged: sum of numel x element size over the tensors."""
    return int(sum(p.size * p.itemsize for p in params.values()))


def forward(params, X):
    z1 = X @ params["W1"] + params["b1"]
    a1 = np.maximum(z1, 0)
    out = a1 @ params["W2"] + params["b2"][0]
    return out, (X, z1, a1)


def loss_and_grads(params, X, y):
    out, (X, z1, a1) = forward(params, X)
    n = len(y)
    err = out - y
    loss = float((err.astype(np.float64) ** 2).mean())
    dout = (2.0 / n) * err
    g = {"W2": a1.T @ dout, "b2": np.array([dout.sum()], dtype=dout.dtype)}
    dz1 = np.outer(dout, params["W2"]) * (z1 > 0)
    g["W1"] = X.T @ dz1
    g["b1"] = dz1.sum(axis=0)
    return loss, g


def predict(params, X, batch=500_000):
    return np.concatenate([forward(params, X[i:i + batch])[0] for i in range(0, len(X), batch)])


def get_flat(params):
    return np.concatenate([params[k].ravel() for k in ORDER])


def set_flat(params, vec):
    i = 0
    for k in ORDER:
        n = params[k].size
        params[k][...] = vec[i:i + n].reshape(params[k].shape)
        i += n


def copy_params(params):
    return {k: v.copy() for k, v in params.items()}


class Adam:
    """Standard Adam. State is local to whoever owns the optimiser (never communicated)."""

    def __init__(self, params, lr=1e-3, b1=0.9, b2=0.999, eps=1e-8):
        self.lr, self.b1, self.b2, self.eps, self.t = lr, b1, b2, eps, 0
        self.m = {k: np.zeros_like(v) for k, v in params.items()}
        self.v = {k: np.zeros_like(v) for k, v in params.items()}

    def step(self, params, grads):
        self.t += 1
        c1, c2 = 1 - self.b1 ** self.t, 1 - self.b2 ** self.t
        for k in params:
            self.m[k] = self.b1 * self.m[k] + (1 - self.b1) * grads[k]
            self.v[k] = self.b2 * self.v[k] + (1 - self.b2) * grads[k] ** 2
            params[k] -= (self.lr * (self.m[k] / c1) / (np.sqrt(self.v[k] / c2) + self.eps)).astype(params[k].dtype)


def train_epochs(params, X, y, epochs, batch, rng, opt):
    """Mini-batch training with a fresh shuffle each epoch. Returns mean training loss per epoch."""
    losses = []
    n = len(y)
    for _ in range(epochs):
        perm = rng.permutation(n)
        tot, cnt = 0.0, 0
        for i in range(0, n, batch):
            idx = perm[i:i + batch]
            loss, g = loss_and_grads(params, X[idx], y[idx])
            opt.step(params, g)
            tot += loss * len(idx)
            cnt += len(idx)
        losses.append(tot / cnt)
    return losses
