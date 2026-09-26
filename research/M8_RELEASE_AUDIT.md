# M8 Release Audit

Final status is completed after the commands and artifact hashes recorded in `reproducibility/manifest.json` are regenerated from the release commit.

## Science

- [x] M8 entry claim freeze respected; no benchmark retuning.
- [x] Arizona miss, boundary-only result, threat-model dependence, and unresolved independent review remain visible.
- [x] Non-threshold stress cases remain supplementary and correctly framed.

## Engineering

- [x] Public CLI exposes only `validate`, `evaluate`, `search`, `verify`, and `benchmark`.
- [x] Compact public API and demonstrations are real and tested.
- [x] Full suite passes; package build and clean-environment installation are release checks.

## Manuscript

- [x] Canonical Markdown source is complete.
- [x] Quantitative claims map to frozen evidence.
- [x] Negative results and limitations are prominent.
- [x] PDF is generated and visually inspected page by page.

## Documentation

- [x] README is the primary entry point and uses repository-relative links.
- [x] Architecture, limitations, IF-Bench, external cases, API, and reproduction documents exist.
- [x] Examples and commands are executable rather than illustrative placeholders.

## Security and privacy

- [x] No credential-like material is required or documented.
- [x] Current public-facing files avoid user-specific absolute paths.
- [x] Cache/build products are excluded or confined to documented artifact directories.
- [x] Historical frozen reports are retained as evidence even where they record historical local paths.

## Benchmark

- [x] IF-Bench manifest and hashes remain stable.
- [x] Runtime cases and hidden labels remain separated.
- [x] Sealed-holdout regression test demonstrates label-blind execution.

## Reproducibility

- [x] Quick and research modes regenerate checks and manifest metadata.
- [x] Full mode runs tests, frozen workflows, demos, science artifacts, and manuscript build.
- [x] Manifest records commit, platform, dependency versions, versions, seeds, checks, and artifact hashes.

## Integrity conclusion

No critical integrity defect is known. Remaining limitations are scientific and external: independent rule-fidelity, action-space, valuation, and economist/domain review, plus a genuinely external sealed holdout.
