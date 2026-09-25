# IncentiveSpec v0.1

IncentiveSpec v0.1 is a YAML serialization of the M1 typed intermediate representation. It is deliberately not a universal economics language.

```yaml
incentive_spec_version: "0.1"
institution:
  id: scholarship_cliff
  name: Scholarship Cliff
  description: Synthetic hard cutoff
  version: "1"
parameters:
  threshold: {type: money, value: 500000, provenance: S}
attributes:
  true_income:
    {type: money, lower: 0, upper: 2000000,
     observable: false, manipulable: true, role: latent}
  reported_income:
    {type: money, lower: 0, upper: 2000000,
     observable: true, manipulable: true, role: reported}
rules:
  benefit:
    if:
      condition: {lt: [{var: reported_income}, {var: threshold}]}
      then: {const: {value: 100000, unit: money}}
      else: {const: {value: 0, unit: money}}
utility: {add: [{var: true_income}, {var: benefit}]}
designer_outcomes: {fiscal_cost: {var: benefit}}
properties: []
```

Required top-level fields are version, institution metadata, attributes, rules, utility, designer outcomes, and properties; parameters and actions may be empty. Parameters require provenance `E`, `L`, `S`, or `A`. Attributes require finite inclusive bounds and explicit observability/manipulability. Action transitions may target only attributes declared manipulable.

See `SEMANTICS.md` for normative behavior and `examples/` for complete specifications.

