# Behavioral Scenarios

- **B0 full optimization:** evaluates every registered candidate and adopts the maximum strictly positive adjusted gain.
- **B1 limited search:** evaluates the first three candidates in deterministic order and adopts the maximum strictly positive adjusted gain.
- **B2 satisficing:** evaluates every candidate but adopts only if the maximum gain is both positive and at least 100.

Adjusted gain equals M1 utility gain minus the extra base action cost implied by the member's cost multiplier, minus fixed friction. B2 records a profitable opportunity even when it is not adopted, keeping opportunity prevalence separate from behavioral response.

These are sensitivity scenarios, not measured behavioral models. Candidate order is part of B1's assumption and is deliberately exposed in the manifest.
