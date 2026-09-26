# M5 Manual Derivation Correction

Recorded after the first engine-versus-golden validation run and before broader M5 experiments.

The precommitted payoff matrix was correct, and exact enumeration returned the precommitted equilibrium set `{(HONEST,HONEST), (MANIPULATE,MANIPULATE)}`. Two statements in the prose derivation were wrong:

1. At `(HONEST,MANIPULATE)`, both players have profitable deviations. A can change `HONEST -> MANIPULATE`, increasing payoff `10 -> 12`; B can change `MANIPULATE -> HONEST`, increasing `8 -> 10`. The original text named only B's deviation.
2. Against a manipulating opponent, the focal payoff difference is `12-10=2`, not `12-8=4`. Therefore the complementarity increment is `2-(-2)=4`, not 6.

The error came from using the opponent's payoff in the focal player's honest-action comparison. No fixture parameter, payoff cell, or expected equilibrium was changed. Tests retain constants derived directly from the frozen payoff matrix.
