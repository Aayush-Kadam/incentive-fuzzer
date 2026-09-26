# Repair Objectives and Constraints

M6 keeps objectives separate. Registered dimensions include maximum residual exploit gain, population exposure, fiscal deviation, schedule distance, recipient impact, normalized parameter distance, complexity, harmful-equilibrium count, and mutation fragility.

Candidate A dominates B only when it is no worse on every selected dimension and strictly better on at least one. The Pareto frontier contains all non-dominated passing candidates. No weighted repair score is computed.

Normalized parameter distance is the sum of absolute changes divided by predeclared scales. Schedule distance is the sum of absolute output changes on registered states. Recipient impact is the fraction of registered states with changed outputs. Complexity records schedule segments or declared structural units; it is not a complete administrative-cost model.

Constraints are exact comparisons over named metrics. They prevent zero-award, zero-purpose, action-removal, and other declared over-repairs. Passing technical constraints does not make a candidate a policy recommendation.
