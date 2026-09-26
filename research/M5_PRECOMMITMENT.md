# M5 Precommitment

Frozen before implementation of the finite-game engine: 2026-09-26.

## Central question

Can exact finite-game analysis identify an incentive failure that is absent when an agent is evaluated against a neutral opponent action, while returning every pure-strategy Nash equilibrium without adding an equilibrium-selection claim?

## First validation fixture

The frozen fixture is `aggregate_threshold_claim`, a two-player synthetic matching-claim program. Players are `A` and `B`. Each simultaneously chooses `HONEST` or `MANIPULATE`. Both have complete information about types, actions, timing, mechanism, and payoffs. No player observes the other's contemporaneous choice.

Each player begins with an endowment of 10. `MANIPULATE` costs 2. If and only if both players manipulate, the aggregate claim threshold of two is met and each manipulator receives a payout of 4. Honest players receive no payout. Payoffs are realized after the joint action:

`U_i = 10 - 2 * I(a_i = MANIPULATE) + 4 * I(a_i = MANIPULATE and claim_count >= 2)`.

Designer outcomes are `payout_total`, equal to total program payout, and `manipulation_count`. No welfare ranking is assigned.

## Hand-derived predictions

The expected matrix, with row player A first, is:

| A / B | HONEST | MANIPULATE |
|---|---:|---:|
| HONEST | (10, 10) | (10, 8) |
| MANIPULATE | (8, 10) | (12, 12) |

Best-response correspondences are:

- `BR_A(B=HONEST) = {HONEST}` and symmetrically for B;
- `BR_A(B=MANIPULATE) = {MANIPULATE}` and symmetrically for B.

Expected pure Nash equilibria are exactly `(HONEST, HONEST)` and `(MANIPULATE, MANIPULATE)`.

## Interaction-dependent vulnerability

The neutral/default opponent action is `HONEST`. Against it, manipulation changes utility from 10 to 8 and is not profitable. Against a manipulating opponent, manipulation changes utility from 8 to 12 and is profitable. The intended finding is therefore an aggregate-threshold strategic-complementarity cascade, provisionally classified as `IF-021`, not a prediction that real agents coordinate.

## Equilibrium reporting and selection

Exact enumeration must return every pure equilibrium in the declared finite action space. The engine must not select one as the outcome. Any best-response dynamic is a separately declared selection experiment and must independently replay its terminal equilibrium or report a cycle.

## Success conditions

1. The engine reproduces all four payoff cells exactly with Decimal arithmetic.
2. It reproduces the complete best-response correspondences and exactly the two predicted equilibria.
3. Every equilibrium replays by exhaustive unilateral-deviation checking.
4. The isolated baseline records no profitable manipulation, while the interactive analysis records manipulation as a best response to manipulation.
5. Ties, multiple equilibria, non-equilibrium witnesses, and cycles are represented explicitly.

## Failure conditions

Stop broad M5 evaluation if the frozen payoff matrix or equilibrium set disagrees with the engine. Do not revise this file to match engine output. Any error in the derivation must be recorded and corrected in a separate commit.

## Scope exclusions

This precommitment does not authorize mixed strategies, Bayesian games, sequential games, coalitions, large-N simulation, empirical behavior, equilibrium prediction, solver-backed Nash claims, or M6 repair.
