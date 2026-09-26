# Incentive Fuzzer 0.1.0 Research Preview

This local release candidate packages the frozen M0-M7.5 evidence as an inspectable research artifact. It includes exact deterministic rule execution, bounded adversarial search, exact-rational formal checking for a restricted property, synthetic robustness and strategic-interaction analysis, bounded repair regression, IF-Bench v0.1, public demonstrations, and three reproduction modes.

## Frozen benchmark results

- Historical encoded-component rediscovery: 5/6.
- Positive holdouts: 4/4; negative holdout findings: 0/2.
- Negative controls: 10/10 clean.
- Boundary-only and combined search: 19 detections each; boundary-only used fewer evaluations.
- SMT-only: 26/30 supported, 15/16 supported positives, 0/10 negative-control false positives, 25/26 ground-truth agreement, 15/15 violating-witness replay.

Arizona remains a preserved miss. External detections disappear when downward-adjustment and splitting actions are ablated. Independent economist/domain review has not been completed.

## Reproduce

Install Python 3.12 and `.[test]`, then run `python scripts/reproduce.py full`.

## Release limitations

This is not production software or validation for policy use. External encodings are partial and project-authored beyond their cited rule components. No empirical behavior, prevalence, legality, welfare, complete program audit, general synthesis, or optimal repair is claimed.

## Open release decision

No software license is granted by this preview yet. `CITATION.cff` records `NOASSERTION`. Before public publication, the project lead should select a license after confirming intended reuse terms and the separate attribution/licensing constraints of benchmark source material.

