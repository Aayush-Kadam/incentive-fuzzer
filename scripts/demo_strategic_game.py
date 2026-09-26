"""Synthetic strategic-complementarity and bounded repair demonstration."""
from decimal import Decimal
import json
from incentive_fuzzer.game import enumerate_pure_nash
from incentive_fuzzer.game_fixtures import aggregate_threshold_claim

def profiles(game): return [list(eq.joint_action.actions.values()) for eq in enumerate_pure_nash(game).equilibria]
def main():
    original=profiles(aggregate_threshold_claim()); repaired=profiles(aggregate_threshold_claim(bonus=Decimal("3"),cost=Decimal("4"),threshold=2))
    print(json.dumps({"demo":"synthetic strategic complementarity","isolated_manipulation_gain":"-2","interactive_manipulation_gain":"+2","original_equilibria":original,"bounded_repair":{"cost":"4","bonus":"3","threshold":2,"equilibria":repaired},"qualification":"Complete-information finite pure-strategy demonstration; no equilibrium-selection claim."},indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
