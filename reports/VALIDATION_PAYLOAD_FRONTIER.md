# Validation Payload Frontier (Posthoc Descriptive Supplement)

> **Validation, not test.** This supplement asks when each frozen FedAvg run first reached a seed-matched validation-MAE target, using the actual recorded cumulative payload. It does not invent test-by-round predictions.

## Scope and interpretation

For seed *s*, the target at tolerance δ is `target_s,δ = (1 + δ) × best centralised validation MAE_s`, with δ ∈ {1%, 2%, 5%, 10%}. The centralised reference is the seed-matched `best_checkpoint.val_mae` in the three primary centralised JSONs. A hit is the **first recorded round** whose validation MAE is at or below that target; payload is copied from that same row's `cumulative_bytes` field. A missing hit is reported as `NOT_REACHED_CENSORED`, never as zero.

The frontier is a posthoc descriptive analysis of existing checkpoints—not a new preregistered hypothesis, not an operational early-stop rule, and not a claim about completed scheduled cost. The 30-round main schedule completed at **615600 bytes** and the 100-round diagnostic schedule completed at **2052000 bytes**. These runs use one fixed architecture across three seeds, without privacy or bandwidth guarantees.

## Seed-matched centralised validation references

| Seed | Best centralised validation MAE | 1% target | 2% target | 5% target | 10% target |
|---:|---:|---:|---:|---:|---:|
| 0 | 13.56922721862793 | 13.70491949081421 | 13.840611763000489 | 14.247688579559327 | 14.926149940490724 |
| 1 | 13.54646110534668 | 13.681925716400146 | 13.817390327453614 | 14.223784160614015 | 14.901107215881348 |
| 2 | 13.57068920135498 | 13.70639609336853 | 13.84210298538208 | 14.24922366142273 | 14.927758121490479 |

## Findings

- The CSV contains 48 run-target rows (39 reached; 9 censored). All four schedules/partitions have three seed traces.
- Every 5% and 10% target was reached in both 30-round main and 100-round diagnostic runs (12/12 rows at each tolerance: four schedule/partition combinations × three seeds).
- Main30 IID reached the stringent 1% target at seed-0/1/2 rounds 22, 13, and 22 (payloads 451440, 266760, and 451440 bytes, respectively). Main30 non-IID did not reach any 1% or 2% target within 30 rounds (6 censored rows).
- Diagnostic100 non-IID reached the 2% target for all seeds, but only late: rounds 57, 50, and 46 (payloads 1169640, 1026000, and 943920 bytes). Its 1% target remained unreached for all three seeds.
- Main30 IID reached 2% at rounds 8, 5, and 9; diagnostic100 IID has the same first-hit rounds because those early histories are identical. First-hit payloads are therefore reported from the recorded cumulative byte field, not inferred from a nominal rate.

## Frontier table

The machine-readable full-precision table is [`tables/validation_payload_frontier.csv`](tables/validation_payload_frontier.csv). Blank first-hit fields occur only with explicit `NOT_REACHED_CENSORED` status and the censoring reason shown in the CSV.

| Schedule | Partition | δ | Reached seeds | First-hit rounds (seed 0 / 1 / 2) | First-hit payloads (bytes; seed 0 / 1 / 2) |
|---|---|---:|---:|---|---|
| main30 | iid | 1% | 3/3 | 22 / 13 / 22 | 451,440 B / 266,760 B / 451,440 B |
| main30 | iid | 2% | 3/3 | 8 / 5 / 9 | 164,160 B / 102,600 B / 184,680 B |
| main30 | iid | 5% | 3/3 | 3 / 2 / 3 | 61,560 B / 41,040 B / 61,560 B |
| main30 | iid | 10% | 3/3 | 2 / 2 / 2 | 41,040 B / 41,040 B / 41,040 B |
| main30 | non_iid | 1% | 0/3 | NOT_REACHED / NOT_REACHED / NOT_REACHED | NOT_REACHED / NOT_REACHED / NOT_REACHED |
| main30 | non_iid | 2% | 0/3 | NOT_REACHED / NOT_REACHED / NOT_REACHED | NOT_REACHED / NOT_REACHED / NOT_REACHED |
| main30 | non_iid | 5% | 3/3 | 9 / 6 / 4 | 184,680 B / 123,120 B / 82,080 B |
| main30 | non_iid | 10% | 3/3 | 4 / 2 / 3 | 82,080 B / 41,040 B / 61,560 B |
| diagnostic100 | iid | 1% | 3/3 | 22 / 13 / 22 | 451,440 B / 266,760 B / 451,440 B |
| diagnostic100 | iid | 2% | 3/3 | 8 / 5 / 9 | 164,160 B / 102,600 B / 184,680 B |
| diagnostic100 | iid | 5% | 3/3 | 3 / 2 / 3 | 61,560 B / 41,040 B / 61,560 B |
| diagnostic100 | iid | 10% | 3/3 | 2 / 2 / 2 | 41,040 B / 41,040 B / 41,040 B |
| diagnostic100 | non_iid | 1% | 0/3 | NOT_REACHED / NOT_REACHED / NOT_REACHED | NOT_REACHED / NOT_REACHED / NOT_REACHED |
| diagnostic100 | non_iid | 2% | 3/3 | 57 / 50 / 46 | 1,169,640 B / 1,026,000 B / 943,920 B |
| diagnostic100 | non_iid | 5% | 3/3 | 9 / 6 / 4 | 184,680 B / 123,120 B / 82,080 B |
| diagnostic100 | non_iid | 10% | 3/3 | 4 / 2 / 3 | 82,080 B / 41,040 B / 61,560 B |

## Figure and reproducibility

[`figures/validation_payload_frontier.png`](../figures/validation_payload_frontier.png) plots each run's running-minimum **validation** MAE against that run's cumulative payload, with one trace per seed and the 30-round budget marker. Lines are not a common pooled target: targets are seed-matched and vary by seed as listed above and in the CSV. The plot is descriptive; it should not be read as a deployment stopping policy or as a test-performance curve.

Regenerate only these supplement artifacts from the project root with:

```bash
python3 src/communication_frontier.py --root .
```

Source inputs are the frozen `results/full_results/fedavg_{iid,non_iid}_seed{0,1,2}.json`, `results/diagnostic_100rounds/fedavg_{iid,non_iid}_seed{0,1,2}.json`, and `results/full_results/centralised_seed{0,1,2}.json` files. No training or new neural-network evaluation is performed.
