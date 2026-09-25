# Current Limitations

- Search is one-agent, one-period, deterministic, and finite-domain.
- Boundary extraction handles simple one-dimensional attribute-versus-constant/parameter comparisons only.
- Action-boundary algebra recognizes `x' = x - control`; other transitions fall back to generic candidates.
- Property generation is a small seeded strategy, not a mature coverage-guided engine.
- Exhaustive ground truth is feasible only for toy domains.
- Finding equivalence is structural and can merge economically distinct causes sharing one action/boundary.
- Action interpretation is supplied by experiment metadata; it is not inferred reliably from M1 specs.
- Designer-loss direction is based on outcome naming conventions and may be absent; it is not a welfare model.
- No empirical behavior, probability of exploitation, real-world legality, equilibrium, formal verification, or repair claim is supported.
- The synthetic suite was authored by the same project and is not an external benchmark.

