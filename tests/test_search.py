from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import pytest

from incentive_fuzzer import load_spec
from incentive_fuzzer.search import (
    ReductionStatus, SearchBudget, SearchDomain, SearchEngine, SearchMethod,
    SearchProblem, SearchStatus, boundary_candidates, deduplicate,
    extract_boundaries, finding_to_json, reduce_finding, replay_finding,
)

ROOT = Path(__file__).parents[1]
EXAMPLES = ROOT / "examples"
BENCH = ROOT / "benchmarks" / "m2" / "specs"


def problem(path, states, controls, steps=None, actions=(), records=None, action_kinds=None):
    spec = load_spec(path)
    domain = SearchDomain(
        {k: tuple(Decimal(str(x)) for x in v) for k, v in states.items()},
        {a: {k: tuple(Decimal(str(x)) for x in v) for k, v in c.items()} for a, c in controls.items()},
        {k: Decimal(str(v)) for k, v in (steps or {}).items()},
        None if records is None else tuple({k: Decimal(str(v)) for k, v in row.items()} for row in records),
    )
    return SearchProblem(spec, domain, allowed_actions=actions, action_kinds=action_kinds or {})


@pytest.fixture
def scholarship_problem():
    return problem(EXAMPLES / "scholarship_cliff.yaml",
        {"true_income": [499999, 500000, 500001, 500002], "reported_income": [499999, 500000, 500001, 500002]},
        {"reduce_work": {"amount": [0, 1, 2, 3]}, "misreport_income": {"amount": [0, 1, 2, 3]}},
        {"true_income": 1, "reported_income": 1}, actions=("reduce_work",),
        records=[{"true_income": x, "reported_income": x} for x in [499999, 500000, 500001, 500002]],
        action_kinds={"reduce_work": "productive_effort"})


def test_boundary_extraction_scholarship(scholarship_problem):
    boundaries = extract_boundaries(scholarship_problem.spec)
    assert any(b.attribute == "reported_income" and b.value == 500000 and b.operator == "lt" for b in boundaries)


def test_boundary_extraction_phase_out():
    boundaries = extract_boundaries(load_spec(EXAMPLES / "linear_phase_out.yaml"))
    assert boundaries == ()  # v0.1 extracts comparisons, not min/max kinks.


def test_boundary_candidates_explain_origin(scholarship_problem):
    candidates = list(boundary_candidates(scholarship_problem))
    assert candidates
    assert all(c.boundary_origin is not None and "crosses" in c.generation_metadata["reason"] for c in candidates)


@pytest.mark.parametrize("method", list(SearchMethod))
def test_search_methods_find_scholarship(method, scholarship_problem):
    result = SearchEngine(scholarship_problem).run(method, SearchBudget(10000, 10000, 10), seed=7)
    assert result.status is SearchStatus.VIOLATION_FOUND
    assert result.findings
    assert all(replay_finding(scholarship_problem.spec, f) for f in result.findings)


def test_boundary_search_is_efficient_on_scholarship(scholarship_problem):
    engine = SearchEngine(scholarship_problem)
    boundary = engine.run("boundary", SearchBudget(10000, 10000, 10))
    exhaustive = engine.run("exhaustive", SearchBudget(10000, 10000, 10))
    assert boundary.statistics.evaluations_to_first_violation < exhaustive.statistics.evaluations_to_first_violation


def test_budget_exhaustion(scholarship_problem):
    result = SearchEngine(scholarship_problem).run("exhaustive", SearchBudget(1, 1, 10))
    assert result.status is SearchStatus.SEARCH_BUDGET_EXHAUSTED


def test_deterministic_config(scholarship_problem):
    engine = SearchEngine(scholarship_problem)
    a = engine.run("property", seed=13)
    b = engine.run("property", seed=13)
    assert [f.finding_id for f in a.raw_findings] == [f.finding_id for f in b.raw_findings]
    assert a.statistics.evaluation_count == b.statistics.evaluation_count


def test_finding_json_and_replay(scholarship_problem):
    finding = SearchEngine(scholarship_problem).run("boundary").findings[0]
    text = finding_to_json(finding)
    assert '"replay_status": "REPLAYED"' in text
    assert replay_finding(scholarship_problem.spec, finding)


def test_replay_rejects_wrong_policy(scholarship_problem):
    finding = SearchEngine(scholarship_problem).run("boundary").findings[0]
    assert not replay_finding(load_spec(EXAMPLES / "linear_phase_out.yaml"), finding)


def test_deduplication_collapses_equivalent_findings(scholarship_problem):
    result = SearchEngine(scholarship_problem).run("exhaustive")
    assert len(deduplicate(result.raw_findings)) <= len(result.raw_findings)
    assert len(result.raw_findings) > len(result.findings)


def test_reduction_produces_minimal_scholarship_case(scholarship_problem):
    finding = max(SearchEngine(scholarship_problem).run("boundary").raw_findings, key=lambda f: sum(f.action.controls.values()))
    reduced = reduce_finding(scholarship_problem, finding, SearchBudget(10000, 10000, 10))
    assert reduced.reduction_status in {ReductionStatus.REDUCED.value, ReductionStatus.ALREADY_MINIMAL_UNDER_OBJECTIVE.value}
    assert sum(reduced.action.controls.values()) == Decimal(1)
    assert reduced.baseline_state["true_income"] == Decimal(500000)
    assert replay_finding(scholarship_problem.spec, reduced)


def test_honest_reporting_negative_control():
    p = problem(EXAMPLES / "honest_reporting_control.yaml",
        {"true_income": range(0, 21), "reported_income": range(0, 21)},
        {"misreport": {"amount": range(0, 11)}}, actions=("misreport",))
    result = SearchEngine(p).run("exhaustive", SearchBudget(20000, 20000, 20))
    assert result.status is SearchStatus.EXHAUSTIVE_NO_VIOLATION


@pytest.mark.parametrize("name,expected", [
    ("cliff_low_cost", True), ("cliff_small_award", True), ("inclusive_cliff", True),
    ("cliff_cost_one", True), ("safe_high_cost", False), ("safe_zero_award", False),
    ("reported_cliff", True), ("reported_safe_penalty", False), ("stacked_close", True),
    ("stacked_wide", True), ("boundary_at_lower", True), ("boundary_at_upper", True),
])
def test_frozen_benchmark_exhaustive_ground_truth(name, expected):
    spec = load_spec(BENCH / f"{name}.yaml")
    states = {k: range(0, 31) for k in spec.attributes}
    p = problem(BENCH / f"{name}.yaml", states, {"deviation": {"amount": range(0, 11)}}, actions=("deviation",))
    result = SearchEngine(p).run("exhaustive", SearchBudget(50000, 50000, 20))
    assert bool(result.raw_findings) is expected


def test_reported_finding_classification():
    p = problem(BENCH / "reported_cliff.yaml", {"true_income": range(0, 31), "reported_income": range(0, 31)},
                {"deviation": {"amount": range(0, 11)}}, actions=("deviation",), action_kinds={"deviation": "report_only"})
    findings = SearchEngine(p).run("boundary", SearchBudget(10000, 10000, 10)).findings
    assert findings and all(f.if_cwe_id == "IF-005" for f in findings)


def test_search_does_not_mutate_spec(scholarship_problem):
    before = scholarship_problem.spec.canonical_data.copy()
    SearchEngine(scholarship_problem).run("combined")
    assert scholarship_problem.spec.canonical_data == before


def test_boundary_origin_requires_truth_change():
    p = problem(BENCH / "stacked_close.yaml", {"income": range(0, 31)},
                {"deviation": {"amount": range(0, 11)}}, actions=("deviation",))
    exhaustive = SearchEngine(p).run("exhaustive", SearchBudget(50000, 50000, 10))
    boundary = SearchEngine(p).run("boundary", SearchBudget(50000, 50000, 10))
    ground = {f.if_cwe_id for f in exhaustive.findings}
    assert {f.if_cwe_id for f in boundary.findings} <= ground
