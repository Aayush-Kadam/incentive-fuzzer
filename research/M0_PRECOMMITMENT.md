# M0 Precommitment

Recorded: 2026-09-25, before implementation of the scientific engine.

## Unit of evaluation

The project is not evaluated on whether a threshold cliff can be found. It is evaluated on whether a shared specification and evidence model can support heterogeneous economic rules, economically valid attacks, minimized witnesses, and repair regression better than straightforward composition of existing tools.

## Continue

Continue to M1 only if all conditions hold:

1. No reviewed system already provides the full rule -> strategic attack -> property witness -> economic shrink -> robustness -> repair -> re-test workflow across more than one institutional domain.
2. A precise restricted semantics can separate state, action, observation, cost, enforcement, utility, and designer property.
3. At least three benchmark families require different attack structures: scalar manipulation, policy composition, and entity/transaction restructuring.
4. Findings can carry assumptions, provenance, feasibility, legality, and deterministic replay data.
5. Claims are explicitly narrower than automated mechanism design, policy microsimulation, property-based testing, and general SMT verification.

## Narrow

Narrow to deterministic single-agent, finite-horizon, piecewise-linear rules if arbitrary nonlinear or multi-agent semantics prevent differential verification. Remove “general” from public claims until at least three institution classes share the same intermediate representation without custom solver logic. Treat repair as candidate search, not automatic policy design, until held-out attacks are used.

## Pivot

Pivot to an audit layer for OpenFisca/PolicyEngine or to an economic-property benchmark suite if rule encoding duplicates mature engines but the attack/property corpus remains useful. Pivot to a research benchmark, rather than a product, if domain experts cannot agree on a portable attack ontology or utility semantics.

## Archive

Archive the general framework claim if any of these occur:

- an existing maintained system is found with materially equivalent end-to-end scope;
- vulnerabilities cannot be distinguished reproducibly from intended response without bespoke human judgment in the flagship cases;
- the shared semantics require institution-specific escape hatches for all nontrivial examples;
- solver and runtime semantics cannot be made observationally equivalent on the restricted core;
- the system adds only a thin UI over optimization, property testing, or microsimulation.

## M1 success gate

M1 must deliver a versioned schema and reference evaluator for the scholarship cliff, benefit stack, and procurement/entity-splitting examples; reject unsafe code; state units and time; validate bounds and provenance; and pass hand-derived semantic fixtures. Until then, later milestones remain unearned.

