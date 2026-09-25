# Research Log

## 2026-09-25 — M0

- Hypothesis: novelty might lie in automated strategic attack generation for policy rules.
- Contrary evidence: strategic classification, automated mechanism design, formal mechanism verification, property-based testing, and current behavioral microsimulation each cover substantial pieces.
- Narrowed hypothesis: the contribution may be a benchmarked cross-domain audit protocol and evidence model.
- Unexpected result: PolicyEngine's current documentation already includes configurable behavioral responses, weakening any static-microsimulation contrast.
- Methodological concern: absence of an end-to-end tool was not established systematically.
- Deferred: formal systematic review, expert taxonomy validation, benchmark encoding, evaluator implementation, and all performance claims.
- Negative result preserved: broad novelty and automatic-repair claims failed M0 review.

## 2026-09-25 — M1

- Rejected expression strings and arbitrary Python in favor of a closed YAML AST.
- Chose Decimal over binary float; rejected rational arithmetic for v0.1 dependency simplicity. Non-terminating phase-out slopes remain explicit finite approximations.
- Semantic ambiguity found: canonical key sorting changed ordered rule dependencies. Canonicalization now preserves rule order.
- Negative-control error found: a penalty rate of two did not deter a one-unit report change that unlocked a five-unit benefit. Rate raised to six; the failed expectation was not hidden.
- Performance anomaly found: hashing canonical YAML on each evaluation made the smoke test unacceptably slow. Immutable identity is now computed at parse time.
- Property bug found during audit: participation read `maximum` rather than `minimum`. Fixed with a regression test.
- Limitation: internal fixtures and evaluator share authorship; independent semantic reproduction remains untested.

