# Interaction Semantics

M5 separates player-local state from joint aggregates. The implemented fixtures expose `claim_count`, threshold status, and capacity while retaining player-specific actions and payoffs.

The flagship aggregate-threshold claim game uses:

`U_i = 10 - 2 I(a_i=M) + 4 I(a_i=M and claim_count>=2)`.

Against an honest opponent, manipulation changes payoff by -2. Against a manipulating opponent, it changes payoff by +2. The difference-in-differences is +4, demonstrating strategic complementarity within this synthetic game.

The scarcity-capture game is a strategic-substitution contrast. A sole manipulator captures a capacity-one prize and gains 5 net; a second manipulator causes collision and loses 1 relative to honesty. Its pure equilibria have exactly one manipulator.

`IF-021 Strategic Complementarity Cascade` is added only for the demonstrated case: an action becomes more attractive as other agents take the same action, creating a harmful high-action equilibrium absent from the neutral isolated baseline. The label describes model structure, not coordination in a real population.
