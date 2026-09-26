# Benchmark Contribution Policy

Every proposed external case must include:

1. an authoritative primary source and stable URL;
2. a frozen rule date or version;
3. a precise component boundary and representability assessment;
4. encoding notes listing all material omissions;
5. an explicit actor, information set, action space, timing, costs, legality assumptions, and property;
6. runtime input with no expected result, pathology, or hidden label fields;
7. a separately stored label with ground-truth method and match standard;
8. provenance and redistribution notes;
9. deterministic replay or an explicit unsupported status;
10. tests for schema, leakage, source metadata, and package hashes.

Cases must not be simplified in a way that removes the feature motivating inclusion. Misses and exclusions must be preserved. Existing holdout results may not be rewritten. Contributor-sealed cases should use `external_review/sealed_holdout_template/`; evaluation must occur before labels are delivered or opened.

New cases do not automatically create IF-Bench v0.2. Versioning requires a declared protocol change and a new frozen evaluation.

