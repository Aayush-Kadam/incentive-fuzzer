# M7 Encoding Audit

## Audit result

All ten external runtime files match the cited scalar threshold or phase-out direction and preserve frozen dates. Units are explicit. Strictness is encoded as reported: the ACA case loses eligibility above its limit; CMS cases use inclusive levels; FAR splitting compares aggregate value against the historical $3,500 threshold. The current FAR page is not used for the historical threshold value.

## Double-entry checks

| Rule | Manual source calculation | Evaluator check | Result |
|---|---|---|---|
| ACA 2020 | one-person 400% FPL = $49,960 | boundary at 49,960 | agree |
| FAR 2017 | two $1,750 parts aggregate to $3,500 | split action crosses per-transaction boundary | agree structurally |
| SSA 2024 | $22,322 implies $1 withheld | rate 0.5 above $22,320 | agree |
| EITC 2024 | one-child phase-out begins $22,720 and completes $49,084 | encoded start 22,720, rate 0.1598 locally | agree within rounded local component |
| PA CHIP | coverage level through 208% FPL | inclusive boundary 208 | agree |

## Material omissions

The benefit/coverage cases omit nonfinancial eligibility, deductions, premiums, reconciliation, continuous eligibility, take-up, household changes, and the monetary value of coverage. ACA and coverage values are illustrative/normalized assumptions. FAR omits enforcement probability and legitimate transaction separability. Actions are plausible mathematical perturbations, not findings of legality or empirical behavior.

The Arizona interaction is the critical audit warning: official Medicaid and CHIP thresholds do not justify treating two programs as additive cash awards. The benchmark therefore uses a smooth proxy and preserves the resulting miss. Its expected IF-015 label is only a stress test of composition mapping, not established ground truth for observed pathology.
