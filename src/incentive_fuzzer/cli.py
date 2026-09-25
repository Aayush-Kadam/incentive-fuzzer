from __future__ import annotations

import argparse
from decimal import Decimal
import json
from pathlib import Path

from .core import ValueType, load_spec
from .search import SearchBudget, SearchDomain, SearchEngine, SearchProblem, finding_to_json


def _values(lower, upper, boundaries):
    lower, upper = int(lower), int(upper)
    values = {lower, upper, 0}
    for boundary in boundaries:
        values.update({int(boundary) - 1, int(boundary), int(boundary) + 1})
    return tuple(Decimal(v) for v in sorted(v for v in values if lower <= v <= upper))


def main(argv=None):
    parser = argparse.ArgumentParser(prog="incentive-fuzzer")
    sub = parser.add_subparsers(dest="command", required=True)
    search = sub.add_parser("search")
    search.add_argument("spec")
    search.add_argument("--method", default="combined", choices=["exhaustive", "boundary", "property", "grid", "combined"])
    search.add_argument("--max-evaluations", type=int, default=1000)
    search.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    spec = load_spec(args.spec)
    from .search import extract_boundaries
    boundaries = extract_boundaries(spec)
    state_values = {}
    for name, attr in spec.attributes.items():
        related = [b.value for b in boundaries if b.attribute == name]
        if attr.type is ValueType.BOOLEAN:
            state_values[name] = (False, True)
        else:
            state_values[name] = _values(attr.lower, attr.upper, related)
    action_values = {}
    for name, action in spec.actions.items():
        action_values[name] = {control: _values(defn.lower, defn.upper, ()) for control, defn in action.controls.items()}
    problem = SearchProblem(spec, SearchDomain(state_values, action_values))
    result = SearchEngine(problem).run(args.method, SearchBudget(args.max_evaluations, args.max_evaluations, 30))
    payload = {
        "run_id": result.run_id, "status": result.status.value,
        "statistics": {k: str(v) if isinstance(v, Decimal) else v for k, v in result.statistics.__dict__.items()},
        "findings": [json.loads(finding_to_json(f)) for f in result.findings],
    }
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.output: args.output.write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__": main()
