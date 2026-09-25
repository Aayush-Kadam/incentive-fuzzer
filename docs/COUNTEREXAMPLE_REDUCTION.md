# Counterexample Reduction v1

Reduction enumerates the explicit finite M2 domain through the M1 evaluator and preserves the same finding-equivalence class. It minimizes the lexicographic tuple:

1. action count (one in M2);
2. number of nonzero controls;
3. sum of absolute control magnitudes;
4. baseline distance to the attributed boundary;
5. negative private gain as a tie-breaker.

Every candidate is replayed. A reduction cannot rely on algebraic assumptions. Statuses are `REDUCED`, `ALREADY_MINIMAL_UNDER_OBJECTIVE`, `PARTIALLY_REDUCED`, `REDUCTION_BUDGET_EXHAUSTED`, and `FAILED_REPLAY`; v1 currently returns the first, second, or last of these.

“Minimal” always means minimal under this objective and supplied finite domain. It is not a global mathematical claim.

