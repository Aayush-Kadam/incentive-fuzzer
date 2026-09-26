# M5 Hostile Review

## Verdict

**PASS WITH LIMITATIONS.** Exact finite-game machinery is internally credible and interaction changes the modeled incentives, but the scientific evidence remains a small set of hand-authored synthetic games.

## Are these genuine interactions or toy matrices?

The flagship and scarcity games compute payoffs from aggregate claim counts and capacity rather than merely looking up a named policy outcome. They are genuine strategic interactions in the formal sense because each player's payoff depends on the other's action. They remain toy mechanisms whose economics were selected by the project author.

## Were multiple equilibria manufactured?

Yes, the aggregate-threshold parameters were deliberately selected to create coordination structure. That is legitimate for validation but weak evidence of external relevance. The safe control, strategic-substitution game, textbook games, and parameter sweep reduce—but do not eliminate—this concern.

## Does architecture preserve M1?

M1 is unchanged. M5 uses a separate game wrapper and exact Decimal payoffs. This preserves backward compatibility but creates a new trusted boundary: mechanism-specific joint evaluators are ordinary Python code rather than a closed multi-agent AST.

## Are equilibria exact and complete?

For supplied finite pure-action spaces, yes. Every joint profile and unilateral deviation is enumerated with exact Decimal comparison. All equilibria are returned, ties remain correspondences, and replay rechecks deviations. Matching Pennies honestly returns zero pure equilibria. Mixed equilibria are not implemented.

## Is selection being smuggled in?

The exact equilibrium set is separate from dynamics. Synchronous and asynchronous outcomes are labeled by update rule. The flagship's off-diagonal profiles cycle synchronously but converge under asynchronous A-then-B updates, demonstrating rather than hiding selection dependence.

## Is the interaction finding nontrivial?

Within the declared model, yes: isolated manipulation loses 2, but manipulation against a manipulating opponent gains 2, and mutual manipulation is an equilibrium with payout cost 8. Independent analysis would therefore miss a high-manipulation equilibrium. This does not show such a mechanism exists or that agents can coordinate into it.

## Scaling

The implementation supports arbitrary small finite games but uses brute-force enumeration. Runtime rose from roughly 0.0006 seconds at two binary players to 0.716 seconds at twelve in the frozen artifact run, with 4,096 profiles. This is not evidence of industrial equilibrium-solving scale; deviation checks compound the exponential profile growth.

## Strongest surviving criticism

All game forms, payoffs, types, parameters, and dynamics are self-authored and synthetic, and the multi-agent payoff layer is trusted code rather than independently specified semantics. Correct Nash computation cannot rescue a misspecified game. External mechanisms and independent economic review are required before any policy claim.

## Unresolved critical conceptual error

None inside the declared exact finite pure-game scope. The initial manual prose contained a focal-payoff error; it was preserved and corrected separately before broader experiments. The payoff matrix and equilibrium prediction were unchanged.
