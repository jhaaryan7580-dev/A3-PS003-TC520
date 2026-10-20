#!/usr/bin/env python3
"""Posthoc validation-payload frontier for the frozen FedAvg artifacts.

This module deliberately uses validation MAE only.  It never reads or predicts
per-round test MAE and never changes training/checker artifacts.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any, Iterable

DELTAS = (0.01, 0.02, 0.05, 0.10)
SEEDS = (0, 1, 2)
CONDITIONS = {
    "main30_iid": ("main30", "iid", "results/full_results"),
    "main30_non_iid": ("main30", "non_iid", "results/full_results"),
    "diagnostic100_iid": ("diagnostic100", "iid", "results/diagnostic_100rounds"),
    "diagnostic100_non_iid": ("diagnostic100", "non_iid", "results/diagnostic_100rounds"),
}
CSV_FIELDS = [
    "schedule",
    "partition",
    "condition",
    "seed",
    "delta",
    "delta_percent",
    "central_best_val_mae",
    "target_val_mae",
    "first_hit_round",
    "first_hit_cumulative_bytes",
    "first_hit_val_mae",
    "status",
    "censoring_reason",
    "scheduled_rounds",
    "scheduled_total_bytes",
    "source_json",
    "central_source_json",
]


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def central_best_val_mae(root: Path, seed: int) -> tuple[float, Path]:
    path = root / "results" / "full_results" / f"centralised_seed{seed}.json"
    payload = read_json(path)
    return float(payload["best_checkpoint"]["val_mae"]), path


def first_hit(history: Iterable[dict[str, Any]], target: float) -> dict[str, Any] | None:
    """Return the first recorded validation hit, retaining the exact byte field."""
    for point in history:
        if float(point["val_mae"]) <= target:
            if "cumulative_bytes" not in point:
                raise KeyError("frontier requires history.cumulative_bytes")
            return point
    return None


def running_min(history: Iterable[dict[str, Any]]) -> list[tuple[int, int, float]]:
    """Return (cumulative_bytes, round, running-min validation MAE) points."""
    out: list[tuple[int, int, float]] = []
    best = math.inf
    for point in history:
        value = float(point["val_mae"])
        best = min(best, value)
        out.append((int(point["cumulative_bytes"]), int(point["round"]), best))
    return out


def _float_text(value: float) -> str:
    # repr is round-trippable and preserves the precision represented in JSON.
    return repr(float(value))


def build_rows(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for condition, (schedule, partition, directory) in CONDITIONS.items():
        for seed in SEEDS:
            central_mae, central_path = central_best_val_mae(root, seed)
            result_path = root / directory / f"fedavg_{partition}_seed{seed}.json"
            payload = read_json(result_path)
            history = payload["history"]
            communication = payload.get("communication", {})
            scheduled_rounds = len(history)
            scheduled_bytes = int(communication.get("total_bytes", history[-1]["cumulative_bytes"]))
            for delta in DELTAS:
                target = central_mae * (1.0 + delta)
                hit = first_hit(history, target)
                if hit is None:
                    hit_round: int | str = ""
                    hit_bytes: int | str = ""
                    hit_mae: float | str = ""
                    status = "NOT_REACHED_CENSORED"
                    reason = "target_not_reached_within_scheduled_history"
                else:
                    hit_round = int(hit["round"])
                    hit_bytes = int(hit["cumulative_bytes"])
                    hit_mae = float(hit["val_mae"])
                    status = "REACHED"
                    reason = ""
                rows.append(
                    {
                        "schedule": schedule,
                        "partition": partition,
                        "condition": condition,
                        "seed": seed,
                        "delta": _float_text(delta),
                        "delta_percent": _float_text(delta * 100.0),
                        "central_best_val_mae": _float_text(central_mae),
                        "target_val_mae": _float_text(target),
                        "first_hit_round": hit_round,
                        "first_hit_cumulative_bytes": hit_bytes,
                        "first_hit_val_mae": "" if hit_mae == "" else _float_text(hit_mae),
                        "status": status,
                        "censoring_reason": reason,
                        "scheduled_rounds": scheduled_rounds,
                        "scheduled_total_bytes": scheduled_bytes,
                        "source_json": str(result_path.relative_to(root)),
                        "central_source_json": str(central_path.relative_to(root)),
                    }
                )
    return rows


def write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _fmt_bytes(value: int | str) -> str:
    return "NOT_REACHED" if value == "" else f"{int(value):,} B"


def write_report(root: Path, rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    reached = [row for row in rows if row["status"] == "REACHED"]
    targets = sorted({float(row["delta_percent"]) for row in rows})
    central = {seed: central_best_val_mae(root, seed)[0] for seed in SEEDS}
    lines = [
        "# Validation Payload Frontier (Posthoc Descriptive Supplement)",
        "",
        "> **Validation, not test.** This supplement asks when each frozen FedAvg run first reached a seed-matched validation-MAE target, using the actual recorded cumulative payload. It does not invent test-by-round predictions.",
        "",
        "## Scope and interpretation",
        "",
        "For seed *s*, the target at tolerance δ is `target_s,δ = (1 + δ) × best centralised validation MAE_s`, with δ ∈ {1%, 2%, 5%, 10%}. The centralised reference is the seed-matched `best_checkpoint.val_mae` in the three primary centralised JSONs. A hit is the **first recorded round** whose validation MAE is at or below that target; payload is copied from that same row's `cumulative_bytes` field. A missing hit is reported as `NOT_REACHED_CENSORED`, never as zero.",
        "",
        "The frontier is a posthoc descriptive analysis of existing checkpoints—not a new preregistered hypothesis, not an operational early-stop rule, and not a claim about completed scheduled cost. The 30-round main schedule completed at **615600 bytes** and the 100-round diagnostic schedule completed at **2052000 bytes**. These runs use one fixed architecture across three seeds, without privacy or bandwidth guarantees.",
        "",
        "## Seed-matched centralised validation references",
        "",
        "| Seed | Best centralised validation MAE | 1% target | 2% target | 5% target | 10% target |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for seed in SEEDS:
        value = central[seed]
        targets_for_seed = [(1.0 + d) * value for d in DELTAS]
        lines.append("| {} | {} | {} | {} | {} | {} |".format(seed, *[_float_text(x) for x in [value, *targets_for_seed]]))

    lines += [
        "",
        "## Findings",
        "",
        f"- The CSV contains {len(rows)} run-target rows ({len(reached)} reached; {len(rows) - len(reached)} censored). All four schedules/partitions have three seed traces.",
        "- Every 5% and 10% target was reached in both 30-round main and 100-round diagnostic runs (12/12 rows at each tolerance: four schedule/partition combinations × three seeds).",
        "- Main30 IID reached the stringent 1% target at seed-0/1/2 rounds 22, 13, and 22 (payloads 451440, 266760, and 451440 bytes, respectively). Main30 non-IID did not reach any 1% or 2% target within 30 rounds (6 censored rows).",
        "- Diagnostic100 non-IID reached the 2% target for all seeds, but only late: rounds 57, 50, and 46 (payloads 1169640, 1026000, and 943920 bytes). Its 1% target remained unreached for all three seeds.",
        "- Main30 IID reached 2% at rounds 8, 5, and 9; diagnostic100 IID has the same first-hit rounds because those early histories are identical. First-hit payloads are therefore reported from the recorded cumulative byte field, not inferred from a nominal rate.",
        "",
        "## Frontier table",
        "",
        "The machine-readable full-precision table is [`tables/validation_payload_frontier.csv`](tables/validation_payload_frontier.csv). Blank first-hit fields occur only with explicit `NOT_REACHED_CENSORED` status and the censoring reason shown in the CSV.",
        "",
        "| Schedule | Partition | δ | Reached seeds | First-hit rounds (seed 0 / 1 / 2) | First-hit payloads (bytes; seed 0 / 1 / 2) |",
        "|---|---|---:|---:|---|---|",
    ]
    for schedule in ("main30", "diagnostic100"):
        for partition in ("iid", "non_iid"):
            for delta_pct in targets:
                subset = [r for r in rows if r["schedule"] == schedule and r["partition"] == partition and float(r["delta_percent"]) == delta_pct]
                hit_count = sum(r["status"] == "REACHED" for r in subset)
                rounds = " / ".join(str(r["first_hit_round"]) if r["first_hit_round"] != "" else "NOT_REACHED" for r in subset)
                bytes_ = " / ".join(_fmt_bytes(r["first_hit_cumulative_bytes"]) for r in subset)
                lines.append(f"| {schedule} | {partition} | {delta_pct:g}% | {hit_count}/3 | {rounds} | {bytes_} |")

    lines += [
        "",
        "## Figure and reproducibility",
        "",
        "[`figures/validation_payload_frontier.png`](../figures/validation_payload_frontier.png) plots each run's running-minimum **validation** MAE against that run's cumulative payload, with one trace per seed and the 30-round budget marker. Lines are not a common pooled target: targets are seed-matched and vary by seed as listed above and in the CSV. The plot is descriptive; it should not be read as a deployment stopping policy or as a test-performance curve.",
        "",
        "Regenerate only these supplement artifacts from the project root with:",
        "",
        "```bash",
        "python3 src/communication_frontier.py --root .",
        "```",
        "",
        "Source inputs are the frozen `results/full_results/fedavg_{iid,non_iid}_seed{0,1,2}.json`, `results/diagnostic_100rounds/fedavg_{iid,non_iid}_seed{0,1,2}.json`, and `results/full_results/centralised_seed{0,1,2}.json` files. No training or new neural-network evaluation is performed.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def plot_frontier(root: Path, path: Path) -> None:
    import matplotlib.pyplot as plt

    path.parent.mkdir(parents=True, exist_ok=True)
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, axes = plt.subplots(2, 2, figsize=(14, 9), sharex=False, sharey=True)
    colors = {0: "#0072B2", 1: "#D55E00", 2: "#009E73"}
    for ax, condition in zip(axes.flat, CONDITIONS):
        schedule, partition, directory = CONDITIONS[condition]
        for seed in SEEDS:
            result_path = root / directory / f"fedavg_{partition}_seed{seed}.json"
            payload = read_json(result_path)
            points = running_min(payload["history"])
            x = [p[0] / 1_000_000.0 for p in points]
            y = [p[2] for p in points]
            ax.plot(x, y, color=colors[seed], linewidth=1.8, label=f"seed {seed}")
        main_budget = 0.6156
        ax.axvline(main_budget, color="#333333", linestyle="--", linewidth=1.2)
        ax.text(main_budget, 0.985, "30-round cost", transform=ax.get_xaxis_transform(), ha="right", va="top", fontsize=8, rotation=90, color="#333333")
        if schedule == "diagnostic100":
            diagnostic_budget = 2.0520
            ax.axvline(diagnostic_budget, color="#666666", linestyle=":", linewidth=1.2)
            ax.text(diagnostic_budget, 0.985, "100-round cost", transform=ax.get_xaxis_transform(), ha="right", va="top", fontsize=8, rotation=90, color="#666666")
        ax.set_title(f"{schedule} · {partition}", loc="left", fontweight="bold")
        ax.set_xlabel("Per-run cumulative payload (MB)")
        ax.set_ylabel("Running-min validation MAE")
        ax.legend(frameon=True, fontsize=8, loc="upper right")
        ax.text(0.02, 0.04, "Targets are seed-matched\n(see table; no common target line)", transform=ax.transAxes, fontsize=8, color="#444444", bbox={"facecolor": "white", "alpha": 0.8, "edgecolor": "none"})
    fig.suptitle("Communication frontier: validation MAE versus cumulative payload", fontsize=16, fontweight="bold", y=0.98)
    fig.text(0.5, 0.01, "Posthoc descriptive supplement · validation only, not test · traces are running minima of recorded checkpoints", ha="center", fontsize=9, color="#444444")
    fig.tight_layout(rect=(0, 0.04, 1, 0.95))
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def generate(root: Path, csv_path: Path | None = None, report_path: Path | None = None, figure_path: Path | None = None) -> list[dict[str, Any]]:
    rows = build_rows(root)
    write_csv(rows, csv_path or root / "reports/tables/validation_payload_frontier.csv")
    write_report(root, rows, report_path or root / "reports/VALIDATION_PAYLOAD_FRONTIER.md")
    plot_frontier(root, figure_path or root / "figures/validation_payload_frontier.png")
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--csv", type=Path, default=None)
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--figure", type=Path, default=None)
    args = parser.parse_args()
    rows = generate(args.root.resolve(), args.csv, args.report, args.figure)
    print(f"wrote {len(rows)} run-target rows")


if __name__ == "__main__":
    main()
