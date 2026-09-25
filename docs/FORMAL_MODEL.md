# Formal Model M1

M1 implements the restricted object \(M=(S,A,T,R,C,U,P,\Theta)\) for one agent and one evaluation period.

- \(S\) is a total assignment to declared, bounded attributes. Attributes have type, unit, observability, manipulability, and role (`latent`, `reported`, or another explicit label).
- \(A\) is a named action definition plus a total assignment to bounded control variables.
- \(T:S\times A\rightarrow S\) is deterministic. Effects are evaluated simultaneously against the pre-action state.
- \(R\) is an ordered sequence of typed expressions. A rule may reference state, parameters, and earlier rule outputs.
- \(C:S\times A\rightarrow\mathbb{D}_{\ge0}\) is a declared money-valued direct cost.
- \(U\) is one money-valued expression evaluated from post-action state, rule outputs, and action cost.
- \(P\) is a set of bounded executable assertions. Results describe only the enumerated domain.
- \(\Theta\) is a fixed set of typed parameters with E/L/S/A provenance.

Numeric values are Python `Decimal` values constructed from source text. Integer, decimal, money, and Boolean types are distinct schema types. Money uses the money unit; no implicit currency conversion exists. Rates and scalars may multiply another numeric unit; multiplication of two dimensional quantities is rejected.

True and reported attributes are distinct ordinary symbols with different roles. The evaluator never synchronizes them implicitly. A work action may update both; a reporting action may update only the reported attribute.

The model excludes probability distributions, endogenous enforcement, multiple agents, equilibrium, recursion, unbounded variables, stochastic transitions, and intertemporal state.

