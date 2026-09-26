# Review Card: ext-ssa-ret-2024

- **Case ID:** `ext-ssa-ret-2024`
- **Rule source:** [SSA 2024 COLA Fact Sheet](https://www.ssa.gov/news/en/cola/factsheets/2024.html) — `ssa-ret`
- **Frozen date/version:** 2024
- **Encoded component:** `phase_out` over `retirement`, bounded `22316` to `22330`
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
