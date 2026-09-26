# Multi-Layer Repair Regression

The standard M6 gate is:

```text
candidate and original-witness replay
-> fresh M2 exhaustive and combined search
-> M3 exact-rational profitable-deviation check
-> M4 frozen-population evaluation
-> M5 exact equilibrium-set comparison
-> mutation stress
-> constraint and Pareto classification
```

Layers that do not apply are recorded as `NOT_APPLICABLE`; they are never silently counted as passes. `REPAIR_PASS` requires target elimination, satisfied constraints, and no failed applicable check.

M2 fresh search includes boundary-aligned states so moving a threshold does not merely move an exploit outside the original witness location. M3 language remains domain-scoped. M4 uses frozen states, frictions, multipliers, and B0 semantics. M5 returns complete pure-equilibrium sets for the supplied game and rejects newly introduced target equilibria.

`REPAIR_INDUCED_VULNERABILITY` takes precedence when a candidate fixes the local target but creates a declared failure in another layer. Replaying the old witness alone is insufficient; fresh attack is mandatory.
