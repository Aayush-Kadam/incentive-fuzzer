# M5 Manual Fixture Derivation

This derivation was written before the equilibrium engine. It is the independent golden oracle for `aggregate_threshold_claim`.

Let `H` denote `HONEST`, `M` denote `MANIPULATE`, and let `k` be the total number of manipulators. For player `i`:

`U_i = 10 - 2 I(a_i=M) + 4 I(a_i=M and k>=2)`.

## Payoff cells

1. `(H,H)`: `k=0`. Neither player pays a cost or receives a payout. Payoffs are `(10,10)`. Designer outcomes are payout 0 and manipulation count 0.
2. `(H,M)`: `k=1`. A remains at 10. B pays 2 and receives no payout, so B receives 8. Payoffs are `(10,8)`. Designer outcomes are payout 0 and manipulation count 1.
3. `(M,H)`: symmetric to the previous cell. Payoffs are `(8,10)`. Designer outcomes are payout 0 and manipulation count 1.
4. `(M,M)`: `k=2`. Each pays 2 and receives 4, so each receives `10-2+4=12`. Payoffs are `(12,12)`. Designer outcomes are payout 8 and manipulation count 2.

## Best responses

Against `H`, a player obtains 10 from `H` and 8 from `M`; the unique best response is `H`.

Against `M`, a player obtains 8 from `H` and 12 from `M`; the unique best response is `M`.

Therefore the pure-strategy Nash equilibrium set is exactly `{(H,H), (M,M)}`. The off-diagonal profiles are not equilibria. At `(H,M)`, A can switch to `M` and increase from 10 to 12, while B can switch to `H` and increase from 8 to 10; the symmetric statement holds at `(M,H)`.

## Strategic-complementarity calculation

For the focal player, define `Delta U(k)=U(M|k)-U(H|k)`, where `k` is the number of other manipulators.

| Other manipulators `k` | `Delta U(k)` | Best response |
|---:|---:|---|
| 0 | -2 | HONEST |
| 1 | +2 | MANIPULATE |

The complementarity increment is `Delta U(1)-Delta U(0)=4>0`. This statement is restricted to the declared synthetic game.

## Correction record

The initially committed prose incorrectly assigned the honest action a payoff of 8 when the opponent manipulated, producing `Delta U(1)=4` and an increment of 6. The frozen payoff matrix itself correctly showed `(H,M)=(10,8)`, and the predicted equilibrium set was unaffected. The first golden-test run exposed the inconsistency before broader M5 work. See `M5_DERIVATION_CORRECTION.md`.
