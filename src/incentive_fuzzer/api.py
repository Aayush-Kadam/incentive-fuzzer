"""Small convenience API for research-preview integrations.

Advanced users may import layer-specific classes from their modules. These wrappers keep
the common load/search/verify/benchmark path compact without hiding scoped statuses.
"""
from pathlib import Path
from decimal import Decimal

from .benchmark import load_runtime_suite, run_case
from .core import ValueType, load_spec
from .search import SearchBudget, SearchDomain, SearchEngine, SearchProblem, extract_boundaries
from .verify import FormalDomain, FormalVerifier


def _values(lower, upper, boundaries):
    lower,upper=int(lower),int(upper)
    values={lower,upper,0,lower+1,lower+2,upper-1,(lower+upper)//2}
    for boundary in boundaries: values.update({int(boundary)-1,int(boundary),int(boundary)+1})
    return tuple(Decimal(v) for v in sorted(v for v in values if lower<=v<=upper))


def validate_spec(path):
    return load_spec(path)


def _declared_domain(spec):
    boundaries=extract_boundaries(spec); states={}; actions={}
    for name,attribute in spec.attributes.items():
        related=[boundary.value for boundary in boundaries if boundary.attribute==name]
        states[name]=(False,True) if attribute.type is ValueType.BOOLEAN else _values(attribute.lower,attribute.upper,related)
    for name,action in spec.actions.items():
        actions[name]={control:_values(definition.lower,definition.upper,()) for control,definition in action.controls.items()}
    return states,actions


def search_spec(path, method="combined", max_evaluations=1000):
    spec=load_spec(path); states,actions=_declared_domain(spec)
    return SearchEngine(SearchProblem(spec,SearchDomain(states,actions))).run(
        method,SearchBudget(max_evaluations,max_evaluations,30))


def verify_spec(path, action, timeout_ms=5000):
    spec=load_spec(path); states,actions=_declared_domain(spec)
    return FormalVerifier(spec,FormalDomain(states,actions[action]),timeout_ms).verify_no_profitable_deviation(action)


def run_benchmark(root=Path("benchmarks/if_bench/v0.1"), method="combined", max_evaluations=100):
    return tuple(run_case(case,method,max_evaluations) for case in load_runtime_suite(root))
