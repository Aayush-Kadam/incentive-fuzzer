# M1 Report

## Objective

Determine whether a bounded deterministic economic rule can be specified and evaluated without semantic ambiguity sufficient to invalidate later adversarial search.

## Scope

One actor, one period, deterministic simultaneous transitions, bounded attributes and controls, finite Decimal arithmetic, typed units, ordered piecewise-linear rules, direct action cost, money-valued utility, separate designer outcomes, and explicit finite property domains.

## Formal model

The implemented object is \(M=(S,A,T,R,C,U,P,\Theta)\). Its definitions and exclusions are in `docs/FORMAL_MODEL.md`.

## IncentiveSpec design

Version `0.1` uses YAML only as serialization. Parsing produces typed frozen dataclasses and an allow-listed expression IR. Unsupported versions, symbols, units, targets, bounds, and operators fail closed with `IncentiveSpecError`.

## Numeric representation

All numeric evaluation uses `Decimal` constructed from textual representations. ₹500,000 is exact. Comparisons have no tolerance. There is no division operator; finite-decimal rate approximation is explicit and hash-visible.

## Expression semantics

Supported nodes: constants, variables, addition, subtraction, scalar/rate multiplication, min, max, five comparisons, and total if/else. Nested if/else represents piecewise schedules without overlap/gap ambiguity. Rules run in declaration order.

## Reference evaluator

The evaluator validates total state, action controls and feasibility; applies transition effects simultaneously; revalidates bounds; evaluates cost, rules, utility, and designer outcomes; and returns a structured deterministic trace plus cached canonical spec identity. It is the future replay oracle, not a formal prover.

## Properties implemented

Budget bound, resource monotonicity, maximum local resource drop, no profitable downward manipulation, no profitable misreporting, and participation. Results are `SATISFIED_ON_ENUMERATED_DOMAIN`, `VIOLATED`, `NOT_EVALUATED`, `UNSUPPORTED`, or `INVALID_SPEC`.

## Canonical fixtures

- Hard scholarship cliff: exact strict cutoff and separate true/reported income.
- Linear phase-out: capped affine transfer with declared finite-decimal slope.
- Two stacked programs: ordered additive composition and local resource drop.
- Procurement threshold: inclusive process-cost boundary outside welfare terminology.
- Honest-reporting control: expected penalty eliminates profitable tested misreports.

No fixture uses bespoke evaluator code.

## Golden-test results

Nine independently listed state/action/output calculations passed. They cover scholarship below/equal/above threshold and a profitable two-unit work reduction, phase-out endpoints, stacked-program discontinuities, procurement equality, and the honest-reporting penalty case.

## Test results

`65 passed in 2.34s` on Python 3.12.10. Coverage run before the final participation regression test reported 90% statement coverage; the metric was not used as a gate. A 10,000-evaluation smoke test completed in 0.640 seconds (about 15,624 evaluations/second) after moving spec hashing to parse time.

## Semantic audit

**PASS.** All nine manual cases matched. The first implementation test cycle exposed four issues: rule-order loss during canonicalization, a finite-decimal slope expectation mismatch, an underpowered negative-control penalty, and repeated hashing overhead. All were corrected with regression coverage. A later audit found participation read the wrong bound key; that defect was corrected and tested.

## Known limitations

No independent evaluator, published JSON Schema, rational division, statutory rounding modes, multiple periods/agents, aggregates, stochasticity, equilibrium, solver translation, or empirical calibration. Property enumeration is explicit and Cartesian. Logical paths, not YAML line numbers, identify errors. Declarative provenance classes are stored but sources are not yet machine-validated.

## Hostile-review response

The core is more than arbitrary YAML because it has a closed AST, typed economic objects, unit checking, explicit state/action distinctions, and no user code execution. The hostile review correctly notes that internal consistency is not independent semantic validation; this restriction is carried into M2 authorization.

## M1 verdict

**PASS WITH LIMITATIONS.** All twelve exit conditions are met within the stated subset; limitations materially restrict downstream claims but do not block bounded M2 search.

## M2 authorization

M2 may search only one-agent, one-period, deterministic IncentiveSpec v0.1 models using finite Decimal values, bounded explicit action controls, simultaneous transitions, the supported AST, and direct money costs. Every candidate must replay through this evaluator. M2 may add boundary enumeration and property-based candidate generation, but not multi-agent/equilibrium reasoning, dynamics, automated repair, historical claims, adapters, arbitrary code, or formal-verification language.

