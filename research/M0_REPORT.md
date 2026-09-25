# M0 Report: Novelty, Prior Art, Threat Model, and Research Specification

Date: 2026-09-25  
Author / Project Lead: Aayush Kadam

# M0 VERDICT

**PASS WITH LIMITATIONS**

## What was attempted

A hostile scoping review compared the proposal with mechanism design, robust and automated mechanism design, computer-aided verification, strategic classification, tax bunching and enforcement evidence, tax-benefit microsimulation, rules as code, property-based testing, SMT, game solvers, agent-based modeling, robust optimization, and program repair. The review also converted the concept into a threat model, provisional weakness taxonomy, research questions, restricted architecture, benchmarks, and falsifiable continuation criteria.

This was a current web search of authoritative papers and official software documentation, but not a systematic review of subscription databases. That limitation prevents a definitive priority claim.

## What was built

- an evidence-qualified novelty matrix;
- broad, conservative, and minimal claims with attacks;
- a threat model separating intended response, adaptation, manipulation, and ambiguity;
- a 20-class provisional IF-CWE taxonomy;
- 12 synthetic and 12 historically motivated benchmark candidates;
- an architecture using a trusted evaluator and untrusted witness generators;
- a precommitment with continuation, narrowing, pivot, and archive conditions;
- a claim ledger, decision log, research log, and independent hostile review.

## Key findings

### Broad claim — rejected

> Incentive Fuzzer is a general computational framework that automatically discovers and repairs vulnerabilities in economic institutions.

**Attack:** Mechanism design already studies strategic response and design; automated mechanism design computationally constructs mechanisms; robust mechanism design treats uncertainty; strategic classification optimizes against gaming; SMT and computer-aided verification produce countermodels/proofs; property-based tools generate and shrink failures; policy simulators execute rules and now model some behavioral responses; program repair supplies iterative repair patterns. “General” and “automatically repairs” are unsupported without implementation, cross-domain evidence, and held-out repair evaluation.

**Disposition:** Do not use.

### Conservative claim — research hypothesis

> Incentive Fuzzer is an open workflow for specifying economic threat models and properties, generating actor-feasible deviations, replaying and minimizing property violations, testing robustness, and regression-testing candidate repairs across multiple institutional domains.

**Attack:** This may still be an obvious composition of mature tools. A shared schema could collapse under domain-specific utility, equilibrium, legal, and behavioral assumptions. Economic validity may require expert judgment that prevents portable automation.

**Disposition:** Test in M1–M7; not yet a novelty claim.

### Minimal defensible claim — survives M0

> The project will evaluate whether software-testing disciplines—explicit properties, adversarial witness generation, deterministic replay, domain-aware reduction, provenance, and repair regression—can be made into a reproducible benchmarked protocol for economic rules spanning at least tax-benefit, procurement, and commercial incentive examples.

**Attack:** Even this is a research agenda, not a result. The protocol must beat baselines and show that domain-aware reduction and evidence packaging add measurable value.

**Disposition:** Defensible statement of intended contribution.

## Prior-art synthesis

OpenFisca is a mature rules-as-code and static microsimulation engine; its documentation explicitly says the core does not account for elasticity or behavior. PolicyEngine materially narrows that gap: its current model includes user-configurable labor-supply and capital-gains responses. Neither reviewed documentation describes adversarial witness search, domain-aware counterexample reduction, or repair regression, but absence from sampled documentation is not proof of absence.

Hypothesis already finds edge cases and reduces them to simple examples; therefore generic “fuzzing plus shrinking” is not novel. Z3 already supplies satisfiability models for encodable theories; therefore symbolic counterexamples are not novel. Gambit computes equilibria, and Mesa supplies agent-based simulation. The engineering question is whether a shared economic semantics can coordinate these capabilities while preserving assumptions and replay.

Automated mechanism design is the strongest threat to repair claims because it directly computes mechanisms subject to incentive constraints. Strategic classification is the strongest narrow analogue for a designer facing costly feature manipulation. Formal verification of mechanisms directly threatens claims about incentive-property verification. The differentiator, if any, must be cross-institution audit workflow, benchmark coverage, economic witness minimization, evidence provenance, and regression after repair.

## Strongest defensible novelty claim

No positive novelty claim is established at M0. The strongest defensible candidate is: **an open, benchmarked, counterexample-driven audit protocol that unifies explicit economic threat models, executable properties, actor-feasible adversarial search, deterministic witness replay, economic multi-objective reduction, robustness analysis, and held-out repair regression across heterogeneous rule systems.** Novelty attaches, if at all, to the validated integration and benchmark methodology, not its components.

## Biggest prior-art threat

Automated/robust mechanism design plus computer-aided mechanism verification is the biggest intellectual threat; OpenFisca/PolicyEngine plus Hypothesis/Z3 is the biggest engineering “just compose existing tools” threat.

## Research contribution candidate

A formal evidence model and benchmark methodology for counterexample-driven institutional testing, with explicit distinctions among intended response, adaptation, and proxy manipulation; lexicographic economic witness reduction; and differential verification between executable and symbolic semantics.

## Product contribution candidate

A CI-style audit tool that accepts a restricted rule specification, runs threat-model-scoped attacks, and returns replayable traces and scoped assurance statements. It should integrate with mature rule engines rather than replace them.

## Benchmark results

No performance benchmark was run in M0. The benchmark output is a candidate register only. Reporting detection rates now would fabricate evidence.

## What survived hostile review

- The problem framing is useful if property, action feasibility, information, and costs are first-class.
- A reference-evaluator/replay boundary can prevent solver or LLM output from becoming the source of truth.
- Cross-domain benchmark design and domain-aware witness reduction are plausible research gaps.
- A narrow piecewise-linear M1 is testable and falsifiable.

## What failed

- The broad novelty claim failed.
- “Penetration testing for economic institutions” is positioning, not scholarship.
- Generic fuzzing, shrinking, formal counterexamples, strategic behavior, robustness, equilibrium computation, and automated repair each have strong prior art.
- A scalar vulnerability score is unjustified at this stage.

## Tests and experiments

No scientific engine exists, so no software tests or experiments were represented as complete. M0 artifacts were checked for required sections, source URLs, candidate counts, and forbidden universal-safety language.

## Repository state

Branch: `master`  
HEAD: `671c9a7` at initial M0 commit (the final documentation-state commit may differ after handoff metadata updates)  
Working tree: M0 document set only

## Scientific limitations

The literature search is scoped, English-language, and web-accessible. No economist, public administrator, procurement expert, or formal-methods reviewer independently validated the taxonomy or benchmarks. Historical candidates are not encoded and must not be described as demonstrated exploits. No empirical behavior, search superiority, solver equivalence, or repair quality has been established.

## Decision

Proceed to M1: **YES, but only under the narrowed M1 boundary in `ARCHITECTURE_V0.md`.** Do not proceed to M2 until the schema and reference semantics pass independent fixtures for the three flagship examples. M0 does not authorize claims of novelty or readiness.

## Exact reason to continue

The sampled prior art did not reveal one maintained end-to-end system with the complete proposed audit and evidence workflow, and the restricted semantics plus three structurally distinct flagship mechanisms create a falsifiable next step. The reason to continue is to test that integration hypothesis—not because novelty has been proven.
