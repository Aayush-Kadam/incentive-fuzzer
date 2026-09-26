"""Generate compact review cards from frozen M7 runtime, label, source, and formal artifacts."""
from pathlib import Path
import csv, json, sys

ROOT=Path(__file__).parents[1]; sys.path.insert(0,str(ROOT/"src"))
from incentive_fuzzer.benchmark import load_labels_for_scoring, load_runtime_suite

BENCH=ROOT/"benchmarks"/"if_bench"/"v0.1"
OUT=ROOT/"external_review"/"cases"

def main():
    cases=load_runtime_suite(BENCH); labels=load_labels_for_scoring(BENCH)
    sources=json.loads((BENCH/"sources"/"SOURCE_REGISTER.json").read_text(encoding="utf-8"))
    formal={row["benchmark_id"]:row for row in csv.DictReader((ROOT/"experiments"/"m7"/"tables"/"formal_confirmation.csv").open(encoding="utf-8"))}
    external=[case for case in cases if case.source_id not in {"internal-m2","internal-m7"}]
    OUT.mkdir(parents=True,exist_ok=True)
    for case in external:
        label=labels[case.benchmark_id]; source=sources[case.source_id]; result=formal.get(case.benchmark_id,{})
        actions=", ".join(str(value) for value in case.action_values)
        finding="expected encoded structural finding" if label.known_vulnerability else "negative control; no finding expected"
        text=f"""# Review Card: {case.benchmark_id}

- **Case ID:** `{case.benchmark_id}`
- **Rule source:** [{source['title']}]({source['url']}) — `{case.source_id}`
- **Frozen date/version:** {case.rule_version}
- **Encoded component:** `{case.model}` over `{case.domain}`, bounded `{case.lower}` to `{case.upper}`
- **Representability:** {case.representability}
- **Omitted components:** eligibility, administration, enforcement, dynamics, behavioral calibration, and valuation details not explicitly encoded; see encoding notes
- **Threat model:** {json.dumps(case.threat_model,sort_keys=True)}
- **Allowed actions:** {actions}
- **System finding:** {finding}
- **Known pathology/control:** {label.pathology_name}; expected class `{label.expected_if_cwe}`
- **Match rationale:** {label.match_standard}
- **Formal result:** {result.get('status','UNSUPPORTED')}
- **Limitations:** component-level and domain-scoped; actions and valuations remain project-authored

## Reviewer fields

- Rule fidelity:
- Action realism and legality:
- Missing actions or constraints:
- Valuation assessment:
- Pathology mapping:
- Scope assessment:
- Repair-interpretation concerns:
- Disposition and required changes:
"""
        (OUT/f"{case.benchmark_id}.md").write_text(text,encoding="utf-8")
    print(f"generated {len(external)} review cards")

if __name__=="__main__": main()
