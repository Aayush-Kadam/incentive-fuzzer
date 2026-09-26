"""Execute contributor runtime cases without loading any hidden-label directory."""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
import json, sys

ROOT=Path(__file__).parents[1]; sys.path.insert(0,str(ROOT/"src"))
from incentive_fuzzer.external_package import load_external_formal_suite, run_external_formal_case

def main(runtime_root, output):
    root=Path(runtime_root).resolve(); rows=[]
    for case in load_external_formal_suite(root):
        result=run_external_formal_case(case)
        rows.append({"case_id":case.case_id,"status":result.status.value,
            "replayed":bool(result.witness and result.witness.runtime_replay),
            "seconds":result.build_seconds+result.solve_seconds+result.decode_seconds+result.replay_seconds})
    payload={"runtime_root_hash":sha256("".join(sorted(p.read_text(encoding="utf-8") for p in root.rglob("*") if p.is_file())).encode()).hexdigest(),"results":rows}
    Path(output).write_text(json.dumps(payload,indent=2,sort_keys=True),encoding="utf-8")

if __name__=="__main__":
    if len(sys.argv)!=3: raise SystemExit("usage: run_sealed_holdout.py RUNTIME_ROOT RESULTS_JSON")
    main(sys.argv[1],sys.argv[2])
