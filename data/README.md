# PEMS08 dataset

The raw dataset is excluded from the GitHub-ready package. Obtain it locally as `data/PEMS08.npz` from the [ASTGNN source repository](https://github.com/guoshnBJTU/ASTGNN).

[Direct PEMS08 download](https://raw.githubusercontent.com/guoshnBJTU/ASTGNN/main/data/PEMS08/PEMS08.npz)

From the project root:

```bash
curl -L --fail --output data/PEMS08.npz \
  https://raw.githubusercontent.com/guoshnBJTU/ASTGNN/main/data/PEMS08/PEMS08.npz
sha256sum data/PEMS08.npz
python scripts/reproduce_data.py
```

The URL returned the exact audited bytes when checked on October 19. Expected SHA-256:

```text
e1d03ce74e9fb79149e6e7c37c680214822c4a285baa2f42278cacabcd25c075
```

The NPZ contains key `data` with shape `(17856,170,3)`. Channel 0 is flow, channel 1 occupancy and channel 2 speed. Five-minute observations cover approximately 62 days. Caltrans [PeMS](https://dot.ca.gov/programs/traffic-operations/mpr/pems-source) supplies the measurement-source context. This is California freeway data, not a Bengaluru or verified-intersection dataset.

The isolated wrapper recomputes the audit and baselines in `artifacts/reproduced_data/` rather than overwriting frozen evidence. Expected properties are 0 NaNs, 0 infinities and 10,560 exact-zero flow entries. Complete-case filtering gives 2,098,136 train, 448,263 validation and 448,533 test windows. Zero-as-missing is an assumption, not proof that every zero is invalid.

## Licensing and redistribution

Public availability does not establish redistribution or commercial-use permission. Those rights were not verified for this delivery. Do not bundle the NPZ or grant a licence for third-party data merely because it has a checksum or download link. Retrieve it upstream and inspect the applicable terms before redistribution or commercial use.
