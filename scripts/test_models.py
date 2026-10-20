import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import models as Mo


def tiny(n=64, seed=0, dtype=np.float64):
    rng = np.random.default_rng(seed)
    X = rng.standard_normal((n, 14)).astype(dtype)
    y = (np.sin(X[:, 0]) + 0.5 * X[:, 3]).astype(dtype)
    return X, y


def test_parameter_count_and_payload_bytes():
    p = Mo.init_params(0)
    assert Mo.n_params() == 513
    assert sum(v.size for v in p.values()) == 513
    assert Mo.payload_bytes(p) == 2052                      # 513 x 4 bytes, float32
    assert Mo.get_flat(p).size == 513


def test_forward_shape_and_finite():
    p = Mo.init_params(0)
    X, _ = tiny(dtype=np.float32)
    out, _ = Mo.forward(p, X)
    assert out.shape == (64,) and np.isfinite(out).all()


def test_gradients_match_finite_differences():
    p = Mo.init_params(1, dtype=np.float64)
    X, y = tiny()
    _, g = Mo.loss_and_grads(p, X, y)
    eps = 1e-6
    worst = 0.0
    for k in Mo.ORDER:
        flat = p[k].reshape(-1)
        for i in np.random.default_rng(0).choice(flat.size, min(flat.size, 12), replace=False):
            old = flat[i]
            flat[i] = old + eps; lp, _ = Mo.loss_and_grads(p, X, y)
            flat[i] = old - eps; lm, _ = Mo.loss_and_grads(p, X, y)
            flat[i] = old
            num = (lp - lm) / (2 * eps)
            ana = g[k].reshape(-1)[i]
            worst = max(worst, abs(num - ana) / max(1e-8, abs(num) + abs(ana)))
    assert worst < 1e-5


def test_training_is_deterministic_and_seed_dependent():
    X, y = tiny(n=256, dtype=np.float32)
    def run(seed):
        p = Mo.init_params(seed)
        Mo.train_epochs(p, X, y, 2, 32, np.random.default_rng(seed), Mo.Adam(p))
        return Mo.get_flat(p)
    assert np.array_equal(run(0), run(0))
    assert not np.array_equal(run(0), run(1))


def test_adam_reduces_loss():
    X, y = tiny(n=512, dtype=np.float32)
    p = Mo.init_params(0)
    l0, _ = Mo.loss_and_grads(p, X, y)
    Mo.train_epochs(p, X, y, 20, 64, np.random.default_rng(0), Mo.Adam(p, lr=1e-2))
    l1, _ = Mo.loss_and_grads(p, X, y)
    assert l1 < 0.5 * l0


def test_flat_roundtrip():
    p = Mo.init_params(3)
    v = Mo.get_flat(p)
    q = Mo.init_params(4)
    Mo.set_flat(q, v)
    assert np.array_equal(Mo.get_flat(q), v)
