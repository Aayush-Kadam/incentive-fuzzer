"""Synthetic scholarship end-to-end demonstration."""
from pathlib import Path
import csv, json, sys
ROOT=Path(__file__).parents[1]; sys.path.insert(0,str(ROOT/"src"))
from incentive_fuzzer import search_spec, verify_spec
from incentive_fuzzer.search import replay_finding
from incentive_fuzzer import load_spec

def main():
    path=ROOT/"examples"/"scholarship_cliff.yaml"; spec=load_spec(path)
    search=search_spec(path,"boundary",1000); finding=search.findings[0]
    formal=verify_spec(path,"reduce_work")
    m4=list(csv.DictReader((ROOT/"experiments"/"m4"/"tables"/"scenario_summary.csv").open(encoding="utf-8"))) if (ROOT/"experiments"/"m4"/"tables"/"scenario_summary.csv").exists() else []
    m6=list(csv.DictReader((ROOT/"experiments"/"m6"/"tables"/"scholarship_repairs.csv").open(encoding="utf-8")))
    payload={"demo":"synthetic scholarship cliff","search_status":search.status.value,"minimal_action":str(finding.action.controls["amount"]),"private_gain":str(finding.utility_delta),"replay":replay_finding(spec,finding),"formal_status":formal.status.value,"formal_replay":bool(formal.witness and formal.witness.runtime_replay),"frozen_m4_b0_profitable_share":"0.515625","passing_phase_out_candidates":sum(row.get("gate")=="REPAIR_PASS" and row.get("family")=="STRUCTURAL_TRANSFORM" for row in m6),"qualification":"Synthetic bounded demonstration; not a policy recommendation."}
    print(json.dumps(payload,indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
