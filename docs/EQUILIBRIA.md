# Pure-Strategy Equilibria

For every supplied finite game, M5 enumerates every joint action. A profile is a pure-strategy Nash equilibrium exactly when no player has a strictly profitable unilateral deviation. Comparisons use exact Decimal values.

The result contains all equilibria; it never returns only the first. Tied maximal actions all belong to the best-response correspondence. A candidate that is not equilibrium carries the first deterministic profitable-deviation witness, including player, actions, and both payoffs.

`PURE_NASH` establishes mutual best response only in the declared finite action space. It is not policy success, equilibrium uniqueness, a behavioral prediction, or evidence that omitted actions are unprofitable. `NONE_PURE` is reported honestly; M5 does not implement mixed equilibria.

Equilibrium replay recomputes the joint outcome and exhaustively checks every unilateral deviation. The finite enumeration is complete for the supplied action sets, but its profile count grows as the product of action counts—`2^N` for N binary players.
