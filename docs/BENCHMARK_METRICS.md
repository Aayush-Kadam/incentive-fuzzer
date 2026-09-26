# Benchmark Metrics

- **Case recall:** positive labeled cases with at least one replayed structural finding divided by positive labeled cases.
- **Class recall:** positive cases whose first frozen finding matches the expected IF-CWE divided by positive cases.
- **Finding match:** same encoded boundary and structural class; theoretical incentive does not establish observed behavior.
- **False positive:** a replayed finding on a predeclared negative control. Unexpected findings on non-controls require the surprise protocol instead.
- **Evaluation budget:** candidate executions; B0–B4 receive 100 each per case.
- **Discovery latency:** evaluations and elapsed wall time through the first replayed finding.
- **Replay rate:** frozen findings that reproduce exact state and utility deltas.
- **Formal confirmation rate:** supported findings independently returned as `FORMALLY_VIOLATED` by M3 and replayed.
- **Reduction ratio:** reduced action magnitude divided by raw action magnitude. It measures only the registered scalar objective.

Percentages are descriptive for this curated benchmark, not estimates for an IID population of mechanisms.
