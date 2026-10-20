import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import check_results as C

ROOT = Path(__file__).resolve().parents[1]
FULL = ROOT / "results" / "full_results"
CFG = json.loads((ROOT / "configs" / "full.json").read_text())


def copy_full(tmp_path):
    out = tmp_path / "full"
    shutil.copytree(FULL, out)
    return out


def test_wrongcfg_is_rejected(tmp_path):
    out = copy_full(tmp_path)
    wrong = {**CFG, "rounds": CFG["rounds"] + 1}
    problems = C.check_dir(out, wrong)
    assert any("config hash" in p or "metadata config" in p for p in problems)


def test_malformed_json_is_a_failure_not_traceback(tmp_path):
    out = copy_full(tmp_path)
    (out / "fedavg_iid_seed0.json").write_text("{not json")
    problems = C.check_dir(out, CFG)
    assert any("malformed JSON" in p for p in problems)


def test_missing_files_are_reported(tmp_path):
    out = copy_full(tmp_path)
    (out / "centralised_seed0.json").unlink()
    assert any("centralised_seed0.json" in p and "missing" in p for p in C.check_dir(out, CFG))


def test_local_history_must_be_complete(tmp_path):
    out = copy_full(tmp_path)
    path = out / "local_iid_seed0.json"
    result = json.loads(path.read_text())
    result["history"] = [row for row in result["history"] if not (row["client"] == 4 and row["epoch"] == 30)]
    path.write_text(json.dumps(result))
    assert any("client 4" in p and "epoch" in p for p in C.check_dir(out, CFG))


def test_bad_best_value_is_rejected(tmp_path):
    out = copy_full(tmp_path)
    path = out / "centralised_seed0.json"
    result = json.loads(path.read_text())
    result["best_checkpoint"]["val_mae"] += 1.0
    path.write_text(json.dumps(result))
    assert any("checkpoint val_mae" in p for p in C.check_dir(out, CFG))


def test_pooled_rmse_identity_is_rejected(tmp_path):
    out = copy_full(tmp_path)
    path = out / "fedavg_iid_seed0.json"
    result = json.loads(path.read_text())
    result["test"]["overall"]["rmse"] += 1.0
    path.write_text(json.dumps(result))
    assert any("pooled" in p and "RMSE" in p for p in C.check_dir(out, CFG))


def test_subset_conditions_is_supported(tmp_path):
    out = tmp_path / "diag"
    shutil.copytree(ROOT / "results" / "diagnostic_100rounds", out)
    diag = json.loads((ROOT / "configs" / "diagnostic_100rounds.json").read_text())
    assert C.check_dir(out, diag, ["fedavg_iid", "fedavg_non_iid"]) == []
