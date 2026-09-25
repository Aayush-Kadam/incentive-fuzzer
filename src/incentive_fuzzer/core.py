from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from enum import Enum
from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping

import yaml


class IncentiveSpecError(ValueError):
    """A user-facing specification or evaluation error."""


class Unit(str, Enum):
    MONEY = "money"
    SCALAR = "scalar"
    RATE = "rate"
    COUNT = "count"
    BOOLEAN = "boolean"


class ValueType(str, Enum):
    INTEGER = "integer"
    DECIMAL = "decimal"
    BOOLEAN = "boolean"
    MONEY = "money"


class PropertyStatus(str, Enum):
    SATISFIED_ON_ENUMERATED_DOMAIN = "SATISFIED_ON_ENUMERATED_DOMAIN"
    VIOLATED = "VIOLATED"
    NOT_EVALUATED = "NOT_EVALUATED"
    UNSUPPORTED = "UNSUPPORTED"
    INVALID_SPEC = "INVALID_SPEC"


@dataclass(frozen=True)
class Institution:
    id: str
    name: str
    description: str
    version: str


@dataclass(frozen=True)
class EntityType:
    id: str = "agent"


@dataclass(frozen=True)
class Parameter:
    name: str
    type: ValueType
    unit: Unit
    value: Decimal | bool
    provenance: str


@dataclass(frozen=True)
class AttributeDefinition:
    name: str
    type: ValueType
    unit: Unit
    lower: Decimal | bool
    upper: Decimal | bool
    observable: bool
    manipulable: bool
    role: str


@dataclass(frozen=True)
class Expression:
    node: Mapping[str, Any]
    unit: Unit


Condition = Expression


@dataclass(frozen=True)
class Transition:
    effects: Mapping[str, Expression]


@dataclass(frozen=True)
class CostFunction:
    expression: Expression


@dataclass(frozen=True)
class ActionDefinition:
    name: str
    controls: Mapping[str, AttributeDefinition]
    feasibility: Condition
    transition: Transition
    cost: CostFunction


@dataclass(frozen=True)
class ActionInstance:
    name: str
    controls: Mapping[str, Decimal | bool] = field(default_factory=dict)


@dataclass(frozen=True)
class Rule:
    name: str
    expression: Expression


@dataclass(frozen=True)
class Transfer(Rule):
    pass


@dataclass(frozen=True)
class UtilityFunction:
    expression: Expression


@dataclass(frozen=True)
class Property:
    id: str
    kind: str
    config: Mapping[str, Any]


@dataclass(frozen=True)
class InstitutionSpec:
    incentive_spec_version: str
    institution: Institution
    entity_type: EntityType
    parameters: Mapping[str, Parameter]
    attributes: Mapping[str, AttributeDefinition]
    actions: Mapping[str, ActionDefinition]
    rules: tuple[Rule, ...]
    utility: UtilityFunction
    designer_outcomes: tuple[Rule, ...]
    properties: tuple[Property, ...]
    canonical_data: Mapping[str, Any]
    identity_hash: str


@dataclass(frozen=True)
class AgentState:
    values: Mapping[str, Decimal | bool]


@dataclass(frozen=True)
class Outcome:
    rule_outputs: Mapping[str, Decimal | bool]
    designer_outcomes: Mapping[str, Decimal | bool]


@dataclass(frozen=True)
class EvaluationContext:
    spec_hash: str
    parameters: Mapping[str, Decimal | bool]


@dataclass(frozen=True)
class TraceStep:
    phase: str
    name: str
    value: Any
    detail: str


@dataclass(frozen=True)
class EvaluationResult:
    baseline_state: AgentState
    action: ActionInstance | None
    resulting_state: AgentState
    outcome: Outcome
    action_cost: Decimal
    utility: Decimal
    trace: tuple[TraceStep, ...]
    context: EvaluationContext


@dataclass(frozen=True)
class Violation:
    property_id: str
    message: str
    witness: Mapping[str, Any]


@dataclass(frozen=True)
class PropertyResult:
    property_id: str
    status: PropertyStatus
    checked_cases: int
    violation: Violation | None = None


def _fail(path: str, message: str) -> None:
    raise IncentiveSpecError(f"Invalid IncentiveSpec at {path}: {message}")


def _decimal(value: Any, path: str) -> Decimal:
    if isinstance(value, bool) or value is None:
        _fail(path, "expected exact numeric value")
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        _fail(path, f"invalid numeric value {value!r}")


def _unit_for_type(value_type: ValueType, explicit: str | None, path: str) -> Unit:
    default = {ValueType.MONEY: Unit.MONEY, ValueType.BOOLEAN: Unit.BOOLEAN,
               ValueType.INTEGER: Unit.COUNT, ValueType.DECIMAL: Unit.SCALAR}[value_type]
    unit = Unit(explicit) if explicit else default
    if value_type is ValueType.MONEY and unit is not Unit.MONEY:
        _fail(path, "money type requires money unit")
    if value_type is ValueType.BOOLEAN and unit is not Unit.BOOLEAN:
        _fail(path, "boolean type requires boolean unit")
    return unit


def _symbol_units(spec_parts: Mapping[str, Any]) -> dict[str, Unit]:
    units = {name: p.unit for name, p in spec_parts["parameters"].items()}
    units.update({name: a.unit for name, a in spec_parts["attributes"].items()})
    units["action_cost"] = Unit.MONEY
    return units


def _expr(node: Any, symbols: Mapping[str, Unit], path: str) -> Expression:
    if not isinstance(node, dict) or len(node) != 1:
        _fail(path, "expression must be a one-key AST object")
    op, arg = next(iter(node.items()))
    if op == "const":
        if not isinstance(arg, dict) or "value" not in arg or "unit" not in arg:
            _fail(path, "const requires value and unit")
        unit = Unit(arg["unit"])
        value = bool(arg["value"]) if unit is Unit.BOOLEAN else _decimal(arg["value"], path)
        return Expression({"const": {"value": value, "unit": unit.value}}, unit)
    if op == "var":
        if arg not in symbols:
            _fail(path, f"unknown symbol {arg!r}")
        return Expression({"var": arg}, symbols[arg])
    if op in {"add", "sub", "min", "max"}:
        if not isinstance(arg, list) or len(arg) != 2:
            _fail(path, f"{op} requires two operands")
        left, right = _expr(arg[0], symbols, path + ".0"), _expr(arg[1], symbols, path + ".1")
        if left.unit != right.unit or left.unit is Unit.BOOLEAN:
            _fail(path, f"{op} operands must have the same non-boolean unit")
        return Expression({op: [left, right]}, left.unit)
    if op == "mul":
        if not isinstance(arg, list) or len(arg) != 2:
            _fail(path, "mul requires two operands")
        left, right = _expr(arg[0], symbols, path + ".0"), _expr(arg[1], symbols, path + ".1")
        if left.unit in {Unit.SCALAR, Unit.RATE} and right.unit not in {Unit.BOOLEAN}:
            unit = right.unit
        elif right.unit in {Unit.SCALAR, Unit.RATE} and left.unit not in {Unit.BOOLEAN}:
            unit = left.unit
        else:
            _fail(path, "multiplication requires one scalar/rate operand")
        return Expression({"mul": [left, right]}, unit)
    if op in {"lt", "le", "gt", "ge", "eq"}:
        if not isinstance(arg, list) or len(arg) != 2:
            _fail(path, f"{op} requires two operands")
        left, right = _expr(arg[0], symbols, path + ".0"), _expr(arg[1], symbols, path + ".1")
        if left.unit != right.unit:
            _fail(path, f"comparison operands have incompatible units: {left.unit.value}, {right.unit.value}")
        return Expression({op: [left, right]}, Unit.BOOLEAN)
    if op == "if":
        if not isinstance(arg, dict) or set(arg) != {"condition", "then", "else"}:
            _fail(path, "if requires condition, then, and else")
        condition = _expr(arg["condition"], symbols, path + ".condition")
        then = _expr(arg["then"], symbols, path + ".then")
        otherwise = _expr(arg["else"], symbols, path + ".else")
        if condition.unit is not Unit.BOOLEAN or then.unit != otherwise.unit:
            _fail(path, "if requires boolean condition and equal branch units")
        return Expression({"if": {"condition": condition, "then": then, "else": otherwise}}, then.unit)
    _fail(path, f"unsupported expression operator {op!r}")


def _attribute(name: str, raw: Any, path: str, *, control: bool = False) -> AttributeDefinition:
    if not isinstance(raw, dict):
        _fail(path, "expected mapping")
    try:
        value_type = ValueType(raw["type"])
        unit = _unit_for_type(value_type, raw.get("unit"), path + ".unit")
    except (KeyError, ValueError) as exc:
        _fail(path, f"invalid type or unit: {exc}")
    if value_type is ValueType.BOOLEAN:
        lower, upper = False, True
    else:
        lower = _decimal(raw.get("lower"), path + ".lower")
        upper = _decimal(raw.get("upper"), path + ".upper")
        if lower > upper:
            _fail(path, "lower bound exceeds upper bound")
        if value_type is ValueType.INTEGER and (lower != lower.to_integral() or upper != upper.to_integral()):
            _fail(path, "integer bounds must be integral")
    return AttributeDefinition(name, value_type, unit, lower, upper,
                               bool(raw.get("observable", False if control else None)),
                               bool(raw.get("manipulable", False if control else None)),
                               str(raw.get("role", "control" if control else "latent")))


def parse_spec(raw: Mapping[str, Any]) -> InstitutionSpec:
    if not isinstance(raw, dict):
        _fail("$", "document must be a mapping")
    if raw.get("incentive_spec_version") != "0.1":
        _fail("incentive_spec_version", "only version '0.1' is supported")
    meta = raw.get("institution")
    if not isinstance(meta, dict):
        _fail("institution", "expected mapping")
    try:
        institution = Institution(*(str(meta[k]) for k in ("id", "name", "description", "version")))
    except KeyError as exc:
        _fail("institution", f"missing {exc.args[0]}")
    parameters: dict[str, Parameter] = {}
    for name, item in (raw.get("parameters") or {}).items():
        try:
            vt = ValueType(item["type"])
            unit = _unit_for_type(vt, item.get("unit"), f"parameters.{name}.unit")
            value = bool(item["value"]) if vt is ValueType.BOOLEAN else _decimal(item["value"], f"parameters.{name}.value")
            provenance = str(item["provenance"])
        except (KeyError, ValueError) as exc:
            _fail(f"parameters.{name}", f"invalid parameter: {exc}")
        if provenance not in {"E", "L", "S", "A"}:
            _fail(f"parameters.{name}.provenance", "expected E, L, S, or A")
        parameters[name] = Parameter(name, vt, unit, value, provenance)
    attributes = {name: _attribute(name, item, f"attributes.{name}") for name, item in (raw.get("attributes") or {}).items()}
    if not attributes:
        _fail("attributes", "at least one attribute is required")
    parts = {"parameters": parameters, "attributes": attributes}
    symbols = _symbol_units(parts)
    actions: dict[str, ActionDefinition] = {}
    for name, item in (raw.get("actions") or {}).items():
        controls = {n: _attribute(n, v, f"actions.{name}.controls.{n}", control=True) for n, v in (item.get("controls") or {}).items()}
        local_symbols = symbols | {n: a.unit for n, a in controls.items()}
        feasibility = _expr(item["feasibility"], local_symbols, f"actions.{name}.feasibility")
        if feasibility.unit is not Unit.BOOLEAN:
            _fail(f"actions.{name}.feasibility", "must be boolean")
        effects = {target: _expr(expr, local_symbols, f"actions.{name}.transition.{target}") for target, expr in item["transition"].items()}
        for target, expr in effects.items():
            if target not in attributes or not attributes[target].manipulable:
                _fail(f"actions.{name}.transition.{target}", "target must be a manipulable attribute")
            if expr.unit != attributes[target].unit:
                _fail(f"actions.{name}.transition.{target}", "effect unit differs from attribute unit")
        cost = _expr(item["cost"], local_symbols, f"actions.{name}.cost")
        if cost.unit is not Unit.MONEY:
            _fail(f"actions.{name}.cost", "action cost must have money unit")
        actions[name] = ActionDefinition(name, controls, feasibility, Transition(effects), CostFunction(cost))
    rule_symbols = symbols.copy()
    rules: list[Rule] = []
    for name, node in (raw.get("rules") or {}).items():
        expr = _expr(node, rule_symbols, f"rules.{name}")
        rules.append(Transfer(name, expr) if expr.unit is Unit.MONEY else Rule(name, expr))
        rule_symbols[name] = expr.unit
    utility = _expr(raw.get("utility"), rule_symbols | {"action_cost": Unit.MONEY}, "utility")
    if utility.unit is not Unit.MONEY:
        _fail("utility", "utility must have money unit")
    designer: list[Rule] = []
    for name, node in (raw.get("designer_outcomes") or {}).items():
        expr = _expr(node, rule_symbols | {"action_cost": Unit.MONEY}, f"designer_outcomes.{name}")
        designer.append(Rule(name, expr))
    properties = tuple(Property(str(p["id"]), str(p["kind"]), {k: v for k, v in p.items() if k not in {"id", "kind"}}) for p in raw.get("properties", []))
    canonical = _normalize(raw)
    canonical_text = yaml.safe_dump(canonical, sort_keys=False, allow_unicode=True, default_flow_style=False)
    identity_hash = sha256(canonical_text.encode("utf-8")).hexdigest()
    return InstitutionSpec("0.1", institution, EntityType(), parameters, attributes, actions,
                           tuple(rules), UtilityFunction(utility), tuple(designer), properties, canonical, identity_hash)


def load_spec(path: str | Path) -> InstitutionSpec:
    try:
        raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise IncentiveSpecError(f"Invalid IncentiveSpec YAML: {exc}") from None
    return parse_spec(raw)


def _normalize(value: Any) -> Any:
    if isinstance(value, dict):
        # Mapping order is semantic for rules, whose outputs may feed later rules.
        # PyYAML preserves source order; canonical serialization therefore preserves it too.
        return {str(k): _normalize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_normalize(v) for v in value]
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, float):
        return format(Decimal(str(value)), "f")
    return value


def canonical_yaml(spec: InstitutionSpec) -> str:
    return yaml.safe_dump(spec.canonical_data, sort_keys=False, allow_unicode=True, default_flow_style=False)


def spec_hash(spec: InstitutionSpec) -> str:
    return spec.identity_hash


def _eval(expr: Expression, env: Mapping[str, Decimal | bool]) -> Decimal | bool:
    op, arg = next(iter(expr.node.items()))
    if op == "const": return arg["value"]
    if op == "var": return env[arg]
    if op in {"add", "sub", "mul", "min", "max", "lt", "le", "gt", "ge", "eq"}:
        a, b = _eval(arg[0], env), _eval(arg[1], env)
        return {"add": lambda: a + b, "sub": lambda: a - b, "mul": lambda: a * b,
                "min": lambda: min(a, b), "max": lambda: max(a, b), "lt": lambda: a < b,
                "le": lambda: a <= b, "gt": lambda: a > b, "ge": lambda: a >= b,
                "eq": lambda: a == b}[op]()
    if op == "if":
        return _eval(arg["then"], env) if _eval(arg["condition"], env) else _eval(arg["else"], env)
    raise AssertionError(op)


def _coerce_state(spec: InstitutionSpec, state: Mapping[str, Any]) -> dict[str, Decimal | bool]:
    if set(state) != set(spec.attributes):
        missing, extra = set(spec.attributes) - set(state), set(state) - set(spec.attributes)
        raise IncentiveSpecError(f"State fields mismatch; missing={sorted(missing)}, extra={sorted(extra)}")
    result: dict[str, Decimal | bool] = {}
    for name, definition in spec.attributes.items():
        value = bool(state[name]) if definition.type is ValueType.BOOLEAN else _decimal(state[name], f"state.{name}")
        if definition.type is ValueType.INTEGER and value != value.to_integral():
            raise IncentiveSpecError(f"state.{name} must be integral")
        if value < definition.lower or value > definition.upper:
            raise IncentiveSpecError(f"state.{name} outside [{definition.lower}, {definition.upper}]")
        result[name] = value
    return result


def evaluate(spec: InstitutionSpec, state: Mapping[str, Any], action: ActionInstance | None = None) -> EvaluationResult:
    baseline = _coerce_state(spec, state)
    params = {name: p.value for name, p in spec.parameters.items()}
    current = baseline.copy()
    cost = Decimal("0")
    trace = [TraceStep("state", name, value, "initial") for name, value in baseline.items()]
    if action:
        if action.name not in spec.actions:
            raise IncentiveSpecError(f"Unknown action {action.name!r}")
        definition = spec.actions[action.name]
        if set(action.controls) != set(definition.controls):
            raise IncentiveSpecError(f"Action controls mismatch for {action.name}")
        controls: dict[str, Decimal | bool] = {}
        for name, control in definition.controls.items():
            value = bool(action.controls[name]) if control.type is ValueType.BOOLEAN else _decimal(action.controls[name], f"action.{name}")
            if value < control.lower or value > control.upper:
                raise IncentiveSpecError(f"action.{name} outside [{control.lower}, {control.upper}]")
            controls[name] = value
        env = params | baseline | controls
        if not _eval(definition.feasibility, env):
            raise IncentiveSpecError(f"Action {action.name!r} is infeasible in the supplied state")
        updates = {name: _eval(expr, env) for name, expr in definition.transition.effects.items()}
        current.update(updates)
        current = _coerce_state(spec, current)
        cost = _eval(definition.cost.expression, env)
        if cost < 0:
            raise IncentiveSpecError("Action cost evaluated negative")
        trace.append(TraceStep("action", action.name, dict(controls), "feasible"))
        trace.extend(TraceStep("transition", name, value, "post-action") for name, value in updates.items())
        trace.append(TraceStep("cost", "action_cost", cost, "direct cost"))
    env = params | current | {"action_cost": cost}
    outputs: dict[str, Decimal | bool] = {}
    for rule in spec.rules:
        value = _eval(rule.expression, env | outputs)
        outputs[rule.name] = value
        trace.append(TraceStep("rule", rule.name, value, "evaluated in declaration order"))
    utility = _eval(spec.utility.expression, env | outputs)
    trace.append(TraceStep("utility", "utility", utility, "post-rule less declared costs"))
    designer = {rule.name: _eval(rule.expression, env | outputs) for rule in spec.designer_outcomes}
    trace.extend(TraceStep("designer", name, value, "designer outcome") for name, value in designer.items())
    return EvaluationResult(AgentState(baseline), action, AgentState(current), Outcome(outputs, designer), cost,
                            utility, tuple(trace), EvaluationContext(spec_hash(spec), params))


def evaluate_properties(spec: InstitutionSpec) -> tuple[PropertyResult, ...]:
    results: list[PropertyResult] = []
    for prop in spec.properties:
        try:
            results.append(_evaluate_property(spec, prop))
        except IncentiveSpecError as exc:
            results.append(PropertyResult(prop.id, PropertyStatus.INVALID_SPEC, 0,
                                          Violation(prop.id, str(exc), {})))
    return tuple(results)


def _states(spec: InstitutionSpec, domain: Mapping[str, list[Any]]) -> list[dict[str, Any]]:
    if set(domain) != set(spec.attributes):
        raise IncentiveSpecError("property domain must enumerate every state attribute")
    states = [{}]
    for name in spec.attributes:
        states = [s | {name: value} for s in states for value in domain[name]]
    return states


def _evaluate_property(spec: InstitutionSpec, prop: Property) -> PropertyResult:
    domain = prop.config.get("domain")
    if not isinstance(domain, dict):
        return PropertyResult(prop.id, PropertyStatus.NOT_EVALUATED, 0)
    states = _states(spec, domain)
    cases = 0
    if prop.kind in {"budget_bound", "participation"}:
        field = prop.config.get("field", "fiscal_cost" if prop.kind == "budget_bound" else None)
        key = "maximum" if prop.kind == "budget_bound" else "minimum"
        bound = _decimal(prop.config.get(key, 0), f"properties.{prop.id}.{key}")
        for state in states:
            result = evaluate(spec, state)
            cases += 1
            value = result.outcome.designer_outcomes.get(field) if prop.kind == "budget_bound" else result.utility
            failed = value > bound if prop.kind == "budget_bound" else value < bound
            if failed:
                return PropertyResult(prop.id, PropertyStatus.VIOLATED, cases,
                                      Violation(prop.id, f"{field or 'utility'}={value} violates bound {bound}", state))
    elif prop.kind in {"resource_monotonicity", "maximum_local_resource_drop"}:
        attribute, resource = prop.config["attribute"], prop.config["resource"]
        max_drop = _decimal(prop.config.get("maximum_drop", 0), f"properties.{prop.id}.maximum_drop")
        ordered = sorted(states, key=lambda s: _decimal(s[attribute], attribute))
        previous = None
        for state in ordered:
            result = evaluate(spec, state); cases += 1
            value = result.outcome.rule_outputs.get(resource, result.outcome.designer_outcomes.get(resource))
            if previous and value - previous[1] < -max_drop:
                return PropertyResult(prop.id, PropertyStatus.VIOLATED, cases,
                                      Violation(prop.id, f"resource drop {value - previous[1]} exceeds {max_drop}",
                                                {"from": previous[0], "to": state}))
            previous = (state, value)
    elif prop.kind in {"no_profitable_downward_manipulation", "no_profitable_misreporting"}:
        action_name, control = prop.config["action"], prop.config["control"]
        alternatives = prop.config.get("alternatives", [])
        for state in states:
            baseline = evaluate(spec, state); cases += 1
            for amount in alternatives:
                try:
                    candidate = evaluate(spec, state, ActionInstance(action_name, {control: amount})); cases += 1
                except IncentiveSpecError:
                    continue
                if candidate.utility > baseline.utility:
                    return PropertyResult(prop.id, PropertyStatus.VIOLATED, cases,
                        Violation(prop.id, f"utility gain {candidate.utility - baseline.utility}",
                                  {"state": state, "action": action_name, control: amount}))
    else:
        return PropertyResult(prop.id, PropertyStatus.UNSUPPORTED, 0)
    return PropertyResult(prop.id, PropertyStatus.SATISFIED_ON_ENUMERATED_DOMAIN, cases)
