# M6 Report

## Objective

Test whether bounded deterministic repair can eliminate declared incentive failures while rejecting repairs that violate policy constraints or create failures in single-agent, formal, population, strategic, or mutation regression layers.

## Authorized scope

Exact finite parameter grids, one recognized hard-cutoff structural transform, deterministic M1 mechanisms, M2 search, M3's profitable-deviation property, M4 synthetic populations, M5 finite pure games, and local exact mutation neighborhoods. No optimal-policy, welfare, empirical, stochastic, dynamic, Bayesian, coalition, or unrestricted synthesis claim is authorized.

## Repair model

The implementation adds typed repair problems, parameters, candidates, constraints, objectives, evaluations, regression checks, frontiers, mutations, budgets, and bounded iterations. Candidate identity binds parent hash, repair family, parameter diff, and provenance. Status and layer evidence remain separate.

## Repair parameterization

Scholarship searches threshold and award edits plus four phase-outs. Stacked programs search award pairs. Procurement searches threshold, process cost, and action-cost multipliers. The strategic game searches cost, bonus, and aggregate threshold. All values were frozen in `M6_PRECOMMITMENT.md`.

## Constraints

Scholarship benefit at income 480,000 must remain at least 50,000, maximum benefit at most 100,000, and schedule segments at most three. Stacked awards must remain at least 4 and 3. Procurement process cost must remain at least 10. Game bonus must remain at least 3, payout capability positive, and `(HONEST,HONEST)` preserved.

## Repair-distance semantics

Normalized parameter distance, discrete schedule distance, recipient impact, fiscal deviation, and structural complexity are reported separately. No scalar repair score exists.

## Candidate generation

Generation is deterministic `EXHAUSTIVE_GRID`. Parameter edits and structural transforms record `PARAMETER_GRID` or `STRUCTURAL_TRANSFORM` provenance. The registered run evaluated 74 candidates with 351 regression checks.

## Structural repairs

The generic structural transformer recognizes a hard-cutoff `if award else zero` rule and replaces it with an exact capped linear phase-out using `max`, `min`, and an exact finite-decimal withdrawal rate. It does not branch on the scholarship fixture name.

## Parameter repairs

Exact edits cover benefit/threshold values, stacked awards, procurement parameters and action costs, and M5 game costs, bonuses, and thresholds. Parameter-only scholarship edits did not pass; procurement action-cost multipliers 19 and 20 and six strategic-game combinations passed their declared gates.

## Counterexample-driven loop

The bounded scholarship loop began from the M2 cliff witness, selected an unvisited non-dominated passing structural candidate, re-attacked it, and stopped after one iteration with `REGRESSION_SUITE_PASSED`. Repetition, infeasibility, missing target, and iteration-budget stops are separately tested.

## M2 regression

Every single-agent repair received exhaustive and combined search. Threshold edits were attacked at their new boundary, preventing a shifted cliff from masquerading as a fix. All four scholarship phase-outs, procurement multipliers 19/20, and no stacked candidates under constraints achieved zero M2 residual gain as reported.

## M3 regression

All 43 spec candidates were checked where supported. Passing scholarship phase-outs and procurement cost repairs returned `FORMALLY_SATISFIED_WITHIN_DOMAIN`. The best constraint-feasible stacked candidate remained `FORMALLY_VIOLATED`. These are domain-scoped conclusions, not exploit-proof certificates.

## M4 regression

The original scholarship B0 profitable share was 0.515625. All four phase-outs reduced it to 0 on the frozen M4 grid. Procurement multipliers 19 and 20 reduced the frozen B0 share from 0.4 to 0. The best feasible stacked edit, awards 4 and 3, reduced share from 0.190476 to 0.119048 but retained maximum gain 5 and failed.

## M5 equilibrium regression

The strategic flagship originally had `(H,H)` and `(M,M)`. Six candidate games preserved `(H,H)` and removed `(M,M)` under exact enumeration. The two Pareto candidates were `(cost=4, bonus=3, threshold=2)` and `(cost=5, bonus=3, threshold=2)`.

## Repair-induced vulnerabilities

The registered enforcement-rebate candidate increased penalty from 1 to 2, changing isolated gain from +1 to 0. Because interaction bonus was `3*penalty`, the same change raised bonus from 3 to 6 against manipulation cost 5 and created `(M,M)`. The regression gate rejected it as `REPAIR_INDUCED_VULNERABILITY`.

## Pareto analysis

The scholarship frontier contains `(L=480000,U=580000)` and `(L=480000,U=680000)`. Both eliminate registered gain and population exposure. The shorter repair has normalized distance 1, fiscal deviation +48,747.5, and fragility 0.4; the wider has distance 2, fiscal deviation +58,748.75, and fragility 0. Neither dominates the other.

The game frontier contains `(cost=4,bonus=3,threshold=2)` with distance 3 and fragility 0.5, and `(cost=5,bonus=3,threshold=2)` with distance 4 and fragility approximately 0.286. Again, neither dominates under declared dimensions.

## Mutation fragility

The run executed 245 exact registered mutations at `±1`, `±5`, and `±10` where valid. Mutation failure remains a separate objective; zero observed fragility means only no tested neighbor failed.

## Scholarship repair

Original maximum gain was 99,999. Award reductions left residual gains of 49,999–99,998. Threshold shifts moved rather than removed the cliff and failed fresh boundary-aligned attack or coverage. Zero award fixed the target but violated coverage. All four structural phase-outs passed M2, M3, and M4 within declared domains.

## Stacked-program repair

No constraint-feasible award pair fully removed the vulnerability. The best feasible pair `(award_a=4, award_b=3)` reduced maximum gain from 11 to 5 and population share to 0.119048, but remained formally and executably violated. Exact-grid result: no feasible full repair in the registered family.

## Procurement repair

Threshold changes moved the exploit; low process-cost edits conflicted with the preserved-purpose constraint. Action-cost multipliers 19 and 20 reduced maximum gain from 18 to 0, population share from 0.4 to 0, and produced domain-scoped M3 UNSAT. Multiplier 19 is closer under the declared distance.

## Strategic-game repair

The equilibrium condition validated the hand-derived boundary: at threshold two, a tie `bonus=cost` retains `(M,M)` because ties are best responses; strict `bonus<cost` removes it. Passing candidates preserve `(H,H)` and payout capability.

## Safe-control result

`safe_interaction_control` retained only `(HONEST,HONEST)` and returned `NO_REPAIR_NEEDED`. No candidate was applied.

## Performance

The frozen run evaluated 74 candidates, 351 regression checks, 43 formal checks, and 245 mutation cases in approximately 11 seconds. This is small local grid search, not scalable synthesis.

The final suite contains 200 passing tests, including all 170 inherited M1–M5 tests. Total statement coverage is 92%; the repair module has 93% coverage.

## Limitations

All repair spaces and objectives are synthetic and self-authored. Structural generation covers one pattern. Fiscal and coverage metrics use finite synthetic states. Population and equilibrium regressions inherit M4/M5 limitations. Passing candidates may fail omitted attacks, domains, objectives, or behavioral models.

## Hostile-review response

The hostile review correctly characterizes the search as mostly brute-force tuning and obvious smoothing. M6's defensible value is the auditable multi-layer rejection framework, not creative mechanism invention. The stacked no-repair result, zero-award rejection, induced-equilibrium failure, Pareto tradeoffs, and mutation failures are preserved rather than optimized away.

## M6 verdict

**PASS WITH LIMITATIONS.** Counterexample-driven bounded repair works, and multi-layer regression materially prevents false confidence. Generality, normative validity, external calibration, and scaling remain limited.

## M7 authorization

M7 may benchmark the bounded repair and regression workflow on independently sourced or historically frozen mechanisms. Mature claims are deterministic candidate reproducibility, exact constraint enforcement, bounded M2/M3/M4/M5 regression, Pareto reporting, and repair-induced-failure detection. M7 must not treat M6 candidates as real policy recommendations or assume current repair families are comprehensive.
