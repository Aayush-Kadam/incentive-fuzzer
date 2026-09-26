# Finite Games

M5 adds a wrapper for exact, complete-information, simultaneous finite games without changing IncentiveSpec v0.1. A `Game` contains typed players, finite action sets, local player state, a named mechanism, exact parameters, timing, information, and a deterministic evaluator. A `JointAction` is evaluated into exact Decimal player payoffs, aggregate variables, and separate designer outcomes.

The wrapper is deliberately small. Mechanism-specific evaluators implement interaction semantics; the equilibrium engine is generic over their finite payoff mapping. Game identity binds the mechanism name, parameters, player types and states, action sets, timing, information, neutral action, and equilibrium concept. Evaluator source code is not itself serialized, so artifact reproducibility also depends on the recorded Git commit.

Supported M5 aggregation patterns are exact counts, finite thresholds, and deterministic capacity allocation. Division, stochastic allocation, incomplete information, sequential moves, continuous actions, coalitions, and mixed strategies are outside the implemented scope.

M1 remains the trusted oracle for IncentiveSpec v0.1 individual mechanisms. M5 does not silently reinterpret v0.1 or claim that arbitrary M1 rules are automatically games.
