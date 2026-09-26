# M7 Precommitment

Frozen before IF-Bench implementation and evaluation: 2026-09-26.

## Research question

Can the existing bounded Incentive Fuzzer workflow rediscover structural incentive vulnerabilities in independently authored rules, without access to pathology labels, and add detection efficiency or evidence quality beyond simple search baselines?

## Candidate funnel and exclusions

Twenty-eight external candidates were screened. Ten rule components are included. Eighteen are excluded before evaluation because the action space, benefit valuation, time dynamics, stochastic allocation, or governing version could not be encoded without material distortion. Exclusions are preserved in `M7_EXCLUSIONS.md`.

## Frozen benchmark

IF-Bench v0.1 contains 30 cases:

- internal development: `int-cliff-low`, `int-cliff-inclusive`, `int-stacked-close`, `int-procurement`, `int-reporting`, `int-boundary-low`, `int-boundary-high`, `int-zero-award`, `int-high-cost`, `int-linear-phaseout`, `int-stacked-wide`, `int-honest-reporting`;
- external historical/development: `ext-aca-ptc-2020`, `ext-far-mpt-2017`, `ext-snap-gross-2024`, `ext-al-medicaid-parent-2023`, `ext-az-child-interaction-2023`, `ext-pa-chip-2022`;
- external current/validation: `ext-co-medicaid-adult-2023`, `ext-ny-fcep-2024`;
- external negative controls: `ext-ssa-ret-2024`, `ext-eitc-one-child-2024`;
- internal negative controls: `neg-linear-half`, `neg-linear-third`, `neg-no-award`, `neg-cost-dominates`;
- holdout: `int-boundary-high`, `int-stacked-wide`, `ext-co-medicaid-adult-2023`, `ext-ny-fcep-2024`, `ext-ssa-ret-2024`, `ext-eitc-one-child-2024`.

Historical labels are stored outside runtime cases. Frozen positive labels are IF-001 for hard eligibility losses, IF-007 for the FAR transaction-splitting case, and IF-015 for the Arizona Medicaid/CHIP interaction. Smooth phase-outs and cost-dominant mechanisms are negative controls. Structural detection is not evidence of behavioral prevalence.

## Representability

All included cases are bounded, deterministic, single-period scalar encodings. External cases are `PARTIALLY_REPRESENTABLE`: they encode only the cited income or procurement rule component. Omitted nonfinancial eligibility, deductions, premiums, tax reconciliation, benefit valuation, enforcement, household dynamics, and administrative processes are documented. No whole-program audit claim is authorized.

## Blind protocol

Runtime files contain rule, action, property, provenance pointer, and threat-model fields, but no known vulnerability, expected class, pathology name, or ground-truth result. Labels live under `labels/` and are unavailable through the runtime loader. The evaluator freezes runtime findings before a separate scorer loads labels. Automated tests inspect leakage and loader reachability.

## Search methods and budgets

Methods are B0 deterministic random, B1 uniform grid, B2 boundary-only, B3 exhaustive where the finite domain is tractable, B4 combined boundary plus grid, and B5 SMT-only for supported scalar cases. B0–B4 receive at most 100 candidate evaluations per case and seed `20260926`; B3 may terminate earlier after complete enumeration. B5 receives 5 seconds. Candidate domains and evaluators are identical across B0–B4. No benchmark-name branching is allowed.

## Metrics

Frozen metrics are case recall, IF-CWE class recall, safe-control false-positive fraction, evaluations and time to first valid finding, replay fraction, formal-confirmation fraction, and witness reduction ratio. A pathology match requires the frozen finding to have the same structural class and materially cross the cited rule boundary. Unexpected findings are unresolved until the surprise protocol is complete.

## Success thresholds

M7 can pass with limitations if: all integrity tests pass; no label leakage occurs; at least 4/6 historical structural cases are rediscovered; external negative-control false positives are zero; at least one external finding is independently confirmed by M3; holdout case recall is at least 50%; and the combined workflow either improves median discovery cost over random/grid on positives or adds replay/reduction/formal evidence not supplied by those baselines. Perfect recall is neither required nor expected.

## Repair subset

Three bounded external repair tasks are frozen: ACA 2020 hard-cutoff to phase-out, SNAP 2024 eligibility cutoff to phase-out, and FAR 2017 threshold-cost regression. Repairs are structural test candidates only, never policy recommendations. Comparison with later reforms is qualitative and performed only after candidates are frozen.

## Threat-model sensitivity and ablation

Headline positive cases receive a narrow action domain and a broader domain adding larger income/scope changes. Action ablation removes downward adjustment entirely; loss of rediscovery is reported as model dependence, not hidden as a failure. The FAR case additionally ablates transaction splitting while retaining scope reduction.

## Exclusion and change control

Only predeclared exclusions are allowed: insufficient authoritative source, unfrozen version, material unrepresentability, or ambiguous structural label. Generic implementation defects may be fixed, followed by a full rerun and research-log entry. Holdout-specific heuristic tuning is prohibited.
