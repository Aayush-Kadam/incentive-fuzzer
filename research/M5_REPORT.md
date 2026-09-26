# M5 Report

## Objective

Determine whether exact finite-game analysis can expose incentive failures caused by strategic interdependence and report multiple equilibrium outcomes without claiming equilibrium selection or empirical behavior.

## Authorized scope

Deterministic, simultaneous, complete-information finite games with exact Decimal payoffs, small action spaces, pure-strategy Nash equilibrium, and explicitly declared best-response dynamics. No mixed, Bayesian, sequential, coalition, empirical, or large-scale claims are authorized.

## Precommitted game

`aggregate_threshold_claim` has two players choosing `HONEST` or `MANIPULATE`. Each begins with 10, manipulation costs 2, and each manipulator receives 4 only when both manipulate. The fixture, matrix, information, timing, equilibrium concept, and expected equilibrium set were committed before engine implementation.

## Manual derivation

The frozen payoff matrix is `(H,H)=(10,10)`, `(H,M)=(10,8)`, `(M,H)=(8,10)`, and `(M,M)=(12,12)`. The predicted pure equilibria were `(H,H)` and `(M,M)`. The first validation run found a prose error: the focal honest payoff against manipulation had been confused with the opponent's payoff. The correct complementarity increment is 4, not 6. The matrix and equilibrium prediction were correct; the correction was recorded separately before broader work.

## Multi-agent architecture

M5 adds an external `Game` wrapper rather than changing IncentiveSpec v0.1. Typed players carry local state and finite actions. A joint evaluator computes aggregate state, player-specific exact payoffs, and designer outcomes. Generic logic then computes best-response correspondences, verifies profiles, enumerates equilibria, replays results, runs declared dynamics, and enumerates basins.

## Timing and information

All M5 research games are simultaneous and complete information. Players know types, actions, mechanism, and payoffs but do not observe contemporaneous choices before acting.

## Payoff semantics

Payoffs and parameters use exact Decimal arithmetic. Initial games avoid division and rounding ambiguity. Local state and aggregate variables are separate. Designer outcomes are not included in private payoff unless the mechanism evaluator explicitly does so.

## Best-response implementation

For each fixed opponent profile, every player action is evaluated. Every exactly maximal action is returned; ties are never silently broken. Dynamics use a separately declared stay-on-tie and action-order policy.

## Pure-Nash enumeration

Every joint action is enumerated and every unilateral deviation is checked. A non-equilibrium result contains a profitable-deviation witness. This procedure is complete only for the supplied finite pure-action space.

## Validation results

The engine reproduced all four hand-derived payoff cells and exactly the two precommitted equilibria. Every equilibrium replay passed. Textbook tests reproduced one Prisoner's Dilemma equilibrium, two coordination equilibria, two anti-coordination equilibria, and zero pure equilibria for Matching Pennies. Exact tie tests returned both best responses and all four equilibria in the all-tied game. The final suite contains 170 passing tests (35 added in M5) with 91% total statement coverage; the game module has 92% coverage and fixture module 100%.

## Multiple equilibria

The flagship returns both `(HONEST,HONEST)` and `(MANIPULATE,MANIPULATE)`. At the honest equilibrium program payout is 0 and manipulation count is 0; at the manipulation equilibrium payout is 8 and manipulation count is 2. M5 reports both and does not select one.

## Strategic complements/substitutes

For the flagship, `Delta U(0)=-2` and `Delta U(1)=+2`; the complementarity increment is +4. The scarcity-capture contrast has manipulation gain +5 against honesty and -1 against manipulation, yielding the two asymmetric equilibria `(M,H)` and `(H,M)`.

## Interaction-dependent vulnerabilities

The neutral isolated baseline finds no profitable manipulation: gain is -2. Interactive analysis finds manipulation is the unique best response to manipulation: gain is +2. Thus a high-manipulation equilibrium exists only because the aggregate threshold changes incentives. This supports the provisional `IF-021 Strategic Complementarity Cascade` classification in this synthetic model.

## M4 comparison

An M4-style independent response calculation holding the rival at the neutral honest action predicts no manipulator. M5 identifies both zero-manipulation and two-manipulation equilibria. The independent baseline therefore omits one self-consistent strategic outcome; M5 does not claim which equilibrium occurs.

## Best-response dynamics

Under synchronous updates, both equilibria are fixed and the two off-diagonal profiles enter a two-state cycle. Under asynchronous deterministic A-then-B updates, all four initial profiles converge and every terminal state independently verifies as Nash.

## Basin analysis

Synchronous basin counts are one initial profile at each equilibrium and two cycles. Asynchronous counts are two initial profiles at `(H,H)` and two at `(M,M)`, with no cycles. These are counts under explicit update rules, not probabilities.

## Parameter sensitivity

A 56-cell sweep crosses thresholds `{1,2}`, costs `1..4`, and bonuses `0..6`. It records honest-only, manipulation-only, multiple-equilibrium, and tie-dependent `OTHER` regimes. For threshold two, bonus below cost yields honest-only; bonus at or above cost admits both honest and manipulation equilibria. Threshold one can produce manipulation-only behavior when bonus exceeds cost.

## Performance/scaling

Exact enumeration was measured for two through twelve binary players. In the frozen artifact run, joint profiles rose from 4 to 4,096 and runtime from about 0.0006 to 0.716 seconds. M5 therefore declares exact small finite games—not broad scalable equilibrium solving—as its engineering boundary.

## Limitations

All games and parameters are synthetic and self-authored. Joint evaluators are trusted Python rather than a closed AST. Pure equilibria omit mixed strategies. Dynamics are schedule-dependent assumptions. No external calibration, behavioral validation, coalition behavior, learning, formal multi-agent proof, or real-world policy evidence exists.

## Hostile-review response

The strongest criticism survives: exact algorithms on deliberately constructed toy games demonstrate semantic capability, not economic external validity. The explicit safe control, substitution case, zero-pure textbook case, correction record, raw artifacts, and selection separation make the evidence auditable but do not make it empirical.

## M5 verdict

**PASS WITH LIMITATIONS.** Strategic interaction materially changes the modeled vulnerability set, and the exact finite-game machinery passes hand-derived and textbook validation. Generality, scaling, and behavioral interpretation remain sharply limited.

## M6 authorization

M6 may study counterexample-driven repair only for deterministic bounded mechanisms, and every candidate repair must be regression-tested against M2 single-agent findings, M4 robustness cells, and M5 exact finite-game equilibrium sets and designer outcomes. A repair fails if it removes an isolated exploit but creates a worse declared strategic equilibrium. M6 may not claim automatic optimal policy design, empirical welfare improvement, or equilibrium prediction.
