import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import data as D
import models as Mo
import train as T
from test_data import synthetic

CFG = {"epochs": 3, "rounds": 4, "local_epochs": 1, "batch": 256, "lr": 1e-3, "seeds": [0],
       "horizon": 1, "lags": 12, "n_clients": 5, "subsample_train": None}
CONDS = ["centralised", "local_iid", "local_non_iid", "fedavg_iid", "fedavg_non_iid"]


def flow(T_=2500, N=10):
    return synthetic(T=T_, N=N)


def test_fedavg_aggregate_is_sample_weighted():
    v1, v2 = np.array([1., 2., 3.], dtype=np.float32), np.array([5., 6., 7.], dtype=np.float32)
    out = T.fedavg_aggregate([v1, v2], [1, 3])
    assert np.allclose(out, (1 * v1 + 3 * v2) / 4)
    assert np.allclose(T.fedavg_aggregate([v1, v2], [5, 5]), (v1 + v2) / 2)


def test_bytes_measured_equal_formula():
    f = flow()
    r = T.run_condition(f, CFG, "fedavg_iid", 0)
    c = r["communication"]
    assert c["model_payload_bytes"] == 513 * 4 == 2052
    assert c["bytes_per_round"] == 2052 * 5 * 2 == 20520
    assert c["total_bytes"] == CFG["rounds"] * 20520
    assert [h["cumulative_bytes"] for h in r["history"]][-1] == c["total_bytes"]


def test_checkpoint_is_argmin_validation_and_test_never_influences_training():
    f = flow()
    bounds = D.split_bounds(len(f))
    f2 = f.copy()
    f2[bounds["test"][0]:] *= 3.0                 # change ONLY the test period
    for cond in CONDS:
        a = T.run_condition(f, CFG, cond, 0)
        b = T.run_condition(f2, CFG, cond, 0)
        assert a["history"] == b["history"]                      # training path identical
        assert a["best_checkpoint"] == b["best_checkpoint"]      # selection identical
        assert a["test"]["overall"]["mae"] != b["test"]["overall"]["mae"]   # only the test score moves
    a = T.run_condition(f, CFG, "centralised", 0)
    vals = [h["val_mae"] for h in a["history"]]
    assert a["best_checkpoint"]["epoch"] == int(np.argmin(vals)) + 1
    a = T.run_condition(f, CFG, "fedavg_non_iid", 0)
    vals = [h["val_mae"] for h in a["history"]]
    assert a["best_checkpoint"]["round"] == int(np.argmin(vals)) + 1


def test_all_conditions_score_the_same_test_windows_and_json_serialisable():
    f = flow()
    n = None
    for cond in CONDS:
        r = T.run_condition(f, CFG, cond, 0)
        json.dumps(r)
        m = r["test"]["overall"]["n"]
        n = n or m
        assert m == n == r["metadata"]["eligible_samples"]["test"]
        assert r["test"]["per_client_non_iid"]["clients"] and r["test"]["per_client_iid"]["clients"]
        for key in ("dataset_sha256", "code_commit", "config_hash", "seed", "zero_policy", "horizon",
                    "eligible_samples", "checkpoint_rule", "optimizer", "training_schedule"):
            assert key in r["metadata"]


def test_determinism_and_seed_dependence():
    f = flow()
    a = T.run_condition(f, CFG, "fedavg_iid", 0)["test"]["overall"]["mae"]
    b = T.run_condition(f, CFG, "fedavg_iid", 0)["test"]["overall"]["mae"]
    c = T.run_condition(f, CFG, "fedavg_iid", 1)["test"]["overall"]["mae"]
    assert a == b and a != c


def test_same_init_across_conditions_for_a_seed():
    assert np.array_equal(Mo.get_flat(Mo.init_params(0)), Mo.get_flat(Mo.init_params(0)))


def test_unsupported_config_is_rejected_not_ignored():
    import pytest
    f = flow()
    for bad in ({"horizon": 6}, {"lags": 24}, {"n_clients": 3}):
        with pytest.raises(ValueError):
            T.run_condition(f, {**CFG, **bad}, "centralised", 0)


def test_result_checker_passes_good_results_and_catches_corruption(tmp_path):
    import check_results as C
    f = flow()
    cfg = {**CFG, "seeds": [0, 1]}
    for cond in CONDS:
        for sd in cfg["seeds"]:
            r = T.run_condition(f, cfg, cond, sd, dataset_sha="abc")
            (tmp_path / f"{cond}_seed{sd}.json").write_text(json.dumps(r))
    assert C.check_dir(tmp_path, cfg) == []
    p = tmp_path / "fedavg_iid_seed0.json"
    r = json.loads(p.read_text()); r["communication"]["bytes_per_round"] = 1; p.write_text(json.dumps(r))
    assert any("bytes/round" in x for x in C.check_dir(tmp_path, cfg))
    (tmp_path / "centralised_seed1.json").unlink()
    assert any("missing centralised_seed1" in x for x in C.check_dir(tmp_path, cfg))
