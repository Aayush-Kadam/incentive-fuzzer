# M7 Report — IF-Bench v0.1

## Objective

Test whether Incentive Fuzzer can rediscover structural vulnerabilities in independently authored rule components under frozen, blind, equal-budget evaluation.

## Benchmark philosophy

IF-Bench v0.1 prioritizes provenance, label separation, failures, and component-level claims over breadth or perfect recall. All external encodings are explicitly partial.

## Candidate funnel

Twenty-eight external candidates were screened; 18 were excluded before evaluation and 10 included. Exclusions are grouped in `M7_EXCLUSIONS.md`.

## Inclusion/exclusion criteria

Included rules had authoritative sources, a frozen version, deterministic bounded semantics, and an explicit scalar action. Insufficient sources, unfrozen versions, or materially distorted encodings were excluded.

## IF-Bench schema

Each case records ID, title, origin, domain, difficulty, split, version, source pointer, representability, runtime model, threat model, properties, and omissions. Hidden labels are separate JSON files. A hashed manifest binds all package files.

## Benchmark composition

Thirty cases: 12 inherited internal synthetic, 8 additional internal/control cases, 10 external, 6 historical, 10 negative controls, and 6 holdouts. Counts overlap by design.

## External sources and historical versions

Official IRS, Acquisition.gov, oversight/OIG, CMS/Medicaid, SSA, and Federal Reserve sources were accessed 2026-09-26. Historical freezes are ACA 2020, FAR 2017, SNAP rule statement 2024, CMS table 2023-12-01, Pennsylvania 2022, and New York 2024-01-11.

## Blind-label protocol

Runtime search loaded only `cases/`. Findings were frozen before `labels/` was loaded by the scorer. Integrity tests reject six forbidden label fields recursively. No leakage was detected.

## Threat-model design

The narrow model permits small nonnegative downward changes or declared transaction splitting. The broad sensitivity model adds one larger action. Legality and prevalence are not inferred.

## Baseline methods and search budgets

B0 random, B1 uniform grid, B2 boundary-only, B3 bounded exhaustive, and B4 combined each received 100 evaluations per case. Seed was 20260926. M3 confirmation received five seconds per supported case. An SMT-only detection baseline was not completed; M3 was used independently for confirmation, a deviation from the desired B5 comparison.

## Development and holdout results

Combined search detected 19/20 labeled positives overall with 0/10 negative-control findings. Holdout performance was 4/4 positives detected and 0/2 negative-control findings. These are raw curated-benchmark fractions, not population estimates.

## Historical rediscovery

| Case | Domain | Known pathology | IF finding | Match | Method | Formal? |
|---|---|---|---|---|---|---|
| ACA PTC 2020 | tax | 400% FPL eligibility cliff | boundary-crossing gain | YES, encoded component | combined | yes |
| FAR MPT 2017 | procurement | split purchase avoids threshold | split gain | YES | combined | unsupported model |
| SNAP gross screen | benefit | eligibility cliff | boundary-crossing gain | YES, encoded component | combined | yes |
| Alabama parent Medicaid | health | income eligibility cutoff | boundary-crossing gain | YES, encoded component | combined | yes |
| Arizona child transition | health | composition stress label | none | NO | combined | scoped non-violation |
| Pennsylvania CHIP | health | income eligibility cutoff | boundary-crossing gain | YES, encoded component | combined | yes |

The externally documented evidence establishes rules and broad structural concerns; it does not establish that each modeled action occurred empirically.

## Negative controls

All ten controls were clean under combined search. External SSA and EITC smooth-withdrawal controls were also `FORMALLY_SATISFIED_WITHIN_DOMAIN`.

## Formal confirmations

M3 independently confirmed six external violations (ACA, Alabama, Colorado, New York, Pennsylvania, SNAP) and three external scoped non-violations (Arizona proxy, EITC, SSA). All SAT witnesses replayed.

## Threat-model sensitivity and action-space ablations

Seven detected external positives remained detected under the broader action set; Arizona remained missed. Removing downward/split actions removed every external finding. Results therefore depend fundamentally on the declared action class.

## Surprise findings

None. No negative control produced a finding, so no unresolved surprise was forced into TP/FP accounting.

## Miss/error analysis

Arizona is the sole combined-search miss: `PROPERTY_MISMATCH` / `MODEL_SCOPE_LIMIT`. The official transition thresholds do not license additive cash valuation, so the honest smooth proxy has no profitable deviation and maps poorly to IF-015. Fixing this requires a source-backed coverage/payoff model, not heuristic tuning.

B3 bounded exhaustive missed two positives because the equal 100-evaluation budget ended before full enumeration; one was recovered by boundary-prioritized methods. This is `BUDGET_EXHAUSTION`, not a proof of safety.

## Counterexample reduction results

All 19 combined findings replayed. Scalar shrinking retained the first profitable registered action. Reductions are meaningful only under action magnitude; they do not minimize semantic complexity.

## Baseline results

| Method | Cases detected | Eval count | Median discovery cost | Safe-control false positives |
|---|---:|---:|---:|---:|
| Random | 19 | 1,204 | 3 | 0 |
| Grid | 19 | 1,061 | 17 | 0 |
| Boundary | 19 | 369 | 10 | 0 |
| Bounded exhaustive | 18 | 1,813 | 37 | 0 |
| Combined | 19 | 1,261 | 10 | 0 |

Random's low median is seed- and small-domain-dependent. Boundary-only matches combined recall and discovery median while using fewer total evaluations. The integrated search does not beat the strongest trivial baseline here.

## Repair benchmark results

| Case | Target | Repair generated | Regression pass | Historical reform similarity |
|---|---|---|---|---|
| ACA 2020 | cutoff to bounded phase-out | yes | yes | direction resembles temporary 2021–2025 cutoff removal; not optimality |
| SNAP | bounded phase-out | yes | yes | not evaluated |
| FAR | make split proxy nonprofitable | yes | yes | enforcement-cost proxy only |

These are workflow checks, not policy recommendations.

## Performance

The final generated run completed in 0.730385 seconds on the local machine. B0–B4 executed 5,708 candidate evaluations total. Formal checks were all below 0.02 seconds individually in the recorded run.

## Limitations

The suite is US-heavy, scalar, threshold-heavy, project-modeled, and small. All external benefit values/actions are partly assumed. There is no external strategic game, empirical prevalence validation, independent coding review, or complete SMT-only baseline. Boundary search explains essentially all recall.

## Hostile-review response

The strongest criticism survives: external rules do not make the project-authored threat models external. M7 mitigates this with explicit omissions, sensitivity, ablation, a preserved miss, and sober component-level language; it does not eliminate the problem.

## M7 verdict

**PASS WITH LIMITATIONS.** The exit gate is met for versioning, multiple external cases, external controls, blindness, frozen holdout evaluation, fair B0–B4 budgets, manual review, M3 confirmation, sensitivity, miss analysis, zero leakage, and inherited regression. Limitations prevent a full PASS: easy thresholds dominate, B4 does not outperform B2, B5 is incomplete, and independent expert review is absent.

## M8 authorization

M8 is authorized only for a research preview/reproducibility package that foregrounds these limitations. Before public claims, add independent rule/action review, a genuinely external benchmark contribution, non-threshold mechanisms, and a completed SMT-only baseline.
