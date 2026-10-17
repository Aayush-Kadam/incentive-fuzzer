# Independently evaluate Incentive Fuzzer

For researchers and formal/property-testing developers: find and replay profitable deviations in explicitly bounded synthetic economic rules.

The checker searches the authored scholarship cutoff, replays its witness, forges the stated gain and requires rejection, then asks Z3 for a bounded reduce_work witness. Expected: VIOLATION_FOUND, action=misreport_income, amount=1, gain=100000, replay=true, forged_replay=false, FORMALLY_VIOLATED and formal_replay=true. Work reduction instead has gain 99999. No tolerance on these exact arithmetic results; timings and finding IDs may differ. This is not measured economic harm, predicted human behavior, a policy recommendation or universal proof.

## Source, installation and five-minute check

This review branch is based on merged master 0638d2141474b788e9497010d0b4f9a6ec3d0bc1. The reviewer infrastructure is proposed separately; it is not a published release. Record its actual HEAD with `git rev-parse HEAD`. Use the exact commit listed in the delivered package manifest; do not silently substitute latest main.

Windows and Ubuntu Python 3.12 are covered by existing project CI; macOS is not freshly qualified. Use Python 3.12 for this procedure. Git and initial package-registry network access are required; no API key, paid service or Docker is required. Resource estimate, not measurement: 2 GB free RAM, 1 GB free disk; allow additional space for optional development dependencies. Five minutes is a target after dependencies are installed, not a measured cold-network guarantee.

```powershell
git clone https://github.com/Aayush-Kadam/incentive-fuzzer.git
cd incentive-fuzzer
git checkout m3/reviewer-ready
py -3.12 -m venv .venv
.venv/Scripts/python.exe -m pip install -e ".[test]"
.venv/Scripts/python.exe scripts/reviewer_check.py
.venv/Scripts/python.exe -m pytest -q
```

On Ubuntu, create with `python3.12 -m venv .venv` and replace `.venv/Scripts/python.exe` with `.venv/bin/python`. Commands run from the repository root. The reviewer script uses installed packages and synthetic data; it must exit zero only when both positive and negative expectations hold. Save stdout, stderr and the actual exit code. Also save `python -m pip freeze` and `git rev-parse HEAD`.

Dependencies are PyYAML==6.0.3 and z3-solver==4.15.3.0; test extras pin pytest/coverage. Source reuse terms remain unresolved: see LICENSE_DECISION.md. This package grants no new rights. External distribution/adoption outreach is HOLD pending the owner's license decision; a public repository is not an open-source grant.

## Troubleshooting and feedback

If Python is missing, install a supported Python from its official provider, then create an isolated environment. If imports fail, use the same interpreter for installation and the check; do not mix environments. Report solver-wheel/architecture failures instead of substituting another solver. On Windows, temporary-directory permission failures should be investigated under your normal account; do not disable endpoint protection. A failed negative test is a bug and must not be relabeled success. ID/hash differences alone are expected; semantic differences are not.

Open the repository's independent-reproduction issue template only when you choose to disclose the report publicly. Alternatively send the completed fields privately through an owner-agreed channel. Provide environment, install/test failures, negative outcomes, documentation friction, usefulness and missing features. Do not disclose reviewer identity or communications without consent. Author-run checks are labeled self-tests and never populate the independent evidence ledger.
