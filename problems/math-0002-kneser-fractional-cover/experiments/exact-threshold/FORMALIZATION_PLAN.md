# Formalization plan after finite certification

The SAT certificates target only the two finite combinatorial lemmas. After both certify UNSAT, the end-to-end Lean layer should proceed in this order:

1. define the 28 vertices and 210 edges of `KG(8,2)` and the induced Petersen graph on a five-set;
2. import or restate the two finite lemmas as generated Boolean theorems, preferably with checked LRAT evidence;
3. formalize the three-point weight function and prove the independent-set inequality implies dual feasibility;
4. formalize the finite fractional-chromatic dual lower bound `31/10`;
5. prove that a cover with both thresholds below `3` reduces to a triangle-free edge partition;
6. formalize the two-coordinate ternary upper-bound construction.

No exact-threshold status should be upgraded before the finite certificates and the written bridge have both been audited.
