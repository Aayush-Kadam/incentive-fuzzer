# Examples

- `scholarship_cliff.yaml`: synthetic hard cutoff used by the flagship search/verification/repair demonstration.
- `linear_phase_out.yaml`: smooth synthetic comparison with capped withdrawal.
- `honest_reporting_control.yaml`: true-versus-reported-income example whose declared penalty removes profitable tested misreporting.
- `stacked_programs.yaml`: synthetic two-program composition example.
- `procurement_threshold.yaml`: synthetic process-threshold example.
- Strategic complementarity: run `python scripts/demo_strategic_game.py`; the exact game fixture lives in `src/incentive_fuzzer/game_fixtures.py`.
- Repair: run `python scripts/demo_scholarship.py`; frozen candidate evidence lives under `experiments/m6/`.
- External encoded component: run `python scripts/demo_external_case.py`; it uses the ACA component under `benchmarks/if_bench/v0.1/`.

Synthetic examples validate capability and semantics. External examples are partial encoded components, not full program audits.

