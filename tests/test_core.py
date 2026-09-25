from decimal import Decimal
from pathlib import Path

import pytest
import yaml

from incentive_fuzzer import (
    ActionInstance, IncentiveSpecError, PropertyStatus, canonical_yaml,
    evaluate, evaluate_properties, load_spec, parse_spec, spec_hash,
)

ROOT = Path(__file__).parents[1]
EXAMPLES = ROOT / "examples"


@pytest.fixture(params=["scholarship_cliff", "linear_phase_out", "stacked_programs", "procurement_threshold", "honest_reporting_control"])
def spec(request):
    return load_spec(EXAMPLES / f"{request.param}.yaml")


def test_all_fixtures_parse(spec):
    assert spec.incentive_spec_version == "0.1"


def test_canonical_round_trip(spec):
    reparsed = parse_spec(yaml.safe_load(canonical_yaml(spec)))
    assert canonical_yaml(reparsed) == canonical_yaml(spec)
    assert spec_hash(reparsed) == spec_hash(spec)


def test_hash_is_sha256(spec):
    assert len(spec_hash(spec)) == 64


@pytest.mark.parametrize("income,benefit,resources", [
    (499999, 100000, 599999), (500000, 0, 500000), (500001, 0, 500001),
])
def test_scholarship_boundaries(income, benefit, resources):
    spec = load_spec(EXAMPLES / "scholarship_cliff.yaml")
    result = evaluate(spec, {"true_income": income, "reported_income": income})
    assert result.outcome.rule_outputs["benefit"] == Decimal(benefit)
    assert result.outcome.rule_outputs["resources"] == Decimal(resources)


def test_scholarship_reduce_work_golden():
    spec = load_spec(EXAMPLES / "scholarship_cliff.yaml")
    result = evaluate(spec, {"true_income": 500001, "reported_income": 500001}, ActionInstance("reduce_work", {"amount": 2}))
    assert result.resulting_state.values == {"true_income": Decimal(499999), "reported_income": Decimal(499999)}
    assert result.action_cost == 0
    assert result.utility == Decimal(599999)
    assert [step.phase for step in result.trace] == ["state", "state", "action", "transition", "transition", "cost", "rule", "rule", "utility", "designer", "designer"]


def test_misreport_changes_report_only():
    spec = load_spec(EXAMPLES / "scholarship_cliff.yaml")
    result = evaluate(spec, {"true_income": 500001, "reported_income": 500001}, ActionInstance("misreport_income", {"amount": 2}))
    assert result.resulting_state.values["true_income"] == Decimal(500001)
    assert result.resulting_state.values["reported_income"] == Decimal(499999)
    assert result.utility == Decimal(600001)


@pytest.mark.parametrize("income,expected", [(479999, 100000), (480000, 100000), (620000, 0), (620001, 0)])
def test_phase_out_boundaries(income, expected):
    result = evaluate(load_spec(EXAMPLES / "linear_phase_out.yaml"), {"income": income})
    assert result.outcome.rule_outputs["benefit"] == Decimal(expected)


def test_phase_out_midpoint_exact_decimal():
    result = evaluate(load_spec(EXAMPLES / "linear_phase_out.yaml"), {"income": 550000})
    # Exact evaluation of the explicitly declared finite-decimal slope.
    assert result.outcome.rule_outputs["benefit"] == Decimal("50000.0000000000010000")


@pytest.mark.parametrize("income,a,b,total", [(9, 8, 5, 13), (10, 8, 5, 13), (11, 0, 5, 5), (12, 0, 0, 0), (13, 0, 0, 0)])
def test_stacked_programs_golden(income, a, b, total):
    result = evaluate(load_spec(EXAMPLES / "stacked_programs.yaml"), {"income": income})
    assert result.outcome.rule_outputs["program_a"] == Decimal(a)
    assert result.outcome.rule_outputs["program_b"] == Decimal(b)
    assert result.outcome.rule_outputs["total_transfer"] == Decimal(total)


@pytest.mark.parametrize("value,cost", [(99, 0), (100, 20), (101, 20)])
def test_procurement_inclusive_threshold(value, cost):
    result = evaluate(load_spec(EXAMPLES / "procurement_threshold.yaml"), {"transaction_value": value})
    assert result.outcome.rule_outputs["administrative_cost"] == Decimal(cost)


def test_procurement_action_cost_timing():
    spec = load_spec(EXAMPLES / "procurement_threshold.yaml")
    result = evaluate(spec, {"transaction_value": 101}, ActionInstance("reduce_scope", {"amount": 2}))
    assert result.outcome.rule_outputs["administrative_cost"] == 0
    assert result.outcome.rule_outputs["retained_value"] == 99
    assert result.action_cost == 2
    assert result.utility == 97


def test_honest_reporting_control_property():
    results = {r.property_id: r for r in evaluate_properties(load_spec(EXAMPLES / "honest_reporting_control.yaml"))}
    assert results["P5"].status is PropertyStatus.SATISFIED_ON_ENUMERATED_DOMAIN
    assert results["P6"].status is PropertyStatus.SATISFIED_ON_ENUMERATED_DOMAIN


def test_scholarship_property_detects_violation():
    results = {r.property_id: r for r in evaluate_properties(load_spec(EXAMPLES / "scholarship_cliff.yaml"))}
    assert results["P1"].status is PropertyStatus.SATISFIED_ON_ENUMERATED_DOMAIN
    assert results["P4"].status is PropertyStatus.VIOLATED
    assert results["P4"].violation.witness["amount"] == 2


def test_stacked_drop_violation():
    result = evaluate_properties(load_spec(EXAMPLES / "stacked_programs.yaml"))[0]
    assert result.status is PropertyStatus.VIOLATED
    assert "drop" in result.violation.message


def test_determinism_and_trace(spec):
    state = {name: definition.lower for name, definition in spec.attributes.items()}
    a = evaluate(spec, state)
    b = evaluate(spec, state)
    assert a == b


def test_zero_action_identity():
    spec = load_spec(EXAMPLES / "linear_phase_out.yaml")
    result = evaluate(spec, {"income": 500000}, ActionInstance("reduce_income", {"amount": 0}))
    assert result.resulting_state.values["income"] == Decimal(500000)


@pytest.mark.parametrize("amount", [-1, 100001])
def test_action_control_bounds(amount):
    spec = load_spec(EXAMPLES / "scholarship_cliff.yaml")
    with pytest.raises(IncentiveSpecError, match="outside"):
        evaluate(spec, {"true_income": 500001, "reported_income": 500001}, ActionInstance("reduce_work", {"amount": amount}))


def test_state_bounds():
    with pytest.raises(IncentiveSpecError, match="outside"):
        evaluate(load_spec(EXAMPLES / "stacked_programs.yaml"), {"income": -1})


def test_infeasible_action():
    spec = load_spec(EXAMPLES / "stacked_programs.yaml")
    with pytest.raises(IncentiveSpecError, match="infeasible"):
        evaluate(spec, {"income": 1}, ActionInstance("reduce_income", {"amount": 2}))


def test_unknown_action():
    with pytest.raises(IncentiveSpecError, match="Unknown action"):
        evaluate(load_spec(EXAMPLES / "stacked_programs.yaml"), {"income": 1}, ActionInstance("invented", {}))


def test_state_field_mismatch():
    with pytest.raises(IncentiveSpecError, match="State fields mismatch"):
        evaluate(load_spec(EXAMPLES / "stacked_programs.yaml"), {})


def test_unsupported_version():
    raw = yaml.safe_load((EXAMPLES / "stacked_programs.yaml").read_text())
    raw["incentive_spec_version"] = "1.0"
    with pytest.raises(IncentiveSpecError, match="only version '0.1'"):
        parse_spec(raw)


def test_unknown_expression_operator():
    raw = yaml.safe_load((EXAMPLES / "stacked_programs.yaml").read_text())
    raw["utility"] = {"eval": "income"}
    with pytest.raises(IncentiveSpecError, match="unsupported expression"):
        parse_spec(raw)


def test_invalid_add_units():
    raw = yaml.safe_load((EXAMPLES / "stacked_programs.yaml").read_text())
    raw["parameters"]["rate"] = {"type": "decimal", "unit": "rate", "value": "0.2", "provenance": "S"}
    raw["utility"] = {"add": [{"var": "income"}, {"var": "rate"}]}
    with pytest.raises(IncentiveSpecError, match="same non-boolean unit"):
        parse_spec(raw)


def test_invalid_money_unit():
    raw = yaml.safe_load((EXAMPLES / "stacked_programs.yaml").read_text())
    raw["attributes"]["income"]["unit"] = "rate"
    with pytest.raises(IncentiveSpecError, match="money type requires money unit"):
        parse_spec(raw)


def test_invalid_transition_target():
    raw = yaml.safe_load((EXAMPLES / "stacked_programs.yaml").read_text())
    raw["actions"]["reduce_income"]["transition"] = {"unknown": {"var": "income"}}
    with pytest.raises(IncentiveSpecError, match="manipulable attribute"):
        parse_spec(raw)


def test_immutable_transition_rejected():
    raw = yaml.safe_load((EXAMPLES / "honest_reporting_control.yaml").read_text())
    raw["actions"]["misreport"]["transition"]["true_income"] = {"var": "true_income"}
    with pytest.raises(IncentiveSpecError, match="manipulable attribute"):
        parse_spec(raw)


def test_negative_cost_rejected_at_evaluation():
    raw = yaml.safe_load((EXAMPLES / "stacked_programs.yaml").read_text())
    raw["actions"]["reduce_income"]["cost"] = {"const": {"value": -1, "unit": "money"}}
    spec = parse_spec(raw)
    with pytest.raises(IncentiveSpecError, match="cost evaluated negative"):
        evaluate(spec, {"income": 5}, ActionInstance("reduce_income", {"amount": 1}))


@pytest.mark.parametrize("op,expected_at_equal", [("lt", False), ("le", True), ("gt", False), ("ge", True), ("eq", True)])
def test_comparison_semantics(op, expected_at_equal):
    raw = yaml.safe_load((EXAMPLES / "stacked_programs.yaml").read_text())
    raw["rules"] = {"flag": {"if": {"condition": {op: [{"var": "income"}, {"var": "threshold_a"}]}, "then": {"const": {"value": 1, "unit": "money"}}, "else": {"const": {"value": 0, "unit": "money"}}}}}
    raw["utility"] = {"var": "flag"}; raw["designer_outcomes"] = {}; raw["properties"] = []
    result = evaluate(parse_spec(raw), {"income": 10})
    assert (result.outcome.rule_outputs["flag"] == 1) is expected_at_equal


def test_yaml_parse_error(tmp_path):
    path = tmp_path / "bad.yaml"; path.write_text("x: [")
    with pytest.raises(IncentiveSpecError, match="Invalid IncentiveSpec YAML"):
        load_spec(path)


def test_unsupported_property_status():
    raw = yaml.safe_load((EXAMPLES / "stacked_programs.yaml").read_text())
    raw["properties"] = [{"id": "PX", "kind": "general_incentive_compatibility", "domain": {"income": [1]}}]
    result = evaluate_properties(parse_spec(raw))[0]
    assert result.status is PropertyStatus.UNSUPPORTED


def test_property_without_domain_not_evaluated():
    raw = yaml.safe_load((EXAMPLES / "stacked_programs.yaml").read_text())
    raw["properties"] = [{"id": "P0", "kind": "budget_bound", "maximum": 10}]
    result = evaluate_properties(parse_spec(raw))[0]
    assert result.status is PropertyStatus.NOT_EVALUATED


def test_participation_uses_declared_minimum():
    raw = yaml.safe_load((EXAMPLES / "stacked_programs.yaml").read_text())
    raw["properties"] = [{"id": "P6", "kind": "participation", "minimum": 100, "domain": {"income": [1]}}]
    result = evaluate_properties(parse_spec(raw))[0]
    assert result.status is PropertyStatus.VIOLATED
