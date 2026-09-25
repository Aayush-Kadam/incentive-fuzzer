# IF-CWE: Provisional Incentive Weakness Enumeration

These identifiers classify modeled failures, not moral blame or observed real-world conduct. Each finding must specify feasibility, legality, information, cost, and objective. “Detector” means candidate method; none is presumed sound and complete.

## IF-001 Hard Eligibility Cliff

**Definition:** a small adverse change in an assignment variable causes a discrete loss exceeding the underlying change. **Example:** income 500,001 yields no 100,000 award while 499,999 qualifies. **Intuition:** a notch creates a profitable interval for downward adjustment. **Symptoms:** discontinuity and local net-resource decrease. **Detectors:** boundary enumeration, symbolic inequality solving, finite differences. **False positives:** immutable income, rounding, waitlists, high adjustment cost. **Limits:** the cliff may be intentional and redistribution-sensitive.

## IF-002 Strategic Bunching

**Definition:** best responses concentrate at a rule kink, notch, cap, or tier. **Example:** reported sales cluster just above a bonus threshold. **Intuition:** marginal rewards change sharply. **Symptoms:** mass near thresholds or optimizer convergence. **Detectors:** best-response sweeps, density tests, breakpoint search. **False positives:** natural heaping and administrative rounding. **Limits:** simulated bunching is not empirical evidence.

## IF-003 Effort Suppression

**Definition:** the rule makes reducing productive effort privately optimal relative to a stated intended-effort objective. **Example:** benefit withdrawal plus tax makes an extra shift reduce utility. **Intuition:** effective marginal burden exceeds the value of output. **Symptoms:** negative participation/effort gradient. **Detectors:** marginal utility analysis, constrained optimization. **False positives:** leisure is legitimately valued; labor constraints. **Limits:** requires credible effort cost and wage opportunity set.

## IF-004 Temporal Arbitrage

**Definition:** timing changes eligibility or payment without a corresponding change in intended economic substance. **Example:** defer an invoice across a measurement date. **Intuition:** snapshot rules ignore intertemporal equivalence. **Symptoms:** value jumps under small date shifts. **Detectors:** event-time mutation and finite-horizon optimization. **False positives:** real discounting or statutory period differences. **Limits:** needs liquidity, delay cost, and legal timing constraints.

## IF-005 Reporting-Reality Divergence

**Definition:** an agent profits by changing a reported measure while true state/objective is unchanged. **Example:** reclassify revenue rather than reduce emissions. **Intuition:** the mechanism rewards a proxy. **Symptoms:** report/true-state gaps. **Detectors:** dual-state modeling, audit expected utility, invariant checks. **False positives:** legitimate accounting elections. **Limits:** depends on observability and enforcement.

## IF-006 Entity Splitting

**Definition:** one economic unit gains by reorganizing into multiple entities under per-entity rules. **Example:** divide a firm to claim several caps. **Intuition:** aggregation boundary is manipulable. **Symptoms:** payoff rises with entity count while consolidated activity is fixed. **Detectors:** partition search, MILP, symmetry reduction. **False positives:** real decentralization costs or independent ownership. **Limits:** legal and beneficial-ownership rules are essential.

## IF-007 Transaction Splitting

**Definition:** dividing an economically equivalent transaction changes treatment advantageously. **Example:** split a purchase below a reporting threshold. **Intuition:** per-transaction thresholds lack aggregation. **Symptoms:** subadditivity of liability/review. **Detectors:** integer partition search and metamorphic tests. **False positives:** volume discounts or separate delivery costs. **Limits:** equivalence window must be specified.

## IF-008 Household Restructuring

**Definition:** formal household composition changes yield gains without the intended substantive change. **Example:** nominally separate households to bypass a joint cap. **Intuition:** eligibility unit differs from economic unit. **Symptoms:** discontinuities across relationship declarations. **Detectors:** graph rewrites and coalition utility checks. **False positives:** genuine separation or caregiving changes. **Limits:** privacy, law, and nonpecuniary costs dominate.

## IF-009 Metric Substitution

**Definition:** effort shifts from the true objective to a rewarded measured dimension. **Example:** teach only tested items while broader learning falls. **Intuition:** proxy optimization. **Symptoms:** proxy rises while objective is flat/falls. **Detectors:** causal/objective model and multi-output optimization. **False positives:** proxy is the accepted objective. **Limits:** cannot be inferred without an explicit objective mapping.

## IF-010 Participation Cycling

**Definition:** repeated entry/exit extracts benefits or avoids obligations. **Example:** churn accounts to repeatedly obtain a new-user reward. **Intuition:** state resets fail to preserve identity/history. **Symptoms:** profitable periodic action trace. **Detectors:** bounded model checking and cycle detection. **False positives:** intended renewable eligibility. **Limits:** identity resolution and horizon matter.

## IF-011 Coalition Exploitation

**Definition:** a group can coordinate transfers/actions for joint gain when no member alone can. **Example:** bidders rotate bids and share surplus. **Intuition:** individual constraints omit group deviations. **Symptoms:** positive coalition surplus under side payments. **Detectors:** coalition enumeration, cooperative-game bounds, MILP. **False positives:** unenforceable side payments. **Limits:** combinatorial explosion and coalition stability.

## IF-012 Dynamic Exploit Chain

**Definition:** individually benign actions create a harmful profitable sequence through state transitions. **Example:** change status, claim benefit, then restore status. **Intuition:** local checks miss path dependence. **Symptoms:** multi-step witness with intermediate enabling states. **Detectors:** planning, bounded model checking, RL only as candidate generator. **False positives:** infeasible ordering or missing cooldown. **Limits:** bounded horizons do not prove long-run safety.

## IF-013 Capacity Capture

**Definition:** strategic demand consumes scarce allocation capacity disproportionate to the intended objective. **Example:** submit low-cost duplicate applications for limited grants. **Intuition:** allocation ignores demand-generation incentives. **Symptoms:** allocation dominated by repeat/low-value claims. **Detectors:** congestion simulation and adversarial demand generation. **False positives:** legitimately high need. **Limits:** requires a welfare priority model.

## IF-014 Queue Manipulation

**Definition:** actors alter position or service priority through strategic timing, identity, or request structure. **Example:** duplicate bookings increase priority odds. **Intuition:** queue discipline is gameable. **Symptoms:** priority gains without higher need. **Detectors:** discrete-event simulation and sequence search. **False positives:** valid urgent rescheduling. **Limits:** operational stochasticity complicates replay.

## IF-015 Policy Composition Failure

**Definition:** policies safe in isolation jointly violate a property. **Example:** overlapping phase-outs create an excessive effective marginal tax rate. **Intuition:** marginal incentives add and thresholds interact. **Symptoms:** violation only in composed evaluator. **Detectors:** compositional breakpoint analysis and differential runs. **False positives:** double counting or inconsistent units. **Limits:** jurisdiction and take-up alignment required.

## IF-016 Multiple-Equilibrium Vulnerability

**Definition:** a rule admits materially different equilibria, including an undesirable or unstable one, contrary to design assumptions. **Example:** adoption subsidies support both no-adoption and high-adoption equilibria. **Intuition:** strategic complementarities create selection risk. **Symptoms:** multiple fixed points/best-response intersections. **Detectors:** equilibrium enumeration, continuation, stability analysis. **False positives:** duplicate numerical representations. **Limits:** enumeration is incomplete for broad games; selection must be explicit.

## IF-017 Audit Avoidance

**Definition:** actions reduce detection probability enough to make prohibited behavior profitable. **Example:** distribute declarations across low-risk channels. **Intuition:** enforcement rule is itself strategic. **Symptoms:** optimal action trades substantive return for lower audit exposure. **Detectors:** expected-utility optimization and adversarial audit model. **False positives:** lawful risk segmentation. **Limits:** operational audit models are sensitive and uncertain.

## IF-018 Cross-Jurisdiction Arbitrage

**Definition:** location or legal nexus shifts treatment without corresponding intended activity. **Example:** book a transaction in a lower-burden jurisdiction. **Intuition:** non-harmonized rule boundaries reward relabeling/location. **Symptoms:** payoff jumps across borders with small relocation cost. **Detectors:** graph/location search and comparative evaluation. **False positives:** genuine relocation and public-service differences. **Limits:** conflict-of-law and compliance details are domain-specific.

## IF-019 Strategic Default

**Definition:** nonperformance is privately optimal because relief, renegotiation, or enforcement rules dominate compliance. **Example:** intentionally miss a threshold to qualify for forgiveness. **Intuition:** downside is capped or transferred. **Symptoms:** default payoff exceeds feasible compliance payoff. **Detectors:** state-contingent utility and dynamic optimization. **False positives:** involuntary default. **Limits:** credit, reputation, and legal consequences must be modeled.

## IF-020 Goodhart/KPI Exploitation

**Definition:** optimizing a target metric degrades the latent goal or unmeasured dimensions. **Example:** support staff close tickets prematurely to meet closure targets. **Intuition:** a measure ceases to be informative under optimization. **Symptoms:** KPI improves while quality/goal worsens. **Detectors:** multi-metric invariants, causal stress scenarios, adversarial action models. **False positives:** metric correctly encodes the objective. **Limits:** needs defensible latent-goal measurement; cannot be solved by syntax alone.

## Cross-cutting labels

Each instance also records: response class; legal/illegal/uncertain; deterministic/stochastic; single/multi-agent; static/dynamic; information regime; evidence level (candidate, replayed, robust, formally verified); and provenance of every material parameter.

