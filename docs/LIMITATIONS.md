# Current Limitations

- Each evaluation remains one-agent, one-period, deterministic, and finite-domain; M4 populations aggregate independent types rather than model interaction.
- Boundary extraction handles simple one-dimensional attribute-versus-constant/parameter comparisons only.
- Action-boundary algebra recognizes `x' = x - control`; other transitions fall back to generic candidates.
- Property generation is a small seeded strategy, not a mature coverage-guided engine.
- Exhaustive ground truth is feasible only for toy domains.
- Finding equivalence is structural and can merge economically distinct causes sharing one action/boundary.
- Action interpretation is supplied by experiment metadata; it is not inferred reliably from M1 specs.
- Designer-loss direction is based on outcome naming conventions and may be absent; it is not a welfare model.
- No empirical behavior, probability of exploitation, real-world legality, equilibrium, formal verification, or repair claim is supported.
- The synthetic suite was authored by the same project and is not an external benchmark.
- M3 shares M1 parsing and schema validation; it independently validates semantic interpretation after parsing, not the parser.
- M3 formally encodes profitable-deviation existence only. Four other M1 property families remain enumeration-only.
- Formal domains need explicit finite values or steps to ensure solver witnesses are valid finite-decimal M1 inputs.
- UNSAT says nothing about omitted actions, misspecified utility, or real-world behavior.
- Population weights and behavioral scenarios are synthetic assumptions, not estimates. Monte Carlo uncertainty excludes model and parameter uncertainty.
- Population summaries are not SMT-verified; M3 spot checks apply only to selected individual domains before M4 cost overlays.
- Fixed-friction grids can only identify tested-grid disappearance; exact thresholds follow the modeled finite candidate set.
