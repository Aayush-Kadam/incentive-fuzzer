# Contributing

## Development setup

Create a Python 3.12 environment and install `.[test]`. Run `python -m pytest` before submitting changes. Run `python scripts/reproduce.py quick` for public-surface and benchmark-integrity checks.

## Scientific discipline

- Do not change frozen results to improve headline metrics.
- Preserve exact statuses and scoped language.
- Add regression tests for semantic or evidence changes.
- Separate project-authored assumptions from sourced rule facts.
- Do not call a modeled opportunity observed behavior.
- Do not label a bounded repair optimal or recommended without supplied objectives and external review.

## Benchmark changes

Follow `docs/BENCHMARK_CONTRIBUTIONS.md`. Runtime evaluation must not read labels. A new external case requires authoritative sources, frozen version, representability, encoding notes, threat model, separate labels, and provenance. Do not add a case after viewing its result without recording that development status.

## Sealed holdouts

Independent contributors should prepare runtime and label packages separately using `external_review/sealed_holdout_template/`. The project runs `scripts/run_sealed_holdout.py` on runtime files only, freezes and hashes results, and scores only after labels are released.

## Review

External feedback should use `external_review/REVIEW_FORM.md`. Corrections are versioned; frozen historical labels and reports are not silently overwritten.

