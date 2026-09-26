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
## M5 finite-game layer

M5 leaves IncentiveSpec v0.1 unchanged and adds an external exact-game wrapper:

```text
player-local types and finite actions
              -> joint action
              -> mechanism-specific exact aggregator
              -> player payoffs + designer outcomes
              -> exact best-response correspondence
              -> exhaustive pure-Nash enumeration and replay
```

Best-response dynamics consume the same exact evaluator but remain separate from equilibrium discovery. M1–M4 modules do not depend on the game layer.

## M6 repair layer

```text
target counterexample + finite repair space
                  -> deterministic candidate generation
                  -> transformed spec or game
                  -> M2/M3/M4/M5 regression adapters
                  -> constraint gate + mutation stress
                  -> explicit repair status + Pareto frontier
```

The repair module owns mechanism-independent identities, constraints, dominance, mutation neighborhoods, and bounded iteration. Registered experiment adapters construct layer-specific domains. This keeps fixture names out of structural transformation logic while making economic evaluation assumptions explicit.
