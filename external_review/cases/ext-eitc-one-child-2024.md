# Review Card: ext-eitc-one-child-2024

- **Case ID:** `ext-eitc-one-child-2024`
- **Rule source:** [IRS Internal Revenue Bulletin 2023-48](https://www.irs.gov/irb/2023-48_IRB) — `irs-eitc`
- **Frozen date/version:** 2024
- **Encoded component:** `phase_out` over `tax`, bounded `22716` to `22730`
- **Representability:** PARTIALLY_REPRESENTABLE
- **Omitted components:** eligibility, administration, enforcement, dynamics, behavioral calibration, and valuation details not explicitly encoded; see encoding notes
- **Threat model:** {"action": "nonnegative downward metric adjustment or declared split", "agent": "bounded rule subject", "horizon": "single period", "information": "full encoded rule knowledge", "legality": "not inferred"}
- **Allowed actions:** 0, 1, 2, 3, 4, 5, 6, 7
- **System finding:** negative control; no finding expected
- **Known pathology/control:** negative control; expected class `None`
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
