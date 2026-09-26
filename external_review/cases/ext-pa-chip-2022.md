# Review Card: ext-pa-chip-2022

- **Case ID:** `ext-pa-chip-2022`
- **Rule source:** [Pennsylvania CHIP State Plan Amendment PA-22-0002](https://www.medicaid.gov/CHIP/Downloads/PA-22-0002-CHIP.pdf) — `pa-chip`
- **Frozen date/version:** 2022
- **Encoded component:** `inclusive_cliff` over `health`, bounded `204` to `213`
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
