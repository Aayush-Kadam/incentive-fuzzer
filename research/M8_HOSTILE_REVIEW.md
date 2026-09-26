# M8 Hostile Review

## Verdict under adversarial reading

The artifact is credible as a bounded research preview, not as evidence of general policy-auditing accuracy. Its strongest contribution is the disciplined evidence pipeline and preservation of negative results. Its strongest weakness is that the benchmark remains small, scalar, threshold-heavy, and substantially project-authored.

1. **Mostly a threshold scanner?** Much of IF-Bench rewards boundary inspection. The population, game, repair, and formal layers are real but evaluated mostly on synthetic or narrow cases.
2. **Does boundary-only undermine the integrated system?** Yes, as a recall claim: boundary-only found the same 19 cases with 369 evaluations versus combined search’s 1,261. Integration must be justified by replay, blindness, formal cross-checking, and regression structure—not superior recall.
3. **External cases too scalar and threshold-heavy?** Yes. The non-threshold supplement is only three cases and cannot establish broad coverage.
4. **Actions project-authored?** Yes. Findings are conditional on those declared actions.
5. **Normalized valuations arbitrary?** They are modeling choices, not externally validated welfare estimates. Sensitivity analysis helps but does not establish realism.
6. **Is 5/6 too small to generalize?** Yes. It is a rediscovery result on curated partial encodings, not an accuracy estimate.
7. **Repairs obvious grid tuning?** Often. M6 demonstrates regression discipline, not general synthesis or optimal design.
8. **M5 games too synthetic?** Yes. They prove the implementation can represent strategic complementarity, not that real populations coordinate this way.
9. **Formal verification too narrow?** Yes. Four IF-Bench cases are unsupported, including transaction splitting and composition structures.
10. **Does the paper overuse “formal”?** It must always pair the term with “supported fragment” or domain-scoped statuses.
11. **401(k) framed as vulnerability?** It must not be. It is an intended-response control.
12. **Value beyond manual analysis?** Reproducible search, exact replay, label separation, solver cross-checking, and repair re-attack are useful. The present benchmark does not show better discovery than careful boundary inspection.
13. **Reduction contribution externally?** Weak in M7: the reported reduction ratio was 1.0. Reduction infrastructure exists, but this evaluation showed no compression benefit.
14. **Is IF-CWE useful?** Potentially as vocabulary; external adoption or inter-rater agreement has not been established.
15. **Can an economist reproduce encodings?** They can inspect and run them, but independent rule-fidelity review is still missing.
16. **Can a software researcher clean-install?** M8 tests this locally and records the procedure; cross-platform independent reproduction remains outstanding.
17. **Any claim stronger than evidence?** The risk centers on “external,” “formal,” and “repair.” The claim ledger constrains each.
18. **Hidden manual interventions?** Case authoring, threat models, valuation choices, and benchmark labels involve human judgment. Runtime evaluation is automated and labels remain separated.
19. **Ready only for review?** Yes. It is a research preview / external-review package, not submission-ready or policy-validated.
20. **Likely journal rejection reason?** Insufficient independent external validation and a benchmark whose structure allows a simple boundary baseline to match the integrated search recall.

## Strongest remaining criticism

The project’s infrastructure is broader than its empirical evidence. A skeptical reviewer can reasonably argue that the current results validate careful engineering around a narrow family of hand-encoded rules rather than a generally useful auditing method. Only independent encoding review and an externally contributed sealed holdout can materially answer that criticism.
