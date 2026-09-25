# Finding Semantics

A finding is a replayed profitable deviation against an explicitly declared `no_profitable_deviation` search property. It contains the policy hash, baseline, action, result, utilities, designer outcomes, trace, search source, evidence metadata, and transparent severity components.

Private gain alone is not silently called fraud or gaming. `action_kinds` may identify `report_only` or `productive_effort`; absent explicit metadata, reporting classifications are not inferred from a changed field alone.

## Equivalence

Findings are equivalent when they share:

1. property ID;
2. action definition;
3. deterministic IF-CWE classification;
4. boundary attribute, value, and rule, or all have no boundary.

Deduplication retains the greatest private-gain representative. Raw findings remain available, so deduplication cannot erase evidence from the run artifact.

## Classification

- `IF-005` requires explicit `report_only` action interpretation.
- `IF-015` requires one action to change outputs governed by more than one extracted boundary rule.
- `IF-002` is used when a boundary-crossing candidate ends exactly on an inclusive/exclusive boundary and the condition truth actually changes.
- `IF-001` covers an attributable single hard-boundary crossing.
- `IF-003` requires explicit productive-effort interpretation when no harder boundary class applies.
- otherwise the result is `UNCLASSIFIED_PROPERTY_VIOLATION`.

These labels describe model structure, not real-world conduct.

## Severity

M2 stores private gain, violation magnitude, direct action cost, designer loss where direction is named, and distance to boundary. It assigns no opaque score or categorical severity.

