from pathlib import Path
import importlib.util

ROOT=Path(__file__).parents[1]

def test_reproduction_script_has_three_modes():
    text=(ROOT/"scripts"/"reproduce.py").read_text(encoding="utf-8")
    assert all(mode in text for mode in ('"quick"','"research"','"full"'))
    assert "artifact_hashes" in text and "benchmark_checks" in text
    assert "timestamp_utc" in text and "m75_stress_version" in text
    assert 'scripts/build_paper.py' in text

def test_release_artifacts_exist():
    for path in ["research/m8_entry/HEADLINE_TABLES.md","research/m8_entry/if_bench_method_comparison.svg","research/M8_ENTRY_CLAIM_LEDGER.md"]:
        assert (ROOT/path).is_file()
