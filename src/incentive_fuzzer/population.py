from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
from decimal import Decimal
from enum import Enum
from hashlib import sha256
from itertools import product
import json, math, random
from typing import Any, Mapping

from .core import ActionInstance, IncentiveSpecError, InstitutionSpec, evaluate, spec_hash


class Provenance(str, Enum):
    E="E"; L="L"; S="S"; A="A"


class BehavioralKind(str, Enum):
    FULL_OPTIMIZATION="B0_FULL_OPTIMIZATION"
    LIMITED_SEARCH="B1_LIMITED_SEARCH"
    SATISFICING="B2_SATISFICING"


@dataclass(frozen=True)
class ParameterProvenance:
    provenance: Provenance
    source: str | None
    rationale: str


@dataclass(frozen=True)
class AgentType:
    id: str
    weight: Decimal
    state: Mapping[str, Decimal | bool]
    cost_multiplier: Decimal=Decimal(1)
    fixed_cost: Decimal=Decimal(0)
    hurdle: Decimal=Decimal(0)
    action_availability: tuple[str,...]=()
    provenance: Mapping[str,ParameterProvenance]=field(default_factory=dict)


@dataclass(frozen=True)
class BehavioralScenario:
    id: str
    kind: BehavioralKind
    candidate_limit: int | None=None
    hurdle: Decimal=Decimal(0)


@dataclass(frozen=True)
class PopulationSpecification:
    id: str
    members: tuple[AgentType,...]

    def __post_init__(self):
        if not self.members or sum((m.weight for m in self.members),Decimal(0))<=0:
            raise ValueError("population must have positive total weight")
        if any(m.weight<0 for m in self.members): raise ValueError("population weights cannot be negative")
        if len({m.id for m in self.members}) != len(self.members): raise ValueError("member ids must be unique")


@dataclass(frozen=True)
class IndividualResult:
    member_id: str
    weight: Decimal
    baseline_utility: Decimal
    best_action: ActionInstance | None
    raw_gain: Decimal
    adjusted_gain: Decimal
    adopted: bool
    profitable: bool
    profitable_actions: int
    baseline_designer: Mapping[str,Decimal|bool]
    strategic_designer: Mapping[str,Decimal|bool]
    resulting_state: Mapping[str,Decimal|bool]
    evaluations: int


@dataclass(frozen=True)
class DistributionSummary:
    profitable_share: Decimal
    response_share: Decimal
    mean_positive_gain: Decimal
    max_gain: Decimal
    designer_change: Mapping[str,Decimal]
    action_shares: Mapping[str,Decimal]


@dataclass(frozen=True)
class PopulationResult:
    study_id: str
    spec_hash: str
    population_hash: str
    scenario: BehavioralScenario
    search_method: str
    individuals: tuple[IndividualResult,...]
    summary: DistributionSummary
    evaluations: int


@dataclass(frozen=True)
class RobustnessEnvelope:
    parameter_names: tuple[str,...]
    cells: tuple[Mapping[str,Any],...]
    profitable_cells: int
    total_cells: int
    scenario_robustness: Decimal


def _norm(value):
    if isinstance(value,Decimal): return format(value,"f")
    if isinstance(value,Enum): return value.value
    if hasattr(value,"__dataclass_fields__"): return _norm(asdict(value))
    if isinstance(value,dict): return {k:_norm(v) for k,v in sorted(value.items())}
    if isinstance(value,(tuple,list)): return [_norm(v) for v in value]
    return value


def population_hash(population: PopulationSpecification)->str:
    return sha256(json.dumps(_norm(population),sort_keys=True).encode()).hexdigest()


def deterministic_grid(base_id:str, states:Mapping[str,tuple[Any,...]], fixed_costs:tuple[Any,...],
                       multipliers:tuple[Any,...]=(1,), hurdle=0, correlated:bool=False)->PopulationSpecification:
    members=[]
    state_rows=[]
    if correlated:
        lengths={len(v) for v in states.values()}
        if len(lengths)!=1: raise ValueError("correlated state columns require equal lengths")
        state_rows=[dict(zip(states,(vals[i] for vals in states.values()))) for i in range(next(iter(lengths)))]
    else:
        keys=tuple(states); state_rows=[dict(zip(keys,vals)) for vals in product(*(states[k] for k in keys))]
    for index,(state,fixed,mult) in enumerate(product(state_rows,fixed_costs,multipliers)):
        members.append(AgentType(f"{base_id}-{index}",Decimal(1),{k:Decimal(str(v)) for k,v in state.items()},
            Decimal(str(mult)),Decimal(str(fixed)),Decimal(str(hurdle)),(),
            {"state":ParameterProvenance(Provenance.S,None,"precommitted synthetic grid"),
             "cost":ParameterProvenance(Provenance.A,None,"adversarial sensitivity bound")}))
    weight=Decimal(1)/Decimal(len(members))
    return PopulationSpecification(base_id,tuple(replace(m,weight=weight) for m in members))


def evaluate_member(spec:InstitutionSpec, member:AgentType, action_values:Mapping[str,Mapping[str,tuple[Any,...]]],
                    scenario:BehavioralScenario)->IndividualResult:
    baseline=evaluate(spec,member.state); options=[]; evaluations=1
    allowed=member.action_availability or tuple(action_values)
    for action_name in allowed:
        names=tuple(action_values[action_name]); candidates=list(product(*(action_values[action_name][n] for n in names)))
        if scenario.kind is BehavioralKind.LIMITED_SEARCH and scenario.candidate_limit is not None:
            candidates=candidates[:scenario.candidate_limit]
        for values in candidates:
            try: result=evaluate(spec,member.state,ActionInstance(action_name,dict(zip(names,values)))); evaluations+=1
            except IncentiveSpecError: continue
            raw=result.utility-baseline.utility
            adjusted=raw-(member.cost_multiplier-Decimal(1))*result.action_cost-member.fixed_cost
            options.append((adjusted,raw,action_name,values,result))
    options.sort(key=lambda x:(x[0],tuple(-Decimal(str(v)) for v in x[3])),reverse=True)
    best=options[0] if options else None
    gain=best[0] if best else Decimal(0); threshold=max(member.hurdle,scenario.hurdle)
    profitable=gain>0; adopted=profitable if scenario.kind is not BehavioralKind.SATISFICING else profitable and gain>=threshold
    if best:
        adjusted,raw,name,values,best_result=best
        chosen=ActionInstance(name,dict(zip(action_values[name],values)))
    else:
        adjusted=raw=Decimal(0); chosen=None; best_result=baseline
    strategic=best_result if adopted else baseline
    profitable_actions=sum(1 for x in options if x[0]>0)
    return IndividualResult(member.id,member.weight,baseline.utility,chosen,raw,adjusted,adopted,profitable,
        profitable_actions,baseline.outcome.designer_outcomes,strategic.outcome.designer_outcomes,
        strategic.resulting_state.values,evaluations)


def evaluate_population(spec:InstitutionSpec,population:PopulationSpecification,scenario:BehavioralScenario,
                        action_values:Mapping[str,Mapping[str,tuple[Any,...]]],study_id="population-study")->PopulationResult:
    results=tuple(evaluate_member(spec,m,action_values,scenario) for m in population.members)
    total=sum((r.weight for r in results),Decimal(0)); profitable=sum((r.weight for r in results if r.profitable),Decimal(0))/total
    response=sum((r.weight for r in results if r.adopted),Decimal(0))/total
    positive=[r for r in results if r.profitable]; pw=sum((r.weight for r in positive),Decimal(0))
    mean=sum((r.weight*r.adjusted_gain for r in positive),Decimal(0))/pw if pw else Decimal(0)
    maximum=max((r.adjusted_gain for r in results),default=Decimal(0))
    designer={}
    for r in results:
        for name in r.baseline_designer:
            designer[name]=designer.get(name,Decimal(0))+r.weight*(Decimal(r.strategic_designer[name])-Decimal(r.baseline_designer[name]))/total
    shares={}
    for r in results:
        name=r.best_action.name if r.adopted and r.best_action else "no_deviation"; shares[name]=shares.get(name,Decimal(0))+r.weight/total
    summary=DistributionSummary(profitable,response,mean,maximum,designer,shares)
    return PopulationResult(study_id,spec_hash(spec),population_hash(population),scenario,"exhaustive",results,summary,sum(r.evaluations for r in results))


def sample_weighted(population:PopulationSpecification,n:int,seed:int)->PopulationSpecification:
    rng=random.Random(seed); members=list(population.members); weights=[float(m.weight) for m in members]
    draws=rng.choices(members,weights=weights,k=n); weight=Decimal(1)/Decimal(n)
    sampled=tuple(AgentType(f"sample-{i}",weight,d.state,d.cost_multiplier,d.fixed_cost,d.hurdle,d.action_availability,d.provenance) for i,d in enumerate(draws))
    return PopulationSpecification(f"{population.id}-mc-{n}-{seed}",sampled)


def wilson_interval(successes:int,n:int,z=1.96)->tuple[float,float]:
    if n<=0: raise ValueError("n must be positive")
    p=successes/n; den=1+z*z/n; center=(p+z*z/(2*n))/den
    half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return center-half,center+half
