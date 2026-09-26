# Review Card: ext-az-child-interaction-2023

- **Case ID:** `ext-az-child-interaction-2023`
- **Rule source:** [Medicaid, CHIP, and BHP Eligibility Levels](https://www.medicaid.gov/medicaid/national-medicaid-chip-program-information/medicaid-childrens-health-insurance-program-basic-health-program-eligibility-levels) — `cms-levels`
- **Frozen date/version:** 2023-12-01
- **Encoded component:** `phase_out` over `health`, bounded `128` to `205`
- **Representability:** PARTIALLY_REPRESENTABLE
- **Omitted components:** eligibility, administration, enforcement, dynamics, behavioral calibration, and valuation details not explicitly encoded; see encoding notes
- **Threat model:** {"action": "nonnegative downward metric adjustment or declared split", "agent": "bounded rule subject", "horizon": "single period", "information": "full encoded rule knowledge", "legality": "not inferred"}
- **Allowed actions:** 0, 1, 2, 3, 4, 5, 6, 7
- **System finding:** expected encoded structural finding
- **Known pathology/control:** frozen structural vulnerability; expected class `IF-015`
- **Match rationale:** same boundary and structural class
- **Formal result:** FORMALLY_SATISFIED_WITHIN_DOMAIN
- **Limitations:** component-level and domain-scoped; actions and valuations remain project-authored

## Reviewer fields

- Rule fidelity:
- Action realism and legality:
- Missing actions or constraints:
- Valuation assessment:
- Pathology mapping:
- Scope assessment:
- Repair-interpretation concerns:
- Disposition and required changes:
