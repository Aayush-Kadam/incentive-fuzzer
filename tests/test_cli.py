import json
from pathlib import Path

from incentive_fuzzer import run_benchmark, search_spec, validate_spec, verify_spec
from incentive_fuzzer.cli import main

ROOT=Path(__file__).parents[1]
SPEC=ROOT/"examples"/"scholarship_cliff.yaml"

def test_cli_help_and_version(capsys):
    assert main(["validate",str(SPEC)])==0
    assert json.loads(capsys.readouterr().out)["status"]=="VALID_SPEC"

def test_cli_evaluate(capsys):
    state='{"true_income":500000,"reported_income":500000}'
    assert main(["evaluate",str(SPEC),"--state",state])==0
    assert json.loads(capsys.readouterr().out)["status"]=="EVALUATED"

def test_cli_search_preserves_status(capsys):
    assert main(["search",str(SPEC),"--method","boundary","--max-evaluations","100"])==0
    assert json.loads(capsys.readouterr().out)["status"]=="VIOLATION_FOUND"

def test_cli_verify_preserves_formal_status(capsys):
    assert main(["verify",str(SPEC),"--action","reduce_work"])==0
    assert json.loads(capsys.readouterr().out)["status"]=="FORMALLY_VIOLATED"

def test_cli_benchmark_is_label_blind(capsys):
    suite=ROOT/"benchmarks"/"if_bench"/"v0.1"
    assert main(["benchmark","--suite",str(suite),"--method","boundary"])==0
    payload=json.loads(capsys.readouterr().out)
    assert payload["cases"]==30 and payload["violations"]==19

def test_public_convenience_api():
    assert validate_spec(SPEC).institution.id=="scholarship_cliff"
    assert search_spec(SPEC,"boundary",100).status.value=="VIOLATION_FOUND"
    assert verify_spec(SPEC,"reduce_work").status.value=="FORMALLY_VIOLATED"
    assert len(run_benchmark(ROOT/"benchmarks"/"if_bench"/"v0.1","boundary"))==30
