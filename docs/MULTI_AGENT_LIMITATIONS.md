# Multi-Agent Limitations

- Games are synthetic, deterministic, simultaneous, complete-information, and finite.
- Pure strategies only are supported; absence of a pure equilibrium is not absence of equilibrium in mixed strategies.
- Mechanism-specific joint evaluators are trusted code and are not generated from IncentiveSpec v0.1.
- Exact enumeration is exponential in the number of players and actions; the measured M5 boundary stops at 12 binary players and 4,096 profiles.
- Best-response dynamics depend on update schedule, player order, and stay-on-tie policy.
- Basins are not empirical probabilities and convergence is not predicted behavior.
- No coalitions, side payments, learning, incomplete information, endogenous types, continuous actions, stochasticity, or intertemporal state are modeled.
- Game hashes bind declared data but not evaluator source independently of Git identity.
- M3 does not formally verify Nash equilibria or multi-agent aggregation.
- Designer outcomes are separate accounting quantities, not a welfare ordering.
- Interaction findings say only what follows from supplied payoffs and actions; model misspecification remains the primary risk.
