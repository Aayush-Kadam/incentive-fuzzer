# M4 Report

## Objective

Test whether M1 counterexamples survive transparent heterogeneity in states, manipulation frictions, and bounded behavioral response, while retaining individual traceability and M3's narrow formal boundary.

## Design and implementation

The experiment was frozen before implementation in `M4_PRECOMMITMENT.md`. The new population layer is immutable and deterministic. It normalizes arbitrary positive weights and delegates every individual outcome to M1. B0 fully enumerates registered actions; B1 inspects the first three deterministic candidates; B2 observes all candidates but requires a gain of 100 to respond. All headline grids are synthetic.

## Main results

Under B0, profitable shares were 0.515625 for the scholarship grid, 0 for the linear phase-out, 0.190476 for stacked programs, 0.4 for procurement, and 0 for honest reporting. The largest adjusted gains were respectively 99,999; 0; 11; 18; and 0. Thus the hard scholarship cliff is robust over many—but not all—registered friction cells, while the linear phase-out and honest-reporting control remain negative controls in the tested domains.

B1 reduced profitable share to 0.09375 for scholarship, 0.107143 for stacked programs, and 0.145455 for procurement. Signed B1-minus-B0 errors are therefore -0.421875, -0.083333, and -0.254545. The result is expected from the registered action ordering: three candidates often cannot reach the discontinuity. B2 left profitable-opportunity shares unchanged but suppressed all responses for the low-gain stacked and procurement fixtures; scholarship gains remained above its hurdle in the profitable cells.

The weighted scholarship population's exact profitable and response share was 0.9. Seeded estimates were 0.92 at N=100, 0.908 at N=1,000, and 0.9044 at N=5,000. These demonstrate reproducibility and numerical convergence only, not empirical uncertainty.

The reserved incomes 500006–500010 all produced the analytically expected minimum crossing action (income minus 499999), with gains declining from 99,993 to 99,989. This is a small implementation holdout, not out-of-sample policy evidence.

## Designer outcomes and distributional interpretation

Designer-outcome changes and action shares are preserved in individual and aggregate artifacts. Where a response crosses a scholarship cliff, fiscal cost increases; where B2 declines a low-gain action, the realized designer change is zero despite a recorded opportunity. These quantities are accounting outputs, not social welfare.

## Formal spot checks

M3 is rerun on a scholarship boundary domain and the honest-reporting negative control. It validates the unchanged individual semantics: scholarship is formally violated with a replayed witness and honest reporting is formally satisfied within its declared domain. Cost overlays and population aggregates are not formally verified.

## Verdict

**PASS WITH LIMITATIONS.** M4 delivers deterministic heterogeneous-type evaluation, behavioral sensitivities, robustness envelopes, exact weighted aggregation, reproducible sampling, individual traceability, and scoped formal spot checks. It does not establish behavioral realism, external validity, equilibrium effects, or population-level formal guarantees.

## M5 authorization

M5 may study interaction or repair only if it preserves the M1/M3 semantic boundary, precommits new claims and domains, and does not relabel synthetic population assumptions as empirical calibration.
