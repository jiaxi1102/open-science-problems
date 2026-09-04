# Independent audit checklist

- Reconstruct the 28 Kneser vertices and 210 edges from definitions.
- Confirm the 420 triangle constraints are complete and duplicate-free.
- Confirm each five-set contributes exactly the 15 Petersen edges.
- Confirm the `petersen` CNF negates the universal monochromatic-Petersen statement.
- Exhaustively regression-test the sequential cardinality encoding on small instances.
- Confirm the fixed Petersen graph uses one legitimate symmetry representative.
- Confirm the selected family is independent in the same colour as the fixed Petersen graph.
- Confirm weighted size at least 11 exactly negates the `31/10` dual constraint.
- Replay every UNSAT trace with an independently compiled checker.
- Verify any SAT assignment against graph semantics rather than auxiliary clauses alone.
