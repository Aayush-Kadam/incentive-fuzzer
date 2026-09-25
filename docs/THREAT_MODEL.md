# Threat Model v0

## Scope

An institution is a versioned rule evaluated over economic state. An attack is a feasible deviation from a baseline action under a stated information and enforcement model. A vulnerability exists only relative to an explicit property or designer loss. Private gain alone is insufficient.

## Actors

Supported threat classes are: an individual beneficiary or taxpayer; a household with joint choices; a firm or supplier; a platform participant; an intermediary; and a coordinated coalition. M1 begins with one decision-maker. Household, firm, and coalition models are separate actor types rather than aliases for a person.

The designer, administrator, auditor, and rule author are trusted to execute the encoded rule but may have incomplete information or misspecified objectives. Corruption of the evaluator and arbitrary code execution are software-security threats outside the initial economic model.

## Manipulable variables

Each variable must declare an action channel. Candidate channels include real effort or production; labor/income choice; timing; location; participation; report or declaration; transaction size/count; entity ownership/count; household membership; bids; and allocation-relevant choices. A variable is not manipulable merely because it is an input.

Actions have domains, preconditions, transition effects, costs, reversibility, observability, legality class, and applicable periods. Reported and true values are distinct state fields where misreporting is possible.

## Immutable or exogenous variables

Age already realized, historical facts, assigned identifiers, random audit draws after action, market prices treated as exogenous, and other agents' types are immutable unless a model explicitly defines a causal action channel. Protected attributes are never silently treated as manipulable. Bounds are part of the model, not search conveniences.

## Information models

- **Full rule:** actor knows formulas, thresholds, audit probabilities, and own type.
- **Public rule, uncertain enforcement:** actor knows the mechanism but holds a declared belief set over enforcement.
- **Partial/noisy rule:** actor observes a specified abstraction or noisy signal.
- **Strategic interaction:** knowledge of other types and history is declared separately.

Search must not use information unavailable to the modeled actor. A tool may use omniscient search to discover a failure, but the witness is behaviorally admissible only if it can be mapped to the actor's information.

## Costs and enforcement

Utility accounts separately for opportunity cost, transaction cost, delay, legal/compliance cost, coordination cost, cognitive/search cost, audit probability, detection conditional on audit, penalty, and risk attitude. Costs use provenance labels E (estimated), L (literature-calibrated), S (scenario), or A (adversarial bound).

Illegal evasion and legal avoidance are distinct findings. Expected-penalty models must expose probability and penalty assumptions. A zero-cost attack is an adversarial upper bound, not a behavioral prediction.

## Response classification

- **Intended response:** real behavior changes in the designer-valued direction.
- **Adaptation:** legitimate adjustment anticipated by the mechanism.
- **Manipulation:** private benefit arises mainly through measurement, reporting, timing, classification, structure, or other divergence from the stated objective.
- **Ambiguous:** classification depends on a normative mapping not supplied by the model.

Every witness records this classification and its justification. The engine may calculate objective deltas; it must not infer normative intent from prose.

## Properties and loss

Properties are executable predicates over baseline, deviation, and outcomes. Examples include no profitable misreport, local monotonicity, budget feasibility, maximum cliff, no splitting arbitrage, participation, and coalition resistance. Severity is a vector: private gain, welfare loss, fiscal loss, affected share, robustness, cost, complexity, coalition size, and detection risk.

## Evidence boundary

A valid finding includes the policy version/hash, baseline state, action sequence, resulting state, rule trace, utility calculation, violated property, assumptions, provenance, legality, feasibility checks, seed/solver version, and replay instructions. A solver model is a witness candidate until replayed by the reference evaluator.

“No violation found” means only no witness in domain D under assumptions A using search configuration C. Formal verification is claimed only for the encoded property and theory fragment.

## Abuse and safety

The project can reveal evasion strategies. Public examples should prefer synthetic or already documented mechanisms. Reports distinguish defensive remediation from operational instructions and avoid sensitive personal data. IncentiveSpec never executes arbitrary user Python.

