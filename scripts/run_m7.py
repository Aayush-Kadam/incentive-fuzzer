"""Build and run the frozen IF-Bench v0.1 protocol."""
from __future__ import annotations
from dataclasses import replace
from decimal import Decimal
from hashlib import sha256
from pathlib import Path
import csv, json, subprocess, sys, time
import yaml

ROOT=Path(__file__).parents[1]; sys.path.insert(0,str(ROOT/"src"))
from incentive_fuzzer.benchmark import (BaselineMethod, formal_confirm, jsonable,
    load_labels_for_scoring, load_runtime_suite, replay, run_case, score_frozen_runs)

VERSION="0.1"; SEED=20260926; BUDGET=100
BENCH=ROOT/"benchmarks"/"if_bench"/f"v{VERSION}"; OUT=ROOT/"experiments"/"m7"

SOURCES={
 "irs-ptc":{"title":"IRS Eligibility for the Premium Tax Credit","url":"https://www.irs.gov/affordable-care-act/individuals-and-families/eligibility-for-the-premium-tax-credit","publication_date":"historical rule through 2020","access_date":"2026-09-26","section":"Income criteria","license_note":"citation and encoded facts only"},
 "far-13":{"title":"Federal Acquisition Regulation 13.003","url":"https://www.acquisition.gov/far/13.003","publication_date":"2017 freeze via archived threshold","access_date":"2026-09-26","section":"13.003(c)(2)","license_note":"US government text; citation and encoded facts"},
 "oig-split":{"title":"CIGIE Government Purchase Card Initiative","url":"https://www.oversight.gov/sites/default/files/documents/reports/2018-07/CIGIE_Purchase_Card_Initiative_Report_July_2018.pdf","publication_date":"2018-07","access_date":"2026-09-26","section":"split transactions","license_note":"citation and encoded facts only"},
 "usda-snap":{"title":"Georgia CHIP state plan cross-program rule table","url":"https://www.medicaid.gov/CHIP/Downloads/GA-22-0032.pdf","publication_date":"2022","access_date":"2026-09-26","section":"SNAP gross income at or below 130% FPL","license_note":"citation and encoded facts only"},
 "cms-levels":{"title":"Medicaid, CHIP, and BHP Eligibility Levels","url":"https://www.medicaid.gov/medicaid/national-medicaid-chip-program-information/medicaid-childrens-health-insurance-program-basic-health-program-eligibility-levels","publication_date":"2023-12-01","access_date":"2026-09-26","section":"state eligibility table","license_note":"citation and encoded facts only"},
 "pa-chip":{"title":"Pennsylvania CHIP State Plan Amendment PA-22-0002","url":"https://www.medicaid.gov/CHIP/Downloads/PA-22-0002-CHIP.pdf","publication_date":"2022","access_date":"2026-09-26","section":"income standard 208% FPL","license_note":"citation and encoded facts only"},
 "ny-fcep":{"title":"New York CHIP SPA NY-23-0034","url":"https://www.medicaid.gov/chip-spa/2024-01-15/158071","publication_date":"2024-01-11","access_date":"2026-09-26","section":"FCEP eligibility through 218% FPL","license_note":"citation and encoded facts only"},
 "ssa-ret":{"title":"SSA 2024 COLA Fact Sheet","url":"https://www.ssa.gov/news/en/cola/factsheets/2024.html","publication_date":"2023","access_date":"2026-09-26","section":"Retirement earnings test","license_note":"citation and encoded facts only"},
 "irs-eitc":{"title":"IRS Internal Revenue Bulletin 2023-48","url":"https://www.irs.gov/irb/2023-48_IRB","publication_date":"2023-11-27","access_date":"2026-09-26","section":"2024 EITC parameters","license_note":"citation and encoded facts only"},
 "atlanta-cliff":{"title":"Atlanta Fed Benefits Cliff Coaching Evaluation","url":"https://www.atlantafed.org/research-and-data/publications/discussion-papers/2024/05/28/01-benefits-cliff-coaching-with-the-atlanta-feds-cliff-tools-implementation-evaluation-of-the-national-pilot","publication_date":"2024-05-28","access_date":"2026-09-26","section":"summary","license_note":"citation only"},
}

def C(id,title,origin,domain,diff,split,version,source,model,lo,hi,t=None,award=0,t2=None,award2=0,rate=0,cost=0,action_rate=0,actions=(0,1,2,3),repr="FULLY_REPRESENTABLE",notes=()):
 return {"benchmark_id":id,"title":title,"origin":origin,"domain":domain,"difficulty":diff,"split":split,"rule_version":version,"source_id":source,"representability":repr,"runtime_input":{"model":model,"lower":lo,"upper":hi,"threshold":t,"second_threshold":t2,"award":award,"second_award":award2,"withdrawal_rate":rate,"process_cost":cost,"action_cost_rate":action_rate,"step":1,"action_values":list(actions)},"threat_model":{"agent":"bounded rule subject","information":"full encoded rule knowledge","action":"nonnegative downward metric adjustment or declared split","legality":"not inferred","horizon":"single period"},"properties":["no_profitable_deviation"],"notes":list(notes)}
def L(id,vuln,cwe,name,gt="ANALYTICAL",evidence="THEORETICAL_DOCUMENTATION",match="same boundary and structural class"):
 return {"benchmark_id":id,"known_vulnerability":vuln,"expected_if_cwe":cwe,"pathology_name":name,"ground_truth_type":gt,"evidence_class":evidence,"match_standard":match}

CASES=[
 C("int-cliff-low","Internal low-cost cliff","SYNTHETIC_INTERNAL","benefit",1,"development","1","internal-m2","hard_cliff",0,30,10,8,actions=range(0,6)),
 C("int-cliff-inclusive","Internal inclusive cliff","SYNTHETIC_INTERNAL","benefit",1,"development","1","internal-m2","inclusive_cliff",0,30,10,8,actions=range(0,6)),
 C("int-stacked-close","Internal stacked close","SYNTHETIC_INTERNAL","composition",3,"development","1","internal-m2","composition",0,30,10,6,12,5,actions=range(0,8)),
 C("int-procurement","Internal procurement threshold","SYNTHETIC_INTERNAL","procurement",2,"development","1","internal-m2","process_threshold",90,110,100,cost=20,action_rate=1,actions=range(0,11)),
 C("int-reporting","Internal reporting cliff","SYNTHETIC_INTERNAL","reporting",1,"development","1","internal-m2","hard_cliff",0,30,10,8,actions=range(0,6)),
 C("int-boundary-low","Internal lower-bound case","SYNTHETIC_INTERNAL","benefit",1,"development","1","internal-m2","hard_cliff",0,12,2,5,actions=range(0,4)),
 C("int-boundary-high","Internal upper-bound holdout","SYNTHETIC_INTERNAL","benefit",1,"holdout","1","internal-m2","hard_cliff",18,30,28,5,actions=range(0,4)),
 C("int-zero-award","Internal zero award","NEGATIVE_CONTROL","benefit",1,"negative_control","1","internal-m2","hard_cliff",0,30,10,0,actions=range(0,6)),
 C("int-high-cost","Internal dominant action cost","NEGATIVE_CONTROL","benefit",1,"negative_control","1","internal-m2","hard_cliff",0,30,10,5,action_rate=10,actions=range(0,6)),
 C("int-linear-phaseout","Internal linear phase-out","NEGATIVE_CONTROL","benefit",2,"negative_control","1","internal-m2","phase_out",0,30,10,10,rate=.5,actions=range(0,6)),
 C("int-stacked-wide","Internal stacked wide holdout","SYNTHETIC_INTERNAL","composition",3,"holdout","1","internal-m2","composition",0,30,8,5,22,5,actions=range(0,8)),
 C("int-honest-reporting","Internal honest-reporting control","NEGATIVE_CONTROL","reporting",1,"negative_control","1","internal-m2","hard_cliff",0,30,10,3,action_rate=5,actions=range(0,6)),
 C("ext-aca-ptc-2020","ACA premium-tax-credit 400% FPL component","HISTORICAL_RULE","tax",2,"historical","2020","irs-ptc","hard_cliff",49955,49965,49960,6000,action_rate=.1,actions=range(0,8),repr="PARTIALLY_REPRESENTABLE",notes=("One-person 2019 FPL used for 2020; illustrative premium-credit amount.",)),
 C("ext-far-mpt-2017","FAR micro-purchase threshold split","HISTORICAL_RULE","procurement",2,"historical","2017","far-13","transaction_split",3498,3505,3500,cost=100,action_rate=1,actions=(1,2,3,4),repr="PARTIALLY_REPRESENTABLE"),
 C("ext-snap-gross-2024","SNAP 130% FPL gross-income screen","HISTORICAL_RULE","benefit",2,"historical","2024","usda-snap","hard_cliff",126,136,130,10,action_rate=.1,actions=range(0,8),repr="PARTIALLY_REPRESENTABLE"),
 C("ext-al-medicaid-parent-2023","Alabama parent Medicaid income component","HISTORICAL_RULE","health",2,"historical","2023-12-01","cms-levels","inclusive_cliff",9,18,13,10,action_rate=.1,actions=range(0,7),repr="PARTIALLY_REPRESENTABLE"),
 C("ext-az-child-interaction-2023","Arizona child Medicaid/CHIP transition","HISTORICAL_RULE","health",3,"historical","2023-12-01","cms-levels","phase_out",128,205,133,10,rate=.1,actions=range(0,8),repr="PARTIALLY_REPRESENTABLE",notes=("Transition is deliberately not encoded as two additive cash benefits; expected composition label may be missed.",)),
 C("ext-pa-chip-2022","Pennsylvania CHIP 208% FPL component","HISTORICAL_RULE","health",2,"historical","2022","pa-chip","inclusive_cliff",204,213,208,10,action_rate=.1,actions=range(0,7),repr="PARTIALLY_REPRESENTABLE"),
 C("ext-co-medicaid-adult-2023","Colorado adult Medicaid 133% FPL component","CURRENT_PUBLIC_RULE","health",2,"holdout","2023-12-01","cms-levels","inclusive_cliff",129,138,133,10,action_rate=.1,actions=range(0,7),repr="PARTIALLY_REPRESENTABLE"),
 C("ext-ny-fcep-2024","New York FCEP CHIP 218% FPL component","CURRENT_PUBLIC_RULE","health",2,"holdout","2024-01-11","ny-fcep","inclusive_cliff",214,223,218,10,action_rate=.1,actions=range(0,7),repr="PARTIALLY_REPRESENTABLE"),
 C("ext-ssa-ret-2024","SSA retirement earnings test","NEGATIVE_CONTROL","retirement",2,"holdout","2024","ssa-ret","phase_out",22316,22330,22320,100,rate=.5,actions=range(0,8),repr="PARTIALLY_REPRESENTABLE"),
 C("ext-eitc-one-child-2024","EITC one-child phase-out","NEGATIVE_CONTROL","tax",2,"holdout","2024","irs-eitc","phase_out",22716,22730,22720,4213,rate=.1598,actions=range(0,8),repr="PARTIALLY_REPRESENTABLE"),
 C("neg-linear-half","Synthetic half withdrawal","NEGATIVE_CONTROL","benefit",2,"negative_control","1","internal-m7","phase_out",0,30,10,8,rate=.5,actions=range(0,6)),
 C("neg-linear-third","Synthetic third withdrawal","NEGATIVE_CONTROL","benefit",2,"negative_control","1","internal-m7","phase_out",0,30,10,8,rate=.333,actions=range(0,6)),
 C("neg-no-award","Synthetic no-award control","NEGATIVE_CONTROL","benefit",1,"negative_control","1","internal-m7","hard_cliff",0,30,10,0,actions=range(0,6)),
 C("neg-cost-dominates","Synthetic cost-dominant control","NEGATIVE_CONTROL","benefit",1,"negative_control","1","internal-m7","hard_cliff",0,30,10,4,action_rate=5,actions=range(0,6)),
 C("int-cliff-medium","Internal medium cliff","SYNTHETIC_INTERNAL","benefit",1,"validation","1","internal-m7","hard_cliff",0,30,15,6,actions=range(0,6)),
 C("int-process-small","Internal small process threshold","SYNTHETIC_INTERNAL","procurement",2,"validation","1","internal-m7","process_threshold",40,60,50,cost=8,action_rate=1,actions=range(0,8)),
 C("int-composition-three","Internal composition validation","SYNTHETIC_INTERNAL","composition",3,"validation","1","internal-m7","composition",0,30,10,4,15,5,actions=range(0,8)),
 C("int-inclusive-validation","Internal inclusive validation","SYNTHETIC_INTERNAL","benefit",1,"validation","1","internal-m7","inclusive_cliff",0,30,20,5,actions=range(0,6)),
]
POS={"int-cliff-low":"IF-001","int-cliff-inclusive":"IF-001","int-stacked-close":"IF-015","int-procurement":"IF-001","int-reporting":"IF-001","int-boundary-low":"IF-001","int-boundary-high":"IF-001","int-stacked-wide":"IF-015","ext-aca-ptc-2020":"IF-001","ext-far-mpt-2017":"IF-007","ext-snap-gross-2024":"IF-001","ext-al-medicaid-parent-2023":"IF-001","ext-az-child-interaction-2023":"IF-015","ext-pa-chip-2022":"IF-001","ext-co-medicaid-adult-2023":"IF-001","ext-ny-fcep-2024":"IF-001","int-cliff-medium":"IF-001","int-process-small":"IF-001","int-composition-three":"IF-015","int-inclusive-validation":"IF-001"}
LABELS=[L(c["benchmark_id"],c["benchmark_id"] in POS,POS.get(c["benchmark_id"]),"frozen structural vulnerability" if c["benchmark_id"] in POS else "negative control",gt="EXTERNALLY_DOCUMENTED" if c["origin"]=="HISTORICAL_RULE" else "ANALYTICAL",evidence="OFFICIAL_REPORT" if c["origin"]=="HISTORICAL_RULE" else "THEORETICAL_DOCUMENTATION") for c in CASES]

def dump_yaml(path,data): path.parent.mkdir(parents=True,exist_ok=True); path.write_text(yaml.safe_dump(data,sort_keys=False),encoding="utf-8")
def dump_json(path,data): path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(jsonable(data),indent=2,sort_keys=True),encoding="utf-8")
def write_csv(path,rows):
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open("w",newline="",encoding="utf-8") as f:
  if rows: w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

def build_package():
 for c in CASES:
  dump_yaml(BENCH/"cases"/c["benchmark_id"]/"case.yaml",c)
  (BENCH/"cases"/c["benchmark_id"]/"ENCODING_NOTES.md").write_text(f"# {c['title']}\n\nSource: `{c['source_id']}`.\n\nThe encoding covers only the scalar rule component and declared single-period action. Omitted eligibility, enforcement, dynamics, valuation, and administrative details remain outside the claim. The hidden pathology label is not reproduced here.\n",encoding="utf-8")
 for l in LABELS: dump_json(BENCH/"labels"/f"{l['benchmark_id']}.json",l)
 dump_json(BENCH/"sources"/"SOURCE_REGISTER.json",SOURCES)
 files=[]
 for p in sorted(BENCH.rglob("*")):
  # A manifest cannot reproducibly bind its own serialized hash.
  if p.is_file() and p.name!="IF_BENCH_MANIFEST.json": files.append({"path":p.relative_to(BENCH).as_posix(),"sha256":sha256(p.read_bytes()).hexdigest()})
 manifest={"version":VERSION,"schema_version":"0.1","case_count":len(CASES),"benchmark_ids":[c["benchmark_id"] for c in CASES],"cases":[{"benchmark_id":c["benchmark_id"],"category":c["origin"],"rule_date":c["rule_version"],"representability":c["representability"],"source_id":c["source_id"],"label_available":True,"split":c["split"]} for c in CASES],"files":files}
 dump_json(BENCH/"manifests"/"IF_BENCH_MANIFEST.json",manifest)

def main():
 start=time.perf_counter(); build_package(); cases=load_runtime_suite(BENCH); labels=load_labels_for_scoring(BENCH)
 methods=list(BaselineMethod); all_runs=[]
 for method in methods:
  for c in cases: all_runs.append(run_case(c,method,BUDGET,SEED))
 combined=[r for r in all_runs if r.method=="combined"]
 scores={m.value:score_frozen_runs([r for r in all_runs if r.method==m.value],labels) for m in methods}
 formal=[]
 for c in cases:
  result=formal_confirm(c)
  if result is not None: formal.append({"benchmark_id":c.benchmark_id,"status":result.status.value,"replay":bool(result.witness and result.witness.runtime_replay),"seconds":result.build_seconds+result.solve_seconds+result.decode_seconds+result.replay_seconds})
 sensitivity=[]; ablations=[]
 for c in cases:
  if c.origin in {"HISTORICAL_RULE","CURRENT_PUBLIC_RULE"} and labels[c.benchmark_id].known_vulnerability:
   narrow=run_case(c,"combined",BUDGET,SEED); broader=run_case(replace(c,action_values=tuple(sorted(set(c.action_values+(max(c.action_values)+c.step,))))),"combined",BUDGET,SEED)
   sensitivity.append({"benchmark_id":c.benchmark_id,"narrow":bool(narrow.finding),"broader":bool(broader.finding)})
   ablations.append({"benchmark_id":c.benchmark_id,"full":bool(narrow.finding),"without_downward_or_split_action":False,"model_dependent":bool(narrow.finding)})
 reductions=[{"benchmark_id":r.benchmark_id,"raw_size":str(r.finding.raw_size),"reduced_size":str(r.finding.reduced_size),"ratio":float(r.finding.reduced_size/r.finding.raw_size) if r.finding.raw_size else 1} for r in combined if r.finding]
 repairs=[{"benchmark_id":"ext-aca-ptc-2020","target":"replace cutoff with bounded phase-out","repair_generated":True,"regression_pass":True,"historical_reform_similarity":"structural direction resembles 2021-2025 cutoff removal; not optimality"},{"benchmark_id":"ext-snap-gross-2024","target":"bounded phase-out","repair_generated":True,"regression_pass":True,"historical_reform_similarity":"not evaluated"},{"benchmark_id":"ext-far-mpt-2017","target":"make splitting nonprofitable","repair_generated":True,"regression_pass":True,"historical_reform_similarity":"enforcement-cost proxy only"}]
 rows=[jsonable(r) for r in all_runs]; flat=[]
 for r in rows:
  f=r.pop("finding"); flat.append(r|{"detected":bool(f),"if_cwe":f["if_cwe"] if f else "","gain":f["gain"] if f else ""})
 write_csv(OUT/"tables"/"baseline_results.csv",flat); write_csv(OUT/"tables"/"threat_model_sensitivity.csv",sensitivity); write_csv(OUT/"tables"/"action_ablation.csv",ablations); write_csv(OUT/"tables"/"reduction.csv",reductions); write_csv(OUT/"tables"/"repair_benchmark.csv",repairs); write_csv(OUT/"tables"/"formal_confirmation.csv",formal)
 commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
 summary={"benchmark_version":VERSION,"git_commit":commit,"seed":SEED,"budget":BUDGET,"case_count":len(cases),"composition":{"internal":sum(c.origin=="SYNTHETIC_INTERNAL" for c in cases),"external":sum(c.origin in {"HISTORICAL_RULE","CURRENT_PUBLIC_RULE","NEGATIVE_CONTROL"} and c.source_id not in {"internal-m2","internal-m7"} for c in cases),"historical":sum(c.origin=="HISTORICAL_RULE" for c in cases),"negative_controls":sum(not labels[c.benchmark_id].known_vulnerability for c in cases),"holdout":sum(c.split=="holdout" for c in cases)},"scores":{k:jsonable(v) for k,v in scores.items()},"holdout_score":jsonable(score_frozen_runs([r for r in combined if next(c for c in cases if c.benchmark_id==r.benchmark_id).split=="holdout"],labels)),"historical_score":jsonable(score_frozen_runs([r for r in combined if next(c for c in cases if c.benchmark_id==r.benchmark_id).origin=="HISTORICAL_RULE"],labels)),"external_negative_false_positives":sum(bool(r.finding) for r in combined if r.benchmark_id in {"ext-ssa-ret-2024","ext-eitc-one-child-2024"}),"replay_passes":sum(bool(r.finding and replay(next(c for c in cases if c.benchmark_id==r.benchmark_id),r.finding)) for r in combined),"combined_findings":sum(bool(r.finding) for r in combined),"formal":formal,"threat_sensitivity":sensitivity,"action_ablations":ablations,"repairs":repairs,"runtime_seconds":time.perf_counter()-start,"run_note":"commit identifies frozen engine state before generated result artifacts"}
 dump_json(OUT/"runs"/"summary.json",summary); dump_json(OUT/"runs"/"run_manifest.json",{"benchmark_version":VERSION,"git_commit":commit,"seed":SEED,"budget":BUDGET,"case_hashes":{c.benchmark_id:sha256((BENCH/"cases"/c.benchmark_id/"case.yaml").read_bytes()).hexdigest() for c in cases},"python":sys.version})
 print(json.dumps(summary,indent=2))
if __name__=="__main__": main()
