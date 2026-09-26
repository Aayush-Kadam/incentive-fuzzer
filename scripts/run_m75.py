"""Run the M7.5 B5 baseline and separate non-threshold stress supplement."""
from __future__ import annotations
from dataclasses import asdict
from hashlib import sha256
from pathlib import Path
import csv, json, subprocess, sys

ROOT=Path(__file__).parents[1]; sys.path.insert(0,str(ROOT/"src"))
from incentive_fuzzer.benchmark import (jsonable, load_labels_for_scoring, load_runtime_suite,
    run_case, run_smt_baseline, score_smt_frozen_runs)
from incentive_fuzzer.external_package import (load_external_formal_suite, load_external_labels,
    run_external_formal_case)

M7=ROOT/"benchmarks"/"if_bench"/"v0.1"
STRESS=ROOT/"benchmarks"/"m75_stress"/"v0.1"
OUT=ROOT/"experiments"/"m75"

def dump(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(jsonable(data),indent=2,sort_keys=True),encoding="utf-8")

def table(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="",encoding="utf-8") as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)

def manifest(root):
    return {path.relative_to(root).as_posix():sha256(path.read_bytes()).hexdigest()
            for path in sorted(root.rglob("*")) if path.is_file() and path.name!="MANIFEST.json"}

def main():
    cases=load_runtime_suite(M7)
    # Labels are intentionally loaded only after B5 and comparison runs are frozen.
    b5=[run_smt_baseline(case) for case in cases]
    combined=[run_case(case,"combined",100,20260926) for case in cases]
    labels=load_labels_for_scoring(M7)
    score=score_smt_frozen_runs(b5,labels,combined)
    b5_rows=[jsonable(run) for run in b5]
    table(OUT/"tables"/"smt_baseline.csv",b5_rows)

    stress_cases=load_external_formal_suite(STRESS)
    stress_results=[]
    for case in stress_cases:
        result=run_external_formal_case(case)
        stress_results.append({"case_id":case.case_id,"status":result.status.value,
            "replayed":bool(result.witness and result.witness.runtime_replay),
            "seconds":result.build_seconds+result.solve_seconds+result.decode_seconds+result.replay_seconds})
    stress_labels=load_external_labels(STRESS)
    for row in stress_results:
        row["expected_status"]=stress_labels[row["case_id"]]["expected_status"]
        row["agreement"]=row["status"]==row["expected_status"]
        row["label_type"]=stress_labels[row["case_id"]]["label_type"]
    table(OUT/"tables"/"nonthreshold_stress.csv",stress_results)
    package_manifest=manifest(STRESS); dump(STRESS/"MANIFEST.json",package_manifest)

    summary={"git_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
        "m7_b5":jsonable(score),"m7_b5_total_solve_seconds":sum(run.elapsed_seconds for run in b5),
        "m7_b5_case_results":b5_rows,"stress_case_count":len(stress_cases),
        "stress_status_agreements":sum(row["agreement"] for row in stress_results),
        "stress_results":stress_results,"run_note":"commit identifies the pre-M7.5 frozen M7 engine plus working-tree M7.5 implementation"}
    dump(OUT/"runs"/"summary.json",summary)
    dump(OUT/"runs"/"run_manifest.json",{"m7_case_hashes":{c.benchmark_id:sha256((M7/"cases"/c.benchmark_id/"case.yaml").read_bytes()).hexdigest() for c in cases},"stress_manifest_sha256":sha256((STRESS/"MANIFEST.json").read_bytes()).hexdigest(),"python":sys.version})
    print(json.dumps(summary,indent=2))

if __name__=="__main__": main()
