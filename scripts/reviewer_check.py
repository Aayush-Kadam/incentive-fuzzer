"""Bounded synthetic acceptance and negative replay case; no policy endorsement."""
from dataclasses import replace
from decimal import Decimal
import json
from pathlib import Path

from incentive_fuzzer import load_spec, search_spec, verify_spec
from incentive_fuzzer.search import replay_finding


def main():
    path = Path(__file__).resolve().parents[1] / 'examples/scholarship_cliff.yaml'
    spec = load_spec(path)
    found = search_spec(path, 'boundary', 1000)
    witness = found.findings[0]
    genuine = replay_finding(spec, witness)
    forged = replay_finding(spec, replace(witness, utility_delta=witness.utility_delta + Decimal(1)))
    formal = verify_spec(path, 'reduce_work')
    result = {'search': found.status.value, 'action': witness.action.name,
              'amount': str(witness.action.controls['amount']), 'gain': str(witness.utility_delta),
              'replay': genuine, 'forged_replay': forged,
              'formal': formal.status.value,
              'formal_replay': bool(formal.witness and formal.witness.runtime_replay),
              'scope': 'Authored synthetic rule and bounded assumptions; not observed behavior'}
    if not (result['search'] == 'VIOLATION_FOUND' and result['amount'] == '1'
            and result['gain'] == '100000' and genuine and not forged
            and result['formal'] == 'FORMALLY_VIOLATED' and result['formal_replay']):
        raise AssertionError(result)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
