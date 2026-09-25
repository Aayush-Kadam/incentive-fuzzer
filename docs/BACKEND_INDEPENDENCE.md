# Backend Independence

| Component | Shared | Independent | Reason |
|---|---:|---:|---|
| YAML parser | Yes | No | Common input representation |
| Schema validation and typed AST | Yes | No | Avoid testing two different languages |
| Decimal-to-rational conversion | No | Yes | Numeric differential target |
| Expression evaluation | No | Yes | Z3 translation never calls M1 `_eval` |
| Transition semantics | No | Yes | Independently encodes simultaneous RHS evaluation |
| Rule execution/order | No | Yes | Rebuilds ordered symbolic environment |
| Cost and utility calculation | No | Yes | Independent symbolic terms |
| Property encoding | No | Yes | SMT asserts existential profitable deviation |
| Witness validity | Shared oracle | Yes, then replayed | Z3 predicts; M1 independently replays |

The formal backend imports immutable model classes but not runtime semantic helpers. Sharing the parser means differential agreement does not validate parsing itself. It validates two interpretations of the same parsed AST.

