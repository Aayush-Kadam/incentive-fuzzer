"""Public command-line interface for the research preview."""
from __future__ import annotations

import argparse
from decimal import Decimal
import json
from pathlib import Path
import sys

from .benchmark import load_runtime_suite, run_case
from .core import ActionInstance, IncentiveSpecError, ValueType, evaluate, load_spec, spec_hash
from .search import SearchBudget, SearchDomain, SearchEngine, SearchProblem, finding_to_json
from .verify import FormalDomain, FormalVerifier


def _values(lower, upper, boundaries):
    lower, upper=int(lower),int(upper)
    values={lower,upper,0,lower+1,lower+2,upper-1,(lower+upper)//2}
    for boundary in boundaries: values.update({int(boundary)-1,int(boundary),int(boundary)+1})
    return tuple(Decimal(v) for v in sorted(v for v in values if lower<=v<=upper))


def _domain(spec):
    from .search import extract_boundaries
    boundaries=extract_boundaries(spec); states={}; controls={}
    for name,attr in spec.attributes.items():
        related=[b.value for b in boundaries if b.attribute==name]
        states[name]=(False,True) if attr.type is ValueType.BOOLEAN else _values(attr.lower,attr.upper,related)
    for name,action in spec.actions.items():
        controls[name]={key:_values(defn.lower,defn.upper,()) for key,defn in action.controls.items()}
    return states,controls


def _write(payload, output=None):
    text=json.dumps(payload,indent=2,sort_keys=True,default=lambda value:str(value))
    if output: Path(output).write_text(text,encoding="utf-8")
    print(text)


def _parser():
    parser=argparse.ArgumentParser(prog="incentive-fuzzer",description="Adversarial Testing for Economic Rules")
    parser.add_argument("--version",action="version",version="%(prog)s 0.1.0-research-preview")
    sub=parser.add_subparsers(dest="command",required=True)

    validate=sub.add_parser("validate",help="parse and validate an IncentiveSpec")
    validate.add_argument("spec"); validate.add_argument("--output",type=Path)

    ev=sub.add_parser("evaluate",help="evaluate a baseline or declared action exactly")
    ev.add_argument("spec"); ev.add_argument("--state",required=True,help="JSON object")
    ev.add_argument("--action"); ev.add_argument("--controls",default="{}",help="JSON object")
    ev.add_argument("--output",type=Path)

    search=sub.add_parser("search",help="run bounded adversarial candidate search")
    search.add_argument("spec"); search.add_argument("--method",default="combined",choices=["exhaustive","boundary","property","grid","combined"])
    search.add_argument("--max-evaluations",type=int,default=1000); search.add_argument("--output",type=Path)

    verify=sub.add_parser("verify",help="run exact SMT verification for one action")
    verify.add_argument("spec"); verify.add_argument("--action",required=True); verify.add_argument("--timeout-ms",type=int,default=5000)
    verify.add_argument("--output",type=Path)

    bench=sub.add_parser("benchmark",help="run label-blind IF-Bench candidate evaluation")
    bench.add_argument("--suite",type=Path,default=Path("benchmarks/if_bench/v0.1")); bench.add_argument("--method",default="combined",choices=["random","grid","boundary","exhaustive","combined"])
    bench.add_argument("--max-evaluations",type=int,default=100); bench.add_argument("--output",type=Path)
    return parser


def main(argv=None):
    args=_parser().parse_args(argv)
    try:
        if args.command=="validate":
            spec=load_spec(args.spec); _write({"status":"VALID_SPEC","spec_id":spec.institution.id,"spec_hash":spec_hash(spec)},args.output); return 0
        if args.command=="evaluate":
            spec=load_spec(args.spec); state=json.loads(args.state); controls=json.loads(args.controls)
            action=ActionInstance(args.action,controls) if args.action else None; result=evaluate(spec,state,action)
            _write({"status":"EVALUATED","utility":result.utility,"state":result.resulting_state.values,"rule_outputs":result.outcome.rule_outputs,"designer_outcomes":result.outcome.designer_outcomes,"trace":result.trace},args.output); return 0
        if args.command=="search":
            spec=load_spec(args.spec); states,controls=_domain(spec); problem=SearchProblem(spec,SearchDomain(states,controls))
            result=SearchEngine(problem).run(args.method,SearchBudget(args.max_evaluations,args.max_evaluations,30))
            _write({"run_id":result.run_id,"status":result.status.value,"statistics":result.statistics.__dict__,"findings":[json.loads(finding_to_json(f)) for f in result.findings]},args.output); return 0
        if args.command=="verify":
            spec=load_spec(args.spec); states,controls=_domain(spec)
            if args.action not in controls: raise IncentiveSpecError(f"Unknown action {args.action!r}")
            result=FormalVerifier(spec,FormalDomain(states,controls[args.action]),args.timeout_ms).verify_no_profitable_deviation(args.action)
            _write({"status":result.status.value,"property_id":result.property_id,"message":result.message,"replayed":bool(result.witness and result.witness.runtime_replay),"seconds":result.build_seconds+result.solve_seconds+result.decode_seconds+result.replay_seconds},args.output)
            return 0 if result.status.value not in {"UNKNOWN","TIMEOUT","BACKEND_DISAGREEMENT","UNSUPPORTED_FRAGMENT"} else 2
        if args.command=="benchmark":
            cases=load_runtime_suite(args.suite); runs=[run_case(case,args.method,args.max_evaluations) for case in cases]
            _write({"status":"BENCHMARK_COMPLETE","method":args.method,"cases":len(runs),"violations":sum(run.finding is not None for run in runs),"results":[{"benchmark_id":run.benchmark_id,"status":run.status,"evaluations":run.evaluations} for run in runs]},args.output); return 0
    except (IncentiveSpecError,ValueError,KeyError,json.JSONDecodeError,OSError) as exc:
        print(json.dumps({"status":"ERROR","message":str(exc)}),file=sys.stderr); return 2


if __name__=="__main__": raise SystemExit(main())
