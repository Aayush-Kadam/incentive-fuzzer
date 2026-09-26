# M7.5 M8 Entry Hardening Report

## Verdict

**READY FOR M8 WITH UNRESOLVED EXTERNAL-REVIEW DEPENDENCY.**

## B5 SMT-only baseline

B5 consumes only the supported runtime IncentiveSpec adapter, `no_profitable_deviation` property, and declared state/action domain. It does not call M2 candidate generation, use reductions, or load hidden labels before results are frozen.

| Metric | Result |
|---|---:|
| IF-Bench cases | 30 |
| SMT supported | 26 |
| Formally violated | 15 |
| Formally satisfied within domain | 11 |
| Unsupported | 4 |
| Timeout / unknown / disagreement | 0 / 0 / 0 |
| Supported positive detections | 15/16 |
| Supported negative false positives | 0/10 |
| Ground-truth status agreement | 25/26 |
| Combined-search status agreement | 26/26 |
| Violating-witness replay | 15/15 |

Unsupported cases are FAR transaction splitting and three composition fixtures because no current M3 adapter exists for those benchmark model types. Arizona is the only hidden-ground-truth disagreement: B5 and combined search both return a scoped non-violation for the preserved proxy, consistent with M7's `PROPERTY_MISMATCH` / `MODEL_SCOPE_LIMIT` analysis.

B5 is not assigned candidate-evaluation counts. Its recorded aggregate formal time is machine-dependent and is reported separately from search evaluations.

## Method conclusion

Boundary-only remains the most evaluation-efficient detector on threshold-heavy IF-Bench v0.1 and matches combined recall. SMT-only provides exact domain-scoped SAT/UNSAT evidence for 26 supported cases, including min/max piecewise schedules, but has incomplete model coverage and no recall advantage over combined search on supported cases. Combined workflow value remains label blindness, candidate/replay evidence, reduction, and regression integration—not superior raw recall.

## Non-threshold stress supplement

Three separate cases were admitted:

1. IRS 2024 single-filer progressive tax schedule: continuous multi-kink schedule; scoped formal satisfaction.
2. IRS 2024 dependent-care credit percentage staircase: multiple rate steps; replayed modeled local gain. This is analytically derived, not documented manipulation.
3. DOL safe-harbor 401(k) tiered/capped match: replayed positive response explicitly labeled intended behavior rather than vulnerability.

All three matched labels that were stored separately from runtime inputs. They are stress tests, not historical rediscovery, prevalence evidence, or IF-Bench v0.2.

## External review

The repository now contains a review guide, ten M7 case cards, a structured form, and sealed mini-holdout support. No actual independent review has occurred. This remains the principal external dependency.

## Scientific freeze

`M8_ENTRY_CLAIM_LEDGER.md`, generated headline tables/figure, and the expanded limitations register govern M8. M8 may integrate and communicate existing evidence as a research preview; it may not manufacture new headline science or imply external validation.

