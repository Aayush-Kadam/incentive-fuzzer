# Review Card: ext-co-medicaid-adult-2023

- **Case ID:** `ext-co-medicaid-adult-2023`
- **Rule source:** [Medicaid, CHIP, and BHP Eligibility Levels](https://www.medicaid.gov/medicaid/national-medicaid-chip-program-information/medicaid-childrens-health-insurance-program-basic-health-program-eligibility-levels) — `cms-levels`
- **Frozen date/version:** 2023-12-01
- **Encoded component:** `inclusive_cliff` over `health`, bounded `129` to `138`
- **Representability:** PARTIALLY_REPRESENTABLE
- **Omitted components:** eligibility, administration, enforcement, dynamics, behavioral calibration, and valuation details not explicitly encoded; see encoding notes
- **Threat model:** {"action": "nonnegative downward metric adjustment or declared split", "agent": "bounded rule subject", "horizon": "single period", "information": "full encoded rule knowledge", "legality": "not inferred"}
- **Allowed actions:** 0, 1, 2, 3, 4, 5, 6
- **System finding:** expected encoded structural finding
- **Known pathology/control:** frozen structural vulnerability; expected class `IF-001`
- **Match rationale:** same boundary and structural class
- **Formal result:** FORMALLY_VIOLATED
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
