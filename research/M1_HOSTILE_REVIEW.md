# M1 Hostile Review

## Verdict

No critical unresolved semantic flaw was found in the authorized domain, but the core remains deliberately narrow. Recommendation: **PASS WITH LIMITATIONS**.

## Is this YAML around Python functions?

No. Source expressions are allow-listed AST objects, parsed into typed immutable expression nodes, unit-checked, and interpreted without `eval`, imports, callables, or user code. However, the implementation is still a compact single-module interpreter and needs independent reimplementation before semantic portability is demonstrated.

## Are economic concepts explicit?

Institution, parameters/provenance, state attributes, actions, transitions, direct costs, rule outputs, utility, designer outcomes, and properties have separate types. Latent and reported state are distinguished by separate attributes and roles. The role string is validated only syntactically, so later versions need a closed role vocabulary.

## Are units and boundaries meaningful?

Money, scalar, rate, count, and Boolean units prevent obvious invalid addition/comparison. This is not dimensional algebra. Exact Decimal comparison correctly distinguishes `<` from `<=`. Non-terminating slopes must be approximated explicitly because v0.1 has no rational/division node; the phase-out fixture preserves that approximation in the spec and test.

## Can independent implementations reproduce semantics?

The normative order and numeric rules are documented, and nine manually derived cases agree with the evaluator. No second implementation exists, so reproducibility across implementations is not yet empirically established. M3 differential testing remains necessary.

## Are properties executable?

Six property kinds return structured statuses and concrete bounded-domain witnesses. They are enumeration assertions, not general incentive-compatibility checks or proofs. Explicit Cartesian domains can include economically inconsistent state combinations unless fixture authors constrain them manually.

## Could Z3 preserve meaning?

The AST is compatible with a bounded linear-arithmetic translation, but finite Decimal constants must be translated as rationals, rule order preserved, and simultaneous transitions encoded explicitly. No symbolic backend exists in M1.

## Did M2 leak into M1?

No search heuristic, optimizer, generator, or mutation engine exists. The property harness only consumes explicit finite lists and is a semantic oracle.

## Mechanisms still excluded

Stochastic rules, endogenous audit probabilities, temporal dynamics, multiple actors, entity aggregation, transaction splitting as multiple records, nonlinear utility, division/rational literals, rounding statutes, currencies/conversion, missing values, endogenous prices, and equilibria are unsupported.

## Most important surviving criticism

The reference evaluator is internally consistent but not independently validated. Tests and fixtures can share author assumptions with the implementation. M2 must stay within the exact documented subset, and M3 must build a separately implemented differential backend before formal-verification language is used.

