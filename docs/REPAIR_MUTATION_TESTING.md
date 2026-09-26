# Repair Mutation Testing

Mutation testing perturbs repaired numeric parameters within frozen bounds at exact deltas `±1`, `±5`, and `±10`. Each valid neighbor is re-evaluated for target return or declared regression.

Local mutation fragility is `failed registered neighbors / all registered neighbors`.

It is a finite sensitivity statistic, not a derivative, confidence interval, or global robustness proof. Zero means only that no registered neighbor failed. A fragile candidate may still pass the main grid, so fragility remains a separate Pareto dimension.

The scholarship frontier illustrates the tradeoff: a shorter phase-out has lower declared distance and fiscal deviation but 0.4 mutation fragility; a wider phase-out has zero observed local fragility but larger schedule/fiscal change.
