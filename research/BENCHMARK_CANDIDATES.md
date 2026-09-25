# M0 Benchmark Candidates

Candidates are not validated benchmark instances. Synthetic mechanisms can have seeded ground truth. Historically motivated candidates are model templates requiring exact rule versions, authoritative sources, and expert review; inclusion does not claim observed gaming.

## Synthetic candidates

| ID | Mechanism | Seeded issue/control | Primary property |
|---|---|---|---|
| S01 | Scholarship hard cutoff | IF-001 | local monotonicity |
| S02 | Two stacked benefit phase-outs | IF-015 | max effective marginal burden |
| S03 | Procurement review threshold | IF-007 | no transaction splitting |
| S04 | Per-firm green grant cap | IF-006 | consolidation invariance |
| S05 | Tiered sales commission | IF-002 / control with smooth schedule | effort monotonicity |
| S06 | Annual carbon baseline | IF-004/009 | true-emissions improvement |
| S07 | Insurance deductible/reset | IF-004/010 | temporal equivalence |
| S08 | Capacity-limited grant queue | IF-013/014 | priority invariance |
| S09 | Referral bonus with identity reset | IF-010 | one reward per economic actor |
| S10 | Audit-risk declaration model | IF-005/017 | no profitable misreport |
| S11 | Debt-forgiveness threshold | IF-019 | no strategic default |
| S12 | Network-adoption subsidy game | IF-016 | equilibrium uniqueness/stability |

Controls include smooth schedules, aggregation windows, ownership consolidation, cooldowns, and infeasible-action variants. Labels must be generated from analytic proofs or exhaustive bounded enumeration, not from the implementation under test.

## Historically motivated candidates

| ID | Motivation | Candidate model | Source/evidence needed before use |
|---|---|---|---|
| H01 | Earned-income tax kinks/notches | taxable-income bunching | exact tax-year statute and administrative evidence; Saez (2010) as behavioral context |
| H02 | Means-tested benefit cliffs | stacked withdrawal schedule | official program rules for a frozen jurisdiction/date; do not infer behavior from schedule alone |
| H03 | Public procurement reporting thresholds | invoice/contract splitting | statute, aggregation rules, enforcement guidance, documented cases if behavioral claim made |
| H04 | Structuring around transaction reports | repeated sub-threshold transfers | exact reporting law and safe, non-operational presentation; enforcement evidence |
| H05 | Agricultural/payment entity caps | ownership/entity restructuring | statute, attribution/actively-engaged rules, official audits |
| H06 | Renewable-energy/carbon baselines | output or baseline manipulation | protocol version, verification rules, peer-reviewed/official evidence |
| H07 | Hospital/readmission performance incentives | coding or patient-selection response | program specification and causal empirical literature |
| H08 | School accountability thresholds | metric substitution | frozen accountability formula and credible empirical study |
| H09 | Sales compensation accelerators | deal timing/bunching | de-identified contract and transaction data or synthetic calibration |
| H10 | Marketplace new-user/referral rewards | identity/participation cycling | published terms/version and platform evidence, if available |
| H11 | Insurance deductibles/year boundaries | treatment timing | policy contract and clinical/economic evidence |
| H12 | Matching priority systems | strategic declarations/preferences | exact mechanism, admissible reports, and documented strategic incentives |

## Benchmark admission rule

An instance enters IF-Bench only after: rule provenance and date are frozen; normative property is named; feasible actions and costs are reviewed; a ground-truth method independent of the candidate engine is supplied; positive and negative controls exist; expected result and tolerances are precommitted; and licensing permits redistribution.

