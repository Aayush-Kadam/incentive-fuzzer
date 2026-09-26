from dataclasses import replace
from pathlib import Path
import json
import pytest
from incentive_fuzzer.benchmark import (BaselineMethod, BenchmarkError, case_hash,
    formal_confirm, load_labels_for_scoring, load_runtime_case, load_runtime_suite,
    replay, run_case, score_frozen_runs)

ROOT=Path(__file__).parents[1]; BENCH=ROOT/"benchmarks"/"if_bench"/"v0.1"
@pytest.fixture(scope="module")
def cases(): return load_runtime_suite(BENCH)
@pytest.fixture(scope="module")
def labels(): return load_labels_for_scoring(BENCH)
def test_schema_and_count(cases): assert len(cases)==30
def test_unique_ids(cases): assert len({c.benchmark_id for c in cases})==30
def test_manifest_integrity(cases):
 m=json.loads((BENCH/"manifests"/"IF_BENCH_MANIFEST.json").read_text()); assert m["case_count"]==30; assert set(m["benchmark_ids"])=={c.benchmark_id for c in cases}
def test_source_metadata(cases): assert all(c.source_id for c in cases)
def test_labels_separate(cases,labels): assert set(labels)=={c.benchmark_id for c in cases}; assert not hasattr(cases[0],"known_vulnerability")
def test_runtime_api_has_no_label_loader():
 import incentive_fuzzer.benchmark as b
 assert "label" not in b.load_runtime_case.__name__
def test_leakage_rejected(tmp_path):
 p=tmp_path/"case.yaml"; p.write_text("benchmark_id: x\nknown_vulnerability: true\n")
 with pytest.raises(BenchmarkError): load_runtime_case(p)
def test_split_integrity(cases): assert {c.split for c in cases}>={"development","historical","holdout","negative_control"}
def test_reproducible_hash(cases): assert case_hash(cases[0])==case_hash(cases[0])
@pytest.mark.parametrize("method",list(BaselineMethod))
def test_baseline_runner(method,cases): assert run_case(cases[0],method,100).method==method.value
def test_metric_calculation(cases,labels):
 runs=[run_case(c,"combined",100) for c in cases]; score=score_frozen_runs(runs,labels); assert score.total==30; assert 0<=score.detected<=score.positives
def test_replay(cases):
 run=run_case(cases[0],"combined"); assert run.finding and replay(cases[0],run.finding)
def test_negative_controls(cases,labels):
 for c in cases:
  if not labels[c.benchmark_id].known_vulnerability: assert run_case(c,"exhaustive",10000).finding is None
def test_blind_protocol(cases):
 raw=(BENCH/"cases"/cases[0].benchmark_id/"case.yaml").read_text(); assert "known_vulnerability" not in raw and "expected_if_cwe" not in raw
def test_formal_external_confirmation(cases):
 c=next(x for x in cases if x.benchmark_id=="ext-aca-ptc-2020"); assert formal_confirm(c).status.value=="FORMALLY_VIOLATED"
def test_action_ablation(cases):
 c=cases[0]; assert run_case(c,"combined").finding; assert run_case(replace(c,action_values=(0,)),"combined").finding is None
