"""Strict validation gate for saved experiment result JSON files.

The checker validates artifacts only; it never trains a model.  It is deliberately
safe at the release boundary: malformed JSON, missing keys, and wrong types are
reported as FAIL entries rather than escaping as tracebacks.

Examples::

    python src/check_results.py --dir results/full_results --config configs/full.json
    python src/check_results.py --dir results/full_results --config configs/full.json \
        --conditions fedavg_iid local_iid --dataset-sha256 SHA256
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any, Iterable

CONDITIONS = ["centralised", "local_iid", "local_non_iid", "fedavg_iid", "fedavg_non_iid"]
META_KEYS = (
    "dataset_sha256", "code_commit", "config_hash", "seed", "zero_policy",
    "horizon", "eligible_samples", "checkpoint_rule", "optimizer",
    "training_schedule",
)


def _finite(value: Any) -> bool:
    """Return False for NaN/Inf anywhere in a JSON-shaped object."""
    if isinstance(value, bool) or value is None or isinstance(value, str):
        return True
    if isinstance(value, (int, float)):
        return math.isfinite(value)
    if isinstance(value, dict):
        return all(_finite(k) and _finite(v) for k, v in value.items())
    if isinstance(value, (list, tuple)):
        return all(_finite(v) for v in value)
    return False


def _config_hash(cfg: dict[str, Any]) -> str:
    # Must match src/meta.py, including its default JSON separators.
    return hashlib.sha256(json.dumps(cfg, sort_keys=True).encode()).hexdigest()


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _same_number(a: Any, b: Any) -> bool:
    # Saved results are produced from the same JSON float values.  Exact equality
    # intentionally catches even small tampering with a checkpoint value.
    return _is_number(a) and _is_number(b) and math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-12)


def _load_json(path: Path) -> tuple[Any | None, str | None]:
    try:
        def reject_constant(value: str) -> None:
            raise ValueError(f"non-finite JSON constant {value}")
        return json.loads(path.read_text(encoding="utf-8"), parse_constant=reject_constant), None
    except Exception as exc:  # JSONDecodeError, OSError, Unicode errors, etc.
        return None, f"malformed JSON ({type(exc).__name__}: {exc})"


def _get(obj: Any, *keys: str) -> Any:
    """Safe nested lookup used only after validating that obj is a mapping."""
    for key in keys:
        if not isinstance(obj, dict):
            return None
        obj = obj.get(key)
    return obj


def _add(problems: list[str], tag: str, message: str) -> None:
    problems.append(f"{tag}: {message}")


def _check_metric_block(block: Any, tag: str, problems: list[str]) -> tuple[list[dict[str, Any]], int | None]:
    if not isinstance(block, dict):
        _add(problems, tag, "missing/invalid metric block")
        return [], None
    clients = block.get("clients")
    if not isinstance(clients, list):
        _add(problems, tag, "clients is not a list")
        return [], None
    required = ("mae", "rmse", "relative_abs_error", "n")
    total = 0
    for i, metric in enumerate(clients):
        if not isinstance(metric, dict):
            _add(problems, tag, f"client {i} metric is not an object")
            continue
        missing = [k for k in required if k not in metric]
        if missing:
            _add(problems, tag, f"client {i} metric lacks {missing}")
        for k in required[:-1]:
            if k in metric and not _is_number(metric[k]):
                _add(problems, tag, f"client {i} {k} is not finite numeric")
        n = metric.get("n")
        if not isinstance(n, int) or isinstance(n, bool) or n < 0:
            _add(problems, tag, f"client {i} n is not a non-negative integer")
        else:
            total += n
    for k in ("gap_relative_error", "gap_mae"):
        if k not in block or not _is_number(block.get(k)):
            _add(problems, tag, f"missing/non-finite {k}")
    if clients:
        rel = [m.get("relative_abs_error") for m in clients if isinstance(m, dict) and _is_number(m.get("relative_abs_error"))]
        mae = [m.get("mae") for m in clients if isinstance(m, dict) and _is_number(m.get("mae"))]
        if len(rel) == len(clients) and not _same_number(block.get("gap_relative_error"), max(rel) - min(rel)):
            _add(problems, tag, "gap_relative_error is not max-minus-min")
        if len(mae) == len(clients) and not _same_number(block.get("gap_mae"), max(mae) - min(mae)):
            _add(problems, tag, "gap_mae is not max-minus-min")
    return clients, total


def _check_tests(result: dict[str, Any], tag: str, problems: list[str], n_clients: int) -> None:
    test = result.get("test")
    if not isinstance(test, dict):
        _add(problems, tag, "missing test metrics")
        return
    overall = test.get("overall")
    if not isinstance(overall, dict):
        _add(problems, tag, "missing test.overall")
        return
    for k in ("mae", "rmse", "relative_abs_error"):
        if not _is_number(overall.get(k)):
            _add(problems, tag, f"test overall {k} is missing/non-finite")
    n = overall.get("n")
    if not isinstance(n, int) or isinstance(n, bool) or n < 0:
        _add(problems, tag, "test overall n is not a non-negative integer")
        n = None
    client_totals = []
    for part in ("iid", "non_iid"):
        clients, total = _check_metric_block(test.get(f"per_client_{part}"), f"{tag}/test/per_client_{part}", problems)
        if len(clients) != n_clients:
            _add(problems, tag, f"per_client_{part} has {len(clients)} clients, expected {n_clients}")
        client_totals.append(total)
        if n is not None and total is not None and total != n:
            _add(problems, tag, f"test count mismatch for {part}: clients {total} != overall {n}")
        if clients and all(isinstance(m, dict) and _is_number(m.get("mae")) and _is_number(m.get("rmse")) and isinstance(m.get("n"), int) for m in clients):
            total_n = sum(m["n"] for m in clients)
            if total_n > 0:
                pooled_mae = sum(m["mae"] * m["n"] for m in clients) / total_n
                pooled_rmse = math.sqrt(sum((m["rmse"] ** 2) * m["n"] for m in clients) / total_n)
                if not _same_number(overall.get("mae"), pooled_mae):
                    _add(problems, tag, f"overall MAE is not pooled {part} MAE")
                if not _same_number(overall.get("rmse"), pooled_rmse):
                    _add(problems, tag, f"overall RMSE is not pooled {part} RMSE")
    eligible = _get(result, "metadata", "eligible_samples", "test")
    if n is not None and eligible != n:
        _add(problems, tag, f"scored test count {n} != eligible test windows {eligible}")


def _argmin(items: list[dict[str, Any]], key: str) -> tuple[int | None, Any | None]:
    values = [x.get(key) for x in items]
    if not values or not all(_is_number(v) for v in values):
        return None, None
    i = min(range(len(values)), key=lambda j: values[j])
    return i, values[i]


def _check_history(result: dict[str, Any], cfg: dict[str, Any], tag: str, problems: list[str]) -> None:
    condition = result.get("condition")
    history = result.get("history")
    best = result.get("best_checkpoint")
    if not isinstance(history, list):
        _add(problems, tag, "history is not a list")
        return
    if not isinstance(best, dict):
        _add(problems, tag, "best_checkpoint is not an object")
        best = {}
    if condition == "centralised":
        expected = cfg.get("epochs")
        if len(history) != expected:
            _add(problems, tag, f"{len(history)} epochs, expected {expected}")
        epochs = [x.get("epoch") for x in history if isinstance(x, dict)]
        if len(epochs) != len(history) or len(set(epochs)) != len(epochs) or set(epochs) != set(range(1, int(expected) + 1)):
            _add(problems, tag, "history epochs are not a unique complete 1..epochs sequence")
        i, value = _argmin([x for x in history if isinstance(x, dict)], "val_mae")
        if i is not None:
            expected_epoch = i + 1
            if best.get("epoch") != expected_epoch:
                _add(problems, tag, "checkpoint is not the validation argmin")
            if not _same_number(best.get("val_mae"), value):
                _add(problems, tag, "checkpoint val_mae is not the validation minimum")
    elif isinstance(condition, str) and condition.startswith("local_"):
        expected_epochs = cfg.get("epochs")
        expected_clients = cfg.get("n_clients", 5)
        groups: dict[Any, list[dict[str, Any]]] = {}
        for item in history:
            if isinstance(item, dict):
                groups.setdefault(item.get("client"), []).append(item)
            else:
                _add(problems, tag, "local history contains a non-object")
        if expected_clients != 5:
            _add(problems, tag, "local results must contain 5 clients")
        if set(groups) != set(range(int(expected_clients))):
            _add(problems, tag, f"local history clients are not complete 0..{int(expected_clients)-1}")
        for client in range(int(expected_clients)):
            rows = groups.get(client, [])
            if len(rows) != expected_epochs:
                _add(problems, tag, f"client {client} has {len(rows)} epochs, expected {expected_epochs}")
            epochs = [x.get("epoch") for x in rows]
            if len(set(epochs)) != len(epochs) or set(epochs) != set(range(1, int(expected_epochs) + 1)):
                _add(problems, tag, f"client {client} epochs are not a unique complete 1..epochs sequence")
        entries = best.get("per_client")
        if not isinstance(entries, list):
            _add(problems, tag, "best_checkpoint.per_client is not a list")
            entries = []
        if len(entries) != int(expected_clients) or len({x.get("client") for x in entries if isinstance(x, dict)}) != len(entries):
            _add(problems, tag, "best_checkpoint does not contain one entry per client")
        for entry in entries:
            if not isinstance(entry, dict):
                _add(problems, tag, "best_checkpoint contains a non-object")
                continue
            client = entry.get("client")
            rows = groups.get(client, [])
            i, value = _argmin(rows, "val_mae")
            if i is None:
                continue
            if entry.get("epoch") != i + 1:
                _add(problems, tag, f"client {client} checkpoint is not validation argmin")
            if not _same_number(entry.get("val_mae"), value):
                _add(problems, tag, f"client {client} checkpoint val_mae is not validation minimum")
    elif isinstance(condition, str) and condition.startswith("fedavg_"):
        expected = cfg.get("rounds")
        if len(history) != expected:
            _add(problems, tag, f"{len(history)} rounds, expected {expected}")
        rounds = [x.get("round") for x in history if isinstance(x, dict)]
        if len(rounds) != len(history) or len(set(rounds)) != len(rounds) or set(rounds) != set(range(1, int(expected) + 1)):
            _add(problems, tag, "history rounds are not a unique complete 1..rounds sequence")
        i, value = _argmin([x for x in history if isinstance(x, dict)], "val_mae")
        if i is not None:
            if best.get("round") != i + 1:
                _add(problems, tag, "checkpoint is not the validation argmin")
            if not _same_number(best.get("val_mae"), value):
                _add(problems, tag, "checkpoint val_mae is not the validation minimum")
    else:
        _add(problems, tag, f"unknown condition {condition!r}")


def _check_communication(result: dict[str, Any], cfg: dict[str, Any], tag: str, problems: list[str]) -> None:
    if not str(result.get("condition", "")).startswith("fedavg_"):
        return
    c = result.get("communication")
    if not isinstance(c, dict):
        _add(problems, tag, "missing communication block")
        return
    history = result.get("history", [])
    model_params = _get(result, "metadata", "model_params")
    payload = c.get("model_payload_bytes")
    clients = c.get("clients")
    rounds = c.get("rounds")
    for name, value in (("model_payload_bytes", payload), ("clients", clients), ("rounds", rounds), ("bytes_per_round", c.get("bytes_per_round")), ("total_bytes", c.get("total_bytes"))):
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            _add(problems, tag, f"communication {name} is not a non-negative integer")
    if isinstance(model_params, int) and isinstance(payload, int) and payload != model_params * 4:
        _add(problems, tag, f"model payload {payload} != 4 bytes x model_params {model_params}")
    if isinstance(payload, int) and isinstance(clients, int) and c.get("bytes_per_round") != payload * clients * 2:
        _add(problems, tag, "bytes/round (bytes_per_round) does not equal downlink plus uplink payload")
    if isinstance(rounds, int) and isinstance(c.get("bytes_per_round"), int) and c.get("total_bytes") != c["bytes_per_round"] * rounds:
        _add(problems, tag, "total_bytes does not equal bytes_per_round x rounds")
    if isinstance(clients, int) and clients != cfg.get("n_clients"):
        _add(problems, tag, "communication client count differs from config")
    if isinstance(rounds, int) and rounds != cfg.get("rounds"):
        _add(problems, tag, "communication round count differs from config")
    cumulative = 0
    for i, row in enumerate(history if isinstance(history, list) else []):
        if not isinstance(row, dict):
            continue
        rb = row.get("round_bytes")
        cb = row.get("cumulative_bytes")
        if rb != c.get("bytes_per_round"):
            _add(problems, tag, f"round {i + 1} communication bytes differ from bytes_per_round")
        if isinstance(rb, int):
            cumulative += rb
            if cb != cumulative:
                _add(problems, tag, f"round {i + 1} cumulative communication bytes are wrong")


def check_dir(path: str | Path, cfg: dict[str, Any], conditions: Iterable[str] | None = None, dataset_sha256: str | None = None) -> list[str]:
    """Return validation problems; an empty list means PASS.

    The first three parameters retain the original public signature.  The
    optional fourth argument is intentionally keyword-friendly for callers that
    want to pin the dataset hash without using the CLI.
    """
    root = Path(path)
    problems: list[str] = []
    selected = list(CONDITIONS if conditions is None else conditions)
    # Accept either a normal iterable of names or a single comma-separated value.
    selected = [name.strip() for item in selected for name in str(item).split(",") if name.strip()]
    unknown = [name for name in selected if name not in CONDITIONS]
    for name in unknown:
        _add(problems, "conditions", f"unknown condition {name}")
    selected = [name for name in selected if name in CONDITIONS]
    if not isinstance(cfg, dict):
        return problems + ["config is not an object"]
    seeds = cfg.get("seeds")
    if not isinstance(seeds, list) or not all(isinstance(s, int) and not isinstance(s, bool) for s in seeds):
        return problems + ["config seeds is not a list of integers"]
    if not root.is_dir():
        return problems + [f"result directory does not exist: {root}"]
    expected_hash = _config_hash(cfg)
    runs: dict[tuple[str, int], dict[str, Any]] = {}
    expected_names = {f"{cond}_seed{seed}.json" for cond in selected for seed in seeds}
    known_names = {f"{cond}_seed{seed}.json" for cond in CONDITIONS for seed in seeds}
    for cond in selected:
        for seed in seeds:
            filename = f"{cond}_seed{seed}.json"
            f = root / filename
            if not f.is_file():
                _add(problems, filename, f"missing {filename}")
                continue
            value, error = _load_json(f)
            if error:
                _add(problems, filename, error)
                continue
            if not isinstance(value, dict):
                _add(problems, filename, "top-level JSON value is not an object")
                continue
            runs[(cond, seed)] = value
    # Catch stray result-shaped JSON files, while allowing unrelated notes such as
    # smoke_results.json in a result directory.
    for f in root.glob("*.json"):
        # A subset gate may intentionally inspect only FedAvg files in a
        # directory that also contains centralised/local artifacts.  Those
        # names are known and are not stray files; only unknown result-shaped
        # names are rejected.
        if f.name not in expected_names and f.name not in known_names and ("_seed" in f.stem or f.name.startswith("result")):
            _add(problems, f.name, "unexpected result filename")
    if not runs:
        return problems or ["no result files"]
    datasets: set[Any] = set()
    hashes: set[Any] = set()
    counts: set[Any] = set()
    for (condition, seed), result in runs.items():
        tag = f"{condition}/seed{seed}"
        if not _finite(result):
            _add(problems, tag, "non-finite value")
        if result.get("condition") != condition:
            _add(problems, tag, f"filename identity condition mismatch ({result.get('condition')!r})")
        if result.get("seed") != seed:
            _add(problems, tag, f"filename identity seed mismatch ({result.get('seed')!r})")
        metadata = result.get("metadata")
        if not isinstance(metadata, dict):
            _add(problems, tag, "metadata is missing or not an object")
            metadata = {}
        missing = [k for k in META_KEYS if k not in metadata]
        if missing:
            _add(problems, tag, f"metadata lacks {missing}")
        ds = metadata.get("dataset_sha256")
        ch = metadata.get("config_hash")
        datasets.add(ds)
        hashes.add(ch)
        if dataset_sha256 is not None and ds != dataset_sha256:
            _add(problems, tag, f"dataset hash {ds!r} != expected {dataset_sha256!r}")
        if ch != expected_hash:
            _add(problems, tag, "config hash does not match supplied config")
        if metadata.get("config") != cfg:
            _add(problems, tag, "metadata config does not equal supplied config")
        if metadata.get("seed") != seed:
            _add(problems, tag, "metadata seed field mismatch")
        n = _get(result, "test", "overall", "n")
        counts.add(n)
        eligible = _get(metadata, "eligible_samples", "test")
        if n != eligible:
            _add(problems, tag, "scored windows != eligible test windows")
        _check_history(result, cfg, tag, problems)
        _check_communication(result, cfg, tag, problems)
        _check_tests(result, tag, problems, int(cfg.get("n_clients", 5)))
    if len(datasets) > 1:
        _add(problems, "dataset", f"hash differs across files: {datasets}")
    if len(hashes) > 1:
        _add(problems, "config", "config hash differs across files")
    if len(counts) > 1:
        _add(problems, "test", f"different test window counts across conditions: {counts}")
    return problems


def _parse_conditions(values: list[str] | None) -> list[str] | None:
    if values is None:
        return None
    return [v for item in values for v in item.split(",") if v]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--config", required=True)
    ap.add_argument("--conditions", nargs="*", default=None, help="optional condition names (space- or comma-separated)")
    ap.add_argument("--dataset-sha256", default=None)
    args = ap.parse_args(argv)
    try:
        cfg_value, cfg_error = _load_json(Path(args.config))
        if cfg_error or not isinstance(cfg_value, dict):
            problems = [f"config: {cfg_error or 'top-level JSON value is not an object'}"]
        else:
            problems = check_dir(args.dir, cfg_value, _parse_conditions(args.conditions), args.dataset_sha256)
    except Exception as exc:  # release gate must report FAIL, never a traceback
        problems = [f"checker error ({type(exc).__name__}: {exc})"]
    if problems:
        print("FAIL:")
        print("\n".join(f"  {p}" for p in problems))
        return 1
    print("PASS: all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
