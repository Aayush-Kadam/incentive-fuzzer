# M3 Formal Fragment

The implemented theory is quantifier-free linear integer and rational arithmetic with Boolean structure and `ite` expressions (QF_LIRA with `ite`).

| Node | Runtime | SMT | Exact | Restriction |
|---|---:|---:|---:|---|
| const / var | yes | yes | yes | finite Decimal or Boolean |
| add / subtract | yes | yes | yes | typed by M1 |
| multiply | yes | yes | yes | at least one SMT-simplified operand must be constant |
| min / max | yes | yes | yes | encoded with `If` |
| if | yes | yes | yes | total Boolean condition |
| `< <= > >= ==` | yes | yes | yes | exact rational/integer comparison |

Attributes and controls use Int for integer/count values and Real otherwise. Domains are bounded and optionally restricted to explicit values or arithmetic steps. Explicit value sets provide exact comparability with M2 enumeration. Symbolic-by-symbolic multiplication and non-finite-decimal model decoding fail as `UNSUPPORTED_FRAGMENT`.

Finite Decimal `d` maps exactly to its normalized fraction `p/q`; no float conversion occurs. For example `0.25 -> 1/4` and `123.45 -> 2469/20`.

