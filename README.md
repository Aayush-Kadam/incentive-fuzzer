# Incentive Fuzzer

M7 adds **IF-Bench v0.1**, a blind, versioned suite of 30 bounded mechanisms with 10 externally sourced rule components, six holdouts, equal-budget baselines, exact replay, reduction, and M3 confirmation. The frozen result is **PASS WITH LIMITATIONS**: 5/6 historical components and all four positive holdouts were rediscovered, but boundary-only matched the combined search and all external cases remain partial project-authored models.

Run M7 with `python scripts/run_m7.py`; see `research/M7_REPORT.md` for claims and limitations.

**Adversarial Testing and Verification of Economic Institutions**

Author / Project Lead: Aayush Kadam

Incentive Fuzzer is a research program for counterexample-driven testing of economic rules. The project asks whether a specified agent can take a feasible, informed action that improves private utility while violating an explicit designer property. It aims to return a reproducible witness, not an unsupported label.

## Current state

M6 research prototype: IncentiveSpec v0.1, exact-decimal evaluation, bounded search, exact-rational individual verification, heterogeneous robustness analysis, exact finite pure-game analysis, and bounded counterexample-driven repair with multi-layer regression. Population, equilibrium, and repair results are synthetic sensitivity analyses, not predictions or policy recommendations.

## Run the core suite

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -e ".[test]"
$env:PYTHONPATH='src'
.venv\Scripts\python -m pytest
```

Minimal search:

```powershell
.venv\Scripts\incentive-fuzzer search examples\scholarship_cliff.yaml --method boundary --output finding-run.json
```

## Defensible claim under investigation

The candidate contribution is an open, benchmarked workflow that combines explicit economic threat models, executable rule semantics, adversarial search, property checking, domain-aware counterexample reduction, robustness analysis, and repair regression for heterogeneous economic institutions. Each ingredient has substantial prior art; novelty must be demonstrated empirically at the workflow and benchmark level.

## M0 artifacts

- [M0 report](research/M0_REPORT.md)
- [novelty matrix](research/NOVELTY_MATRIX.md)
- [precommitment](research/M0_PRECOMMITMENT.md)
- [hostile review](research/M0_HOSTILE_REVIEW.md)
- [threat model](docs/THREAT_MODEL.md)
- [vulnerability taxonomy](docs/IF_CWE.md)
- [research questions](docs/RESEARCH_QUESTIONS.md)
- [architecture v0](docs/ARCHITECTURE_V0.md)
- [source register](bibliography/SOURCES.md)

## What is not claimed

This repository does not yet establish novelty, completeness, empirical realism, equilibrium coverage, or successful repair. “No violation found” will always be scoped to a stated domain and assumptions.
