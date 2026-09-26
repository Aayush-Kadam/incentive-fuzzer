# IF-Bench v0.1

IF-Bench is an internal, versioned benchmark for structural incentive auditing. Version 0.1 contains 30 deterministic bounded cases: 12 inherited internal synthetic cases, 8 additional internal/controls, and 10 externally sourced rule components. Six cases are held out from search-configuration development.

Runtime cases are under `benchmarks/if_bench/v0.1/cases`; labels are separate under `labels`; source metadata and access dates are under `sources`; the hashed manifest is under `manifests`. `load_runtime_suite` cannot return labels. Scoring requires a separately frozen run sequence and an explicit label load.

Origins are `SYNTHETIC_INTERNAL`, `HISTORICAL_RULE`, `CURRENT_PUBLIC_RULE`, and `NEGATIVE_CONTROL`. External encodings are partial scalar components, not whole-program models. Eligibility status is represented by a declared normalized or illustrative value where the external rule does not specify a cash amount. Such values have assumed provenance and cannot support incidence, welfare, or policy recommendations.

Difficulty tiers used in v0.1 are: 1 single threshold; 2 piecewise or sourced scalar rule; 3 composition. Population, strategic-game, and repair tiers are not claimed as externally benchmarked in this version.

The package is not authorized for public release. It stores encoded facts and citations, not source-document copies. Source restrictions are recorded in the source register.
