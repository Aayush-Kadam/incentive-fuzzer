from decimal import Decimal as D
import pytest

from incentive_fuzzer import *


def spec(name="scholarship_cliff"):
    return load_spec(f"examples/{name}.yaml")


def pop(cost=0, income=500001):
    return PopulationSpecification("p",(AgentType("a",D(1),{"true_income":D(income),"reported_income":D(income)},fixed_cost=D(cost)),))


def b(kind=BehavioralKind.FULL_OPTIMIZATION, **kw):
    return BehavioralScenario(kind.value,kind,**kw)


def test_population_validation_and_hash():
    with pytest.raises(ValueError): PopulationSpecification("x",())
    with pytest.raises(ValueError): PopulationSpecification("x",(AgentType("a",D(-1),{}),))
    with pytest.raises(ValueError): PopulationSpecification("x",(AgentType("a",D(1),{}),AgentType("a",D(1),{})))
    assert population_hash(pop()) == population_hash(pop())


def test_grid_is_deterministic_normalized_and_correlated():
    p=deterministic_grid("g",{"true_income":(1,2),"reported_income":(1,2)},(0,1),correlated=True)
    assert len(p.members)==4 and sum(x.weight for x in p.members)==1
    assert p.members[0].state["true_income"]==p.members[0].state["reported_income"]
    assert p.members[0].provenance["state"].provenance is Provenance.S


def test_full_optimization_finds_cliff_and_designer_effect():
    r=evaluate_population(spec(),pop(),b(),{"reduce_work":{"amount":tuple(range(21))}})
    assert r.summary.profitable_share==1 and r.summary.response_share==1
    assert r.individuals[0].best_action.controls["amount"]==D(2)
    assert r.individuals[0].adjusted_gain==D(99998)
    assert r.summary.designer_change["fiscal_cost"]==D(100000)


def test_fixed_cost_and_satisficing_preserve_latent_gain_but_not_response():
    actions={"reduce_work":{"amount":tuple(range(21))}}
    assert evaluate_population(spec(),pop(99998),b(),actions).summary.profitable_share==0
    r=evaluate_population(spec(),pop(),b(BehavioralKind.SATISFICING,hurdle=D(100000)),actions)
    assert r.summary.profitable_share==1 and r.summary.response_share==0
    assert r.individuals[0].adjusted_gain==D(99998)
    assert r.summary.designer_change["fiscal_cost"]==0


def test_limited_search_understates_response():
    actions={"reduce_work":{"amount":tuple(range(21))}}
    full=evaluate_population(spec(),pop(income=500005),b(),actions)
    limited=evaluate_population(spec(),pop(income=500005),b(BehavioralKind.LIMITED_SEARCH,candidate_limit=3),actions)
    assert full.summary.profitable_share==1 and limited.summary.profitable_share==0


def test_cost_multiplier_applies_to_action_cost():
    p=PopulationSpecification("p",(AgentType("a",D(1),{"transaction_value":D(100)},cost_multiplier=D(2)),))
    r=evaluate_population(spec("procurement_threshold"),p,b(),{"reduce_scope":{"amount":tuple(range(11))}})
    assert r.individuals[0].adjusted_gain==D(17)


def test_sampling_reproducibility_and_wilson():
    p=PopulationSpecification("p",(AgentType("a",D(1),{"true_income":D(1),"reported_income":D(1)}),AgentType("b",D(3),{"true_income":D(2),"reported_income":D(2)})))
    assert population_hash(sample_weighted(p,20,7))==population_hash(sample_weighted(p,20,7))
    assert population_hash(sample_weighted(p,20,7))!=population_hash(sample_weighted(p,20,8))
    lo,hi=wilson_interval(5,10); assert 0 < lo < .5 < hi < 1
    with pytest.raises(ValueError): wilson_interval(0,0)


def test_honest_reporting_negative_control():
    p=PopulationSpecification("h",(AgentType("a",D(1),{"true_income":D(12),"reported_income":D(12)}),))
    r=evaluate_population(spec("honest_reporting_control"),p,b(),{"misreport":{"amount":tuple(range(11))}})
    assert r.summary.profitable_share==0
