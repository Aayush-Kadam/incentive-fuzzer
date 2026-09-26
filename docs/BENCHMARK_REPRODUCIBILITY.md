# Benchmark Reproducibility

From the repository root:

```bash
python scripts/run_m7.py
python -m pytest
```

The runner rebuilds IF-Bench v0.1 deterministically, executes five methods with seed `20260926` and budget 100, runs supported M3 checks, and writes `experiments/m7`. The run manifest records case hashes, frozen Git commit, Python version, budget, and seed. Results intentionally record commit `03d2260`, the configuration frozen before holdout execution.

No cache is used in v0.1. A future cache key must bind case hash, method configuration, evaluator version, solver version, and Git commit.
