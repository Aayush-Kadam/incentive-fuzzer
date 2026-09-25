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

## 2026-09-26 — M2

- Froze 12 synthetic mechanisms before implementing/tuning search heuristics at commit `76a1744`.
- Exhaustive evaluation falsified two planted safe labels at state-domain bounds; labels were corrected separately at `1e04c30` rather than suppressing findings.
- A Cartesian scholarship domain allowed inconsistent true/reported baselines and produced a misleading reducer result. Added explicit correlated state records.
- Initial boundary attribution labeled a profitable candidate against a condition whose truth did not change. Required replayed truth change before retaining boundary origin.
- Role `reported` proved insufficient to classify manipulation: real scope/work changes can also update reported values. Added explicit action interpretation metadata and neutral fallback.
- Boundary search achieved full equivalence recall on the frozen suite with 4,812 evaluations; seeded property and grid baselines missed classes.
- The linear phase-out exposes a limitation: current boundary extraction does not identify min/max kinks.
- The minimum scholarship reproducer in the supplied domain is 500,000 -> 499,999 with amount 1, not the illustrative amount 2.

## 2026-09-26 — M3

- Added pinned Z3 4.15.3 after confirming no solver was installed.
- Independently implemented Decimal-to-fraction conversion, AST translation, simultaneous transitions, ordered rules, costs, utility, model decoding, and profitable-deviation negation.
- Rejected symbolic-by-symbolic multiplication explicitly.
- Restricted formal domains to explicit finite values or steps; unrestricted rationals can yield values M1 Decimal cannot represent finitely.
- Fixed-input differential testing produced 500/500 exact agreements with no rejected cases.
- Canonical status agreement was 5/5; frozen benchmark status agreement was 12/12.
- Canonical SAT replay was 3/3; canonical UNSAT/exhaustive agreement was 2/2.
- Z3 independently handled the phase-out min/max structure that M2 boundary extraction does not recognize.
- No M1/M2 semantic defect was discovered. Formal coverage remains limited to profitable-deviation existence.
