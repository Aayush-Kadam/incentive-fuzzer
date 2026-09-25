from decimal import Decimal
from fractions import Fraction
from pathlib import Path
import random

import pytest
import yaml

from incentive_fuzzer import ActionInstance, evaluate, load_spec, parse_spec
from incentive_fuzzer.verify import (
    FormalDomain, FormalStatus, FormalVerifier, UnsupportedFragment,
    decimal_to_fraction, formal_result_json,
)

ROOT=Path(__file__).parents[1]; EX=ROOT/"examples"; BENCH=ROOT/"benchmarks/m2/specs"


@pytest.mark.parametrize("text,expected", [
    ("500000", Fraction(500000,1)), ("0.25", Fraction(1,4)),
    ("123.45", Fraction(2469,20)), ("-0.001", Fraction(-1,1000)),
    ("0", Fraction(0,1)), ("1.2300", Fraction(123,100)),
])
def test_decimal_to_fraction_exact(text,expected):
    assert decimal_to_fraction(Decimal(text)) == expected


def domain(states, controls):
    return FormalDomain({k:tuple(Decimal(str(v)) for v in vals) for k,vals in states.items()},
                        {k:tuple(Decimal(str(v)) for v in vals) for k,vals in controls.items()})


def test_scholarship_formally_violated_and_replayed():
    spec=load_spec(EX/"scholarship_cliff.yaml")
    d=domain({"true_income":[499999,500000,500001],"reported_income":[499999,500000,500001]}, {"amount":[0,1,2]})
    result=FormalVerifier(spec,d).verify_no_profitable_deviation("reduce_work")
    assert result.status is FormalStatus.FORMALLY_VIOLATED
    assert result.witness.agreement and result.witness.runtime_replay == "PASS"
    assert result.witness.predicted_utility > evaluate(spec,result.witness.decoded_baseline_state).utility


def test_honest_reporting_formally_satisfied():
    spec=load_spec(EX/"honest_reporting_control.yaml")
    d=domain({"true_income":range(21),"reported_income":range(21)}, {"amount":range(11)})
    result=FormalVerifier(spec,d).verify_no_profitable_deviation("misreport")
    assert result.status is FormalStatus.FORMALLY_SATISFIED_WITHIN_DOMAIN
    assert result.witness is None


@pytest.mark.parametrize("income,amount", [(500000,1),(500001,2),(499999,0)])
def test_fixed_scholarship_matches_runtime(income,amount):
    spec=load_spec(EX/"scholarship_cliff.yaml")
    d=domain({"true_income":[income],"reported_income":[income]},{"amount":[amount]})
    action=ActionInstance("reduce_work",{"amount":Decimal(amount)})
    formal=FormalVerifier(spec,d).evaluate_fixed({"true_income":Decimal(income),"reported_income":Decimal(income)},action)
    runtime=evaluate(spec,{"true_income":income,"reported_income":income},action)
    assert formal["state"]==runtime.resulting_state.values
    assert formal["outputs"]==runtime.outcome.rule_outputs
    assert formal["utility"]==runtime.utility
    assert formal["designer"]==runtime.outcome.designer_outcomes


@pytest.mark.parametrize("fixture,state,action", [
    ("linear_phase_out",{"income":Decimal(550000)},ActionInstance("reduce_income",{"amount":Decimal(1)})),
    ("stacked_programs",{"income":Decimal(12)},ActionInstance("reduce_income",{"amount":Decimal(2)})),
    ("procurement_threshold",{"transaction_value":Decimal(100)},ActionInstance("reduce_scope",{"amount":Decimal(1)})),
    ("honest_reporting_control",{"true_income":Decimal(10),"reported_income":Decimal(10)},ActionInstance("misreport",{"amount":Decimal(1)})),
])
def test_fixed_canonical_matches_runtime(fixture,state,action):
    spec=load_spec(EX/f"{fixture}.yaml"); d=domain({k:[v] for k,v in state.items()},{k:[v] for k,v in action.controls.items()})
    formal=FormalVerifier(spec,d).evaluate_fixed(state,action); runtime=evaluate(spec,state,action)
    assert formal["state"]==runtime.resulting_state.values
    assert formal["outputs"]==runtime.outcome.rule_outputs
    assert formal["utility"]==runtime.utility


def test_min_max_phase_out_unsat_on_tested_domain():
    spec=load_spec(EX/"linear_phase_out.yaml")
    d=domain({"income":[479999,480000,480001,550000,619999,620000,620001]},{"amount":range(0,6)})
    result=FormalVerifier(spec,d).verify_no_profitable_deviation("reduce_income")
    assert result.status is FormalStatus.FORMALLY_SATISFIED_WITHIN_DOMAIN


@pytest.mark.parametrize("name,violated", [
    ("cliff_low_cost",True),("cliff_small_award",True),("inclusive_cliff",True),
    ("cliff_cost_one",True),("safe_high_cost",False),("safe_zero_award",False),
    ("reported_cliff",True),("reported_safe_penalty",False),("stacked_close",True),
    ("stacked_wide",True),("boundary_at_lower",True),("boundary_at_upper",True),
])
def test_frozen_suite_status(name,violated):
    spec=load_spec(BENCH/f"{name}.yaml")
    d=domain({k:range(31) for k in spec.attributes},{"amount":range(11)})
    result=FormalVerifier(spec,d).verify_no_profitable_deviation("deviation")
    expected=FormalStatus.FORMALLY_VIOLATED if violated else FormalStatus.FORMALLY_SATISFIED_WITHIN_DOMAIN
    assert result.status is expected
    assert not violated or result.witness.agreement


def test_symbolic_multiplication_rejected():
    raw=yaml.safe_load((BENCH/"cliff_low_cost.yaml").read_text())
    raw["attributes"]["rate"]={"type":"decimal","unit":"rate","lower":0,"upper":1,"observable":True,"manipulable":False,"role":"latent"}
    raw["utility"]={"mul":[{"var":"rate"},{"var":"resources"}]}
    spec=parse_spec(raw)
    d=domain({"income":[10],"rate":["0.5"]},{"amount":[1]})
    result=FormalVerifier(spec,d).verify_no_profitable_deviation("deviation")
    assert result.status is FormalStatus.UNSUPPORTED_FRAGMENT
    assert "symbolic x symbolic" in result.message


def test_formal_result_json_contains_domain_identity():
    spec=load_spec(BENCH/"safe_high_cost.yaml"); d=domain({"income":range(5)},{"amount":range(3)})
    text=formal_result_json(FormalVerifier(spec,d).verify_no_profitable_deviation("deviation"))
    assert '"domain_hash"' in text and '"solver_version": "4.15.3"' in text


def test_generated_fixed_input_differential_500_cases():
    rng=random.Random(20260926)
    paths=list(BENCH.glob("*.yaml")); checked=0
    for _ in range(500):
        path=rng.choice(paths); spec=load_spec(path)
        state={name:Decimal(rng.randint(int(defn.lower),int(defn.upper))) for name,defn in spec.attributes.items()}
        amount=Decimal(rng.randint(0,min(10,int(state.get("reported_income",state.get("income",0))))))
        action=ActionInstance("deviation",{"amount":amount})
        d=domain({k:[v] for k,v in state.items()},{"amount":[amount]})
        formal=FormalVerifier(spec,d).evaluate_fixed(state,action); runtime=evaluate(spec,state,action)
        assert formal["state"]==runtime.resulting_state.values
        assert formal["outputs"]==runtime.outcome.rule_outputs
        assert formal["utility"]==runtime.utility
        checked+=1
    assert checked==500
