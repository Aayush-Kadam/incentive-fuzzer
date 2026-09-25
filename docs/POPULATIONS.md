# Population Model

M4 adds finite, independent single-agent populations. An `AgentType` contains a unique ID, non-negative weight, fixed state, manipulation-cost multiplier, fixed friction, optional hurdle, available actions, and per-parameter provenance. Weights need not sum to one; aggregation normalizes by their positive total. Duplicate IDs, negative weights, and zero-total populations fail closed.

Each member is evaluated with the unchanged M1 evaluator. Population aggregation reports weighted profitable and response shares, conditional mean and maximum adjusted gain, action shares, and changes in each designer outcome. Every aggregate remains linked to an `IndividualResult`, population hash, specification hash, and deterministic scenario.

Types are independent. There are no interactions, equilibrium effects, peer effects, learning, or endogenous prices.
