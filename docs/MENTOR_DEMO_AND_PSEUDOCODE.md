# Prototype demonstration and implementation-faithful pseudocode

## What to demonstrate to the mentor

The required prototype is the executable NumPy simulator. It is not a dashboard or a city deployment. A replay explains saved evidence; a fresh smoke run demonstrates actual learning execution. Keep that distinction explicit.

From the project root, run:

```bash
python -m pytest -q tests
python src/check_results.py --dir results/full_results --config configs/full.json
python src/demo.py --condition fedavg_non_iid --seed 0 --rounds-to-show 3
```

The final command prints **saved-results replay**, dataset/window counts, a validation-selected checkpoint, client disparities and the first three history rows. It does not retrain, choose the best seed, measure a live network or recompute predictions from the JSON.

For a fresh prototype demonstration, first obtain the exact NPZ as described in `data/README.md`, then run:

```bash
python src/demo.py --train-smoke
python src/check_results.py --dir artifacts/demo_smoke --config configs/smoke.json
```

This invokes the unchanged scientific runner on the smoke schedule and writes separate files. Show its output as live simulator execution, not final accuracy evidence. Do not use its errors to tune the frozen matrix. If the dataset is unavailable, show the executable code and labelled replay and arrange a proper training demonstration when data is available.

## A five-minute walkthrough

Use the first minute to identify the dataset and exact scope: public California PEMS08, five virtual clients of 34 sensors, no Bengaluru validation and no privacy guarantee. Show the hash and training/validation/test boundaries.

Use the next minute to explain valid windows and the model: 12 lags plus two global cycle features, a 14–32–1 MLP, train-only scaling, zero handling as an assumption, and 513 parameters. Explain that each sensor-time pair is filtered independently; a zero at one sensor does not remove all 170 sensors at that time.

Use the third minute to walk through the FedAvg loop below: the same initial model, all five clients, one local epoch, fresh local Adam state each round, sample-count-weighted averaging and validation selection. Contrast this with centralised/local-only Adam state, which persists across epochs.

Use the fourth minute to show primary results and the common-group client chart. Centralised has the lowest mean MAE; IID FedAvg is 0.73% higher and non-IID is 2.50% higher. H4 is refuted: the quietest group's FedAvg MAE is 10.42% worse than matched local-only. The method does not “win” just because it is federated.

Use the final minute to explain costs and the separate diagnostic. Thirty rounds cost 615,600 model-payload bytes; 100 rounds cost 2,052,000 bytes. The latter modestly reduces MAE but does not replace the primary budget. Ask for feedback and record only actual mentoring participation and changes.

## Short natural explanation

“We built a simulator to test a trade-off, not to assume FedAvg is better. We use California traffic data because we need a public dataset that everyone can reproduce. We divide its 170 sensors into five virtual clients and compare random sensor groups with quiet-to-busy groups. The model is small: 12 past flows and two cycle features go into a 513-parameter MLP. We select checkpoints using validation data, then report test errors across three seeds. Centralised training gives the best average error. IID FedAvg stays close, but non-IID training makes the quietest group worse than its local-only model. We also count weight bytes explicitly. More rounds help a little, but cost over three times as much communication. So our contribution is a transparent, reproducible comparison with honest client-level limitations.”

## Data preparation pseudocode

```text
flow = load_PEMS08_channel_0()                    # [time, sensor]
train, validation, test = chronological_70_15_15_bounds()
mean, std = statistics(flow[train][flow[train] != 0])

for split in [train, validation, test]:
    split_windows = []
    for global_t from split.start + 12 to split.end - 1:
        for sensor in 0..169:
            lag = flow[global_t-12:global_t, sensor]
            target = flow[global_t, sensor]
            if any(lag == 0) or target == 0:
                continue                           # this sensor-time pair only
            phase = 2*pi*(global_t mod 288)/288
            x = concatenate((lag-mean)/std, sin(phase), cos(phase))
            y_scaled = (target-mean)/std
            save(x, y_scaled, sensor, global_t)

IID_groups(seed) = seeded_permutation(sensors).reshape(5, 34)
non_IID_groups = sensors_sorted_by_valid_training_mean.reshape(5, 34)
```

The scaler and non-IID ranking use training entries only. All lags stay inside their split. Cycle phase uses the **global** target index, not a reset index at each split. The file's missing timestamps do not permit verified calendar or day-of-week claims.

## Model and training pseudocode

```text
for seed in [0, 1, 2]:
    initial = initialise_14_32_1_MLP(seed)

    # Centralised: one Adam object persists across all 30 epochs.
    model = copy(initial)
    optimiser = Adam(model, learning_rate=0.001)
    for epoch in 1..30:
        train_one_epoch(model, all_training_windows, optimiser, batch=1024)
        evaluate_validation_and_store_best(model, epoch)
    test_once_at_best_validation_checkpoint()

    # Local-only, repeated for BOTH IID and non-IID sensor memberships.
    for partition in [IID_groups(seed), non_IID_groups]:
        for client in partition:
            model = copy(initial)
            optimiser = Adam(model, learning_rate=0.001)
            for epoch in 1..30:
                train_one_epoch(model, client.training_windows, optimiser)
                evaluate_client_validation_and_store_best(model, epoch)
            retain_this_client's_validation_selected_checkpoint()
        score_each_test_window_using_its_own_client_model()

    # FedAvg, also repeated for BOTH memberships.
    for partition in [IID_groups(seed), non_IID_groups]:
        global_model = copy(initial)
        for round in 1..30:
            client_updates = []
            for client in partition:                 # all 5 participate
                local = copy(global_model)
                optimiser = Adam(local, learning_rate=0.001)  # reset EACH round
                train_one_epoch(local, client.training_windows, optimiser)
                n_k = count(client.training_windows)
                client_updates.append((local.parameters, n_k))
            global_model = sum(n_k * parameters_k) / sum(n_k)
            model_payload = sum(tensor.element_count * tensor.element_bytes)
            round_bytes = 5 * 2 * model_payload       # 20,520 bytes
            evaluate_validation_and_store_best(global_model, round)
        test_once_at_best_validation_checkpoint()

    # For every final prediction:
    prediction_flow = prediction_scaled * std + mean
    actual_flow = target_scaled * std + mean
    MAE = mean(abs(prediction_flow-actual_flow))
    RMSE = sqrt(mean((prediction_flow-actual_flow)^2))
    relative_absolute_error = sum(abs(error)) / sum(actual_flow)
    score_overall_and_identical_canonical_sensor_groups()
    save_metadata_histories_checkpoint_metrics_and_bytes()
```

Training minimises MSE in scaled-flow units. Scoring uses original flow units. The local optimiser state is never communicated. Neither virtual clients nor shared coordinator statistics prove privacy. The 100-round diagnostic repeats the same FedAvg loop for 100 rounds; it remains a separately labelled schedule.

## Mentor completion evidence

The PS-003 brief asks for a prototype demonstration with pseudocode to the mentor. This document prepares that demonstration; it does not certify that it occurred. Record the actual date, participants, feedback and changes in `docs/MENTORING_AND_WORK_LOG.md` after the session.
