# M0 Hostile Review

## Recommendation

**Major revision before any public novelty claim; permit a restricted M1 feasibility study.**

## Central objection

The proposal currently concatenates established fields and gives the concatenation a compelling security metaphor. Mechanism design supplies incentives and equilibrium; robust design supplies uncertainty; automated design and synthesis supply repair; formal methods supply countermodels; Hypothesis supplies generation and reduction; rule engines supply executable policy; microsimulation supplies distributional outcomes. Integration is engineering until shown to yield a new scientific capability or reproducible empirical advantage.

## Novelty

The M0 search is insufficient for a priority claim. It lacks a registered search protocol, database queries, inclusion/exclusion flow, citation chasing, and expert review. The phrase “economic fuzzing” may be new while the method is not. The novelty matrix records documented capabilities but cannot establish absence.

## Economics

The hardest component is not search. It is specifying feasible actions, counterfactual true state, utility, costs, information, and designer intent. A tool that lets authors select these freely can manufacture any exploit. A tool that fixes them centrally will be wrong across domains. The project needs sensitivity sets and competing models, not one canonical rational agent.

## Threat model

Legality and observability are parameterized, but their values may be unknowable or institution-specific. Omniscient search can produce an attack an actor could not discover. Entity and household restructuring require legal semantics that a generic DSL may flatten incorrectly.

## Computation and verification

Piecewise-linear bounded models are tractable enough to demonstrate but may bias the project toward obvious cliffs. Nonlinear, stochastic, dynamic, and equilibrium models quickly lose completeness. If solver translation and runtime rounding differ, verification becomes misleading. Capability declarations and fail-closed behavior are mandatory.

## Counterexample shrinking

“Minimal” is not unique. Reducing income delta can increase the number of manipulated variables; reducing agents can change equilibrium; reducing periods can change the vulnerability class. The project must define a partial order or declared lexicographic objective and test semantic preservation, not advertise canonical minimality.

## Benchmarks

Synthetic benchmarks risk encoding the detector's own assumptions. Historical examples risk cherry-picking, incorrect law versions, and inferring behavior from schedule shape. Precommit admission, negative controls, blind/held-out cases, independent labels, and baseline budgets are necessary.

## Repair

Smoothing a cliff can increase fiscal cost, inequity, administrative burden, or other distortions. Search against known attacks invites overfitting. Repair must be multi-objective and evaluated on held-out attacks plus policy guardrails. “Auto-harden” is premature product language.

## Product

A generic YAML representation may be less useful than adapters for OpenFisca and PolicyEngine. Users may trust a polished severity label despite fragile behavioral assumptions. Assumptions and provenance must be more visible than severity.

## Requirements for M1 acceptance

1. Independent semantics document with units, time, rounding, undefined values, aggregation, and tie-breaking.
2. Hand-derived fixtures written before evaluator implementation.
3. Three flagship examples that genuinely use one IR.
4. Explicit unsupported-feature errors and no executable user code.
5. Provenance and threat-model fields required, not optional decoration.
6. At least one negative control per positive example.
7. A proof sketch or exhaustive oracle for expected M1 outcomes.

## Verdict

M0: **PASS WITH LIMITATIONS** as a feasibility gate. Any stronger verdict would confuse an untested research program with a contribution.

