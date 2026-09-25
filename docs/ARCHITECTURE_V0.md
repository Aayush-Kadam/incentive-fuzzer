# Architecture v0

## Principle

Use one trusted reference evaluator and treat every search/solver backend as an untrusted witness generator. All witnesses must replay through the evaluator.

## Proposed layers

1. **IncentiveSpec**: versioned declarative schema for entities, typed variables, units, time, actions, transitions, observations, enforcement, utility, objective, and properties.
2. **Semantic IR**: small typed expression language with explicit piecewise, aggregate, and temporal operators; no arbitrary Python.
3. **Reference evaluator**: deterministic interpreter with trace output and decimal/rational policy where required.
4. **Attack generators**: boundary enumeration, property-based generation, black-box optimization, and later coalition/equilibrium search.
5. **Verifiers**: restricted translations to SMT/MILP with capability checks; unsupported constructs fail closed.
6. **Reducer**: lexicographic objectives over agent count, manipulated fields, periods, magnitude, coalition size, and rule slice.
7. **Evidence store**: immutable run manifest, witness, trace, provenance, environment, and replay result.
8. **Repair laboratory**: constrained parameter/structure candidates evaluated on known and held-out attacks, plus designer guardrails.
9. **Adapters**: OpenFisca/PolicyEngine and other engines remain optional; adapter outputs are checked against fixtures.

## Semantic contract

`evaluate(policy, state, action_trace, parameters) -> outcome, trace`

`utility(actor, baseline, outcome, costs, enforcement) -> utility_components`

`property(baseline, candidate, outcome, context) -> pass | fail | undefined`

Undefined is not pass. Units, rounding, period alignment, ordering, and tie-breaking are normative semantics and must be explicit.

## M1 boundary

M1 supports deterministic single-actor, finite-horizon, bounded numeric and Boolean state; affine expressions; piecewise conditions; entity aggregation sufficient for a bounded splitting example; and explicit action costs. It excludes endogenous prices, arbitrary recursion, continuous-time dynamics, Bayesian games, unrestricted coalitions, natural-language legislation ingestion, and automatic repair.

## Differential verification

For every construct supported by a solver encoding:

1. generate bounded models and states;
2. compare interpreter output to encoded evaluation;
3. replay solver witnesses in the interpreter;
4. preserve every mismatch as a regression case;
5. halt verification claims on unresolved mismatch.

## Reproducibility record

Each run records experiment ID, UTC timestamp, code commit, seed, policy hash, schema version, parameters and provenance, attack configuration, solver/runtime versions, platform, duration, outputs, and nondeterminism notes.

## Security

Parsing is data-only. Expressions are allow-listed AST nodes with resource limits. External solvers run with time/memory caps. Uploaded policies cannot access files, network, environment variables, imports, or reflection.

