# Benchmark Reproducibility

From the repository root:

```bash
python scripts/run_m7.py
python -m pytest
```

M7.5 B5 and the separate non-threshold stress supplement are reproduced with:

```text
python scripts/run_m75.py
python scripts/build_external_review_cards.py
python scripts/build_m8_science.py
```

B5 loads hidden labels only after SMT and combined results are frozen in memory. Every IF-Bench case receives an explicit supported/unsupported row. The non-threshold supplement lives under `benchmarks/m75_stress/v0.1` and does not change IF-Bench v0.1, its holdout, or its M7 scores.

Contributor-sealed runtime packages can be evaluated without labels using:

```text
python scripts/run_sealed_holdout.py <runtime-directory> <results.json>
```

The runner rebuilds IF-Bench v0.1 deterministically, executes five methods with seed `20260926` and budget 100, runs supported M3 checks, and writes `experiments/m7`. The run manifest records case hashes, frozen Git commit, Python version, budget, and seed. Results intentionally record commit `03d2260`, the configuration frozen before holdout execution.

No cache is used in v0.1. A future cache key must bind case hash, method configuration, evaluator version, solver version, and Git commit.
