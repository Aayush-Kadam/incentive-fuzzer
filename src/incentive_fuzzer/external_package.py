"""Label-blind execution support for external formal cases and sealed holdouts."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any, Mapping
import json
import yaml

from .benchmark import FORBIDDEN_RUNTIME_FIELDS, BenchmarkError, _walk
from .core import InstitutionSpec, load_spec
from .verify import FormalDomain, FormalResult, FormalVerifier


@dataclass(frozen=True)
class ExternalFormalCase:
    case_id: str
    title: str
    source_id: str
    rule_version: str
    representability: str
    threat_model: Mapping[str, Any]
    property_id: str
    action_name: str
    spec: InstitutionSpec
    domain: FormalDomain
    notes: tuple[str, ...]


def _decimal_map(raw):
    return {name: tuple(Decimal(str(value)) for value in values) for name, values in raw.items()}


def load_external_formal_case(directory: str | Path) -> ExternalFormalCase:
    directory=Path(directory)
    raw=yaml.safe_load((directory/"case.yaml").read_text(encoding="utf-8")); _walk(raw)
    required={"case_id","title","source_id","rule_version","representability","threat_model",
              "property_id","action_name","domain"}
    if not isinstance(raw,dict) or required-raw.keys():
        raise BenchmarkError(f"missing external case fields: {sorted(required-set(raw or {}))}")
    if raw["representability"] not in {"FULLY_REPRESENTABLE","PARTIALLY_REPRESENTABLE"}:
        raise BenchmarkError("external case must record representability")
    domain=raw["domain"]
    return ExternalFormalCase(raw["case_id"],raw["title"],raw["source_id"],str(raw["rule_version"]),
        raw["representability"],raw["threat_model"],raw["property_id"],raw["action_name"],
        load_spec(directory/"spec.yaml"),
        FormalDomain(_decimal_map(domain.get("state_values",{})),_decimal_map(domain.get("control_values",{}))),
        tuple(raw.get("notes",())))


def load_external_formal_suite(root: str | Path):
    cases=tuple(load_external_formal_case(path) for path in sorted((Path(root)/"cases").iterdir()) if path.is_dir())
    if len(cases)!=len({case.case_id for case in cases}): raise BenchmarkError("duplicate external case ID")
    return cases


def run_external_formal_case(case: ExternalFormalCase, timeout_ms: int=5000) -> FormalResult:
    if case.property_id!="no_profitable_deviation":
        raise BenchmarkError(f"unsupported external property {case.property_id!r}")
    return FormalVerifier(case.spec,case.domain,timeout_ms).verify_no_profitable_deviation(case.action_name,case.property_id)


def load_external_labels(root: str | Path):
    labels={}
    for path in sorted((Path(root)/"labels").glob("*.json")):
        raw=json.loads(path.read_text(encoding="utf-8"))
        if raw["case_id"] in labels: raise BenchmarkError("duplicate external label")
        labels[raw["case_id"]]=raw
    return labels
