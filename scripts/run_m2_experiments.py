"""Run the deterministic M2 comparisons and write compact reproducibility artifacts."""
from __future__ import annotations
from dataclasses import asdict
from decimal import Decimal
from pathlib import Path
import csv, json, subprocess

from incentive_fuzzer import load_spec
from incentive_fuzzer.search import (
    SearchBudget, SearchDomain, SearchEngine, SearchMethod, SearchProblem,
    finding_equivalence_key, finding_to_json, reduce_finding, replay_finding,
)

ROOT = Path(__file__).parents[1]
OUT = ROOT / "experiments" / "m2" / "runs"
TABLES = ROOT / "experiments" / "m2" / "tables"
OUT.mkdir(parents=True, exist_ok=True); TABLES.mkdir(parents=True, exist_ok=True)
BUDGET = SearchBudget(50000, 50000, 30)
METHODS = list(SearchMethod)


def dec(values): return tuple(Decimal(str(v)) for v in values)


def make_problem(path, states, action, controls, records=None):
    spec = load_spec(path)
    domain = SearchDomain({k: dec(v) for k,v in states.items()},
                          {action: {k: dec(v) for k,v in controls.items()}},
                          {k: Decimal(1) for k in states},
                          None if records is None else tuple({k: Decimal(str(v)) for k,v in r.items()} for r in records))
    return SearchProblem(spec, domain, allowed_actions=(action,))


canonical = {
    "scholarship_cliff": make_problem(ROOT/"examples/scholarship_cliff.yaml",
        {"true_income":[499998,499999,500000,500001,500002],"reported_income":[499998,499999,500000,500001,500002]},
        "reduce_work", {"amount":range(0,6)}, [{"true_income":x,"reported_income":x} for x in range(499998,500003)]),
    "linear_phase_out": make_problem(ROOT/"examples/linear_phase_out.yaml",
        {"income":[479999,480000,480001,549999,550000,550001,619999,620000,620001]}, "reduce_income", {"amount":range(0,6)}),
    "stacked_programs": make_problem(ROOT/"examples/stacked_programs.yaml", {"income":range(0,21)}, "reduce_income", {"amount":range(0,6)}),
    "procurement_threshold": make_problem(ROOT/"examples/procurement_threshold.yaml", {"transaction_value":range(95,106)}, "reduce_scope", {"amount":range(0,11)}),
    "honest_reporting_control": make_problem(ROOT/"examples/honest_reporting_control.yaml",
        {"true_income":range(0,21),"reported_income":range(0,21)}, "misreport", {"amount":range(0,11)}),
}


def metrics(name, problem):
    exhaustive = SearchEngine(problem).run(SearchMethod.EXHAUSTIVE, BUDGET, 17)
    ground = {finding_equivalence_key(f) for f in exhaustive.findings}
    rows=[]
    for method in METHODS:
        result=SearchEngine(problem).run(method,BUDGET,17)
        found={finding_equivalence_key(f) for f in result.findings}
        tp=len(found & ground); fp=len(found-ground)
        rows.append({"fixture":name,"method":method.value,"ground_truth_violations":len(ground),
          "raw_findings":len(result.raw_findings),"deduplicated_findings":len(result.findings),
          "true_positive_findings":tp,"false_positive_findings":fp,
          "recall":1.0 if not ground and not found else (tp/len(ground) if ground else 0.0),
          "precision":(tp/len(found) if found else (1.0 if not ground else 0.0)),
          "evaluations":result.statistics.evaluation_count,
          "evaluations_to_first":result.statistics.evaluations_to_first_violation,
          "runtime_seconds":result.statistics.elapsed_seconds,
          "best_private_gain":str(max((f.utility_delta for f in result.raw_findings),default=Decimal(0))),
          "all_replay":all(replay_finding(problem.spec,f) for f in result.raw_findings)})
    return rows, exhaustive


rows=[]; reductions=[]; artifacts={}
for name,problem in canonical.items():
    fixture_rows, exhaustive=metrics(name,problem); rows.extend(fixture_rows)
    boundary=SearchEngine(problem).run(SearchMethod.BOUNDARY,BUDGET,17)
    if boundary.raw_findings:
        original=max(boundary.raw_findings,key=lambda f:sum(Decimal(v) for v in f.action.controls.values()))
        reduced=reduce_finding(problem,original,BUDGET)
        reductions.append({"fixture":name,"before_amount":str(sum(original.action.controls.values())),
                           "after_amount":str(sum(reduced.action.controls.values())),
                           "before_gain":str(original.utility_delta),"after_gain":str(reduced.utility_delta),
                           "status":reduced.reduction_status})
        artifacts[name]=json.loads(finding_to_json(reduced))

synthetic=[]
for path in sorted((ROOT/"benchmarks/m2/specs").glob("*.yaml")):
    spec=load_spec(path); states={k:range(0,31) for k in spec.attributes}
    p=make_problem(path,states,"deviation",{"amount":range(0,11)})
    case_rows,_=metrics(path.stem,p); synthetic.extend(case_rows)

fields=list(rows[0]);
for filename,data in (("canonical_search.csv",rows),("synthetic_search.csv",synthetic),("reduction.csv",reductions)):
    if data:
        with (TABLES/filename).open("w",newline="",encoding="utf-8") as fh:
            writer=csv.DictWriter(fh,fieldnames=list(data[0])); writer.writeheader(); writer.writerows(data)
commit=subprocess.check_output(["git","-c",f"safe.directory={ROOT.as_posix()}","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
manifest={"run_id":"m2-deterministic-001","git_commit":commit,"seed":17,"budget":asdict(BUDGET),
          "methods":[m.value for m in METHODS],"canonical_rows":len(rows),"synthetic_rows":len(synthetic)}
(OUT/"run_manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
(OUT/"findings.json").write_text(json.dumps(artifacts,indent=2,sort_keys=True),encoding="utf-8")
summary={"canonical":rows,"synthetic":synthetic,"reductions":reductions}
(OUT/"summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
print(json.dumps({"manifest":manifest,"reduction":reductions},indent=2))
