"""Generate the frozen M2 synthetic suite from declarative case definitions."""
from pathlib import Path
import yaml

ROOT = Path(__file__).parents[1]
OUT = ROOT / "benchmarks" / "m2" / "specs"


def c(value, unit="money"):
    return {"const": {"value": value, "unit": unit}}


def v(name):
    return {"var": name}


def make_case(case_id, threshold, award, cost_rate, strict=True, reported=False, second=None):
    income_name = "reported_income" if reported else "income"
    attributes = {
        "true_income": {"type": "money", "lower": 0, "upper": 30, "observable": False,
                        "manipulable": False, "role": "latent"},
        income_name: {"type": "money", "lower": 0, "upper": 30, "observable": True,
                      "manipulable": True, "role": "reported" if reported else "latent"},
    } if reported else {
        "income": {"type": "money", "lower": 0, "upper": 30, "observable": True,
                   "manipulable": True, "role": "latent"}
    }
    transition = {income_name: {"sub": [v(income_name), v("amount")]}}
    condition = {"lt" if strict else "le": [v(income_name), v("threshold")]}
    rules = {"benefit_a": {"if": {"condition": condition, "then": v("award"), "else": c(0)}}}
    total = v("benefit_a")
    parameters = {
        "threshold": {"type": "money", "value": threshold, "provenance": "S"},
        "award": {"type": "money", "value": award, "provenance": "S"},
        "cost_rate": {"type": "decimal", "unit": "rate", "value": cost_rate, "provenance": "A"},
    }
    if second:
        parameters |= {
            "threshold_b": {"type": "money", "value": second[0], "provenance": "S"},
            "award_b": {"type": "money", "value": second[1], "provenance": "S"},
        }
        rules["benefit_b"] = {"if": {"condition": {"lt": [v(income_name), v("threshold_b")]},
                                        "then": v("award_b"), "else": c(0)}}
        rules["total_transfer"] = {"add": [v("benefit_a"), v("benefit_b")]}
        total = v("total_transfer")
    base_income = v("true_income" if reported else "income")
    rules["resources"] = {"add": [base_income, total]}
    return {
        "incentive_spec_version": "0.1",
        "institution": {"id": case_id, "name": case_id.replace("_", " ").title(),
                        "description": "Frozen synthetic M2 mechanism", "version": "1"},
        "parameters": parameters,
        "attributes": attributes,
        "actions": {"deviation": {
            "controls": {"amount": {"type": "money", "lower": 0, "upper": 10}},
            "feasibility": {"le": [v("amount"), v(income_name)]},
            "transition": transition,
            "cost": {"mul": [v("cost_rate"), v("amount")]},
        }},
        "rules": rules,
        "utility": {"sub": [v("resources"), v("action_cost")]},
        "designer_outcomes": {"fiscal_cost": total},
        "properties": [],
    }


CASES = [
    ("cliff_low_cost", 10, 8, 0, True, False, None, True, "IF-001"),
    ("cliff_small_award", 10, 2, 0, True, False, None, True, "IF-001"),
    ("inclusive_cliff", 10, 6, 0, False, False, None, True, "IF-001"),
    ("cliff_cost_one", 15, 8, 1, True, False, None, True, "IF-003"),
    ("safe_high_cost", 10, 5, 6, True, False, None, False, None),
    ("safe_zero_award", 10, 0, 0, True, False, None, False, None),
    ("reported_cliff", 10, 7, 0, True, True, None, True, "IF-005"),
    ("reported_safe_penalty", 10, 5, 6, True, True, None, False, None),
    ("stacked_close", 10, 5, 0, True, False, (12, 4), True, "IF-015"),
    ("stacked_wide", 8, 3, 0, True, False, (18, 4), True, "IF-015"),
    ("boundary_at_lower", 0, 5, 0, False, False, None, False, None),
    ("boundary_at_upper", 30, 5, 0, True, False, None, False, None),
]

OUT.mkdir(parents=True, exist_ok=True)
labels = []
for case in CASES:
    case_id, threshold, award, cost, strict, reported, second, known, family = case
    data = make_case(case_id, threshold, award, cost, strict, reported, second)
    (OUT / f"{case_id}.yaml").write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    labels.append({"id": case_id, "known_violation": known,
                   "expected_property": "no_profitable_deviation",
                   "expected_attack_family": family,
                   "derivation": "exhaustive enumeration over states 0..30 and action amounts 0..10"})
(ROOT / "benchmarks" / "m2" / "ground_truth.yaml").write_text(
    yaml.safe_dump({"frozen_suite_version": "1", "cases": labels}, sort_keys=False), encoding="utf-8")
