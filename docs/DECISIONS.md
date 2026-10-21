# Decisions (one line each; update when a decision changes)

Frozen 2026-10-18 before any learned-model result exists.

1. Dataset: PEMS08, channel 0 (flow) is the target. California stand-in, not Bengaluru.
2. Split: one chronological 70/15/15 split for all sensors: train 0-12,498, val 12,499-15,176, test 15,177-17,855.
3. Windows: 12 previous flows predict the next 5-minute flow; built inside each split, never crossing a boundary.
4. Zero policy: exact zero flow is treated as missing; any window with a zero in its 12 inputs or target is dropped (complete-case). Forward-fill is a one-seed sensitivity check only.
5. Scaling: mean and std over valid (non-zero) training entries only.
6. Features: 12 scaled lags plus sin/cos of the global target index mod 288 (never a split-local index). No day-of-week.
7. Clients: 5 clients x 34 sensors. IID-style = seeded random assignment. Non-IID = sensors sorted by mean flow over valid training steps, cut into 5 quiet-to-busy bands.
8. Model: 14 -> 32 ReLU -> 1, 513 parameters, float32 payload 2,052 bytes (counted from tensor sizes).
9. Training: MSE on scaled flow, Adam lr 1e-3, batch 1024. Adam state is local and reset each FedAvg round (never communicated).
10. Budgets: centralised 30 epochs, local-only 30 epochs, FedAvg 30 rounds x 1 local epoch. These are different training arrangements, not equal optimiser-step budgets. A 100-round diagnostic checks whether 30 rounds is enough.
11. Checkpoints: chosen by validation MAE for every condition; the test set is evaluated once on the chosen checkpoint.
12. Evaluation: every method is scored on the same complete-case windows of each split.
13. Baselines: persistence; per-(sensor, slot) daily-cycle mean from training data (never pooled across sensors).
14. Fairness: headline gap is on relative absolute error (sum |error| / sum actual); absolute MAE gap is supplementary. The IID gap is the noise floor.
15. Communication: bytes per round = 2,052 x 5 clients x 2 directions = 20,520. Training-flow upload reference = 12,499 x 170 x 4 = 8,499,320 bytes (a labelled reference, not a production network model). Break-even is about 414 rounds.
16. Seeds 0, 1, 2. Non-IID membership is deterministic, so seeds change initialisation and batch order there.
17. Out of scope until the must-have matrix and clean-clone test pass: GRU, dashboard, second dataset, new partitions, privacy mechanism, longer horizon.

18. Heterogeneity statistic (primary): mean pairwise 1-D Wasserstein-1 distance between clients' distributions of per-sensor valid training mean flow (34 values per client). The pooled-value W1 is stored as a secondary, non-comparable field.
19. Local-only models are run on BOTH partitions (local_iid, local_non_iid), so each FedAvg condition has a matched local-only reference. Learned conditions: centralised, local_iid, local_non_iid, fedavg_iid, fedavg_non_iid = 5 x 3 seeds = 15 result files. Every result also stores per-client metrics under both partitions.
20. Byte references: training_flow_upload_reference_bytes = 12,499 x 170 x 4 = 8,499,320 (primary); full_stream_flow_reference_bytes = 17,856 x 170 x 4 = 12,142,080 (not used for the main comparison).
21. Configs are JSON (configs/full.json, configs/smoke.json) to avoid a YAML dependency.

## Hypotheses (write and COMMIT before the first learned-model run on real data)

Proposed by the planning review; the team confirms or edits each line, then commits this file with the message "hypotheses before first run".

H1: IID-style FedAvg will have similar overall test MAE to centralised training, while non-IID FedAvg will show a larger client-level relative-error gap.
H2: the non-IID quiet-to-busy partition will produce more seed variability and slower convergence than IID-style FedAvg.
H3: the compact MLP will beat persistence on the held-out test set under the complete-case protocol.
H4 (Aryan): For the quietest non-IID client, FedAvg will perform better than local-only training because the shared model can benefit from information learned from the other clients, although the improvement may be smaller than for busier clients.
