# M2 Search

M2 searches only bounded, deterministic IncentiveSpec v0.1 mechanisms. Every candidate is evaluated twice by the M1 oracle: once without an action and once with the candidate action. Search never declares validity directly.

## Methods

- **Exhaustive:** Cartesian enumeration of explicit state records/values and action controls. Complete only for that supplied finite domain.
- **Boundary:** extracts one-dimensional `<`, `<=`, `>`, and `>=` comparisons between attributes and constants/parameters, then composes recognized transitions of the form `x' = x - a` with boundary neighbors.
- **Property:** seeded candidate generation that prioritizes extrema, midpoint, and a seeded interior value. This is domain generation, not Hypothesis software testing.
- **Grid:** extrema and midpoint per dimension.
- **Combined:** stable deduplicated boundary, grid, then property candidates.

There is no scholarship or fixture-name branch in search code. Search operates on the expression IR, action transitions, declared domains, and optional action interpretation metadata.

## Budgets and statuses

Runs have maximum evaluations, candidates, and seconds. Two oracle evaluations are charged per feasible tested candidate. Invalid or infeasible actions do not become findings. Statuses distinguish violation found, exhaustive no violation, no violation within budget, budget exhausted, unsupported, invalid, and replay failure.

## Guarantees

For a completed exhaustive run, the result covers the supplied discrete domain. For all other methods, absence of findings is not robustness evidence. “Best” means best discovered unless exhaustive enumeration establishes the bounded-domain optimum.

## Boundaries and increments

The search domain supplies per-attribute steps. Integer/count/money experiments use one unit only because their configured discrete domains do. No universal assumption says that one rupee is always the correct epsilon.

