# Release objective

Publish and archive the frozen Incentive Fuzzer v0.1.0 research preview without changing scientific content, historical tags, benchmark results, or claims.

# Local frozen state

The scientific M8 freeze is commit `c77e3c272de8555d54f5e68a9e1985bf6090846e` on tag `m8-research-preview`. The working release added only CI and release metadata after that freeze.

# GitHub repository

Canonical public repository: https://github.com/Aayush-Kadam/incentive-fuzzer

# CI

GitHub Actions passed on Ubuntu and Windows with Python 3.12. The workflow runs the test suite, CLI smoke checks, benchmark-integrity checks, and quick reproduction. A separate manual research-reproduction workflow is also present.

# Public visibility audit

The README, history, milestone tags, benchmark documentation, external-review package, reproduction instructions, manuscript PDF, and release are public. Current public-facing documentation has no required machine-specific path or private dependency.

# Release tag

`v0.1.0-research-preview` points to release commit `780341efcf6ff9250651a0ca007510f176947fdc`. It is distinct from the scientific M8 freeze and was not moved after archival.

# GitHub release

The release is titled “Incentive Fuzzer v0.1.0 — Research Preview” at https://github.com/Aayush-Kadam/incentive-fuzzer/releases/tag/v0.1.0-research-preview. The tagged repository contains the manuscript PDF and reproduction manifest; GitHub also provides source archives.

# Zenodo workflow used

The current official GitHub integration was enabled first. Its automated ingestion failed with `Citation metadata load failed`, so the documented manual-deposit workflow was used. The exact GitHub tag ZIP was uploaded, previewed, and published as a Zenodo Software record.

# DOI

- Version DOI: `10.5281/zenodo.22982554`
- Concept DOI: `10.5281/zenodo.22982553`
- Record: https://zenodo.org/records/22982554
- Archived version: `v0.1.0-research-preview`
- Publication date: 2026-09-26

# DOI verification

The Zenodo record is public and identifies the correct title, sole creator Aayush Kadam, software resource type, version, exact release archive, limitations, keywords, and `NOASSERTION` rights metadata. DOI.org registration was tested after publication; any initial propagation delay is recorded in the final release handoff.

# Post-DOI metadata commit

The post-DOI commit updates only README citation links and badge, `CITATION.cff`, and this report. It does not modify scientific results or move the release tag.

# Final hashes

- M8 scientific freeze: `c77e3c272de8555d54f5e68a9e1985bf6090846e`
- Public archival release: `780341efcf6ff9250651a0ca007510f176947fdc`
- Release ZIP SHA-256: `99F0BE406B49F27403F81039B7537DB4D35E16DCCA581B21C7953B5F3E330B69`
- Manuscript PDF SHA-256: `DB11514F54647A97020F4F43354BF6D18CD879C5406748F5FB10F803458D4389`
- Reproduction manifest SHA-256: `29477A5D105AC3432D133677A810A3D213221F9AC312CF23C075180D80E2CB5A`

# Final test/CI state

The local M8 baseline is 235 passed with zero failures and zero skips. Required GitHub Actions completed successfully on Ubuntu and Windows, including quick reproduction and benchmark integrity.

# Remaining scientific limitations

External cases remain partial, the benchmark is threshold-heavy, threat models and normalized valuations are project-authored, SMT coverage is restricted, robustness assumptions are synthetic, strategic games are finite, and repair families are bounded. The release makes no behavioral-prediction, policy-recommendation, representative-accuracy, or production-readiness claim.

# Remaining external dependencies

Independent economist/domain review, action-space review, valuation review, encoding review, an externally contributed sealed holdout, and independent human reproduction remain outstanding. Project-controlled CI is not independent validation.

# Recommended next action

Send the public research preview and external-review package to independent economists/domain experts and invite an independently contributed sealed mini-holdout before revising the manuscript toward submission.
