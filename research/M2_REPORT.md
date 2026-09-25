# M2 Report

## Objective

Test whether generic bounded search can autonomously generate, replay, deduplicate, and reduce profitable strategic deviations without fixture-name logic.

## Authorized scope

The M1 domain remained unchanged: one agent, one period, deterministic finite Decimal state/action values, simultaneous transitions, supported IncentiveSpec v0.1 expressions, and direct money costs.

## Search architecture

Immutable search problems contain a policy hash, explicit state records/values, action controls, property ID, action interpretation, budget, and assumptions. Candidates explain their source and optional structural boundary. Only two M1 evaluator calls can turn a candidate into a finding. Findings retain exact replay data and structured traces.

## Search methods

Exhaustive enumeration supplies finite-domain ground truth. Boundary search extracts simple attribute/constant comparisons and composes `x' = x - a` transitions with boundary neighbors. Seeded property generation emphasizes extrema, midpoint, and interior values. Grid uses extrema/midpoint. Combined executes boundary, grid, then seeded candidates with stable candidate deduplication.

## Ground truth construction

Each finite experiment domain was exhaustively evaluated. Ground truth is the set of structural finding-equivalence classes, not the number of profitable state/action pairs. Exhaustive coverage is not called formal verification.

## Canonical fixture results

| Fixture | Ground-truth classes | Boundary recall | Boundary evals | Exhaustive evals | Result |
|---|---:|---:|---:|---:|---|
| Scholarship cliff | 1 | 1.00 | 18 | 60 | found; gain 99,999 |
| Linear phase-out | 0 | 1.00 | 0 | 108 | no profitable deviation in tested domain |
| Stacked programs | 4 | 1.00 | 72 | 237 | four structural classes |
| Procurement threshold | 1 | 1.00 | 36 | 242 | found; gain 18 |
| Honest reporting control | 0 | 1.00 | 1,344 | 8,547 | exhaustive negative control passed |

For the scholarship, boundary search found the first violation after 6 evaluations versus 28 for exhaustive enumeration and recovered the same best gain. The phase-out has no comparison nodes because its kinks use min/max; boundary search therefore evaluated nothing. Other methods and exhaustive enumeration found no profitable deviation there.

## Synthetic benchmark

The frozen suite has 12 mechanisms: nine exhaustively vulnerable and three safe controls. Two originally safe bound-adjacent labels were corrected in a separate commit after exhaustive evaluation disproved them.

| Method | Mean equivalence recall | Total evaluations | Cases with findings | False-positive classes |
|---|---:|---:|---:|---:|
| Exhaustive | 1.000 | 45,144 | 9 | 0 |
| Boundary | 1.000 | 4,812 | 9 | 0 |
| Property | 0.556 | 15,356 | 4 | 0 |
| Grid | 0.375 | 256 | 2 | 0 |
| Combined | 1.000 | 18,512 | 9 | 0 |

Boundary search used 89.3% fewer evaluations than exhaustive search on this suite. This is a suite-specific empirical result, not a general dominance claim.

## Negative controls

`safe_high_cost`, `safe_zero_award`, `reported_safe_penalty`, and the canonical honest-reporting control produced no exhaustive profitable deviation. No unexplained false-positive class remained.

## Recall and precision

Precision is defined against exhaustive structural equivalence classes, not against real-world vulnerability truth. All methods had zero false-positive classes; where findings existed, observed precision was 1.0. Mean recall includes safe cases as correct at 1.0 only when the method also returned no class, matching the documented experiment script.

## Search efficiency

On the scholarship fixture, evaluations to first violation were: boundary 6, property 10, grid 16, exhaustive 28, combined 6. Best gains were 99,999 for boundary/exhaustive/combined, 99,998 for property, and 99,997 for grid.

## Counterexample reduction

Three canonical findings were reduced:

| Fixture | Before amount | After amount | Before gain | After gain |
|---|---:|---:|---:|---:|
| Scholarship | 3 | 1 | 99,997 | 99,999 |
| Stacked programs | 5 | 2 | 8 | 11 |
| Procurement | 6 | 1 | 8 | 18 |

The smaller scholarship witness starts at exactly 500,000 and reduces both true and reported income to 499,999. This follows the frozen strict `< 500000` rule and is smaller than the prompt's illustrative 500,001-to-499,999 witness.

## Replay validation

Every raw finding in the canonical and synthetic experiment tables replayed with exact baseline utility, result utility, utility delta, resulting state, and policy hash. Reduced findings were serialized to `experiments/m2/runs/findings.json`.

## Performance

The final run produced 25 canonical method rows and 60 synthetic method rows under seed 17 and a 50,000-evaluation/30-second budget. Search overhead varies by method; representative canonical runtimes were 0.0026 seconds for scholarship boundary search and 0.92 seconds for honest-control exhaustive search on the recorded machine.

## Limitations

The suite is synthetic and predominantly one-dimensional. Boundary algebra handles only subtractive controls. Action semantics are supplied as metadata. Classification and equivalence are structural approximations. No behavioral prediction, external validity, continuous-domain guarantee, equilibrium, formal proof, or repair is established.

## Hostile review response

The hostile review's strongest criticism survives: M2 validates a threshold-oriented fuzzer on self-authored mechanisms. Quantitative efficiency and replay correctness are real, but scientific novelty and realistic usefulness remain untested.

## Verdict

**PASS WITH LIMITATIONS.** All M2 exit conditions hold inside the bounded M1 domain. Boundary search shows measurable value; generic property/grid baselines remain weak.

## M3 authorization

M3 may independently encode the existing finite Decimal linear subset into exact rational SMT/MILP constraints; generate counterexamples for the six existing property types; replay every solver witness through M1; and differential-test comparison inclusivity, simultaneous transitions, ordered rules, costs, and utility. It may not claim arbitrary nonlinear, stochastic, dynamic, multi-agent, or real-world mechanism verification.

