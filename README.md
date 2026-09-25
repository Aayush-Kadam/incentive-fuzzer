# Incentive Fuzzer

**Adversarial Testing and Verification of Economic Institutions**

Author / Project Lead: Aayush Kadam

Incentive Fuzzer is a research program for counterexample-driven testing of economic rules. The project asks whether a specified agent can take a feasible, informed action that improves private utility while violating an explicit designer property. It aims to return a reproducible witness, not an unsupported label.

## Current state

M0 research specification only. No functioning fuzzer or verified mechanism is claimed. The M0 verdict is **PASS WITH LIMITATIONS**: proceed to a tightly scoped M1 around declarative, deterministic, single-agent, piecewise-linear rules.

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

