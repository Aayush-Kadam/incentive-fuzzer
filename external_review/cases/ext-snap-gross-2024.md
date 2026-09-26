# Review Card: ext-snap-gross-2024

- **Case ID:** `ext-snap-gross-2024`
- **Rule source:** [Georgia CHIP state plan cross-program rule table](https://www.medicaid.gov/CHIP/Downloads/GA-22-0032.pdf) — `usda-snap`
- **Frozen date/version:** 2024
- **Encoded component:** `hard_cliff` over `benefit`, bounded `126` to `136`
- **Representability:** PARTIALLY_REPRESENTABLE
- **Omitted components:** eligibility, administration, enforcement, dynamics, behavioral calibration, and valuation details not explicitly encoded; see encoding notes
- **Threat model:** {"action": "nonnegative downward metric adjustment or declared split", "agent": "bounded rule subject", "horizon": "single period", "information": "full encoded rule knowledge", "legality": "not inferred"}
- **Allowed actions:** 0, 1, 2, 3, 4, 5, 6, 7
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
