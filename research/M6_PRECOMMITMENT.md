# M6 Precommitment

Frozen before repair-engine implementation and final repair experiments: 2026-09-26.

## Research question

Can deterministic bounded repair generation reduce a declared incentive vulnerability while preserving explicit constraints and rejecting candidates that fail single-agent, formal, population, strategic, or mutation regression gates?

## Search method and budgets

All registered searches are `EXHAUSTIVE_GRID`, not heuristic optimization. Maximum candidates are 100 per problem, maximum counterexample-guided iterations are 5, and maximum wall time is 120 seconds per registered problem. Candidate identity binds the parent hash, repair family, parameter changes, and generator provenance.

## Repair distance

Report dimensions separately:

1. normalized parameter distance: sum of absolute parameter changes divided by declared scale;
2. schedule distance: sum of absolute benefit/output changes over the frozen evaluation states;
3. recipient impact: fraction of frozen baseline states whose mechanism output changes;
4. fiscal deviation: mean repaired baseline fiscal cost minus original;
5. structural complexity: branch, parameter, and expression-node counts.

No opaque repair score is authorized.

## Scholarship target and space

Target: profitable `reduce_work` deviation around the frozen 500,000 hard cutoff.

- threshold edits: `{480000, 490000, 499999, 500000, 500001}`;
- award edits: `{0, 50000, 75000, 99999, 100000}`;
- structural hard-cutoff to phase-out candidates `(L,U,award,rate)`:
  - `(480000,580000,100000,1)`;
  - `(480000,680000,100000,0.5)`;
  - `(500000,600000,100000,1)`;
  - `(500000,700000,100000,0.5)`.

Constraints: benefit at income 480,000 must be at least 50,000; maximum benefit must not exceed 100,000; at most three schedule segments; all original actions remain available. The zero-award baseline is included deliberately and must fail the coverage constraint.

Regression domains reuse M4 scholarship states 499,995–500,010, actions 0–20, fixed frictions `{0,1,10,100,1000,50000,99999,100000}`, multipliers `{0,0.5,1,2}`, and B0 semantics. M2 exhaustive and combined search use the same correlated states/actions. M3 checks the same declared action and finite domain where supported.

## Stacked-program target and space

Target: combined profitable income reduction in the frozen income 0–20/action 0–5 domain.

- `award_a`: `{0,2,4,6,8}`;
- `award_b`: `{0,1,3,5}`;
- evaluate single-parameter and Cartesian edits.

Constraints preserve `award_a >= 4`, `award_b >= 3`, both programs, and original action availability. The target is reduction, not guaranteed elimination; an exact-grid no-feasible result is acceptable.

## Procurement target and space

Target: profitable scope reduction around threshold 100 over states 95–105/actions 0–10.

- threshold: `{98,99,100,101,102}`;
- process cost: `{0,5,10,15,20}`;
- action-cost multiplier structural edit: `{1,5,10,19,20}`.

Constraints require process cost at least 10, retain the review threshold, and preserve the scope-reduction action. Setting process cost to zero is an over-repair control and must fail.

## Strategic-game target and space

Target: remove `(MANIPULATE,MANIPULATE)` from the exact equilibrium set of `aggregate_threshold_claim` while preserving `(HONEST,HONEST)`.

- manipulation cost: `{2,3,4,5}`;
- interaction bonus: `{1,2,3,4}`;
- aggregate threshold: `{1,2}`.

Constraints require bonus at least 3, positive payout capability, both actions, and preservation of the honest equilibrium. Exact M5 enumeration is mandatory. The hand-derived boundary is `bonus < cost` for removing the manipulation equilibrium at threshold two; ties do not remove it.

## Safe control

The frozen `safe_interaction_control` must return `NO_REPAIR_NEEDED`; mutation or candidate generation must not alter it by default.

## Repair-induced vulnerability fixture

A deliberately synthetic enforcement-rebate fixture uses parameter `penalty`. The isolated deviation gain is `2-penalty`; the group interaction bonus is `3*penalty` with game manipulation cost 5. Moving penalty from 1 to 2 fixes the isolated target (`1 -> 0`) but creates a strict mutual-manipulation equilibrium (`bonus 6 > cost 5`). The generic regression gate, not candidate generation, must reject it as `REPAIR_INDUCED_VULNERABILITY`.

## Pareto objectives

Minimize, without weighting: maximum residual exploit gain, positive fiscal deviation, normalized repair distance, structural complexity, harmful-equilibrium count, and mutation fragility. Only feasible candidates passing mandatory gates may be called repair passes. Non-dominated alternatives remain separate.

## Mutation neighborhood

For every numeric repair parameter, test valid bounded mutations at `±1`, `±5`, and `±10`. Game cost/bonus additionally use the same exact deltas within non-negative bounds. Fragility is the fraction of registered nearby mutations that reintroduce the target or a declared regression.

## Counterexample loop

At each iteration: replay the current witness, freshly attack, generate deterministic candidates, evaluate mandatory gates, select the lexicographically first non-dominated feasible candidate by target status, regression status, fiscal deviation, distance, complexity, and candidate ID, then re-attack. Stop on no violation, passing regression, iteration budget, repeated candidate, or exact-grid infeasibility.

## Success conditions

M6 succeeds only if a structural and parameter repair are evaluated; M2/M3/M4/M5 gates are applied where relevant; one candidate passes all applicable gates; the induced-vulnerability candidate is rejected; trivial repairs fail constraints; a safe control is unchanged; Pareto and mutation results are produced; and all inherited tests remain green.

## Claim boundary

M6 may establish a reproducible bounded hardening and regression workflow. It may not claim optimal policy design, empirical welfare improvement, complete repair, global robustness, or socially preferred parameter selection.
