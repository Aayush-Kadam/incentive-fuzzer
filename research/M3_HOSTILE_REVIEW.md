# M3 Hostile Review

## Verdict

**PASS WITH LIMITATIONS.** The backend is independently implemented where it matters, but formal property coverage is narrower than the M1 property catalog.

## Genuine independence

The Z3 translator shares parsed AST types but reimplements numeric conversion, expressions, simultaneous transitions, ordered outputs, costs, utility, and the existential property. It does not call M1 expression evaluation. Shared parsing remains a common-mode risk.

## Exactness and domain

Decimals are exact rationals. Strict inequalities remain strict. Explicit finite domains make benchmark comparisons unambiguous. Step-based domains mix integer-grid constraints with rational terms. The backend deliberately rejects non-finite-decimal witness decoding rather than rounding.

## Meaning of UNSAT

UNSAT supports only “no profitable selected action exists within this encoded domain and assumptions.” It does not establish robustness against omitted behavior. No global safe/robust label is emitted.

## Added value over enumeration

On the current tiny explicit domains, exhaustive enumeration is already possible. Symbolic value is demonstrated mainly by independent semantic triangulation and exact `min`/`max` reasoning, not superior runtime. Larger continuous/step domains were not benchmarked sufficiently to establish scaling advantage.

## Differential strength

Five hundred generated fixed-input cases, all canonical fixtures, and all twelve frozen mechanisms agreed. The generated mechanisms come from the existing suite rather than a rich independent grammar, so coverage is meaningful but not broad.

## Formal-fragment criticism

Only profitable-deviation existence has a public formal property encoder. Budget, participation, monotonicity, and local-drop properties remain deferred. Calling the entire M1 property system formally verified would be false.

## Strongest surviving criticism

Formal correctness is conditional on the supplied economic model and action space. M3 can establish \(P(M,A,D)\); it cannot establish that \(M\), \(A\), or \(D\) captures reality.

