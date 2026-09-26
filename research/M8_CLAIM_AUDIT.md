# M8 Claim-to-Evidence Audit

This audit governs the research-preview README, manuscript, release notes, and external-review package. The frozen quantitative evidence is the M7/M7.5 record at `fcaca60e8444fdea866504ff8388892be3cc5923`.

| Public claim | Evidence | Milestone / commit | Limitations | Allowed wording |
|---|---|---|---|---|
| Deterministic exact semantics for the documented bounded subset | `tests/test_core.py`; `research/M1_REPORT.md` | M1 / `9a7450c` | Not arbitrary programs or real-valued unbounded semantics | “IncentiveSpec provides deterministic exact semantics for its documented bounded subset.” |
| Separate SMT backend reproduced supported semantics | `research/M3_REPORT.md` | M3 / `dcaf727` | Only the supported formal fragment | “The separately authored SMT backend reproduced supported M1 semantics in frozen M3 testing.” |
| Historical encoded-component rediscovery was 5/6 | `experiments/m7/runs/summary.json`; `research/M7_REPORT.md` | M7 / `7ab2251` | Small, curated partial encodings; not policy accuracy | “Blind evaluation rediscovered structural pathologies in five of six historical encoded components.” |
| Positive holdouts 4/4; negative holdouts 0/2 findings | `experiments/m7/runs/summary.json`; `research/M7_REPORT.md` | M7 / `7ab2251` | Project-designed benchmark and threat models | “M7 detected 4/4 positive holdouts and produced no findings on 2/2 holdout negatives.” |
| Negative controls 10/10 clean | `experiments/m7/runs/summary.json` | M7 / `7ab2251` | Ten benchmark controls only | “All ten IF-Bench v0.1 negative controls were clean.” |
| Boundary-only matched combined recall with fewer evaluations | `research/m8_entry/HEADLINE_TABLES.md` | M7.5 freeze / `fcaca60` | Case recall, not runtime or general superiority | “Boundary-only matched combined-search case recall (19 cases) using 369 versus 1,261 candidate evaluations.” |
| SMT-only supported 26/30, with 15 violated and 11 satisfied | `experiments/m75/runs/summary.json`; `research/M75_REPORT.md` | M7.5 / `fcaca60` | Domain-scoped status; four unsupported cases | “SMT-only returned exact domain-scoped statuses for 26/30 cases: 15 formally violated and 11 formally satisfied within domain.” |
| SMT-only supported-positive detections 15/16; ground-truth agreement 25/26 | `experiments/m75/runs/summary.json` | M7.5 / `fcaca60` | Supported subset only | State the denominators every time. |
| SMT witnesses replayed 15/15 | `experiments/m75/runs/summary.json` | M7.5 / `fcaca60` | Violating supported cases only | “All 15 violating SMT witnesses replayed in the reference evaluator.” |
| M6 repair exposed equilibrium regression risk | `research/M6_REPORT.md` | M6 / `d73d001` | Synthetic bounded finite game; not optimal policy design | “A candidate repair eliminated an isolated exploit yet created a harmful finite-game equilibrium.” |
| Non-threshold supplement has three stress cases | `research/M75_REPORT.md`; `benchmarks/m75_stress/v0.1/` | M7.5 / `aa1d082` | Supplement only; not IF-Bench v0.2 | Tax schedule is a structural negative control; dependent-care is a modeled opportunity; 401(k) matching is intended response, not a vulnerability. |

## Required negative-result language

- Arizona remains the historical miss and a property-model mismatch.
- Removing relevant downward-adjustment or transaction-splitting actions eliminates the corresponding findings.
- External counterexample reduction ratio was 1.0 where reported; reduction added no compression there.
- Independent economist/domain, encoding, action-space, and valuation review remains outstanding.

No public artifact may translate these bounded results into representative auditing accuracy, legal conclusions, behavioral prevalence, production readiness, or policy recommendations.
