# Scripts

Install dependencies with `python -m pip install -r requirements.txt`. Run `run_average_linkage.py` from the repository root:

```bash
python scripts/run_average_linkage.py \
  --curves /path/to/train_curves.csv \
  --output-dir /path/to/output \
  --train-start 2020-01-01 \
  --train-end 2023-12-31 \
  --n-clusters 20
```

The command writes a registered ranked factor set, cluster assignments, method metadata, a correlation-distance matrix and audit receipts. Outputs belong outside the repository or under an ignored output directory.
