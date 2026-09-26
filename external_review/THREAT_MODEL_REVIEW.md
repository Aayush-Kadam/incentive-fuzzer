# Threat-Model Review Guide

Review the encoded actor, information, action, timing, cost, feasibility, and omitted alternatives independently of the sourced rule. The benchmark's external detections are conditional on small downward metric changes or transaction splitting. The M7 ablation removes every external finding when these actions are removed.

Questions:

- Is the actor able to control the encoded variable directly or only through costly intermediate behavior?
- Does the action preserve household, firm, or transaction identity assumptions?
- Are enforcement, reporting, audit, stigma, liquidity, delay, and legal constraints omitted?
- Does the single-period model omit recapture, reconciliation, future eligibility, or dynamic consequences?
- Are plausible upward, timing, substitution, household-composition, or multi-agent actions missing?
- Should the observed response be classified as intended response, adaptation, manipulation, or ambiguity?

