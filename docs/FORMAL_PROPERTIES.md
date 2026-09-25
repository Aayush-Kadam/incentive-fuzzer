# Formal Properties

## Implemented M3 property

### No profitable deviation

For declared state domain \(D\), action controls \(A\), feasibility \(F\), deterministic transition \(T\), and utility \(U\), the property is:

\[
\forall s\in D, a\in A:\ F(s,a)\Rightarrow U(T(s,a),a)\le U(s,0).
\]

The solver checks its negation:

\[
\exists s,a:\ s\in D\land a\in A\land F(s,a)\land U(T(s,a),a)>U(s,0).
\]

SAT becomes `FORMALLY_VIOLATED` only after exact M1 replay. UNSAT becomes `FORMALLY_SATISFIED_WITHIN_DOMAIN` for this property, domain, spec hash, and formal fragment.

M1's named downward-manipulation and misreporting properties map to this encoding only when the caller selects the corresponding action and exact domain. This mapping is explicit, not inferred from labels.

## Deferred property encodings

Budget bound, resource monotonicity, maximum local resource drop, and participation retain executable M1 enumeration but do not yet have public M3 encoders. They return no formal result through M3. This narrower-than-requested coverage is a principal reason for the `PASS WITH LIMITATIONS` verdict.

