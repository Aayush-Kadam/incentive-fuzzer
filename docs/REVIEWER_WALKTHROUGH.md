# From a rule to replayable evidence

This is a bounded research workflow for inspecting specified incentives. It
does not forecast behavior or certify a real institution.

```text
YAML -> validated typed specification -> exact evaluator
                                     <- bounded candidate search
                                     <- restricted Z3 witness
                                     -> replay and reduced finding
finite population / game / repair adapters -> qualified research results
```

See [the architecture](ARCHITECTURE.md) for layer boundaries. Its M1 discussion
is historical: the current package also has Z3 and the later layers.

After the root README installation, run:

```powershell
.venv\Scripts\python.exe scripts/demo_scholarship.py
.venv\Scripts\python.exe -m pytest
.venv\Scripts\python.exe scripts/reproduce.py quick
```

The demo currently reports `VIOLATION_FOUND`, action amount `1`, private gain
`100000`, replay `true`, and `FORMALLY_VIOLATED` with formal replay `true`.
Search chooses among both `reduce_work` and `misreport_income`. The report-only
change preserves true income; reducing work loses one unit and instead gains
`99999`. Both arise from the authored synthetic 100000 award and strict cutoff.
Do not interpret either amount as measured real-world loss.

On 16 October 2026, the portfolio audit freshly passed 235 tests on
Windows/Python 3.12.14. Quick reproduction separately passed 33 targeted tests,
recomputed 19 detections and zero false positives on the 30 curated IF-Bench
cases, and checked the 26 supported / 4 unsupported SMT baseline split.
These counts overlap; do not add 33 to 235. The benchmark is not representative
of policy auditing, and its labels and valuations remain authored assumptions.

Full research reproduction and independent economist review are separate gates.
The quick command writes a local provenance manifest; do not present it as
independent replication or silently replace frozen scientific artifacts.

See [limitations](LIMITATIONS.md), [contributing](../CONTRIBUTING.md), and
[the unresolved license decision](../LICENSE_DECISION.md).
