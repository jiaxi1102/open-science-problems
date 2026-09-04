# Exact search for R_3^KG(3,3)

## Research question

The five-point construction proves

```text
R_3^KG(3,3) >= 12,
```

while Heath–McCourt–Parker–Schwieder–Zerbib report the computational upper
bound

```text
R_3^KG(3,3) <= 13.
```

Therefore one finite question determines the exact value:

> Does `KG(12,3)` have a red/blue edge coloring with no monochromatic triangle?

- A **SAT** certificate proves `R_3^KG(3,3) = 13`.
- A fully checked **UNSAT** certificate proves `R_3^KG(3,3) = 12`.

A solver status by itself is not accepted as a mathematical certificate.

## Exact encoding

`KG(12,3)` has:

- 220 vertices;
- 9,240 edges, one Boolean variable per red/blue edge color;
- 61,600 triangles;
- two NAE clauses per triangle, for 123,200 triangle clauses.

Three additional unit clauses are a sound symmetry break. A fixed triangle is
normalized to have one specified red edge and two specified blue edges. Every
admissible coloring can be moved to this form by a permutation of the 12
ground points and, if needed, a global color swap.

The generator records hashes of the vertex, edge, triangle, and CNF orderings.
A SAT model is reconstructed and checked independently against all 61,600
triangles before it is accepted.

## Reproduce

```bash
python tools/search_kneser_r3_exact.py generate /tmp/kneser-r3
kissat --sat /tmp/kneser-r3/kg12_3_no_mono_triangle.cnf \
  > /tmp/kneser-r3/solver.out
python tools/search_kneser_r3_exact.py verify \
  /tmp/kneser-r3/solver.out /tmp/kneser-r3
```

The workflow pins Kissat 4.0.4 by SHA-256. Solver output and all generated
certificates are uploaded as run artifacts.

## Claim boundary

This directory is an active research experiment. Until a SAT model passes the
independent verifier or an UNSAT proof trace passes an independent proof
checker, it establishes no new Ramsey-number value.
