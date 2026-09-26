"""One-command research-preview reproduction with quick, research, and full modes."""
from __future__ import annotations
from hashlib import sha256
from importlib.metadata import version
from pathlib import Path
import argparse, json, platform, re, subprocess, sys, time
from datetime import datetime, timezone

ROOT=Path(__file__).parents[1]; sys.path.insert(0,str(ROOT/"src"))
from incentive_fuzzer.benchmark import load_labels_for_scoring, load_runtime_suite, run_case, run_smt_baseline, score_frozen_runs, score_smt_frozen_runs
from incentive_fuzzer.external_package import load_external_formal_suite, load_external_labels, run_external_formal_case
import z3

ARTIFACTS=[
    "experiments/m7/runs/summary.json","experiments/m75/runs/summary.json",
    "research/m8_entry/HEADLINE_TABLES.md","research/m8_entry/if_bench_method_comparison.svg",
    "benchmarks/if_bench/v0.1/manifests/IF_BENCH_MANIFEST.json","benchmarks/m75_stress/v0.1/MANIFEST.json"]

def run(command):
    return subprocess.run(command,cwd=ROOT,text=True,capture_output=True,check=True)

def tests(mode):
    targets=[] if mode in {"research","full"} else ["tests/test_cli.py","tests/test_benchmark.py","tests/test_m75.py"]
    result=run([sys.executable,"-m","pytest",*targets])
    match=re.search(r"(\d+) passed",result.stdout)
    if not match: raise RuntimeError("pytest output did not contain a pass count")
    return int(match.group(1)),result.stdout.strip().splitlines()[-1]

def benchmark_checks():
    root=ROOT/"benchmarks"/"if_bench"/"v0.1"; cases=load_runtime_suite(root)
    blind=[run_case(case,"combined",100,20260926) for case in cases]
    labels=load_labels_for_scoring(root); score=score_frozen_runs(blind,labels)
    b5=[run_smt_baseline(case) for case in cases]; b5score=score_smt_frozen_runs(b5,labels,blind)
    if (score.detected,score.false_positives)!=(19,0): raise RuntimeError("M7 frozen result drift")
    if (b5score.supported,b5score.violated,b5score.satisfied,b5score.unsupported)!=(26,15,11,4): raise RuntimeError("B5 frozen result drift")
    stress_root=ROOT/"benchmarks"/"m75_stress"/"v0.1"; stress=load_external_formal_suite(stress_root); stress_labels=load_external_labels(stress_root)
    agreements=sum(run_external_formal_case(case).status.value==stress_labels[case.case_id]["expected_status"] for case in stress)
    if agreements!=3: raise RuntimeError("M7.5 stress result drift")
    return {"m7_cases":30,"m7_detected":19,"m7_false_positives":0,"b5_supported":26,"b5_violated":15,"b5_satisfied":11,"b5_unsupported":4,"stress_agreements":agreements}

def artifact_hashes():
    return {path:sha256((ROOT/path).read_bytes()).hexdigest() for path in ARTIFACTS}

def main(argv=None):
    parser=argparse.ArgumentParser(); parser.add_argument("mode",nargs="?",default="quick",choices=["quick","research","full"]); args=parser.parse_args(argv)
    start=time.perf_counter(); count,test_line=tests(args.mode); checks=benchmark_checks()
    if args.mode in {"research","full"}: run([sys.executable,"scripts/build_external_review_cards.py"]); run([sys.executable,"scripts/build_m8_science.py"])
    if args.mode=="full":
        run([sys.executable,"scripts/demo_scholarship.py"]); run([sys.executable,"scripts/demo_strategic_game.py"]); run([sys.executable,"scripts/demo_external_case.py"])
        run([sys.executable,"scripts/build_paper.py"])
    commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
    manifest={"mode":args.mode,"status":"PASS","timestamp_utc":datetime.now(timezone.utc).isoformat(),"git_commit":commit,"python":sys.version,"platform":platform.platform(),
        "dependencies":{"PyYAML":version("PyYAML"),"pytest":version("pytest"),"pytest-cov":version("pytest-cov"),"z3-solver":version("z3-solver"),"z3":z3.get_version_string()},
        "benchmark_version":"IF-Bench v0.1","m75_stress_version":"v0.1","test_count":count,"test_summary":test_line,"seeds":{"m2":17,"m4":20260926,"m7":20260926},
        "checks":checks,"artifact_hashes":artifact_hashes(),"runtime_seconds":time.perf_counter()-start}
    output=ROOT/"reproducibility"/"manifest.json"; output.parent.mkdir(exist_ok=True); output.write_text(json.dumps(manifest,indent=2,sort_keys=True),encoding="utf-8")
    print(json.dumps(manifest,indent=2,sort_keys=True)); return 0

if __name__=="__main__": raise SystemExit(main())
