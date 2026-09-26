# Research Log

## 2026-09-25 — M0

- Hypothesis: novelty might lie in automated strategic attack generation for policy rules.
- Contrary evidence: strategic classification, automated mechanism design, formal mechanism verification, property-based testing, and current behavioral microsimulation each cover substantial pieces.
- Narrowed hypothesis: the contribution may be a benchmarked cross-domain audit protocol and evidence model.
- Unexpected result: PolicyEngine's current documentation already includes configurable behavioral responses, weakening any static-microsimulation contrast.
- Methodological concern: absence of an end-to-end tool was not established systematically.
- Deferred: formal systematic review, expert taxonomy validation, benchmark encoding, evaluator implementation, and all performance claims.
- Negative result preserved: broad novelty and automatic-repair claims failed M0 review.

## 2026-09-25 — M1

- Rejected expression strings and arbitrary Python in favor of a closed YAML AST.
- Chose Decimal over binary float; rejected rational arithmetic for v0.1 dependency simplicity. Non-terminating phase-out slopes remain explicit finite approximations.
- Semantic ambiguity found: canonical key sorting changed ordered rule dependencies. Canonicalization now preserves rule order.
- Negative-control error found: a penalty rate of two did not deter a one-unit report change that unlocked a five-unit benefit. Rate raised to six; the failed expectation was not hidden.
- Performance anomaly found: hashing canonical YAML on each evaluation made the smoke test unacceptably slow. Immutable identity is now computed at parse time.
- Property bug found during audit: participation read `maximum` rather than `minimum`. Fixed with a regression test.
- Limitation: internal fixtures and evaluator share authorship; independent semantic reproduction remains untested.

## 2026-09-26 — M2

- Froze 12 synthetic mechanisms before implementing/tuning search heuristics at commit `76a1744`.
- Exhaustive evaluation falsified two planted safe labels at state-domain bounds; labels were corrected separately at `1e04c30` rather than suppressing findings.
- A Cartesian scholarship domain allowed inconsistent true/reported baselines and produced a misleading reducer result. Added explicit correlated state records.
- Initial boundary attribution labeled a profitable candidate against a condition whose truth did not change. Required replayed truth change before retaining boundary origin.
- Role `reported` proved insufficient to classify manipulation: real scope/work changes can also update reported values. Added explicit action interpretation metadata and neutral fallback.
- Boundary search achieved full equivalence recall on the frozen suite with 4,812 evaluations; seeded property and grid baselines missed classes.
- The linear phase-out exposes a limitation: current boundary extraction does not identify min/max kinks.
- The minimum scholarship reproducer in the supplied domain is 500,000 -> 499,999 with amount 1, not the illustrative amount 2.

## 2026-09-26 — M3

- Added pinned Z3 4.15.3 after confirming no solver was installed.
- Independently implemented Decimal-to-fraction conversion, AST translation, simultaneous transitions, ordered rules, costs, utility, model decoding, and profitable-deviation negation.
- Rejected symbolic-by-symbolic multiplication explicitly.
- Restricted formal domains to explicit finite values or steps; unrestricted rationals can yield values M1 Decimal cannot represent finitely.
- Fixed-input differential testing produced 500/500 exact agreements with no rejected cases.
- Canonical status agreement was 5/5; frozen benchmark status agreement was 12/12.
- Canonical SAT replay was 3/3; canonical UNSAT/exhaustive agreement was 2/2.
- Z3 independently handled the phase-out min/max structure that M2 boundary extraction does not recognize.
- No M1/M2 semantic defect was discovered. Formal coverage remains limited to profitable-deviation existence.

## M4 execution — 2026-09-26

- Froze fixtures, ranges, scenarios, metrics, seed, sample sizes, and holdout in commit `385bc33`.
- Did not enlarge ranges after results. Scholarship multipliers were inert because base action cost is zero; retained this negative sensitivity result.
- B1 was strongly downward biased by candidate ordering; reported signed error rather than behavioral prevalence.
- B2 separated opportunity from response: stacked/procurement opportunities remained while response fell to zero at hurdle 100.
- Phase-out and honest reporting produced no profitable deviations in registered domains.
- Rejected welfare aggregation because fixtures define no transferable social objective.
- Monte Carlo converged toward the exact weighted share; intervals remain sampling-only.

## M5 execution — 2026-09-26

- Froze the aggregate-threshold claim fixture and hand-derived matrix before implementing the game engine in commit `1964409`.
- The first golden run exposed a manual prose error: the focal honest payoff against a manipulator was confused with the opponent's payoff. The matrix and equilibrium set were correct; corrected the complementarity increment from 6 to 4 in separate commit `229135f`.
- Chose an external finite-game wrapper rather than IncentiveSpec v0.2, preserving all v0.1 semantics while making joint evaluator code a new trusted boundary.
- Exact enumeration reproduced the four payoff cells and both predicted equilibria. Ties remained correspondences and Matching Pennies returned zero pure equilibria.
- A first experiment run exposed an artifact identity collision because the safe control inherited the flagship game ID. Fixed the ID and regenerated the manifest; equilibrium logic was unaffected.
- Flagship isolated manipulation gain was -2, but gain against a manipulating rival was +2. The resulting equilibria were honest/honest and manipulate/manipulate.
- The scarcity-capacity game showed strategic substitution: gain +5 against honesty and -1 against manipulation, with two asymmetric equilibria.
- Synchronous best response cycled from both off-diagonal flagship profiles. Asynchronous A-then-B response converged with a two/two split across the two equilibria.
- Parameter sweeps included honest-only, manipulation-only, multiple, and tie-dependent regimes. No equilibrium was promoted as the predicted outcome.
- Exact scaling was measured through 12 binary players (4,096 profiles); no broad scalability claim is supported.
- Deferred mixed strategies, sequential/Bayesian games, coalitions, closed multi-agent DSL semantics, external calibration, and solver-backed equilibrium verification.

## M6 execution — 2026-09-26

- Froze repair grids, constraints, objectives, budgets, mutation deltas, and induced-vulnerability fixture before implementation in commit `d3b38b0`.
- Implemented deterministic identities, parameter edits, hard-cutoff phase-out transformation, action-cost transformation, constraints, layer gates, Pareto dominance, mutations, and bounded repair loops.
- Parameter-only scholarship edits did not pass: award reductions retained cliffs; threshold changes moved the boundary; zero award violated coverage.
- All four registered phase-outs passed M2 exhaustive/combined, M3 domain-scoped UNSAT, and frozen M4 population regression.
- The shorter scholarship frontier repair had lower fiscal/distance metrics but 0.4 mutation fragility; the wider repair had zero observed fragility but higher fiscal deviation.
- No constraint-feasible stacked award pair fully repaired the composition failure. Preserved the exact-grid no-feasible result; the best feasible pair reduced gain 11 to 5 but remained violated.
- Procurement threshold edits moved the exploit. Cost multipliers 19 and 20 passed; multiplier 19 was closer.
- Exact M5 regression confirmed `bonus=cost` retains the manipulation equilibrium through ties. Strict `bonus<cost` was required under threshold two.
- The synthetic penalty repair fixed isolated gain but induced `(MANIPULATE,MANIPULATE)` through its coupled rebate and was rejected.
- The safe interaction control returned `NO_REPAIR_NEEDED` and was not modified.
- The frozen run evaluated 74 candidates, 351 regression checks, 43 formal checks, and 245 mutations in about 11 seconds.
- Algorithmic novelty remained weak: candidate search is grid enumeration plus one obvious structural transform. The main result is repair regression, not policy invention.
# M7 log (2026-09-26)

- Froze 30 IDs, labels, six holdouts, budgets, matching rules, and exclusions before implementation (`6f5aa0e`).
- Sourced external components from official IRS, FAR/Acquisition.gov, Oversight/OIG, CMS/Medicaid, SSA, and Federal Reserve material.
- Excluded 18 candidates before evaluation for unrepresentability or insufficient source/payoff detail.
- Fixed two generic formal-adapter defects before the freeze commit: value type `decimal` versus unit `scalar`, and IncentiveSpec operator `mul`.
- Froze engine, catalog, package, and search configuration at `03d2260` before holdout execution.
- Preserved the Arizona composition miss; no heuristic was changed after holdout execution.
- Boundary-only matched combined recall and used fewer evaluations. This defeats any M7 claim that combined candidate generation improves recall on v0.1.
- No surprise finding occurred. External smooth controls remained clean and formally scoped-safe.
- Repair outputs are bounded structural candidates only; none is a recommendation.
- Post-run artifact audit found a self-referential manifest hash. The generic builder was corrected to exclude the manifest itself, then all benchmark evaluations and tests were rerun; detection results were unchanged.
