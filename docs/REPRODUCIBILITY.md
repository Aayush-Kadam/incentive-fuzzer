# Reproducibility

## Environment

Use Python 3.12. Runtime dependencies are pinned in `requirements.lock`; package metadata pins PyYAML 6.0.3 and z3-solver 4.15.3.0. Test extras pin pytest 8.4.2 and pytest-cov 7.0.0.

## Clean installation

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\python -m pip install -e ".[test]"
.venv\Scripts\python -c "import incentive_fuzzer"
.venv\Scripts\incentive-fuzzer --help
.venv\Scripts\python -m pytest
```

Use `.venv/bin/` instead of `.venv\Scripts\` on macOS/Linux.

## One-command modes

```powershell
python scripts\reproduce.py quick
python scripts\reproduce.py research
python scripts\reproduce.py full
```

- `quick` runs public-surface and benchmark-integrity tests and recomputes logical M7/M7.5 checks.
- `research` runs the complete test suite, recomputes logical benchmark checks, and regenerates frozen tables, figures, and review cards.
- `full` additionally runs the scholarship, strategic-game, and external-component demonstrations.

All modes write `reproducibility/manifest.json`. Runtime seconds are diagnostic; hashes, statuses, counts, versions, and seeds are the reproducibility evidence.

Frozen historical experiment artifacts are retained rather than overwritten during routine reproduction. Logical benchmark results are recomputed in memory. Milestone-specific scripts remain available for forensic regeneration but may contain recorded machine timings and commit identifiers that naturally differ after M8.

## Expected research-preview results

- Complete tests: see the current manifest.
- M7 combined detections: 19; false positives: 0.
- B5: 26 supported, 15 violated, 11 satisfied, four unsupported.
- M7.5 stress labels: 3/3 status agreement.
- Headline table and both figures regenerate byte-stably from the committed inputs except where the reproduction manifest records current runtime/environment fields.

