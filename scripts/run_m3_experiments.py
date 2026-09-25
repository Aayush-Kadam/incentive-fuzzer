"""Run and persist M3 exact-rational verification experiments."""
from decimal import Decimal
from pathlib import Path
import csv, json, random, subprocess

import z3
from incentive_fuzzer import ActionInstance, evaluate, load_spec
from incentive_fuzzer.search import SearchBudget, SearchDomain, SearchEngine, SearchProblem
from incentive_fuzzer.verify import FormalDomain, FormalStatus, FormalVerifier, formal_result_json

ROOT=Path(__file__).parents[1]; BASE=ROOT/"experiments/m3"
for d in ("configs","runs","witnesses","tables","figures"): (BASE/d).mkdir(parents=True,exist_ok=True)

def dec(vals): return tuple(Decimal(str(v)) for v in vals)
def fd(states,controls): return FormalDomain({k:dec(v) for k,v in states.items()},{k:dec(v) for k,v in controls.items()})
def exhaustive(spec,states,action,controls):
    sd=SearchDomain({k:dec(v) for k,v in states.items()},{action:{k:dec(v) for k,v in controls.items()}})
    return SearchEngine(SearchProblem(spec,sd,allowed_actions=(action,))).run("exhaustive",SearchBudget(100000,100000,60))
def write_csv(name,rows):
    with (BASE/"tables"/name).open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

canonical_defs={
 "scholarship_cliff":("reduce_work",{"true_income":[499999,500000,500001],"reported_income":[499999,500000,500001]},{"amount":[0,1,2]}),
 "linear_phase_out":("reduce_income",{"income":[479999,480000,480001,550000,619999,620000,620001]},{"amount":range(6)}),
 "stacked_programs":("reduce_income",{"income":range(21)},{"amount":range(6)}),
 "procurement_threshold":("reduce_scope",{"transaction_value":range(95,106)},{"amount":range(11)}),
 "honest_reporting_control":("misreport",{"true_income":range(21),"reported_income":range(21)},{"amount":range(11)}),
}
canonical=[]; witnesses=[]; performance=[]
for name,(action,states,controls) in canonical_defs.items():
    spec=load_spec(ROOT/"examples"/f"{name}.yaml"); ex=exhaustive(spec,states,action,controls)
    result=FormalVerifier(spec,fd(states,controls),5000).verify_no_profitable_deviation(action)
    m2="violation" if ex.raw_findings else "none"; smt="SAT" if result.status is FormalStatus.FORMALLY_VIOLATED else "UNSAT"
    agree=(m2=="violation")==(smt=="SAT")
    canonical.append({"fixture":name,"property":"no_profitable_deviation","m2_exhaustive":m2,"smt":smt,
      "formal_status":result.status.value,"m1_replay":"pass" if result.witness else "n/a","agreement":agree})
    performance.append({"fixture":name,"build_seconds":result.build_seconds,"solve_seconds":result.solve_seconds,
      "decode_seconds":result.decode_seconds,"replay_seconds":result.replay_seconds,
      "total_seconds":result.build_seconds+result.solve_seconds+result.decode_seconds+result.replay_seconds})
    if result.witness:
        (BASE/"witnesses"/f"{name}.json").write_text(formal_result_json(result),encoding="utf-8")
        witnesses.append({"fixture":name,"status":result.status.value,"replay":result.witness.runtime_replay,
                          "agreement":result.witness.agreement})

benchmark=[]
labels={x["id"]:x["known_violation"] for x in __import__("yaml").safe_load((ROOT/"benchmarks/m2/ground_truth.yaml").read_text())["cases"]}
for path in sorted((ROOT/"benchmarks/m2/specs").glob("*.yaml")):
    spec=load_spec(path); states={k:range(31) for k in spec.attributes}; controls={"amount":range(11)}
    result=FormalVerifier(spec,fd(states,controls),5000).verify_no_profitable_deviation("deviation")
    smt_violation=result.status is FormalStatus.FORMALLY_VIOLATED
    benchmark.append({"fixture":path.stem,"expected_violation":labels[path.stem],"formal_status":result.status.value,
      "status_agreement":smt_violation==labels[path.stem],"witness_replay":"pass" if result.witness else "n/a",
      "supported":result.status not in {FormalStatus.UNSUPPORTED_FRAGMENT,FormalStatus.UNKNOWN,FormalStatus.TIMEOUT}})

rng=random.Random(20260926); differential=[]; mismatches=0
paths=list((ROOT/"benchmarks/m2/specs").glob("*.yaml"))
for i in range(500):
    path=rng.choice(paths); spec=load_spec(path)
    state={n:Decimal(rng.randint(int(d.lower),int(d.upper))) for n,d in spec.attributes.items()}
    amount=Decimal(rng.randint(0,min(10,int(state.get("reported_income",state.get("income",0)))))); action=ActionInstance("deviation",{"amount":amount})
    formal=FormalVerifier(spec,fd({k:[v] for k,v in state.items()},{"amount":[amount]})).evaluate_fixed(state,action)
    runtime=evaluate(spec,state,action); ok=(formal["state"]==runtime.resulting_state.values and formal["outputs"]==runtime.outcome.rule_outputs and formal["utility"]==runtime.utility and formal["designer"]==runtime.outcome.designer_outcomes)
    mismatches+=not ok; differential.append({"case":i,"fixture":path.stem,"agreement":ok})

unsat=[{"fixture":r["fixture"],"smt_unsat":r["smt"]=="UNSAT","exhaustive_none":r["m2_exhaustive"]=="none","agreement":r["agreement"]} for r in canonical if r["smt"]=="UNSAT"]
write_csv("canonical_agreement.csv",canonical); write_csv("benchmark_agreement.csv",benchmark)
write_csv("generated_differential.csv",differential); write_csv("witness_replay.csv",witnesses)
write_csv("unsat_agreement.csv",unsat); write_csv("solver_performance.csv",performance)
commit=subprocess.check_output(["git","-c",f"safe.directory={ROOT.as_posix()}","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
summary={"run_id":"m3-exact-smt-001","git_commit":commit,"solver":"Z3","solver_version":z3.get_version_string(),
 "timeout_ms":5000,"canonical":canonical,"benchmark":benchmark,
 "generated_differential":{"cases":500,"mismatches":mismatches,"seed":20260926},
 "sat_witnesses":len(witnesses),"sat_replay_passes":sum(w["agreement"] for w in witnesses),
 "supported_benchmark_cases":sum(r["supported"] for r in benchmark),"benchmark_status_agreements":sum(r["status_agreement"] for r in benchmark),
 "unsat_cases":len(unsat),"unsat_agreements":sum(r["agreement"] for r in unsat)}
(BASE/"runs"/"summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
(BASE/"runs"/"run_manifest.json").write_text(json.dumps({k:summary[k] for k in ("run_id","git_commit","solver","solver_version","timeout_ms")}|{"seed":20260926},indent=2),encoding="utf-8")
print(json.dumps(summary,indent=2))
