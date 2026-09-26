from pathlib import Path
import json

from incentive_fuzzer.external_package import (load_external_formal_suite, load_external_labels,
    run_external_formal_case)

ROOT=Path(__file__).parents[1]
STRESS=ROOT/"benchmarks"/"m75_stress"/"v0.1"

def test_stress_suite_is_separate_and_has_three_cases():
    cases=load_external_formal_suite(STRESS)
    assert len(cases)==3
    assert all(case.source_id and case.representability for case in cases)

def test_stress_runtime_does_not_contain_labels():
    for path in (STRESS/"cases").glob("*/case.yaml"):
        text=path.read_text(encoding="utf-8")
        assert "expected_status" not in text and "label_type" not in text

def test_stress_formal_results_match_separate_labels():
    labels=load_external_labels(STRESS)
    for case in load_external_formal_suite(STRESS):
        result=run_external_formal_case(case)
        assert result.status.value==labels[case.case_id]["expected_status"]
        if result.status.value=="FORMALLY_VIOLATED":
            assert result.witness and result.witness.runtime_replay

def test_intended_response_is_not_labeled_vulnerability():
    label=json.loads((STRESS/"labels"/"dol-safe-harbor-match.json").read_text())
    assert label["label_type"]=="INTENDED_RESPONSE_CONTROL"

def test_sealed_runner_has_no_label_loader():
    text=(ROOT/"scripts"/"run_sealed_holdout.py").read_text(encoding="utf-8")
    assert "load_external_labels" not in text and "hidden_labels" not in text
