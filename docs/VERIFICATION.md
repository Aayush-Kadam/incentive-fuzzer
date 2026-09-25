# Solver-Backed Verification

`FormalVerifier` builds an exact Z3 representation from the typed IncentiveSpec AST. It supports symbolic profitable-deviation queries and fixed-input evaluation for differential testing.

Formal statuses are `FORMALLY_VIOLATED`, `FORMALLY_SATISFIED_WITHIN_DOMAIN`, `UNKNOWN`, `TIMEOUT`, `UNSUPPORTED_FRAGMENT`, `INVALID_SPEC`, `WITNESS_REPLAY_FAILED`, and `BACKEND_DISAGREEMENT`.

A SAT model is decoded only when all values have finite Decimal representations, then replayed through M1. Failure to reproduce state, outputs, utility, and profitability is a backend disagreement, never a finding. UNSAT language is always scoped to the encoded property and domain.

Solver configuration is Z3 4.15.3, timeout 5,000 ms, random seed zero. Results bind the solver version, spec hash, property, action, and domain hash. No human-checkable proof certificate is retained.

