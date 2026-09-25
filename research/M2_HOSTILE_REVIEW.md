# M2 Hostile Review

## Verdict

**PASS WITH LIMITATIONS**, narrowly. The system is now a real bounded counterexample generator, but its strongest result is on synthetic one-dimensional threshold mechanisms that favor boundary extraction.

## Is it merely checking boundaries?

Boundary search is the only method with full synthetic-suite equivalence recall at substantially fewer evaluations than exhaustive search. The generic property generator recovered only 0.556 mean equivalence-class recall and grid only 0.375. This is evidence for a useful structure-aware baseline, but also evidence that M2 remains primarily a threshold fuzzer.

## Would exhaustive enumeration outperform it?

Exhaustive search defines ground truth and always recovers the bounded optimum, but used 45,144 evaluations across the 12-case suite versus 4,812 for boundary search. Exhaustive is superior in guarantee, boundary search in efficiency. The suite is too small and tailored to infer scaling beyond these domains.

## Hardcoding and leakage

Search contains no fixture identifiers or expected labels. It does recognize only simple comparisons and subtractive transitions, which structurally match most benchmark cases. The suite was frozen before heuristics, but two initially planted safe labels were corrected after exhaustive evaluation showed adjacent-state exploits. This is an honest correction and also evidence that benchmark authors can mislabel apparently obvious cases.

## False positives

The three synthetic safe controls and honest-reporting canonical control produced no profitable findings under exhaustive domains. An initial apparent false positive came from incorrect boundary-origin attribution; the deviation was real but the class was wrong. The implementation now requires condition truth to change before attaching a boundary.

## Reduction

Reduction is generic finite-domain enumeration under a documented lexicographic objective. It reduced scholarship, stacked-program, and procurement findings. It is not scalable, and “minimal” is only within supplied values.

## Replay and deduplication

Every experiment finding replayed exactly. Raw findings are preserved alongside representatives. The structural equivalence relation may still merge distinct economic narratives at the same rule/action boundary or split one exploit spanning multiple boundaries.

## Intended response versus gaming

Action interpretation is explicit experiment metadata. Without it, the engine reports a profitable deviation and avoids a reporting-manipulation label. This is safer than inference but places responsibility on benchmark authors. M1 does not yet carry a closed action-semantic vocabulary.

## Non-obviousness

The search found that the truly smallest frozen scholarship witness is baseline 500,000 with a one-unit reduction, not the illustrative 500,001/two-unit case. It also falsified two “safe at domain bound” planted labels. These are useful semantic results, but a skeptical economist would still call the mechanisms elementary.

## Critical unresolved defects

None within the declared finite domain. The most important limitation is external validity: results demonstrate algorithmic behavior on self-authored synthetic threshold rules, not economic discovery in realistic institutions.

