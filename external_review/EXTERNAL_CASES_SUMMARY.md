# External Cases Summary

IF-Bench v0.1 contains ten externally sourced scalar components: ACA premium-tax-credit cutoff, FAR micro-purchase splitting, SNAP gross-income screen, Alabama Medicaid, Arizona child Medicaid/CHIP transition proxy, Colorado Medicaid, Pennsylvania CHIP, New York FCEP CHIP, Social Security retirement earnings test, and the EITC phase-out.

Six are frozen historical components, two are positive holdouts, and two are negative-control holdouts. Combined search rediscovered five of six historical components and all four positive holdouts; all ten negative controls were clean. Arizona is the preserved miss (`PROPERTY_MISMATCH`, `MODEL_SCOPE_LIMIT`).

All encodings are partial. External sources establish rule components, not the project's actions, valuations, threat models, or pathology mappings. Removing downward-adjustment or splitting actions eliminates every external finding. Review cards under `cases/` expose these assumptions case by case.

The separate M7.5 supplement is not IF-Bench v0.2. It contains three structural stress tests: an IRS progressive rate schedule, an IRS dependent-care percentage staircase, and a DOL tiered/capped match. The DOL case is an intended-response control.

