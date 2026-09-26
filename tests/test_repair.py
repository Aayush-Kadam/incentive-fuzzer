from decimal import Decimal
from pathlib import Path

import pytest

from incentive_fuzzer import load_spec
from incentive_fuzzer.core import evaluate, spec_hash
from incentive_fuzzer.game import enumerate_pure_nash, game_hash
from incentive_fuzzer.game_fixtures import aggregate_threshold_claim, safe_interaction_control
from incentive_fuzzer.population import BehavioralKind, BehavioralScenario, deterministic_grid, evaluate_population
from incentive_fuzzer.repair import (
    GateStatus, MutationResult, RegressionCheck, RepairBudget, RepairConstraint, RepairEngine,
    RepairEvaluation, RepairObjective, RepairParameter, RepairProblem, RepairSearchStatus,
    RepairStatus, classify_evaluation, edit_parameters, evaluate_constraints,
    generate_parameter_candidates, hard_cutoff_to_phase_out, lexicographic_best,
    make_candidate, multiply_action_cost, mutation_fragility, mutation_values,
    normalized_distance, pareto_frontier, regression_gate, repair_id, run_repair_loop,
)
from incentive_fuzzer.search import SearchBudget, SearchDomain, SearchEngine, SearchMethod, SearchProblem, SearchStatus
from incentive_fuzzer.verify import FormalDomain, FormalStatus, FormalVerifier


ROOT = Path(__file__).parents[1]
EX = ROOT / "examples"
D = Decimal


def scholarship_problem(spec):
    states = tuple({"true_income": D(x), "reported_income": D(x)} for x in range(499995, 500011))
    domain = SearchDomain({"true_income": tuple(), "reported_income": tuple()},
                          {"reduce_work": {"amount": tuple(D(x) for x in range(21))}},
                          {"true_income": D(1), "reported_income": D(1)}, states)
    return SearchProblem(spec, domain, allowed_actions=("reduce_work",),
                         action_kinds={"reduce_work": "productive_effort"})


def simple_problem():
    spec = load_spec(EX / "scholarship_cliff.yaml")
    parameters = (RepairParameter("award", D(100000), (D(50000), D(100000)), D(100000)),)
    return RepairProblem("tiny", spec_hash(spec), "finding", "property", parameters,
                         (RepairConstraint("coverage", "coverage", ">=", D("0.5")),),
                         (RepairObjective("max_residual_gain", "min"), RepairObjective("distance", "min")),
                         RepairBudget(10, 3, D(10)))


def make_eval(problem, value, residual, distance, passed=True):
    candidate = make_candidate(problem.parent_hash, "PARAMETER_EDIT", {"award": D(value)},
                               problem.parameters, None, f"hash-{value}")
    metrics = {"max_residual_gain": D(residual), "original_max_gain": D(10),
               "distance": D(distance), "coverage": D(1), "fiscal_deviation": D(0),
               "complexity": D(1), "harmful_equilibria": D(0), "mutation_fragility": D(0)}
    constraints = evaluate_constraints(problem.constraints, metrics)
    checks = (RegressionCheck("M2", "target", "PASS" if passed else "FAIL", passed),)
    return classify_evaluation(candidate, metrics, constraints, checks)


def test_repair_id_deterministic_and_sensitive():
    first = repair_id("parent", "family", {"x": D(1)}, "PARAMETER_GRID")
    assert first == repair_id("parent", "family", {"x": D(1)}, "PARAMETER_GRID")
    assert first != repair_id("parent", "family", {"x": D(2)}, "PARAMETER_GRID")


def test_normalized_distance():
    parameters = (RepairParameter("x", D(10), (D(5),), D(10)), RepairParameter("y", D(2), (D(4),), D(2)))
    assert normalized_distance(parameters, {"x": D(5), "y": D(4)}) == D("1.5")


def test_parameter_edit_changes_hash_without_mutating_parent():
    original = load_spec(EX / "scholarship_cliff.yaml")
    repaired = edit_parameters(original, {"award": D(50000)})
    assert original.parameters["award"].value == D(100000)
    assert repaired.parameters["award"].value == D(50000)
    assert spec_hash(original) != spec_hash(repaired)


def test_unknown_parameter_rejected():
    with pytest.raises(ValueError, match="unknown repair parameter"):
        edit_parameters(load_spec(EX / "scholarship_cliff.yaml"), {"missing": D(1)})


def test_structural_phaseout_has_exact_golden_values():
    repaired = hard_cutoff_to_phase_out(load_spec(EX / "scholarship_cliff.yaml"), "benefit",
                                        "reported_income", "award", D(480000), D(580000))
    for income, benefit in ((480000, 100000), (500000, 80000), (580000, 0)):
        result = evaluate(repaired, {"true_income": D(income), "reported_income": D(income)})
        assert result.outcome.rule_outputs["benefit"] == D(benefit)


def test_structural_transform_rejects_bad_range():
    with pytest.raises(ValueError, match="start"):
        hard_cutoff_to_phase_out(load_spec(EX / "scholarship_cliff.yaml"), "benefit",
                                 "reported_income", "award", D(500000), D(500000))


def test_phaseout_fresh_m2_refuzz_is_clean():
    repaired = hard_cutoff_to_phase_out(load_spec(EX / "scholarship_cliff.yaml"), "benefit",
                                        "reported_income", "award", D(480000), D(580000))
    result = SearchEngine(scholarship_problem(repaired)).run(SearchMethod.EXHAUSTIVE, SearchBudget(10000, 10000, 20))
    assert result.status is SearchStatus.EXHAUSTIVE_NO_VIOLATION


def test_phaseout_m3_regression_unsat():
    repaired = hard_cutoff_to_phase_out(load_spec(EX / "scholarship_cliff.yaml"), "benefit",
                                        "reported_income", "award", D(480000), D(580000))
    domain = FormalDomain({"true_income": tuple(D(x) for x in range(499995, 500011)),
                           "reported_income": tuple(D(x) for x in range(499995, 500011))},
                          {"amount": tuple(D(x) for x in range(21))})
    result = FormalVerifier(repaired, domain).verify_no_profitable_deviation("reduce_work")
    assert result.status is FormalStatus.FORMALLY_SATISFIED_WITHIN_DOMAIN


def test_phaseout_m4_population_regression_zero_share():
    repaired = hard_cutoff_to_phase_out(load_spec(EX / "scholarship_cliff.yaml"), "benefit",
                                        "reported_income", "award", D(480000), D(580000))
    population = deterministic_grid("repair", {"true_income": tuple(range(499995, 500011)),
                                                 "reported_income": tuple(range(499995, 500011))},
                                    (0, 1, 10, 100, 1000, 50000, 99999, 100000), (0, .5, 1, 2), correlated=True)
    result = evaluate_population(repaired, population,
                                 BehavioralScenario("B0", BehavioralKind.FULL_OPTIMIZATION),
                                 {"reduce_work": {"amount": tuple(range(21))}})
    assert result.summary.profitable_share == 0


def test_cost_multiplier_repairs_procurement():
    original = load_spec(EX / "procurement_threshold.yaml")
    repaired = multiply_action_cost(original, "reduce_scope", D(19))
    baseline = evaluate(repaired, {"transaction_value": D(100)})
    changed = evaluate(repaired, {"transaction_value": D(100)},
                       __import__("incentive_fuzzer").ActionInstance("reduce_scope", {"amount": D(1)}))
    assert changed.utility == baseline.utility


def test_generate_parameter_candidates_is_deterministic():
    problem = simple_problem()
    spec = load_spec(EX / "scholarship_cliff.yaml")
    builder = lambda changes: (edit_parameters(spec, changes), spec_hash(edit_parameters(spec, changes)))
    first = generate_parameter_candidates(problem, builder)
    second = generate_parameter_candidates(problem, builder)
    assert [item.repair_id for item in first] == [item.repair_id for item in second]
    assert len(first) == 1


@pytest.mark.parametrize("operator,actual,bound,passed", [
    ("<=", "1", "1", True), (">=", "1", "2", False), ("==", "2", "2", True),
    ("<", "1", "2", True), (">", "2", "2", False),
])
def test_constraint_operators(operator, actual, bound, passed):
    constraint = RepairConstraint("c", "x", operator, D(bound))
    assert evaluate_constraints((constraint,), {"x": D(actual)})[0].passed is passed


def test_trivial_zero_award_fails_coverage_constraint():
    problem = simple_problem()
    candidate = make_candidate(problem.parent_hash, "PARAMETER_EDIT", {"award": D(0)},
                               problem.parameters, None, "zero")
    metrics = {"max_residual_gain": D(0), "coverage": D(0)}
    evaluation = classify_evaluation(candidate, metrics, evaluate_constraints(problem.constraints, metrics),
                                     (RegressionCheck("M2", "target", "PASS", True),))
    assert evaluation.repair_status is RepairStatus.CONSTRAINT_VIOLATION


def test_regression_gate_rejects_failed_layer():
    result = regression_gate("r", (RegressionCheck("M2", "target", "PASS", True),
                                    RegressionCheck("M5", "equilibrium", "FAIL", False)))
    assert result.gate_status is GateStatus.REPAIR_FAIL
    assert result.failure_reasons == ("M5:equilibrium:FAIL",)


def test_repair_induced_vulnerability_is_first_class():
    problem = simple_problem()
    candidate = make_candidate(problem.parent_hash, "PARAMETER_EDIT", {"award": D(50000)},
                               problem.parameters, None, "candidate")
    metrics = {"max_residual_gain": D(0), "coverage": D(1)}
    checks = (RegressionCheck("M2", "isolated target", "PASS", True),
              RegressionCheck("M5", "new harmful equilibrium",
                              RepairStatus.REPAIR_INDUCED_VULNERABILITY.value, False))
    evaluation = classify_evaluation(candidate, metrics, evaluate_constraints(problem.constraints, metrics), checks)
    assert evaluation.repair_status is RepairStatus.REPAIR_INDUCED_VULNERABILITY


def test_pareto_frontier_removes_dominated_candidate():
    problem = simple_problem()
    a, b, c = make_eval(problem, 50000, 0, 1), make_eval(problem, 60000, 0, 2), make_eval(problem, 70000, 1, 0)
    frontier = pareto_frontier((a, b, c), problem.objectives, passes_only=False)
    assert {item.candidate.repair_id for item in frontier.candidates} == {a.candidate.repair_id, c.candidate.repair_id}


def test_lexicographic_ordering_is_explicit():
    problem = simple_problem()
    a, b = make_eval(problem, 50000, 0, 2), make_eval(problem, 60000, 0, 1)
    assert lexicographic_best((a, b), ("max_residual_gain", "distance")) == b


def test_mutation_neighborhood_and_fragility():
    assert mutation_values(D(5), D(0), D(10)) == (D(0), D(4), D(6), D(10))
    results = (MutationResult("x", D(5), D(4), False, "clean"),
               MutationResult("x", D(5), D(6), True, "violation"))
    assert mutation_fragility(results) == D("0.5")


def test_game_repair_boundary_is_exact():
    tied = enumerate_pure_nash(aggregate_threshold_claim(bonus=D(4), cost=D(4), threshold=2))
    repaired = enumerate_pure_nash(aggregate_threshold_claim(bonus=D(3), cost=D(4), threshold=2))
    tied_profiles = {tuple(eq.joint_action.actions.values()) for eq in tied.equilibria}
    repaired_profiles = {tuple(eq.joint_action.actions.values()) for eq in repaired.equilibria}
    assert ("MANIPULATE", "MANIPULATE") in tied_profiles
    assert repaired_profiles == {("HONEST", "HONEST")}


def test_safe_control_requires_no_repair():
    equilibria = enumerate_pure_nash(safe_interaction_control()).equilibria
    assert {tuple(eq.joint_action.actions.values()) for eq in equilibria} == {("HONEST", "HONEST")}


def test_repair_engine_returns_pareto_set():
    problem = simple_problem()
    evaluations = {value: make_eval(problem, value, 0, index) for index, value in enumerate((50000, 60000), 1)}
    candidates = tuple(item.candidate for item in evaluations.values())
    result = RepairEngine().run(problem, candidates, lambda candidate: evaluations[int(candidate.parameter_changes["award"])])
    assert result.status is RepairSearchStatus.PARETO_SET_FOUND
    assert result.candidates_evaluated == 2


def test_no_feasible_repair_result():
    problem = simple_problem()
    failed = make_eval(problem, 50000, 5, 1)
    result = RepairEngine().run(problem, (failed.candidate,), lambda _: failed)
    assert result.status is RepairSearchStatus.NO_FEASIBLE_REPAIR_FOUND


def test_loop_stops_when_no_target_violation():
    result = run_repair_loop(None, RepairBudget(), lambda *_: None)
    assert result.stop_reason == "NO_TARGET_VIOLATION"


def test_loop_stops_on_passing_regression():
    problem = simple_problem()
    passed = make_eval(problem, 50000, 0, 1)
    result = run_repair_loop("ce-1", RepairBudget(max_iterations=3), lambda *_: passed)
    assert result.stop_reason == "REGRESSION_SUITE_PASSED"
    assert len(result.iterations) == 1


def test_loop_detects_repeated_candidate():
    problem = simple_problem()
    failed = make_eval(problem, 50000, 1, 1)
    result = run_repair_loop("ce-1", RepairBudget(max_iterations=3), lambda *_: failed)
    assert result.stop_reason == "REPEATED_CANDIDATE"


def test_game_hash_changes_across_parameter_repairs():
    assert game_hash(aggregate_threshold_claim(cost=D(2))) != game_hash(aggregate_threshold_claim(cost=D(3)))
