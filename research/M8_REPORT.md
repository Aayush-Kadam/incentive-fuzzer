# M8 Report

# Objective

Package the frozen M0–M7.5 system as a coherent, reproducible research preview without changing headline science.

# Recovery of interrupted M8 work

Recovery began at clean committed HEAD `fcaca60e8444fdea866504ff8388892be3cc5923` on `master`, with uncommitted M8 modifications and new files. The work included the five-command CLI, compact convenience API, regression tests, README, demos, reproduction driver, release metadata, science-figure updates, and a Markdown-to-PDF manuscript workflow. All valid partial work was preserved. The initial test collection failure was an uninstalled-package environment issue; editable installation restored collection and all 235 tests passed.

# Frozen scientific state

M7 and M7.5 results remain unchanged. IF-Bench contains 30 cases. Combined search detects 19 cases; boundary-only also detects 19 with fewer candidate evaluations. Historical encoded-component rediscovery remains 5/6, including the preserved Arizona miss. Positive holdouts remain 4/4, negative holdout findings 0/2, and negative controls 10/10 clean.

# Final architecture

IncentiveSpec feeds the M1 exact reference evaluator. M2 search, M3 SMT verification, M4 population robustness, M5 finite games, and M6 repair/regression consume those semantics. M7 IF-Bench and the M7.5 formal baseline provide frozen evaluation evidence. M8 adds integration, documentation, reproduction, and review packaging only.

# Public CLI

The CLI exposes `validate`, `evaluate`, `search`, `verify`, and `benchmark`. Structured output retains statuses such as `FORMALLY_SATISFIED_WITHIN_DOMAIN`; unsupported, timeout, unknown, and backend-disagreement results are not relabeled as safe.

# Public Python API

The convenience surface is deliberately small: `validate_spec`, `search_spec`, `verify_spec`, and `run_benchmark`, alongside existing exact evaluation primitives. Advanced population, game, and repair APIs remain explicit expert modules.

# Demonstrations

Tested scripts cover the scholarship pipeline, a synthetic strategic-complementarity game and repair, and a partial external encoded component with provenance and limitations.

# Reproducibility

`scripts/reproduce.py` supplies quick, research, and full modes. The manifest records environment versions, seeds, frozen benchmark checks, artifact hashes, test count, commit, mode, and runtime without embedding machine-specific paths.

# Clean-install results

The release audit uses a fresh virtual environment, installs the built wheel with test dependencies, runs tests and CLI/API smoke checks, and records the outcome in the final release evidence.

# Manuscript / technical report

The canonical source is `paper/INCENTIVE_FUZZER_RESEARCH_PREVIEW.md`. The generated review PDF is paginated, includes the architecture and baseline figure, and is visually inspected after rendering.

# IF-Bench presentation

Random, grid, boundary-only, bounded exhaustive, and combined detect 19, 19, 19, 18, and 19 cases using 1,204, 1,061, 369, 1,813, and 1,261 candidate evaluations. The boundary-only result is prominent rather than buried.

# M7.5 SMT baseline presentation

SMT-only supports 26/30 cases: 15 `FORMALLY_VIOLATED`, 11 `FORMALLY_SATISFIED_WITHIN_DOMAIN`, four unsupported, and no timeout, unknown, or backend disagreement. It detects 15/16 supported positives, has 0/10 negative-control false positives, agrees with ground truth on 25/26 supported cases and combined search on 26/26, and replays 15/15 violating witnesses.

# External-review package

The package contains instructions, summaries, threat-model, encoding, and claim review forms, individual cases, and a sealed-holdout template. It does not imply review has occurred.

# Security/privacy audit

No secrets or credentials are required. Current public documentation is portable. Frozen historical evidence is retained and distinguished from current public-facing material.

# Claim audit

`research/M8_CLAIM_AUDIT.md` maps public numbers and qualitative claims to artifacts, commits, limitations, and allowed wording.

# Hostile review response

`research/M8_HOSTILE_REVIEW.md` concludes that the infrastructure exceeds the breadth of current empirical evidence and that boundary-only performance prevents a search-superiority claim.

# Release audit

`research/M8_RELEASE_AUDIT.md` covers science, engineering, manuscript, documentation, security, benchmark integrity, and reproduction.

# Remaining scientific limitations

The benchmark is small, US-heavy, scalar, and threshold-heavy. Actions and valuations are project-authored. Formal coverage is bounded. Population and game evidence is mainly synthetic. External reduction showed a ratio of 1.0. Independent economist/domain validation has not occurred.

# Remaining engineering limitations

Cross-platform independent reproduction has not yet been demonstrated, and the public interface intentionally omits convenience commands for expert population, game, and repair workflows.

# External dependencies

Independent economist/domain, rule-fidelity, action-space, valuation, encoding/code review, and an externally contributed sealed mini-holdout remain outstanding.

# M8 verdict

PASS WITH LIMITATIONS — subject to the final recorded build, reproduction, and clean-install checks.

# Final project status

RESEARCH PREVIEW READY WITH EXTERNAL-VALIDATION LIMITATIONS.
