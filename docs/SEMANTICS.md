# IncentiveSpec v0.1 Semantics

This document is normative for M1.

## Evaluation order

1. Parse and type-check the complete specification.
2. Coerce every supplied numeric state/control value through its decimal string representation.
3. Require exactly all declared state fields and enforce bounds.
4. If an action exists, validate its controls, evaluate feasibility in the initial state, evaluate all transition effects against that same initial state, apply effects simultaneously, recheck state bounds, then evaluate direct cost in the initial state plus controls.
5. Evaluate rules once in YAML declaration order. Later rules may reference earlier outputs; forward references are invalid.
6. Evaluate utility from post-action state, rule outputs, parameters, and `action_cost`.
7. Evaluate designer outcomes separately from utility.

## Numbers and boundaries

`Decimal(str(value))` is canonical. Thus `500000` and `500000.00` denote the same exact number, and ₹500,000 is exactly representable. No binary floating-point arithmetic is used after parsing. Decimal division is not part of v0.1; non-terminating slopes must be declared as finite decimals and their approximation is part of the specification.

`lt`, `le`, `gt`, `ge`, and `eq` have their ordinary exact Decimal/Boolean meanings. There is no tolerance. Attribute and control bounds are inclusive. A hard condition using `lt` excludes equality; `le` includes it.

## Expressions

Expressions are one-key YAML AST nodes, never source code. Supported nodes are `const`, `var`, `add`, `sub`, `mul`, `min`, `max`, `lt`, `le`, `gt`, `ge`, `eq`, and `if`. Both branches of `if` are type-checked, but only the selected branch is evaluated.

Addition, subtraction, min, max, and comparisons require equal units. Multiplication requires one scalar or rate operand and preserves the other operand's unit. Arbitrary functions, imports, attribute access, loops, and evaluation of Python text are impossible through the grammar.

Nested `if` expressions define piecewise schedules. Because there is no independent list of pieces, overlap and gap ambiguity cannot arise: each Boolean condition has exactly one selected branch and a mandatory else branch. Declaration order, not hidden priority, governs rules.

## Properties

The M1 harness enumerates explicit finite state and action-alternative lists. It does not search, sample, prove, or infer domains. Supported property kinds are budget bound, resource monotonicity, maximum local resource drop, no profitable downward manipulation, no profitable misreporting, and participation. Status `SATISFIED_ON_ENUMERATED_DOMAIN` is not a proof outside the listed cases.

## Serialization

Canonical YAML preserves mapping order because rule declaration order is semantic, normalizes float spellings through Decimal text, emits Unicode, and fixes block formatting. SHA-256 of its UTF-8 bytes is the policy identity. Reordering rules can change meaning and therefore the hash.

## Errors

Schema and evaluation failures raise `IncentiveSpecError` with a logical location or field. Unsupported spec versions fail closed. `UNSUPPORTED` and `NOT_EVALUATED` are never treated as satisfaction.

