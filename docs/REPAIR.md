# Bounded Mechanism Repair

M6 implements deterministic candidate generation and evaluation for bounded mechanisms. A `RepairProblem` declares the parent identity, target finding/property, repairable parameters, finite values, constraints, objectives, and budgets. A `RepairCandidate` binds its parent hash, candidate hash, parameter diff, normalized distance, family, provenance, iteration, and counterexample.

Supported transformations are exact parameter edits, hard-cutoff-to-linear-phase-out conversion, action-cost multiplication, and finite-game parameter edits. Structural conversion recognizes rule shape rather than fixture ID. No arbitrary synthesis, learned proposal, or hidden LLM policy generation occurs.

`RepairEngine` exhausts a supplied candidate tuple subject to candidate and time budgets. A repair passes only when the target has zero residual gain, constraints pass, every applicable regression gate passes, and replay evidence is retained. `NO_FEASIBLE_REPAIR_FOUND` is a valid exact-grid outcome.

The bounded iterative loop records counterexample, candidate, parent, iteration, and stop reason. It stops on a passing regression suite, no target violation, no feasible proposal, repeated candidate, or iteration budget. It is not an unbounded optimizer.
