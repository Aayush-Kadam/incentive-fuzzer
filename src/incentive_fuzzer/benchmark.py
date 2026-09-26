"""Blind, versioned benchmark support for IF-Bench."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from decimal import Decimal
from enum import Enum
from hashlib import sha256
from pathlib import Path
import json, random
from time import perf_counter
from typing import Any, Iterable, Mapping
import yaml
from .core import parse_spec
from .verify import FormalDomain, FormalStatus, FormalVerifier

FORBIDDEN_RUNTIME_FIELDS=frozenset({"known_vulnerability","expected_attack","ground_truth_class","pathology_name","hidden_label","expected_violation"})
class BenchmarkError(ValueError): pass
class BaselineMethod(str,Enum):
    RANDOM="random"; GRID="grid"; BOUNDARY="boundary"; EXHAUSTIVE="exhaustive"; COMBINED="combined"

@dataclass(frozen=True)
class BenchmarkCase:
    benchmark_id:str; title:str; origin:str; domain:str; difficulty:int; split:str
    rule_version:str; source_id:str; representability:str; model:str
    lower:Decimal; upper:Decimal; threshold:Decimal|None; second_threshold:Decimal|None
    award:Decimal; second_award:Decimal; withdrawal_rate:Decimal; process_cost:Decimal
    action_cost_rate:Decimal; step:Decimal; action_values:tuple[Decimal,...]
    threat_model:Mapping[str,Any]; properties:tuple[str,...]; notes:tuple[str,...]
@dataclass(frozen=True)
class HiddenLabel:
    benchmark_id:str; known_vulnerability:bool; expected_if_cwe:str|None; pathology_name:str
    ground_truth_type:str; evidence_class:str; match_standard:str
@dataclass(frozen=True)
class Candidate: baseline:Decimal; action:Decimal; source:str
@dataclass(frozen=True)
class BenchmarkFinding:
    benchmark_id:str; baseline:Decimal; result:Decimal; action:Decimal
    baseline_utility:Decimal; result_utility:Decimal; gain:Decimal; if_cwe:str
    method:str; candidate_source:str; replayed:bool; raw_size:Decimal; reduced_size:Decimal
@dataclass(frozen=True)
class CaseRun:
    benchmark_id:str; method:str; status:str; evaluations:int; elapsed_seconds:float
    evaluations_to_first:int|None; time_to_first:float|None; finding:BenchmarkFinding|None
@dataclass(frozen=True)
class Score:
    total:int; positives:int; detected:int; class_matches:int; negatives:int; false_positives:int
    @property
    def case_recall(self): return self.detected/self.positives if self.positives else None
    @property
    def class_recall(self): return self.class_matches/self.positives if self.positives else None
    @property
    def false_positive_rate(self): return self.false_positives/self.negatives if self.negatives else None

class SMTEligibility(str,Enum):
    SUPPORTED="SMT_SUPPORTED"; UNSUPPORTED="SMT_UNSUPPORTED"

@dataclass(frozen=True)
class SMTBaselineRun:
    benchmark_id:str; eligibility:SMTEligibility; status:str; reason:str
    elapsed_seconds:float; replayed:bool; property_id:str

@dataclass(frozen=True)
class SMTScore:
    total:int; supported:int; violated:int; satisfied:int; unsupported:int
    timeouts:int; unknown:int; backend_disagreements:int; supported_positives:int
    detected:int; supported_negatives:int; false_positives:int
    ground_truth_agreements:int; combined_agreements:int; replayed:int

def _d(v): return v if isinstance(v,Decimal) else Decimal(str(v))
def _walk(v,path="runtime"):
    if isinstance(v,Mapping):
        for k,x in v.items():
            if str(k) in FORBIDDEN_RUNTIME_FIELDS: raise BenchmarkError(f"hidden label field at {path}.{k}")
            _walk(x,f"{path}.{k}")
    elif isinstance(v,list):
        for i,x in enumerate(v): _walk(x,f"{path}[{i}]")

def load_runtime_case(path:str|Path)->BenchmarkCase:
    raw=yaml.safe_load(Path(path).read_text(encoding="utf-8")); _walk(raw)
    required={"benchmark_id","title","origin","domain","difficulty","split","rule_version","source_id","representability","runtime_input","threat_model","properties"}
    if not isinstance(raw,dict) or required-raw.keys(): raise BenchmarkError(f"missing runtime fields: {sorted(required-set(raw or {}))}")
    m=raw["runtime_input"]; actions=tuple(_d(x) for x in m["action_values"])
    if raw["representability"] not in {"FULLY_REPRESENTABLE","PARTIALLY_REPRESENTABLE"}: raise BenchmarkError("included case is not representable")
    if not actions or any(x<0 for x in actions): raise BenchmarkError("invalid action values")
    return BenchmarkCase(raw["benchmark_id"],raw["title"],raw["origin"],raw["domain"],int(raw["difficulty"]),raw["split"],str(raw["rule_version"]),raw["source_id"],raw["representability"],m["model"],_d(m["lower"]),_d(m["upper"]),None if m.get("threshold") is None else _d(m["threshold"]),None if m.get("second_threshold") is None else _d(m["second_threshold"]),_d(m.get("award",0)),_d(m.get("second_award",0)),_d(m.get("withdrawal_rate",0)),_d(m.get("process_cost",0)),_d(m.get("action_cost_rate",0)),_d(m.get("step",1)),actions,raw["threat_model"],tuple(raw["properties"]),tuple(raw.get("notes",())))
def load_runtime_suite(root:str|Path):
    cases=tuple(load_runtime_case(p) for p in sorted((Path(root)/"cases").glob("*/case.yaml")))
    if len(cases)!=len({c.benchmark_id for c in cases}): raise BenchmarkError("duplicate benchmark ID")
    return cases
def load_labels_for_scoring(root:str|Path):
    result={}
    for p in sorted((Path(root)/"labels").glob("*.json")):
        label=HiddenLabel(**json.loads(p.read_text(encoding="utf-8")))
        if label.benchmark_id in result: raise BenchmarkError("duplicate label")
        result[label.benchmark_id]=label
    return result
def jsonable(v):
    if isinstance(v,Decimal): return format(v,"f")
    if isinstance(v,Enum): return v.value
    if hasattr(v,"__dataclass_fields__"): return jsonable(asdict(v))
    if isinstance(v,Mapping): return {str(k):jsonable(x) for k,x in v.items()}
    if isinstance(v,(tuple,list)): return [jsonable(x) for x in v]
    return v
def case_hash(case): return sha256(json.dumps(jsonable(case),sort_keys=True).encode()).hexdigest()

def _benefit(c,x):
    if c.model=="hard_cliff": return c.award if x<c.threshold else Decimal(0)
    if c.model=="inclusive_cliff": return c.award if x<=c.threshold else Decimal(0)
    if c.model=="phase_out": return max(Decimal(0),c.award-c.withdrawal_rate*max(Decimal(0),x-c.threshold))
    if c.model=="composition": return (c.award if x<c.threshold else 0)+(c.second_award if x<c.second_threshold else 0)
    return Decimal(0)
def utility(c,state,action=Decimal(0)):
    if not c.lower<=state<=c.upper or action<0: raise BenchmarkError("input outside domain")
    if c.model=="transaction_split":
        burden=c.process_cost if state>=c.threshold else Decimal(0)
        after=Decimal(0) if action>=2 and state/action<c.threshold else burden
        return state-after-c.action_cost_rate*max(Decimal(0),action-1),state
    result=state-action
    if result<c.lower: raise BenchmarkError("infeasible action")
    if c.model=="process_threshold":
        burden=c.process_cost if result>=c.threshold else Decimal(0)
        return result-burden-c.action_cost_rate*action,result
    return result+_benefit(c,result)-c.action_cost_rate*action,result
def _states(c):
    out=[]; x=c.lower
    while x<=c.upper: out.append(x); x+=c.step
    return tuple(out)
def _all(c): return [Candidate(s,a,"domain") for s in _states(c) for a in c.action_values if c.model=="transaction_split" or s-a>=c.lower]
def _boundary(c):
    states=[]
    for t in (c.threshold,c.second_threshold):
        if t is not None:
            for x in (t-c.step,t,t+c.step):
                if c.lower<=x<=c.upper and x not in states: states.append(x)
    return [Candidate(s,a,"boundary") for s in states for a in c.action_values if c.model=="transaction_split" or s-a>=c.lower]
def candidates(c,method,seed):
    method=BaselineMethod(method); all_items=_all(c)
    if method is BaselineMethod.RANDOM:
        random.Random(seed^int(case_hash(c)[:8],16)).shuffle(all_items); return all_items
    if method is BaselineMethod.BOUNDARY: return _boundary(c)
    if method is BaselineMethod.COMBINED:
        first=_boundary(c); seen={(x.baseline,x.action) for x in first}
        return first+[Candidate(x.baseline,x.action,"grid") for x in all_items if (x.baseline,x.action) not in seen]
    if method is BaselineMethod.GRID:
        stride=max(1,len(all_items)//50); return [Candidate(x.baseline,x.action,"grid") for x in all_items[::stride]]
    return all_items
def classify(c):
    if c.model=="transaction_split": return "IF-007"
    if c.model=="composition": return "IF-015"
    if c.model in {"hard_cliff","inclusive_cliff","process_threshold"}: return "IF-001"
    return "IF-003"
def replay(c,f):
    base,_=utility(c,f.baseline); changed,result=utility(c,f.baseline,f.action)
    return result==f.result and changed-base==f.gain and f.gain>0
def _reduce(c,raw):
    for action in sorted(x for x in c.action_values if 0<x<=raw.action):
        base,_=utility(c,raw.baseline); changed,result=utility(c,raw.baseline,action)
        if changed>base: return BenchmarkFinding(c.benchmark_id,raw.baseline,result,action,base,changed,changed-base,raw.if_cwe,raw.method,raw.candidate_source,True,raw.raw_size,action)
    return raw
def run_case(c,method,max_evaluations=100,seed=20260926,reduce=True):
    method=BaselineMethod(method); start=perf_counter(); evaluated=0; finding=None; first=None
    for candidate in candidates(c,method,seed):
        if evaluated>=max_evaluations: break
        evaluated+=1
        try: base,_=utility(c,candidate.baseline); changed,result=utility(c,candidate.baseline,candidate.action)
        except BenchmarkError: continue
        if changed>base:
            first=perf_counter()-start; finding=BenchmarkFinding(c.benchmark_id,candidate.baseline,result,candidate.action,base,changed,changed-base,classify(c),method.value,candidate.source,True,candidate.action,candidate.action)
            if reduce: finding=_reduce(c,finding)
            break
    complete=method is BaselineMethod.EXHAUSTIVE and evaluated==len(_all(c))
    status="VIOLATION_FOUND" if finding else ("EXHAUSTIVE_NO_VIOLATION" if complete else "NO_VIOLATION_FOUND_WITHIN_BUDGET")
    return CaseRun(c.benchmark_id,method.value,status,evaluated,perf_counter()-start,evaluated if finding else None,first,finding)
def score_frozen_runs(runs:Iterable[CaseRun],labels):
    p=d=cm=n=fp=0; frozen=tuple(runs)
    for run in frozen:
        label=labels[run.benchmark_id]
        if label.known_vulnerability:
            p+=1
            if run.finding: d+=1; cm+=run.finding.if_cwe==label.expected_if_cwe
        else: n+=1; fp+=run.finding is not None
    return Score(len(frozen),p,d,cm,n,fp)

def formal_confirm(c, timeout_ms=5000):
    if c.model not in {"hard_cliff","inclusive_cliff","phase_out","process_threshold"}: return None
    if c.model=="phase_out": benefit={"max":[{"const":{"value":0,"unit":"money"}},{"sub":[{"var":"award"},{"mul":[{"var":"withdrawal_rate"},{"max":[{"const":{"value":0,"unit":"money"}},{"sub":[{"var":"metric"},{"var":"threshold"}]}]}]}]}]}
    elif c.model=="process_threshold": benefit={"mul":[{"const":{"value":-1,"unit":"scalar"}},{"if":{"condition":{"ge":[{"var":"metric"},{"var":"threshold"}]},"then":{"var":"process_cost"},"else":{"const":{"value":0,"unit":"money"}}}}]}
    else:
        op="le" if c.model=="inclusive_cliff" else "lt"; benefit={"if":{"condition":{op:[{"var":"metric"},{"var":"threshold"}]},"then":{"var":"award"},"else":{"const":{"value":0,"unit":"money"}}}}
    raw={"incentive_spec_version":"0.1","institution":{"id":c.benchmark_id,"name":c.title,"description":"IF-Bench component","version":c.rule_version},"parameters":{"threshold":{"type":"money","value":str(c.threshold),"provenance":"L"},"award":{"type":"money","value":str(c.award),"provenance":"A"},"withdrawal_rate":{"type":"decimal","unit":"rate","value":str(c.withdrawal_rate),"provenance":"L"},"process_cost":{"type":"money","value":str(c.process_cost),"provenance":"A"},"action_rate":{"type":"decimal","unit":"rate","value":str(c.action_cost_rate),"provenance":"A"}},"attributes":{"metric":{"type":"money","lower":str(c.lower),"upper":str(c.upper),"observable":True,"manipulable":True,"role":"reported"}},"actions":{"decrease":{"controls":{"amount":{"type":"money","lower":"0","upper":str(max(c.action_values))}},"feasibility":{"le":[{"var":"amount"},{"var":"metric"}]},"transition":{"metric":{"sub":[{"var":"metric"},{"var":"amount"}]}},"cost":{"mul":[{"var":"action_rate"},{"var":"amount"}]}}},"rules":{"benefit":benefit,"resources":{"add":[{"var":"metric"},{"var":"benefit"}]}},"utility":{"sub":[{"var":"resources"},{"var":"action_cost"}]},"designer_outcomes":{"benefit":{"var":"benefit"}},"properties":[]}
    spec=parse_spec(raw); domain=FormalDomain({"metric":tuple(_states(c))},{"amount":tuple(c.action_values)})
    return FormalVerifier(spec,domain,timeout_ms).verify_no_profitable_deviation("decrease")

def run_smt_baseline(c, timeout_ms=5000):
    """Run B5 using only the case runtime spec, formal property, and declared domain.

    The function deliberately has no label argument. Unsupported model adapters remain
    visible instead of disappearing from the baseline denominator.
    """
    supported={"hard_cliff","inclusive_cliff","phase_out","process_threshold"}
    if c.model not in supported:
        return SMTBaselineRun(c.benchmark_id,SMTEligibility.UNSUPPORTED,
            FormalStatus.UNSUPPORTED_FRAGMENT.value,
            f"No IncentiveSpec/M3 adapter for benchmark model {c.model!r}",0.0,False,
            c.properties[0] if c.properties else "")
    if tuple(c.properties)!=("no_profitable_deviation",):
        return SMTBaselineRun(c.benchmark_id,SMTEligibility.UNSUPPORTED,
            FormalStatus.UNSUPPORTED_FRAGMENT.value,
            f"B5 supports only no_profitable_deviation, got {list(c.properties)!r}",0.0,False,
            c.properties[0] if c.properties else "")
    result=formal_confirm(c,timeout_ms)
    elapsed=result.build_seconds+result.solve_seconds+result.decode_seconds+result.replay_seconds
    return SMTBaselineRun(c.benchmark_id,SMTEligibility.SUPPORTED,result.status.value,
        result.message,elapsed,bool(result.witness and result.witness.runtime_replay),result.property_id)

def score_smt_frozen_runs(runs, labels, combined_runs=()):
    frozen=tuple(runs); combined={r.benchmark_id:bool(r.finding) for r in combined_runs}
    supported=[r for r in frozen if r.eligibility is SMTEligibility.SUPPORTED]
    violated=[r for r in supported if r.status==FormalStatus.FORMALLY_VIOLATED.value]
    satisfied=[r for r in supported if r.status==FormalStatus.FORMALLY_SATISFIED_WITHIN_DOMAIN.value]
    timeouts=sum(r.status==FormalStatus.TIMEOUT.value for r in supported)
    unknown=sum(r.status==FormalStatus.UNKNOWN.value for r in supported)
    disagreements=sum(r.status==FormalStatus.BACKEND_DISAGREEMENT.value for r in supported)
    positives=[r for r in supported if labels[r.benchmark_id].known_vulnerability]
    negatives=[r for r in supported if not labels[r.benchmark_id].known_vulnerability]
    truth_agree=sum((r.status==FormalStatus.FORMALLY_VIOLATED.value)==labels[r.benchmark_id].known_vulnerability
                    for r in supported if r.status in {FormalStatus.FORMALLY_VIOLATED.value,FormalStatus.FORMALLY_SATISFIED_WITHIN_DOMAIN.value})
    combined_agree=sum((r.status==FormalStatus.FORMALLY_VIOLATED.value)==combined[r.benchmark_id]
                       for r in supported if r.benchmark_id in combined and r.status in {FormalStatus.FORMALLY_VIOLATED.value,FormalStatus.FORMALLY_SATISFIED_WITHIN_DOMAIN.value})
    return SMTScore(len(frozen),len(supported),len(violated),len(satisfied),len(frozen)-len(supported),
        timeouts,unknown,disagreements,len(positives),sum(r in violated for r in positives),
        len(negatives),sum(r in violated for r in negatives),truth_agree,combined_agree,
        sum(r.replayed for r in violated))
