"""Restrained demonstration of one externally sourced encoded component."""
from pathlib import Path
import json, sys
ROOT=Path(__file__).parents[1]; sys.path.insert(0,str(ROOT/"src"))
from incentive_fuzzer.benchmark import formal_confirm, load_runtime_case, run_case

def main():
    path=ROOT/"benchmarks"/"if_bench"/"v0.1"/"cases"/"ext-aca-ptc-2020"/"case.yaml"
    case=load_runtime_case(path); run=run_case(case,"combined",100,20260926); formal=formal_confirm(case)
    print(json.dumps({"case_id":case.benchmark_id,"source_id":case.source_id,"encoded_component":case.model,"representability":case.representability,"threat_model":case.threat_model,"blind_search_status":run.status,"finding_class":run.finding.if_cwe if run.finding else None,"formal_status":formal.status.value,"formal_replay":bool(formal.witness and formal.witness.runtime_replay),"qualification":"Historical encoded component only; valuation and action are project-authored and program-level auditing is not claimed."},indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
