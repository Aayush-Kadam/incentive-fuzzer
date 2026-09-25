# M1 Architecture

The package has one semantic implementation in `src/incentive_fuzzer/core.py`:

`YAML -> safe loader -> typed dataclasses / expression AST -> reference evaluator -> structured result and trace`

Parsing performs name, type, unit, bound, transition-target, version, and expression checks. The evaluator uses only the typed IR; it never revisits YAML. Property enumeration calls the same public evaluator rather than duplicating rule meaning.

Future symbolic or optimized backends must preserve exact decimal constants, comparison inclusivity, simultaneous transition effects, declaration-order rule dependencies, bounds, units, cost timing, and post-action utility timing. Every future backend witness must replay through `evaluate` before becoming evidence.

M1 intentionally keeps PyYAML as the sole runtime dependency. Dataclasses and Decimal come from the standard library. No frontend, database, solver, optimizer, rule-engine adapter, or LLM is present.

## M2 search layer

`search.py` adds immutable search problems, domains, budgets, candidates, findings, statistics, deterministic generators, replay, structural deduplication, and reduction. Search consumes the M1 IR and calls the public M1 evaluator; it does not duplicate rule evaluation. Experiment artifacts store the committed engine revision, seed, budget, metrics, and reduced replayable findings.

## Known architectural limits

- Dataclasses provide visible domain concepts but not a published JSON Schema yet.
- Expressions are embedded typed objects after parsing, but source locations stop at logical YAML paths rather than line/column spans.
- Rule ordering is semantic, which makes careless YAML reordering a behavior change; canonical serialization preserves it.
- Property domains are explicit lists and may grow combinatorially.
