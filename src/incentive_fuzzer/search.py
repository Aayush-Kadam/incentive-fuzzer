from __future__ import annotations

from dataclasses import asdict, dataclass, field
from decimal import Decimal
from enum import Enum
from hashlib import sha256
from itertools import product
import json
import random
from time import perf_counter
from typing import Any, Iterable, Mapping

from .core import (
    ActionInstance, EvaluationResult, Expression, IncentiveSpecError,
    InstitutionSpec, ValueType, evaluate, spec_hash,
)


class SearchMethod(str, Enum):
    EXHAUSTIVE = "exhaustive"
    BOUNDARY = "boundary"
    PROPERTY = "property"
    GRID = "grid"
    COMBINED = "combined"


class SearchStatus(str, Enum):
    VIOLATION_FOUND = "VIOLATION_FOUND"
    NO_VIOLATION_FOUND_WITHIN_BUDGET = "NO_VIOLATION_FOUND_WITHIN_BUDGET"
    EXHAUSTIVE_NO_VIOLATION = "EXHAUSTIVE_NO_VIOLATION"
    SEARCH_BUDGET_EXHAUSTED = "SEARCH_BUDGET_EXHAUSTED"
    UNSUPPORTED = "UNSUPPORTED"
    INVALID_PROBLEM = "INVALID_PROBLEM"
    REPLAY_FAILED = "REPLAY_FAILED"


class ReductionStatus(str, Enum):
    REDUCED = "REDUCED"
    ALREADY_MINIMAL_UNDER_OBJECTIVE = "ALREADY_MINIMAL_UNDER_OBJECTIVE"
    PARTIALLY_REDUCED = "PARTIALLY_REDUCED"
    REDUCTION_BUDGET_EXHAUSTED = "REDUCTION_BUDGET_EXHAUSTED"
    FAILED_REPLAY = "FAILED_REPLAY"


@dataclass(frozen=True)
class SearchBudget:
    max_evaluations: int = 1000
    max_candidates: int = 1000
    max_seconds: float = 10.0


@dataclass(frozen=True)
class Boundary:
    attribute: str
    value: Decimal
    operator: str
    rule: str


@dataclass(frozen=True)
class SearchDomain:
    state_values: Mapping[str, tuple[Decimal | bool, ...]]
    action_values: Mapping[str, Mapping[str, tuple[Decimal | bool, ...]]]
    steps: Mapping[str, Decimal] = field(default_factory=dict)
    state_records: tuple[Mapping[str, Decimal | bool], ...] | None = None


@dataclass(frozen=True)
class SearchProblem:
    spec: InstitutionSpec
    domain: SearchDomain
    property_id: str = "no_profitable_deviation"
    allowed_actions: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ("deterministic one-period utility",)

    def actions(self) -> tuple[str, ...]:
        return self.allowed_actions or tuple(self.spec.actions)


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    baseline_state: Mapping[str, Decimal | bool]
    action_name: str
    action_parameters: Mapping[str, Decimal | bool]
    candidate_source: str
    boundary_origin: Boundary | None
    generation_metadata: Mapping[str, Any]


@dataclass(frozen=True)
class SeverityComponents:
    private_gain: Decimal
    violation_magnitude: Decimal
    action_cost: Decimal
    designer_loss: Decimal | None
    distance_to_boundary: Decimal | None


@dataclass(frozen=True)
class Finding:
    finding_id: str
    policy_hash: str
    property_id: str
    if_cwe_id: str
    severity_components: SeverityComponents
    baseline_state: Mapping[str, Decimal | bool]
    action: ActionInstance
    result_state: Mapping[str, Decimal | bool]
    baseline_utility: Decimal
    result_utility: Decimal
    utility_delta: Decimal
    baseline_designer_outcomes: Mapping[str, Decimal | bool]
    result_designer_outcomes: Mapping[str, Decimal | bool]
    property_violation: str
    violation_magnitude: Decimal
    action_cost: Decimal
    candidate_source: str
    search_method: str
    replay_status: str
    reduction_status: str | None
    trace: tuple[Any, ...]
    assumptions: tuple[str, ...]
    boundary_origin: Boundary | None


@dataclass(frozen=True)
class SearchStatistics:
    candidate_count: int
    evaluation_count: int
    raw_findings: int
    deduplicated_findings: int
    elapsed_seconds: float
    time_to_first_violation: float | None
    evaluations_to_first_violation: int | None


@dataclass(frozen=True)
class SearchResult:
    run_id: str
    policy_hash: str
    property_id: str
    method: SearchMethod
    budget: SearchBudget
    seed: int
    status: SearchStatus
    findings: tuple[Finding, ...]
    raw_findings: tuple[Finding, ...]
    statistics: SearchStatistics


def _d(value: Any) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(str(value))


def _jsonable(value: Any) -> Any:
    if isinstance(value, Decimal): return format(value, "f")
    if isinstance(value, Enum): return value.value
    if hasattr(value, "__dataclass_fields__"): return _jsonable(asdict(value))
    if isinstance(value, dict): return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)): return [_jsonable(v) for v in value]
    return value


def finding_to_json(finding: Finding) -> str:
    return json.dumps(_jsonable(finding), sort_keys=True, indent=2)


def extract_boundaries(spec: InstitutionSpec) -> tuple[Boundary, ...]:
    found: set[tuple[str, Decimal, str, str]] = set()
    params = {name: p.value for name, p in spec.parameters.items()}

    def walk(expr: Expression, rule: str) -> None:
        op, arg = next(iter(expr.node.items()))
        if op in {"lt", "le", "gt", "ge"}:
            left, right = arg
            pairs = ((left, right, op), (right, left, {"lt": "gt", "le": "ge", "gt": "lt", "ge": "le"}[op]))
            for variable, constant, oriented in pairs:
                if "var" not in variable.node: continue
                name = variable.node["var"]
                if name not in spec.attributes: continue
                if "const" in constant.node:
                    value = constant.node["const"]["value"]
                elif "var" in constant.node and constant.node["var"] in params:
                    value = params[constant.node["var"]]
                else:
                    continue
                found.add((name, _d(value), oriented, rule))
        elif op in {"add", "sub", "mul", "min", "max", "eq"}:
            for child in arg: walk(child, rule)
        elif op == "if":
            walk(arg["condition"], rule); walk(arg["then"], rule); walk(arg["else"], rule)

    for rule in spec.rules:
        walk(rule.expression, rule.name)
    return tuple(Boundary(*item) for item in sorted(found))


def _candidate(state, action, controls, source, boundary=None, metadata=None) -> Candidate:
    payload = json.dumps(_jsonable([state, action, controls, source, boundary]), sort_keys=True)
    return Candidate(sha256(payload.encode()).hexdigest()[:16], dict(state), action, dict(controls), source,
                     boundary, metadata or {})


def _cartesian(mapping: Mapping[str, Iterable[Any]]) -> Iterable[dict[str, Any]]:
    keys = tuple(mapping)
    for values in product(*(mapping[k] for k in keys)):
        yield dict(zip(keys, values))


def _state_iter(domain: SearchDomain) -> Iterable[dict[str, Any]]:
    if domain.state_records is not None:
        yield from (dict(record) for record in domain.state_records)
    else:
        yield from _cartesian(domain.state_values)


def exhaustive_candidates(problem: SearchProblem) -> Iterable[Candidate]:
    for state in _state_iter(problem.domain):
        for action in problem.actions():
            for controls in _cartesian(problem.domain.action_values[action]):
                yield _candidate(state, action, controls, "exhaustive")


def grid_candidates(problem: SearchProblem) -> Iterable[Candidate]:
    def grid(values):
        values = tuple(sorted(set(values)))
        return tuple(dict.fromkeys((values[0], values[len(values)//2], values[-1])))
    states = {k: grid(v) for k, v in problem.domain.state_values.items()}
    state_iter = problem.domain.state_records if problem.domain.state_records is not None else _cartesian(states)
    for state in state_iter:
        for action in problem.actions():
            controls = {k: grid(v) for k, v in problem.domain.action_values[action].items()}
            for params in _cartesian(controls):
                yield _candidate(state, action, params, "grid")


def property_candidates(problem: SearchProblem, seed: int) -> Iterable[Candidate]:
    rng = random.Random(seed)
    state_pool = list(_state_iter(problem.domain))
    rng.shuffle(state_pool)
    for state in state_pool:
        for action in problem.actions():
            pools = {}
            for name, values in problem.domain.action_values[action].items():
                vals = list(dict.fromkeys((values[0], values[-1], values[len(values)//2], rng.choice(values))))
                rng.shuffle(vals); pools[name] = vals
            for controls in _cartesian(pools):
                yield _candidate(state, action, controls, "property", metadata={"seed": seed})


def _transition_pattern(spec: InstitutionSpec, action: str):
    definition = spec.actions[action]
    patterns = []
    for target, expr in definition.transition.effects.items():
        op, arg = next(iter(expr.node.items()))
        if op != "sub": continue
        if arg[0].node.get("var") != target or "var" not in arg[1].node: continue
        control = arg[1].node["var"]
        if control in definition.controls:
            patterns.append((target, control))
    return patterns


def boundary_candidates(problem: SearchProblem) -> Iterable[Candidate]:
    boundaries = extract_boundaries(problem.spec)
    seen = set()
    for boundary in boundaries:
        values = problem.domain.state_values.get(boundary.attribute, ())
        step = problem.domain.steps.get(boundary.attribute, Decimal(1))
        interesting = {boundary.value - step, boundary.value, boundary.value + step}
        for state in _state_iter(problem.domain):
            if state[boundary.attribute] not in interesting and not any(
                state[boundary.attribute] >= boundary.value for _ in [0]
            ):
                continue
            for action in problem.actions():
                for target, control in _transition_pattern(problem.spec, action):
                    if target != boundary.attribute: continue
                    control_values = set(problem.domain.action_values[action][control])
                    for target_value in interesting:
                        amount = _d(state[target]) - target_value
                        if amount not in control_values: continue
                        other = {k: (v[0],) for k, v in problem.domain.action_values[action].items() if k != control}
                        for rest in _cartesian(other):
                            controls = rest | {control: amount}
                            cand = _candidate(state, action, controls, "boundary", boundary,
                                {"reason": f"{target} crosses {boundary.operator} boundary {boundary.value} in {boundary.rule}"})
                            if cand.candidate_id not in seen:
                                seen.add(cand.candidate_id); yield cand


def combined_candidates(problem: SearchProblem, seed: int) -> Iterable[Candidate]:
    seen = set()
    for generator in (boundary_candidates(problem), grid_candidates(problem), property_candidates(problem, seed)):
        for candidate in generator:
            key = (tuple(candidate.baseline_state.items()), candidate.action_name, tuple(candidate.action_parameters.items()))
            if key not in seen:
                seen.add(key); yield candidate


def _designer_loss(base: EvaluationResult, result: EvaluationResult) -> Decimal | None:
    common = set(base.outcome.designer_outcomes) & set(result.outcome.designer_outcomes)
    if not common: return None
    losses = []
    for name in common:
        if "output" in name:
            losses.append(_d(base.outcome.designer_outcomes[name]) - _d(result.outcome.designer_outcomes[name]))
        elif "cost" in name or "burden" in name:
            losses.append(_d(result.outcome.designer_outcomes[name]) - _d(base.outcome.designer_outcomes[name]))
    return max(losses) if losses else None


def _classify(problem: SearchProblem, candidate: Candidate, base: EvaluationResult, result: EvaluationResult) -> str:
    changed = [name for name in base.baseline_state.values if base.baseline_state.values[name] != result.resulting_state.values[name]]
    if any(problem.spec.attributes[name].role == "reported" for name in changed): return "IF-005"
    if candidate.boundary_origin:
        boundary_rules = {b.rule for b in extract_boundaries(problem.spec) if b.attribute == candidate.boundary_origin.attribute}
        changed_rules = {name for name in base.outcome.rule_outputs if base.outcome.rule_outputs[name] != result.outcome.rule_outputs[name]}
        if len(boundary_rules & changed_rules) > 1: return "IF-015"
        if result.resulting_state.values[candidate.boundary_origin.attribute] == candidate.boundary_origin.value:
            return "IF-002"
        return "IF-001"
    if changed: return "IF-003"
    return "UNCLASSIFIED_PROPERTY_VIOLATION"


def _finding(problem: SearchProblem, candidate: Candidate, method: SearchMethod,
             base: EvaluationResult, result: EvaluationResult) -> Finding | None:
    gain = result.utility - base.utility
    if gain <= 0: return None
    distance = abs(_d(candidate.baseline_state[candidate.boundary_origin.attribute]) - candidate.boundary_origin.value) if candidate.boundary_origin else None
    loss = _designer_loss(base, result)
    classification = _classify(problem, candidate, base, result)
    identity = sha256(f"{spec_hash(problem.spec)}:{candidate.candidate_id}:{problem.property_id}".encode()).hexdigest()[:20]
    severity = SeverityComponents(gain, gain, result.action_cost, loss, distance)
    return Finding(identity, spec_hash(problem.spec), problem.property_id, classification, severity,
                   candidate.baseline_state, ActionInstance(candidate.action_name, candidate.action_parameters),
                   result.resulting_state.values, base.utility, result.utility, gain,
                   base.outcome.designer_outcomes, result.outcome.designer_outcomes,
                   "profitable deviation violates declared no-profitable-deviation property", gain,
                   result.action_cost, candidate.candidate_source, method.value, "REPLAYED",
                   None, result.trace, problem.assumptions, candidate.boundary_origin)


def _truth(value: Decimal, operator: str, boundary: Decimal) -> bool:
    return {"lt": value < boundary, "le": value <= boundary,
            "gt": value > boundary, "ge": value >= boundary}[operator]


def _attach_crossed_boundary(problem: SearchProblem, candidate: Candidate,
                             base: EvaluationResult, result: EvaluationResult) -> Candidate:
    if candidate.boundary_origin is not None:
        boundary = candidate.boundary_origin
        before = _d(base.baseline_state.values[boundary.attribute])
        after = _d(result.resulting_state.values[boundary.attribute])
        if _truth(before, boundary.operator, boundary.value) != _truth(after, boundary.operator, boundary.value):
            return candidate
        candidate = field_replace(candidate, boundary_origin=None)
    for boundary in extract_boundaries(problem.spec):
        before = _d(base.baseline_state.values[boundary.attribute])
        after = _d(result.resulting_state.values[boundary.attribute])
        if _truth(before, boundary.operator, boundary.value) != _truth(after, boundary.operator, boundary.value):
            return field_replace(candidate, boundary_origin=boundary)
    return candidate


def finding_equivalence_key(finding: Finding) -> tuple[Any, ...]:
    boundary = None if finding.boundary_origin is None else (
        finding.boundary_origin.attribute, finding.boundary_origin.value, finding.boundary_origin.rule)
    return finding.property_id, finding.action.name, finding.if_cwe_id, boundary


def deduplicate(findings: Iterable[Finding]) -> tuple[Finding, ...]:
    selected = {}
    for finding in findings:
        key = finding_equivalence_key(finding)
        current = selected.get(key)
        if current is None or finding.utility_delta > current.utility_delta:
            selected[key] = finding
    return tuple(selected[k] for k in sorted(selected, key=str))


class SearchEngine:
    def __init__(self, problem: SearchProblem): self.problem = problem

    def run(self, method: SearchMethod | str, budget: SearchBudget = SearchBudget(), seed: int = 0) -> SearchResult:
        method = SearchMethod(method); start = perf_counter(); raw = []; candidates = evaluations = 0
        first_time = first_eval = None; exhausted = False
        generators = {
            SearchMethod.EXHAUSTIVE: exhaustive_candidates(self.problem),
            SearchMethod.BOUNDARY: boundary_candidates(self.problem),
            SearchMethod.PROPERTY: property_candidates(self.problem, seed),
            SearchMethod.GRID: grid_candidates(self.problem),
            SearchMethod.COMBINED: combined_candidates(self.problem, seed),
        }
        for candidate in generators[method]:
            if candidates >= budget.max_candidates or evaluations + 2 > budget.max_evaluations or perf_counter() - start > budget.max_seconds:
                exhausted = True; break
            candidates += 1
            try:
                base = evaluate(self.problem.spec, candidate.baseline_state); evaluations += 1
                result = evaluate(self.problem.spec, candidate.baseline_state,
                                  ActionInstance(candidate.action_name, candidate.action_parameters)); evaluations += 1
            except IncentiveSpecError:
                continue
            candidate = _attach_crossed_boundary(self.problem, candidate, base, result)
            finding = _finding(self.problem, candidate, method, base, result)
            if finding:
                raw.append(finding)
                if first_time is None: first_time, first_eval = perf_counter() - start, evaluations
        deduped = deduplicate(raw); elapsed = perf_counter() - start
        if deduped: status = SearchStatus.VIOLATION_FOUND
        elif method is SearchMethod.EXHAUSTIVE and not exhausted: status = SearchStatus.EXHAUSTIVE_NO_VIOLATION
        elif exhausted: status = SearchStatus.SEARCH_BUDGET_EXHAUSTED
        else: status = SearchStatus.NO_VIOLATION_FOUND_WITHIN_BUDGET
        run_payload = f"{spec_hash(self.problem.spec)}:{method.value}:{budget}:{seed}"
        stats = SearchStatistics(candidates, evaluations, len(raw), len(deduped), elapsed, first_time, first_eval)
        return SearchResult(sha256(run_payload.encode()).hexdigest()[:16], spec_hash(self.problem.spec),
                            self.problem.property_id, method, budget, seed, status, deduped, tuple(raw), stats)


def replay_finding(spec: InstitutionSpec, finding: Finding) -> bool:
    if spec_hash(spec) != finding.policy_hash: return False
    try:
        base = evaluate(spec, finding.baseline_state)
        result = evaluate(spec, finding.baseline_state, finding.action)
    except IncentiveSpecError:
        return False
    return (base.utility == finding.baseline_utility and result.utility == finding.result_utility
            and result.utility - base.utility == finding.utility_delta and result.resulting_state.values == finding.result_state)


def reduction_objective(finding: Finding) -> tuple[Any, ...]:
    controls = [_d(v) for v in finding.action.controls.values()]
    distance = finding.severity_components.distance_to_boundary or Decimal("Infinity")
    return (1, sum(v != 0 for v in controls), sum(abs(v) for v in controls), distance, -finding.utility_delta)


def reduce_finding(problem: SearchProblem, finding: Finding, budget: SearchBudget = SearchBudget()) -> Finding:
    candidates = []
    evaluations = 0
    for candidate in exhaustive_candidates(problem):
        if evaluations + 2 > budget.max_evaluations: break
        candidate = field_replace(candidate, boundary_origin=finding.boundary_origin)
        try:
            base = evaluate(problem.spec, candidate.baseline_state)
            result = evaluate(problem.spec, candidate.baseline_state,
                              ActionInstance(candidate.action_name, candidate.action_parameters))
        except IncentiveSpecError:
            continue
        evaluations += 2
        reduced = _finding(problem, candidate, SearchMethod.EXHAUSTIVE, base, result)
        if reduced: candidates.append(reduced)
    same = [f for f in candidates if finding_equivalence_key(f) == finding_equivalence_key(finding)]
    if not same: return field_replace(finding, reduction_status=ReductionStatus.FAILED_REPLAY.value)
    best = min(same + [finding], key=reduction_objective)
    status = ReductionStatus.REDUCED if reduction_objective(best) < reduction_objective(finding) else ReductionStatus.ALREADY_MINIMAL_UNDER_OBJECTIVE
    return field_replace(best, reduction_status=status.value)


def field_replace(instance, **changes):
    values = {name: getattr(instance, name) for name in instance.__dataclass_fields__}
    values.update(changes)
    return type(instance)(**values)
