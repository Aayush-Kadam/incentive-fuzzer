from __future__ import annotations

from dataclasses import asdict, dataclass, field
from decimal import Decimal
from enum import Enum
from fractions import Fraction
from hashlib import sha256
import json
from time import perf_counter
from typing import Any, Mapping

import z3

from .core import (
    ActionInstance, AttributeDefinition, Expression, IncentiveSpecError,
    InstitutionSpec, Property, TraceStep, ValueType, evaluate, spec_hash,
)


class FormalStatus(str, Enum):
    FORMALLY_VIOLATED = "FORMALLY_VIOLATED"
    FORMALLY_SATISFIED_WITHIN_DOMAIN = "FORMALLY_SATISFIED_WITHIN_DOMAIN"
    UNKNOWN = "UNKNOWN"
    TIMEOUT = "TIMEOUT"
    UNSUPPORTED_FRAGMENT = "UNSUPPORTED_FRAGMENT"
    INVALID_SPEC = "INVALID_SPEC"
    WITNESS_REPLAY_FAILED = "WITNESS_REPLAY_FAILED"
    BACKEND_DISAGREEMENT = "BACKEND_DISAGREEMENT"


class UnsupportedFragment(ValueError):
    pass


@dataclass(frozen=True)
class FormalDomain:
    state_values: Mapping[str, tuple[Decimal | bool, ...]] = field(default_factory=dict)
    control_values: Mapping[str, tuple[Decimal | bool, ...]] = field(default_factory=dict)
    state_steps: Mapping[str, Decimal] = field(default_factory=dict)
    control_steps: Mapping[str, Decimal] = field(default_factory=dict)


@dataclass(frozen=True)
class FormalWitness:
    solver: str
    solver_version: str
    property_id: str
    spec_hash: str
    symbolic_assignment: Mapping[str, str]
    decoded_baseline_state: Mapping[str, Decimal | bool]
    decoded_action: ActionInstance
    predicted_outputs: Mapping[str, Decimal | bool]
    predicted_utility: Decimal
    formal_status: FormalStatus
    runtime_replay: str
    agreement: bool


@dataclass(frozen=True)
class FormalResult:
    status: FormalStatus
    property_id: str
    spec_hash: str
    domain_hash: str
    solver: str
    solver_version: str
    timeout_ms: int
    solver_reason: str | None
    build_seconds: float
    solve_seconds: float
    decode_seconds: float
    replay_seconds: float
    witness: FormalWitness | None
    message: str


def decimal_to_fraction(value: Decimal) -> Fraction:
    sign, digits, exponent = value.as_tuple()
    coefficient = 0
    for digit in digits:
        coefficient = coefficient * 10 + digit
    if sign:
        coefficient = -coefficient
    if exponent >= 0:
        return Fraction(coefficient * (10 ** exponent), 1)
    return Fraction(coefficient, 10 ** (-exponent))


def _q(value: Decimal | int | str) -> z3.RatNumRef:
    fraction = decimal_to_fraction(value if isinstance(value, Decimal) else Decimal(str(value)))
    return z3.Q(fraction.numerator, fraction.denominator)


def _decode(value: z3.ExprRef, boolean: bool = False) -> Decimal | bool:
    if boolean:
        return z3.is_true(value)
    if z3.is_int_value(value):
        return Decimal(value.as_long())
    if z3.is_rational_value(value):
        numerator, denominator = value.numerator_as_long(), value.denominator_as_long()
        reduced = denominator
        while reduced % 2 == 0: reduced //= 2
        while reduced % 5 == 0: reduced //= 5
        if reduced != 1:
            raise UnsupportedFragment(f"model value {numerator}/{denominator} has no finite decimal representation")
        return Decimal(numerator) / Decimal(denominator)
    raise UnsupportedFragment(f"cannot decode model value {value}")


def _domain_hash(spec: InstitutionSpec, domain: FormalDomain, property_id: str, action: str) -> str:
    def norm(value):
        if isinstance(value, Decimal): return format(value, "f")
        if isinstance(value, dict): return {k: norm(v) for k, v in sorted(value.items())}
        if isinstance(value, (tuple, list)): return [norm(v) for v in value]
        return value
    payload = norm({"spec": spec_hash(spec), "domain": asdict(domain), "property": property_id, "action": action})
    return sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


class _Translator:
    """Independent AST-to-Z3 semantics; does not call the M1 expression evaluator."""

    def __init__(self, spec: InstitutionSpec):
        self.spec = spec

    def expression(self, expr: Expression, env: Mapping[str, z3.ExprRef], path: str) -> z3.ExprRef:
        op, arg = next(iter(expr.node.items()))
        if op == "const":
            return z3.BoolVal(arg["value"]) if arg["unit"] == "boolean" else _q(arg["value"])
        if op == "var":
            if arg not in env: raise UnsupportedFragment(f"unknown formal symbol at {path}: {arg}")
            return env[arg]
        if op in {"add", "sub"}:
            left = self.expression(arg[0], env, path + ".0"); right = self.expression(arg[1], env, path + ".1")
            return left + right if op == "add" else left - right
        if op == "mul":
            left = self.expression(arg[0], env, path + ".0"); right = self.expression(arg[1], env, path + ".1")
            left_constant, right_constant = z3.is_rational_value(z3.simplify(left)), z3.is_rational_value(z3.simplify(right))
            if not (left_constant or right_constant):
                raise UnsupportedFragment(f"symbolic x symbolic multiplication at {path}")
            return left * right
        if op in {"min", "max"}:
            left = self.expression(arg[0], env, path + ".0"); right = self.expression(arg[1], env, path + ".1")
            return z3.If(left <= right, left, right) if op == "min" else z3.If(left >= right, left, right)
        if op in {"lt", "le", "gt", "ge", "eq"}:
            left = self.expression(arg[0], env, path + ".0"); right = self.expression(arg[1], env, path + ".1")
            return {"lt": left < right, "le": left <= right, "gt": left > right,
                    "ge": left >= right, "eq": left == right}[op]
        if op == "if":
            return z3.If(self.expression(arg["condition"], env, path + ".condition"),
                         self.expression(arg["then"], env, path + ".then"),
                         self.expression(arg["else"], env, path + ".else"))
        raise UnsupportedFragment(f"unsupported operator {op!r} at {path}")

    def symbol(self, name: str, definition: AttributeDefinition, suffix: str) -> z3.ExprRef:
        if definition.type is ValueType.BOOLEAN: return z3.Bool(f"{name}_{suffix}")
        if definition.type is ValueType.INTEGER or definition.unit.value == "count": return z3.Int(f"{name}_{suffix}")
        return z3.Real(f"{name}_{suffix}")

    def constrain(self, solver, symbol, definition, values, step):
        if definition.type is ValueType.BOOLEAN:
            if values: solver.add(z3.Or(*(symbol == z3.BoolVal(bool(v)) for v in values)))
            return
        solver.add(symbol >= _q(definition.lower), symbol <= _q(definition.upper))
        if values:
            solver.add(z3.Or(*(symbol == _q(v) for v in values)))
        elif step:
            solver.add(z3.IsInt((symbol - _q(definition.lower)) / _q(step)))

    def rules(self, state_env, cost):
        env = {name: _q(parameter.value) if not isinstance(parameter.value, bool) else z3.BoolVal(parameter.value)
               for name, parameter in self.spec.parameters.items()} | dict(state_env) | {"action_cost": cost}
        outputs = {}
        for rule in self.spec.rules:
            outputs[rule.name] = self.expression(rule.expression, env | outputs, f"rules.{rule.name}")
        utility = self.expression(self.spec.utility.expression, env | outputs, "utility")
        designer = {rule.name: self.expression(rule.expression, env | outputs, f"designer.{rule.name}")
                    for rule in self.spec.designer_outcomes}
        return outputs, utility, designer


class FormalVerifier:
    def __init__(self, spec: InstitutionSpec, domain: FormalDomain, timeout_ms: int = 5000):
        self.spec, self.domain, self.timeout_ms = spec, domain, timeout_ms
        self.translation = _Translator(spec)

    def _solver(self):
        solver = z3.Solver(); solver.set(timeout=self.timeout_ms, random_seed=0); return solver

    def _build_deviation(self, action_name: str):
        if action_name not in self.spec.actions: raise IncentiveSpecError(f"Unknown action {action_name!r}")
        solver = self._solver(); action = self.spec.actions[action_name]
        before = {name: self.translation.symbol(name, definition, "0") for name, definition in self.spec.attributes.items()}
        controls = {name: self.translation.symbol(name, definition, "action") for name, definition in action.controls.items()}
        for name, definition in self.spec.attributes.items():
            self.translation.constrain(solver, before[name], definition, self.domain.state_values.get(name, ()), self.domain.state_steps.get(name))
        for name, definition in action.controls.items():
            self.translation.constrain(solver, controls[name], definition, self.domain.control_values.get(name, ()), self.domain.control_steps.get(name))
        params = {name: _q(p.value) if not isinstance(p.value, bool) else z3.BoolVal(p.value) for name,p in self.spec.parameters.items()}
        pre_env = params | before | controls
        solver.add(self.translation.expression(action.feasibility, pre_env, f"actions.{action_name}.feasibility"))
        after = {}
        for name, definition in self.spec.attributes.items():
            after[name] = self.translation.symbol(name, definition, "1")
            rhs = self.translation.expression(action.transition.effects[name], pre_env, f"actions.{action_name}.transition.{name}") if name in action.transition.effects else before[name]
            solver.add(after[name] == rhs)
            self.translation.constrain(solver, after[name], definition, (), None)
        cost = self.translation.expression(action.cost.expression, pre_env, f"actions.{action_name}.cost")
        solver.add(cost >= 0)
        baseline_outputs, baseline_utility, baseline_designer = self.translation.rules(before, _q(0))
        outputs, utility, designer = self.translation.rules(after, cost)
        return solver, before, controls, after, cost, baseline_outputs, baseline_utility, baseline_designer, outputs, utility, designer

    def verify_no_profitable_deviation(self, action_name: str, property_id: str = "no_profitable_deviation") -> FormalResult:
        build_start = perf_counter()
        try:
            model = self._build_deviation(action_name)
            solver, before, controls, after, cost, base_outputs, base_utility, base_designer, outputs, utility, designer = model
            solver.add(utility > base_utility)
        except (UnsupportedFragment, IncentiveSpecError) as exc:
            return self._result(FormalStatus.UNSUPPORTED_FRAGMENT, property_id, action_name, 0, 0, message=str(exc))
        build = perf_counter() - build_start; solve_start = perf_counter(); check = solver.check(); solve = perf_counter() - solve_start
        if check == z3.unsat:
            return self._result(FormalStatus.FORMALLY_SATISFIED_WITHIN_DOMAIN, property_id, action_name, build, solve,
                                message="No profitable deviation exists in the encoded domain and fragment.")
        if check == z3.unknown:
            reason = solver.reason_unknown(); status = FormalStatus.TIMEOUT if "timeout" in reason.lower() else FormalStatus.UNKNOWN
            return self._result(status, property_id, action_name, build, solve, reason, message=reason)
        decode_start = perf_counter(); zmodel = solver.model()
        try:
            state = {name: _decode(zmodel.eval(symbol, model_completion=True), self.spec.attributes[name].type is ValueType.BOOLEAN) for name,symbol in before.items()}
            control_values = {name: _decode(zmodel.eval(symbol, model_completion=True), self.spec.actions[action_name].controls[name].type is ValueType.BOOLEAN) for name,symbol in controls.items()}
            predicted = {name: _decode(zmodel.eval(term, model_completion=True)) for name,term in outputs.items()}
            predicted_utility = _decode(zmodel.eval(utility, model_completion=True))
        except UnsupportedFragment as exc:
            return self._result(FormalStatus.UNSUPPORTED_FRAGMENT, property_id, action_name, build, solve, message=str(exc))
        decode = perf_counter() - decode_start; replay_start = perf_counter()
        action_instance = ActionInstance(action_name, control_values)
        try:
            runtime = evaluate(self.spec, state, action_instance); baseline = evaluate(self.spec, state)
            agreement = (runtime.utility == predicted_utility and runtime.utility > baseline.utility
                         and all(runtime.outcome.rule_outputs[k] == v for k,v in predicted.items()))
        except IncentiveSpecError:
            agreement = False
        replay = perf_counter() - replay_start
        if not agreement:
            return self._result(FormalStatus.BACKEND_DISAGREEMENT, property_id, action_name, build, solve,
                                witness=None, decode=decode, replay=replay, message="SAT witness failed exact M1 replay")
        assignment = {str(decl): str(zmodel[decl]) for decl in zmodel.decls()}
        witness = FormalWitness("Z3", z3.get_version_string(), property_id, spec_hash(self.spec), assignment,
                                state, action_instance, predicted, predicted_utility,
                                FormalStatus.FORMALLY_VIOLATED, "PASS", True)
        return self._result(FormalStatus.FORMALLY_VIOLATED, property_id, action_name, build, solve,
                            witness=witness, decode=decode, replay=replay,
                            message="Profitable deviation exists; witness replayed exactly.")

    def evaluate_fixed(self, state: Mapping[str, Decimal | bool], action: ActionInstance):
        model = self._build_deviation(action.name)
        solver, before, controls, after, cost, _, _, _, outputs, utility, designer = model
        for name,value in state.items(): solver.add(before[name] == (z3.BoolVal(value) if isinstance(value,bool) else _q(value)))
        for name,value in action.controls.items(): solver.add(controls[name] == (z3.BoolVal(value) if isinstance(value,bool) else _q(value)))
        if solver.check() != z3.sat: raise IncentiveSpecError("Fixed formal input is infeasible")
        m=solver.model()
        return {
            "state": {n:_decode(m.eval(v,model_completion=True), self.spec.attributes[n].type is ValueType.BOOLEAN) for n,v in after.items()},
            "outputs": {n:_decode(m.eval(v,model_completion=True)) for n,v in outputs.items()},
            "utility": _decode(m.eval(utility,model_completion=True)),
            "designer": {n:_decode(m.eval(v,model_completion=True)) for n,v in designer.items()},
            "cost": _decode(m.eval(cost,model_completion=True)),
        }

    def _result(self, status, property_id, action, build, solve, reason=None, witness=None, decode=0, replay=0, message=""):
        return FormalResult(status, property_id, spec_hash(self.spec), _domain_hash(self.spec,self.domain,property_id,action),
                            "Z3", z3.get_version_string(), self.timeout_ms, reason, build, solve, decode, replay, witness, message)


def formal_result_json(result: FormalResult) -> str:
    def norm(value):
        if isinstance(value, Decimal): return format(value,"f")
        if isinstance(value, Enum): return value.value
        if hasattr(value,"__dataclass_fields__"): return norm(asdict(value))
        if isinstance(value,dict): return {k:norm(v) for k,v in value.items()}
        if isinstance(value,(tuple,list)): return [norm(v) for v in value]
        return value
    return json.dumps(norm(result),sort_keys=True,indent=2)
