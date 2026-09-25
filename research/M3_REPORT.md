# M3 Report

## Objective and scientific motivation

Test whether a separately authored exact-rational backend reproduces M1 runtime semantics and M2 property statuses, rather than merely confirming one Python implementation with itself.

## Authorized scope

One agent, one period, bounded deterministic transitions, finite Decimal inputs, linear arithmetic, conditionals, min/max, direct action costs, ordered rules, and the selected no-profitable-deviation property.

## Backend independence

Parsing, schema validation, and immutable AST classes are shared. Decimal conversion, AST translation, domains, simultaneous transitions, rule ordering, costs, utility, property negation, model decoding, and formal statuses are independently implemented in `verify.py`. No M1 evaluation helper generates SMT formulas.

## Formal fragment and exact numeric semantics

The backend uses QF_LIRA with Boolean `ite`. Finite Decimals map to normalized exact fractions without binary float. Symbolic-by-symbolic multiplication is rejected. Explicit values or step constraints ensure decoded witnesses belong to replayable finite-decimal domains.

## SMT translation and property encoding

Pre-state attributes, controls, and post-state attributes are distinct symbols. All transition right-hand sides use the pre-state. Rules build an ordered symbolic environment. Z3 checks existence of a feasible action with post-action utility strictly greater than baseline utility. SAT is accepted only after exact replay; UNSAT is scoped to the property/domain hash.

## Differential-validation design

Validation combines hand-calculated conversion/boundary tests, canonical fixed-input cases, 500 seeded fixed-input cases, five canonical property-status comparisons, and twelve frozen benchmark comparisons. M2 exhaustive enumeration supplies property ground truth for these finite domains.

## Canonical fixture results

| Fixture | M2 exhaustive | SMT | M1 replay | Agreement |
|---|---|---|---|---|
| Scholarship cliff | violation | SAT | pass | yes |
| Linear phase-out | none | UNSAT | n/a | yes |
| Stacked programs | violation | SAT | pass | yes |
| Procurement threshold | violation | SAT | pass | yes |
| Honest reporting | none | UNSAT | n/a | yes |

The phase-out result demonstrates exact `min`/`max` reasoning despite M2 boundary extraction returning no kink candidates.

## Frozen M2 benchmark comparison

All 12 mechanisms were supported. SMT status agreed with frozen exhaustive ground truth in 12/12: nine SAT violations and three UNSAT controls. Every SAT benchmark witness replayed; aggregate witness details are preserved in the tables and tests.

## Generated differential tests

Seed 20260926 generated 500 valid fixed state/action cases across the frozen suite. State transitions, rule outputs, utility, and designer outcomes agreed exactly in 500/500; rejection count and mismatch count were zero.

## SAT witness replay and UNSAT comparison

The canonical matrix produced three SAT witnesses and all 3/3 replayed. Both canonical UNSAT results agreed with zero M2 exhaustive violations (2/2). Across the frozen suite, all nine SAT statuses replayed in automated tests and all three UNSAT statuses agreed.

## Solver performance

Z3 4.15.3 used a 5,000 ms timeout and seed zero. Canonical total verification times ranged from about 0.019 seconds (procurement) to 0.048 seconds (honest-reporting control) on the recorded machine. No timeout or unknown occurred.

## Disagreements discovered and fixes

No semantic disagreement was observed. The backend design exposed one scope issue rather than a contradiction: arbitrary rational models are not necessarily finite Decimals, so formal domains require explicit values or step constraints and non-finite model values fail closed.

## Limitations

Only profitable-deviation existence is formally encoded; four other M1 property families remain enumeration-only. The parser is shared. Generated cases reuse the synthetic suite rather than a separate mechanism grammar. No proof objects are retained. Formal conclusions remain conditional on supplied economics and action completeness.

## Hostile-review response

The independent backend materially reduces the risk of a shared semantic implementation bug, but not parser error, model misspecification, or benchmark narrowness. On tiny domains, its scientific value is triangulation and scoped UNSAT conclusions rather than demonstrated scalability.

## M3 verdict

**PASS WITH LIMITATIONS.** The backend independently reproduces the supported semantics and supports precise SAT/UNSAT conclusions for one formal property, but property coverage is narrower than requested.

## M4 authorization

M4 may add heterogeneous populations, distributions over fixed agent parameters, manipulation-cost sensitivity, deterministic Monte Carlo manifests, and robustness envelopes while retaining M1 evaluation for individuals and M3 verification only for individual mechanisms in the current formal fragment. Population-level, probabilistic, equilibrium, and empirical claims are not formally inherited.

