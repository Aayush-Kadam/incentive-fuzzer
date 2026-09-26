# Best-Response Dynamics

Dynamics are selection experiments, not equilibrium proofs or forecasts. Every terminal profile is independently checked for pure Nash status.

- Synchronous mode computes every player's best response to the same current profile and updates all players together.
- Asynchronous deterministic mode updates players in declared order, with later players observing earlier updates in the same round.
- If the current action is tied for best, the player stays. Otherwise the first action in the declared action order is chosen. This is an explicit dynamic policy, not part of equilibrium discovery.

Repeated profiles trigger `CYCLE_DETECTED`; reaching the step cap triggers `MAX_STEPS`. Basin counts enumerate all initial profiles under one declared dynamic. They are counts, not probabilities.

For the flagship game, synchronous updating leaves both equilibria fixed but makes both off-diagonal initial profiles cycle. Asynchronous A-then-B updating sends two initial profiles to each equilibrium. This demonstrates selection sensitivity without selecting a canonical outcome.
