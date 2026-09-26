# Review Card: ext-aca-ptc-2020

- **Case ID:** `ext-aca-ptc-2020`
- **Rule source:** [IRS Eligibility for the Premium Tax Credit](https://www.irs.gov/affordable-care-act/individuals-and-families/eligibility-for-the-premium-tax-credit) — `irs-ptc`
- **Frozen date/version:** 2020
- **Encoded component:** `hard_cliff` over `tax`, bounded `49955` to `49965`
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
