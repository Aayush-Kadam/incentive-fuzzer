from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass, field
from decimal import Decimal
from enum import Enum
from hashlib import sha256
from itertools import product
import json
from time import monotonic
from typing import Any, Callable, Mapping

from .core import InstitutionSpec, parse_spec, spec_hash


class RepairStatus(str, Enum):
    TARGET_FIXED = "TARGET_FIXED"
    PARTIALLY_FIXED = "PARTIALLY_FIXED"
    TARGET_NOT_FIXED = "TARGET_NOT_FIXED"
    REGRESSION_FAILURE = "REGRESSION_FAILURE"
    REPAIR_INDUCED_VULNERABILITY = "REPAIR_INDUCED_VULNERABILITY"
    CONSTRAINT_VIOLATION = "CONSTRAINT_VIOLATION"
    UNSUPPORTED = "UNSUPPORTED"
    NO_REPAIR_NEEDED = "NO_REPAIR_NEEDED"


class GateStatus(str, Enum):
    REPAIR_PASS = "REPAIR_PASS"
    REPAIR_FAIL = "REPAIR_FAIL"


class RepairSearchStatus(str, Enum):
    REPAIR_FOUND = "REPAIR_FOUND"
    PARETO_SET_FOUND = "PARETO_SET_FOUND"
    SEARCH_EXHAUSTED = "SEARCH_EXHAUSTED"
    NO_FEASIBLE_REPAIR_FOUND = "NO_FEASIBLE_REPAIR_FOUND"
    NO_REPAIR_NEEDED = "NO_REPAIR_NEEDED"


@dataclass(frozen=True)
class RepairBudget:
    max_candidates: int = 100
    max_iterations: int = 5
    max_seconds: Decimal = Decimal("120")


@dataclass(frozen=True)
class RepairParameter:
    name: str
    original: Decimal
    values: tuple[Decimal, ...]
    scale: Decimal = Decimal("1")

    def __post_init__(self) -> None:
        if not self.values or self.scale <= 0:
            raise ValueError("repair parameter requires values and positive scale")


@dataclass(frozen=True)
class RepairConstraint:
    id: str
    metric: str
    operator: str
    bound: Decimal


@dataclass(frozen=True)
class RepairObjective:
    metric: str
    direction: str

    def __post_init__(self) -> None:
        if self.direction not in {"min", "max"}:
            raise ValueError("objective direction must be min or max")


@dataclass(frozen=True)
class RepairProblem:
    id: str
    parent_hash: str
    target_finding: str
    target_property: str
    parameters: tuple[RepairParameter, ...]
    constraints: tuple[RepairConstraint, ...]
    objectives: tuple[RepairObjective, ...]
    budget: RepairBudget = RepairBudget()


@dataclass(frozen=True)
class RepairCandidate:
    repair_id: str
    parent_spec_hash: str
    candidate_spec_hash: str
    parameter_changes: Mapping[str, Decimal]
    distance_from_original: Decimal
    repair_family: str
    provenance: str
    repair_iteration: int = 0
    parent_repair_id: str | None = None
    counterexample_id: str | None = None
    mechanism: Any = field(default=None, compare=False, repr=False)


@dataclass(frozen=True)
class ConstraintResult:
    constraint_id: str
    passed: bool
    actual: Decimal
    operator: str
    bound: Decimal


@dataclass(frozen=True)
class RegressionCheck:
    layer: str
    check: str
    status: str
    passed: bool | None
    details: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RepairEvaluation:
    candidate: RepairCandidate
    metrics: Mapping[str, Decimal]
    constraints: tuple[ConstraintResult, ...]
    regressions: tuple[RegressionCheck, ...]
    repair_status: RepairStatus
    gate_status: GateStatus


@dataclass(frozen=True)
class RepairFrontier:
    objectives: tuple[RepairObjective, ...]
    candidates: tuple[RepairEvaluation, ...]


@dataclass(frozen=True)
class MutationResult:
    parameter: str
    baseline: Decimal
    mutated: Decimal
    failed: bool
    reason: str


@dataclass(frozen=True)
class RepairRegressionResult:
    repair_id: str
    gate_status: GateStatus
    checks: tuple[RegressionCheck, ...]
    failure_reasons: tuple[str, ...]


@dataclass(frozen=True)
class RepairSearchResult:
    problem_id: str
    status: RepairSearchStatus
    evaluations: tuple[RepairEvaluation, ...]
    frontier: RepairFrontier
    candidates_evaluated: int
    runtime_seconds: Decimal
    stop_reason: str


@dataclass(frozen=True)
class RepairIteration:
    iteration: int
    counterexample_id: str | None
    chosen_repair_id: str | None
    status: str


@dataclass(frozen=True)
class RepairLoopResult:
    iterations: tuple[RepairIteration, ...]
    stop_reason: str
    final_repair_id: str | None


def _norm(value: Any) -> Any:
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, Enum):
        return value.value
    if hasattr(value, "__dataclass_fields__"):
        return _norm(asdict(value))
    if isinstance(value, Mapping):
        return {str(key): _norm(value[key]) for key in sorted(value)}
    if isinstance(value, (tuple, list)):
        return [_norm(item) for item in value]
    return value


def repair_id(parent_hash: str, family: str, changes: Mapping[str, Decimal], provenance: str) -> str:
    payload = {"parent": parent_hash, "family": family, "changes": changes, "provenance": provenance}
    return sha256(json.dumps(_norm(payload), sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:20]


def normalized_distance(parameters: tuple[RepairParameter, ...], changes: Mapping[str, Decimal]) -> Decimal:
    definitions = {parameter.name: parameter for parameter in parameters}
    return sum((abs(value - definitions[name].original) / definitions[name].scale
                for name, value in changes.items()), Decimal("0"))


def edit_parameters(spec: InstitutionSpec, changes: Mapping[str, Decimal]) -> InstitutionSpec:
    raw = deepcopy(spec.canonical_data)
    for name, value in changes.items():
        if name not in raw.get("parameters", {}):
            raise ValueError(f"unknown repair parameter {name}")
        raw["parameters"][name]["value"] = value
    raw["institution"]["version"] = f"{raw['institution']['version']}-repair"
    return parse_spec(raw)


def hard_cutoff_to_phase_out(spec: InstitutionSpec, rule_name: str, income_symbol: str,
                             award_parameter: str, start: Decimal, end: Decimal) -> InstitutionSpec:
    if start >= end:
        raise ValueError("phase-out start must be below end")
    raw = deepcopy(spec.canonical_data)
    rule = raw["rules"].get(rule_name)
    if not isinstance(rule, Mapping) or "if" not in rule:
        raise ValueError("structural transform requires a hard-cutoff if rule")
    branch = rule["if"]
    if branch.get("then") != {"var": award_parameter}:
        raise ValueError("hard-cutoff award branch is unsupported")
    otherwise = branch.get("else", {}).get("const", {})
    if Decimal(str(otherwise.get("value", "NaN"))) != 0:
        raise ValueError("hard-cutoff else branch must be zero")
    award = Decimal(str(raw["parameters"][award_parameter]["value"]))
    rate = award / (end - start)
    if rate * (end - start) != award:
        raise ValueError("phase-out rate must be exactly representable")
    raw["parameters"]["phase_out_start"] = {"type": "money", "value": start, "provenance": "A"}
    raw["parameters"]["phase_out_end"] = {"type": "money", "value": end, "provenance": "A"}
    raw["parameters"]["withdrawal_rate"] = {"type": "decimal", "unit": "rate", "value": rate, "provenance": "A"}
    rules = {}
    for name, node in raw["rules"].items():
        if name == rule_name:
            raw_name = f"{rule_name}_uncapped"
            rules[raw_name] = {"mul": [{"var": "withdrawal_rate"},
                                        {"sub": [{"var": "phase_out_end"}, {"var": income_symbol}]}]}
            rules[name] = {"max": [{"const": {"value": 0, "unit": "money"}},
                                     {"min": [{"var": award_parameter}, {"var": raw_name}]}]}
        else:
            rules[name] = node
    raw["rules"] = rules
    raw["institution"]["version"] = f"{raw['institution']['version']}-phaseout"
    return parse_spec(raw)


def multiply_action_cost(spec: InstitutionSpec, action_name: str, multiplier: Decimal) -> InstitutionSpec:
    if multiplier < 0:
        raise ValueError("cost multiplier cannot be negative")
    raw = deepcopy(spec.canonical_data)
    if action_name not in raw.get("actions", {}):
        raise ValueError("unknown action")
    raw["parameters"]["repair_cost_multiplier"] = {
        "type": "decimal", "unit": "rate", "value": multiplier, "provenance": "A"}
    original = raw["actions"][action_name]["cost"]
    raw["actions"][action_name]["cost"] = {"mul": [{"var": "repair_cost_multiplier"}, original]}
    raw["institution"]["version"] = f"{raw['institution']['version']}-cost-repair"
    return parse_spec(raw)


def make_candidate(parent_hash: str, family: str, changes: Mapping[str, Decimal],
                   parameters: tuple[RepairParameter, ...], mechanism: Any,
                   candidate_hash: str, provenance: str = "PARAMETER_GRID",
                   iteration: int = 0, parent_repair_id: str | None = None,
                   counterexample_id: str | None = None) -> RepairCandidate:
    identifier = repair_id(parent_hash, family, changes, provenance)
    return RepairCandidate(identifier, parent_hash, candidate_hash, dict(changes),
                           normalized_distance(parameters, changes), family, provenance,
                           iteration, parent_repair_id, counterexample_id, mechanism)


def generate_parameter_candidates(problem: RepairProblem,
                                  builder: Callable[[Mapping[str, Decimal]], tuple[Any, str]],
                                  include_original: bool = False) -> tuple[RepairCandidate, ...]:
    candidates = []
    names = tuple(parameter.name for parameter in problem.parameters)
    originals = {parameter.name: parameter.original for parameter in problem.parameters}
    for values in product(*(parameter.values for parameter in problem.parameters)):
        changes = dict(zip(names, values))
        if not include_original and changes == originals:
            continue
        mechanism, identity = builder(changes)
        candidates.append(make_candidate(problem.parent_hash, "PARAMETER_EDIT", changes,
                                         problem.parameters, mechanism, identity))
        if len(candidates) >= problem.budget.max_candidates:
            break
    return tuple(candidates)


def evaluate_constraints(constraints: tuple[RepairConstraint, ...],
                         metrics: Mapping[str, Decimal]) -> tuple[ConstraintResult, ...]:
    operations = {"<=": lambda a, b: a <= b, ">=": lambda a, b: a >= b,
                  "==": lambda a, b: a == b, "<": lambda a, b: a < b, ">": lambda a, b: a > b}
    results = []
    for constraint in constraints:
        if constraint.metric not in metrics or constraint.operator not in operations:
            raise ValueError(f"cannot evaluate constraint {constraint.id}")
        actual = metrics[constraint.metric]
        results.append(ConstraintResult(constraint.id, operations[constraint.operator](actual, constraint.bound),
                                        actual, constraint.operator, constraint.bound))
    return tuple(results)


def regression_gate(repair_identifier: str, checks: tuple[RegressionCheck, ...]) -> RepairRegressionResult:
    failures = tuple(f"{check.layer}:{check.check}:{check.status}" for check in checks if check.passed is False)
    return RepairRegressionResult(repair_identifier, GateStatus.REPAIR_FAIL if failures else GateStatus.REPAIR_PASS,
                                  checks, failures)


def classify_evaluation(candidate: RepairCandidate, metrics: Mapping[str, Decimal],
                        constraints: tuple[ConstraintResult, ...], checks: tuple[RegressionCheck, ...]) -> RepairEvaluation:
    gate = regression_gate(candidate.repair_id, checks)
    if any(not result.passed for result in constraints):
        status = RepairStatus.CONSTRAINT_VIOLATION
    elif any(check.status == RepairStatus.REPAIR_INDUCED_VULNERABILITY.value for check in checks):
        status = RepairStatus.REPAIR_INDUCED_VULNERABILITY
    elif metrics.get("max_residual_gain", Decimal("0")) > 0:
        original = metrics.get("original_max_gain", metrics["max_residual_gain"])
        status = RepairStatus.PARTIALLY_FIXED if metrics["max_residual_gain"] < original else RepairStatus.TARGET_NOT_FIXED
    elif gate.gate_status is GateStatus.REPAIR_FAIL:
        status = RepairStatus.REGRESSION_FAILURE
    else:
        status = RepairStatus.TARGET_FIXED
    gate_status = GateStatus.REPAIR_PASS if status is RepairStatus.TARGET_FIXED else GateStatus.REPAIR_FAIL
    return RepairEvaluation(candidate, dict(metrics), constraints, checks, status, gate_status)


def dominates(left: RepairEvaluation, right: RepairEvaluation,
              objectives: tuple[RepairObjective, ...]) -> bool:
    no_worse = True
    strictly_better = False
    for objective in objectives:
        a, b = left.metrics[objective.metric], right.metrics[objective.metric]
        if objective.direction == "min":
            no_worse &= a <= b
            strictly_better |= a < b
        else:
            no_worse &= a >= b
            strictly_better |= a > b
    return no_worse and strictly_better


def pareto_frontier(evaluations: tuple[RepairEvaluation, ...],
                    objectives: tuple[RepairObjective, ...],
                    passes_only: bool = True) -> RepairFrontier:
    pool = tuple(item for item in evaluations if not passes_only or item.gate_status is GateStatus.REPAIR_PASS)
    frontier = tuple(item for item in pool if not any(dominates(other, item, objectives)
                                                     for other in pool if other is not item))
    return RepairFrontier(objectives, tuple(sorted(frontier, key=lambda item: item.candidate.repair_id)))


def lexicographic_best(evaluations: tuple[RepairEvaluation, ...], metrics: tuple[str, ...]) -> RepairEvaluation | None:
    feasible = [item for item in evaluations if item.gate_status is GateStatus.REPAIR_PASS]
    return min(feasible, key=lambda item: tuple(item.metrics[name] for name in metrics) + (item.candidate.repair_id,)) if feasible else None


def mutation_values(value: Decimal, lower: Decimal, upper: Decimal,
                    deltas: tuple[Decimal, ...] = (Decimal("1"), Decimal("5"), Decimal("10"))) -> tuple[Decimal, ...]:
    values = {candidate for delta in deltas for candidate in (value - delta, value + delta)
              if lower <= candidate <= upper}
    return tuple(sorted(values))


def mutation_fragility(results: tuple[MutationResult, ...]) -> Decimal:
    return (Decimal(sum(result.failed for result in results)) / Decimal(len(results))) if results else Decimal("0")


class RepairEngine:
    def run(self, problem: RepairProblem, candidates: tuple[RepairCandidate, ...],
            evaluator: Callable[[RepairCandidate], RepairEvaluation]) -> RepairSearchResult:
        started = monotonic()
        evaluations = []
        for candidate in candidates[:problem.budget.max_candidates]:
            if Decimal(str(monotonic() - started)) > problem.budget.max_seconds:
                break
            evaluations.append(evaluator(candidate))
        elapsed = Decimal(str(monotonic() - started))
        result_tuple = tuple(evaluations)
        frontier = pareto_frontier(result_tuple, problem.objectives)
        exhausted = len(evaluations) == min(len(candidates), problem.budget.max_candidates)
        if frontier.candidates:
            status, reason = RepairSearchStatus.PARETO_SET_FOUND, "non-dominated passing repairs found"
        elif exhausted:
            status, reason = RepairSearchStatus.NO_FEASIBLE_REPAIR_FOUND, "finite candidate grid exhausted"
        else:
            status, reason = RepairSearchStatus.SEARCH_EXHAUSTED, "runtime budget reached"
        return RepairSearchResult(problem.id, status, result_tuple, frontier, len(evaluations), elapsed, reason)


def run_repair_loop(initial_counterexample: str | None, budget: RepairBudget,
                    propose: Callable[[int, str | None, frozenset[str]], RepairEvaluation | None]) -> RepairLoopResult:
    history = []
    seen: set[str] = set()
    counterexample = initial_counterexample
    if counterexample is None:
        return RepairLoopResult((), "NO_TARGET_VIOLATION", None)
    for iteration in range(budget.max_iterations):
        evaluation = propose(iteration, counterexample, frozenset(seen))
        if evaluation is None:
            history.append(RepairIteration(iteration, counterexample, None, "NO_FEASIBLE_REPAIR_FOUND"))
            return RepairLoopResult(tuple(history), "NO_FEASIBLE_REPAIR_FOUND", None)
        identifier = evaluation.candidate.repair_id
        if identifier in seen:
            history.append(RepairIteration(iteration, counterexample, identifier, "REPEATED_CANDIDATE"))
            return RepairLoopResult(tuple(history), "REPEATED_CANDIDATE", identifier)
        seen.add(identifier)
        history.append(RepairIteration(iteration, counterexample, identifier, evaluation.gate_status.value))
        if evaluation.gate_status is GateStatus.REPAIR_PASS:
            return RepairLoopResult(tuple(history), "REGRESSION_SUITE_PASSED", identifier)
        counterexample = f"{counterexample}:next"
    return RepairLoopResult(tuple(history), "ITERATION_BUDGET_REACHED", history[-1].chosen_repair_id if history else None)
