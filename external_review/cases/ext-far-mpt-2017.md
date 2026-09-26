# Review Card: ext-far-mpt-2017

- **Case ID:** `ext-far-mpt-2017`
- **Rule source:** [Federal Acquisition Regulation 13.003](https://www.acquisition.gov/far/13.003) — `far-13`
- **Frozen date/version:** 2017
- **Encoded component:** `transaction_split` over `procurement`, bounded `3498` to `3505`
- **Representability:** PARTIALLY_REPRESENTABLE
- **Omitted components:** eligibility, administration, enforcement, dynamics, behavioral calibration, and valuation details not explicitly encoded; see encoding notes
- **Threat model:** {"action": "nonnegative downward metric adjustment or declared split", "agent": "bounded rule subject", "horizon": "single period", "information": "full encoded rule knowledge", "legality": "not inferred"}
- **Allowed actions:** 1, 2, 3, 4
- **System finding:** expected encoded structural finding
- **Known pathology/control:** frozen structural vulnerability; expected class `IF-007`
- **Match rationale:** same boundary and structural class
- **Formal result:** UNSUPPORTED
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
