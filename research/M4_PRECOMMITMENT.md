# M4 Precommitment

Frozen before population-engine implementation and headline execution: 2026-09-26.

## Fixtures

Use the five unchanged M1 canonical fixtures. No historical calibration is claimed.

## Deterministic ranges

- Scholarship: correlated true/reported income 499,995–500,010; reduce-work amount 0–20; fixed friction `{0,1,10,100,1000,50000,99999,100000}`; base-cost multiplier `{0,0.5,1,2}`.
- Phase-out: income `{479999,480000,480001,500000,550000,619999,620000,620001}`; amount 0–20; same fixed-friction set.
- Stacked programs: income 0–20; amount 0–5; fixed friction `{0,1,5,10}`.
- Procurement: transaction value 95–105; amount 0–10; fixed friction `{0,1,5,10,20}`.
- Honest reporting: correlated true/reported income 0–20; amount 0–10; fixed friction `{0,1,5,10}`.

## Behavioral scenarios

- B0: choose the maximum adjusted gain and respond only if positive.
- B1: evaluate the first three deterministic candidates per action; respond only if positive.
- B2: exhaustive candidates, respond only when adjusted gain is at least a fixed hurdle of 100.

These are scenario rules, not behavioral estimates.

## Primary metrics

Weighted profitable share, response share, mean/max positive gain, weighted incremental designer outcomes, dominant action shares, scenario robustness, robustness-region cells, and minimum tested fixed friction eliminating profitability.

## Weighted population

Five scholarship types at incomes `{499999,500000,500001,500005,500010}` with weights `{0.10,0.20,0.30,0.20,0.20}` and fixed friction `{0,1,10,100,1000}` respectively. Provenance is S.

## Monte Carlo

Sample exactly from the frozen weighted types with local RNG seed 20260926 at N `{100,1000,5000}`. Compare profitable share to exact weighted ground truth. Wilson intervals describe sampling uncertainty only.

## Search-error check

Compare B1 against B0 exhaustive candidate enumeration for canonical grids. Report signed profitable-share error.

## Formal spot checks

Use M3 on selected scholarship and honest-reporting individual domains at profitable/unprofitable boundaries. Population summaries are not formally verified.

## Holdout

Reserve scholarship incomes 500,006–500,010 as a small implementation holdout. This is not empirical out-of-sample validation.
