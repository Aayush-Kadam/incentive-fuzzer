# M7.5 Non-Threshold Stress-Test Exclusions

M7.5 screened candidates for structures that were not merely a single `x < c` cutoff. Exclusion was preferred to removing the feature that made a rule interesting.

| Candidate | Source considered | Disposition | Exact reason |
|---|---|---|---|
| Medicare Part B outpatient coinsurance | Medicare.gov costs and coverage pages | Excluded | A constant reimbursement percentage is representable, but no credible strategic action or incentive property was established without inventing treatment demand, provider behavior, medical necessity, or health valuation. |
| Medicare deductible plus coinsurance | Medicare.gov 2024 cost guide | Excluded | The piecewise cost schedule is representable, but a single-period scalar spending action would materially omit coverage choice, episode necessity, provider prices, and health outcomes. |
| Generic traditional 401(k) employer match | U.S. Department of Labor small-business guide | Excluded in favor of safe-harbor formula | The generic match is plan-chosen and lacks one frozen payoff schedule. The official safe-harbor example provides a specific tiered/capped formula. |
| Child and dependent care credit full computation | IRS Publication 503 (2024) | Partially included | Full eligibility, earned-income limits, provider restrictions, employer benefits, expense caps, and nonrefundability exceed honest v0.1 representation. Only the published percentage staircase at fixed qualified expenses is included. |
| Full federal income-tax liability | IRS 2024 instructions and Revenue Procedure 2023-34 | Partially included | Deductions, credits, filing alternatives, capital-gain schedules, and tax-table rounding are omitted. Only the continuous single-filer rate-schedule component is included. |

The resulting three-case supplement is not IF-Bench v0.2 and does not modify M7 scores or holdouts.

