# Public API

The research-preview convenience surface is:

```python
from incentive_fuzzer import load_spec, evaluate, search_spec, verify_spec, run_benchmark
```

- `load_spec(path)` parses and validates IncentiveSpec v0.1.
- `evaluate(spec, state, action=None)` executes exact deterministic semantics.
- `search_spec(path, method="combined", max_evaluations=1000)` builds the documented bounded convenience domain and returns a full `SearchResult`.
- `verify_spec(path, action, timeout_ms=5000)` runs the independent formal backend and returns its exact `FormalResult` status.
- `run_benchmark(root, method="combined", max_evaluations=100)` runs a label-blind benchmark method and returns per-case runs.

The convenience domain is intended for demonstrations. Research experiments should construct explicit `SearchDomain` and `FormalDomain` objects so every tested value is visible and frozen.

Advanced APIs remain in `core`, `search`, `verify`, `population`, `game`, `repair`, and `benchmark`. No API status means universal safety.
