# Primary 30-round / 30-epoch results

| Condition | Test MAE mean ± sample SD | Test RMSE mean ± sample SD |
| --- | ---: | ---: |
| Centralised | 13.862 ± 0.013 | 21.074 ± 0.008 |
| Local IID | 13.992 ± 0.031 | 21.221 ± 0.048 |
| Local non-IID | 13.898 ± 0.005 | 21.096 ± 0.012 |
| FedAvg IID | 13.964 ± 0.014 | 21.211 ± 0.031 |
| FedAvg non-IID | 14.209 ± 0.066 | 21.373 ± 0.079 |

Three seeds; sample SD uses ddof=1. Full-precision inputs are retained in JSON/CSV.
