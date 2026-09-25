# M4 Report

## Objective

Test whether M1 counterexamples survive transparent heterogeneity in states, manipulation frictions, and bounded behavioral response, while retaining individual traceability and M3's narrow formal boundary.

## Authorized scope

Independent one-period agents, bounded deterministic actions, synthetic weighted types, deterministic grids, and reproducible sampling only. No interaction, equilibrium, causal inference, or real-world forecast is authorized.

## Population representation

Finite immutable types carry states, normalized weights, costs, hurdles, action availability, and provenance. Aggregates link to individual M1 results and deterministic hashes.

## Parameter provenance

States and weights are S; behavioral limits, friction grids, and multipliers are A. No M4 input is empirical or literature-calibrated.

## Behavioral scenarios

B0 exhausts candidates, B1 evaluates three ordered candidates, and B2 combines exhaustive discovery with a 100-unit hurdle.

## Manipulation-cost model

Adjusted gain subtracts `(multiplier - 1) × M1 action cost + fixed friction` from M1 utility gain.

## Deterministic robustness grids

Five fixture-specific grids preserve every cell and individual result. They are the finite-grid oracle.

## Weighted population design

Five scholarship types use precommitted weights 0.1, 0.2, 0.3, 0.2, and 0.2.

## Monte Carlo design

Local RNG seed 20260926 samples N=100, 1,000, and 5,000 from those exact types.

## Search method

B0/B2 exhaust declared values. B1 is bounded ordered search, not an optimizer.

## M3 spot-check protocol

M3 checks the scholarship boundary and honest-control domain; it does not encode M4 aggregates or cost overlays.

## Design and implementation

The experiment was frozen before implementation in `M4_PRECOMMITMENT.md`. The new population layer is immutable and deterministic. It normalizes arbitrary positive weights and delegates every individual outcome to M1. B0 fully enumerates registered actions; B1 inspects the first three deterministic candidates; B2 observes all candidates but requires a gain of 100 to respond. All headline grids are synthetic.

## Main results

Under B0, profitable shares were 0.515625 for the scholarship grid, 0 for the linear phase-out, 0.190476 for stacked programs, 0.4 for procurement, and 0 for honest reporting. The largest adjusted gains were respectively 99,999; 0; 11; 18; and 0. Thus the hard scholarship cliff is robust over many—but not all—registered friction cells, while the linear phase-out and honest-reporting control remain negative controls in the tested domains.

B1 reduced profitable share to 0.09375 for scholarship, 0.107143 for stacked programs, and 0.145455 for procurement. Signed B1-minus-B0 errors are therefore -0.421875, -0.083333, and -0.254545. The result is expected from the registered action ordering: three candidates often cannot reach the discontinuity. B2 left profitable-opportunity shares unchanged but suppressed all responses for the low-gain stacked and procurement fixtures; scholarship gains remained above its hurdle in the profitable cells.

The weighted scholarship population's exact profitable and response share was 0.9. Seeded estimates were 0.92 at N=100, 0.908 at N=1,000, and 0.9044 at N=5,000. These demonstrate reproducibility and numerical convergence only, not empirical uncertainty.

The reserved incomes 500006–500010 all produced the analytically expected minimum crossing action (income minus 499999), with gains declining from 99,993 to 99,989. This is a small implementation holdout, not out-of-sample policy evidence.

## Scholarship results

Across income 499995–500010, eight frictions, and four multipliers, B0 profitable share is 0.515625 and maximum gain 99,999. Its zero base action cost makes multipliers inert; fixed friction drives disappearance.

## Phase-out comparison

The registered phase-out grid has zero profitable cases. It shares friction assumptions with the cliff but uses a mechanism-specific state grid, limiting matched-population interpretation.

## Stacked-program results

B0 profitable share is 0.190476 and maximum gain 11. B2 observes those opportunities but has zero response at hurdle 100.

## Procurement results

B0 profitable share is 0.4 and maximum adjusted gain 18; B1 reports 0.145455.

## Negative controls

Honest reporting has zero profitable share under every scenario. Phase-out is also zero in the tested finite domain.

## Robustness envelopes

The cell table maps state × friction × multiplier and retains numeric margins to distinguish positive, zero, and negative gain.

## Break-even thresholds

For each scholarship state, the weak eliminating friction equals maximum raw gain because adoption requires strict positivity. The table separately reports the first tested grid value reaching it.

## Distributional summaries

Exact weighted scholarship profitable share is 0.9. Per-type gains and designer outcomes remain separately inspectable; no welfare sum is constructed.

## Search-error analysis

B1-minus-B0 errors are -0.421875 scholarship, -0.083333 stacked, -0.254545 procurement, and zero for both controls.

## Monte Carlo convergence

Errors versus 0.9 are +0.02, +0.008, and +0.0044. Wilson intervals quantify sampling uncertainty under the synthetic distribution only.

## Designer outcomes and distributional interpretation

Designer-outcome changes and action shares are preserved in individual and aggregate artifacts. Where a response crosses a scholarship cliff, fiscal cost increases; where B2 declines a low-gain action, the realized designer change is zero despite a recorded opportunity. These quantities are accounting outputs, not social welfare.

## Formal spot checks

M3 is rerun on a scholarship boundary domain and the honest-reporting negative control. It validates the unchanged individual semantics: scholarship is formally violated with a replayed witness and honest reporting is formally satisfied within its declared domain. Cost overlays and population aggregates are not formally verified.

## Limitations

All evidence is self-authored and synthetic. Grids are fixture-specific, multipliers are ineffective for zero base costs, only declared actions are searched, and aggregates are not formally verified.

## Hostile-review response

Raw cells, provenance, search error, and the opportunity/response split constrain interpretation but cannot solve external-validity or model-misspecification risk.

## Verdict

**PASS WITH LIMITATIONS.** M4 delivers deterministic heterogeneous-type evaluation, behavioral sensitivities, robustness envelopes, exact weighted aggregation, reproducible sampling, individual traceability, and scoped formal spot checks. It does not establish behavioral realism, external validity, equilibrium effects, or population-level formal guarantees.

## M5 authorization

M5 may study interaction or repair only if it preserves the M1/M3 semantic boundary, precommits new claims and domains, and does not relabel synthetic population assumptions as empirical calibration.
