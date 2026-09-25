# Decision Log

## 2026-09-25 — Narrow M1 semantics

**Decision:** Begin with bounded deterministic single-actor piecewise-linear semantics plus limited aggregation.  
**Alternatives:** arbitrary Python; full multi-agent dynamics; OpenFisca-only plugin.  
**Evidence:** verification and replay require a shared tractable core; unrestricted code is unsafe and semantically opaque.  
**Reason:** makes interpreter/solver differential testing and hand-derived fixtures feasible.  
**Consequences:** “general framework” remains unearned; adapters and games are later gates.

## 2026-09-25 — Trusted evaluator boundary

**Decision:** Treat search, optimization, LLMs, and solvers as witness generators; replay all findings in one reference evaluator.  
**Alternatives:** trust each backend; make an LLM the orchestrating judge.  
**Evidence:** backends can disagree because of encoding, precision, or semantics.  
**Reason:** creates one auditable evidence boundary.  
**Consequences:** evaluator correctness becomes critical and needs independent fixtures.

## 2026-09-25 — No scalar severity

**Decision:** Preserve a severity vector.  
**Alternatives:** Critical/High/Medium/Low score.  
**Evidence:** private gain, welfare, fiscal impact, robustness, and detection risk are not naturally commensurate.  
**Reason:** avoid false precision.  
**Consequences:** presentation is less simple but more defensible.

## 2026-09-25 — Decimal and ordered rules

**Decision:** Parse numeric source text into `Decimal`; make rule declaration order semantic and preserve it canonically.
**Alternatives:** binary float; scaled integer; rational arithmetic; dependency sorting.
**Evidence:** boundary equality must be exact, while rules may intentionally consume earlier outputs.
**Reason:** Decimal exactly represents currency literals and finite declared rates with minimal dependencies.
**Consequences:** non-terminating slopes require visible finite approximation; rule reordering changes identity and possibly behavior.

## 2026-09-25 — Closed expression AST

**Decision:** Use one-key YAML AST nodes and a small interpreter.
**Alternatives:** parse expression strings; execute Python; adopt a large expression framework.
**Evidence:** user code is unsafe and string grammars add an unnecessary second parser.
**Reason:** closed nodes make units, allowed operations, and future solver translation explicit.
**Consequences:** specifications are verbose and division/rounding are deferred.
