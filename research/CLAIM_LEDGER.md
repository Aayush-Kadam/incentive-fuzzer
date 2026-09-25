# Claim Ledger

| Claim | Evidence | Source/experiment | Status | Confidence | Limitations |
|---|---|---|---|---|---|
| No sampled project documents the full proposed workflow | Scoped web review and matrix | M0 source register | PARTIALLY_SUPPORTED | Low | Absence not established; no systematic databases |
| OpenFisca core is static and does not model elasticity/behavior | Official documentation | OpenFisca docs | SUPPORTED | High | Adapters/extensions may add behavior |
| PolicyEngine models selected behavioral responses | Official current documentation | PolicyEngine 2024/current model pages | SUPPORTED | High | Not equivalent to arbitrary strategic attack search |
| Property generation and shrinking are established capabilities | Official Hypothesis docs/code | Hypothesis | SUPPORTED | High | Economic reduction objectives may differ |
| SMT can return models for encoded properties | Official Z3 guide | Z3 | SUPPORTED | High | Only within encoded theories and semantics |
| The integrated workflow is novel | None | Not yet tested | NOT_YET_TESTED | Very low | Central M0 limitation |
| A shared economic IR can cover three domains | Architecture only | M1 target | NOT_YET_TESTED | Very low | May require bespoke semantics |
| Domain-aware shrinking improves interpretability | None | Future benchmark | NOT_YET_TESTED | Very low | Metric and human evaluation required |
| Repair can reduce vulnerabilities without harmful tradeoffs | None | Future held-out tests | NOT_YET_TESTED | Very low | Multi-objective policy judgment required |
| IncentiveSpec v0.1 represents the five bounded deterministic M1 fixtures with one IR | 65-test suite and fixture files | M1 tests/examples | SUPPORTED | High | Does not imply arbitrary institutions |
| Exact declared currency boundaries are deterministic | Decimal boundary and comparison tests | M1 test suite | SUPPORTED | High | No currency conversion or statutory rounding |
| The reference evaluator agrees with nine hand-calculated cases | Independent expected literals in semantic audit | M1 audit | SUPPORTED | Medium | No second evaluator; shared authorship remains |
| Six economic property kinds execute over explicit finite domains | Property tests | M1 test suite | SUPPORTED | High | Enumeration only; no proof or general IC |
| Independent backends reproduce IncentiveSpec semantics | None | M3 target | NOT_YET_TESTED | Very low | Only one implementation exists |
| Boundary search recovered all exhaustive equivalence classes on the 12-case M2 synthetic suite | Frozen suite and summary table | M2 deterministic run 001 | SUPPORTED | High | Self-authored, threshold-heavy finite suite |
| Boundary search used fewer evaluations than exhaustive enumeration on the M2 suite | 4,812 versus 45,144 evaluations | M2 deterministic run 001 | SUPPORTED | High | No general scaling claim |
| All reported M2 experiment findings replay deterministically through M1 | Replay column for all raw findings | M2 deterministic run 001 | SUPPORTED | High | Same implementation is evaluator and replay oracle |
| Domain-aware reduction produced smaller replay-valid canonical counterexamples | Three before/after reductions | M2 deterministic run 001 | SUPPORTED | Medium | Exhaustive reducer and supplied finite domains |
| Incentive Fuzzer predicts real strategic behavior | None | Outside M2 | UNSUPPORTED | High | No empirical behavioral model or validation |
| The exact-rational SMT backend reproduced fixed-input M1 semantics on 500 generated cases | 500/500 exact comparisons | M3 run exact-smt-001 | SUPPORTED | High | Cases drawn from self-authored frozen suite |
| SMT and M2 exhaustive statuses agree on the frozen suite | 12/12 supported cases | M3 benchmark table | SUPPORTED | High | One property and finite domains |
| Every canonical SMT SAT witness replayed through M1 | 3/3 witnesses | M3 witness table | SUPPORTED | High | Parser/schema remain shared |
| SMT established bounded absence for phase-out and honest-reporting controls | UNSAT plus 2/2 exhaustive agreement | M3 canonical table | SUPPORTED | High | Only declared property, action, and domain |
| Incentive Fuzzer formally verifies arbitrary economic mechanisms | None | Outside formal fragment | UNSUPPORTED | High | Narrow QF_LIRA subset and one formal property |
