"""Small matched-domain comparison, not IF-Bench or a population claim."""
import importlib.metadata
import json
import platform
from decimal import Decimal
from itertools import product
from pathlib import Path
from statistics import median
from time import perf_counter

from incentive_fuzzer import SearchBudget, SearchDomain, SearchEngine, SearchProblem, load_spec


def main():
    path = Path(__file__).resolve().parents[1] / 'examples/scholarship_cliff.yaml'
    spec = load_spec(path)
    states = tuple(map(Decimal, (499999, 500000, 500001)))
    amounts = tuple(map(Decimal, (0, 1, 2)))
    problem = SearchProblem(spec, SearchDomain(
        {'true_income': states, 'reported_income': states},
        {name: {'amount': amounts} for name in ('reduce_work', 'misreport_income')}))
    rows = []
    # Independently written arithmetic oracle; no package evaluation/labels.
    for seed in range(30):
        start = perf_counter()
        gains = []
        for true, reported, amount, action in product(states, states, amounts, problem.actions()):
            before = true + (100000 if reported < 500000 else 0)
            after_true = true - amount if action == 'reduce_work' else true
            after = after_true + (100000 if reported - amount < 500000 else 0)
            gains.append(after - before)
        rows.append({'seed': seed, 'method': 'standalone_exhaustive_oracle',
                     'seconds': perf_counter() - start, 'evaluations': 108,
                     'maximum_gain': str(max(gains)), 'found': max(gains) > 0})
        for method in ('exhaustive', 'boundary', 'property'):
            result = SearchEngine(problem).run(method, SearchBudget(108, 54, 10), seed)
            best = max((f.utility_delta for f in result.findings), default=Decimal(0))
            rows.append({'seed': seed, 'method': method,
                         'seconds': result.statistics.elapsed_seconds,
                         'evaluations': result.statistics.evaluation_count,
                         'maximum_gain': str(best), 'found': bool(result.findings),
                         'time_to_first': result.statistics.time_to_first_violation,
                         'evaluations_to_first': result.statistics.evaluations_to_first_violation})
    summary = {method: {'trials': 30, 'found': sum(r['found'] for r in rows if r['method'] == method),
                        'median_seconds': median(r['seconds'] for r in rows if r['method'] == method),
                        'min_seconds': min(r['seconds'] for r in rows if r['method'] == method),
                        'max_seconds': max(r['seconds'] for r in rows if r['method'] == method)}
               for method in ('standalone_exhaustive_oracle', 'exhaustive', 'boundary', 'property')}
    print(json.dumps({'python': platform.python_version(), 'os': platform.platform(),
                      'processor': platform.processor(),
                      'versions': {n: importlib.metadata.version(n) for n in ('incentive-fuzzer', 'z3-solver', 'PyYAML')},
                      'domain': '9 states x 2 actions x 3 amounts; at most 108 utility evaluations',
                      'warning': 'One disclosed synthetic case; engine methods share code. Oracle lacks witness diagnostics. No real-world accuracy or external-library ranking.',
                      'summary': summary, 'rows': rows}, indent=2))


if __name__ == '__main__':
    main()
