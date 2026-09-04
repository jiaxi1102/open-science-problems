# Independent exact verification

This directory contains a verifier independent of the Lean bit-vector encoding.
It reconstructs `KG(8,2)` from first principles and checks the strengthened
finite statement used in the proof.

## Statement checked

There is no red-blue colouring of the 210 edges of `KG(8,2)` such that:

1. none of its 420 triangles is monochromatic;
2. one 11-vertex subset contained in a double star induces only blue edges;
3. another 11-vertex subset contained in a double star induces only red edges.

The triangle constraints are not-all-equal clauses on three Boolean variables.
`verify_11_obstruction.cpp` uses exact unit propagation and exhaustive DPLL;
it does not call an LP, MILP, or probabilistic solver.

## Search-space accounting

After fixing the first double-star core to `{0,1}` by the `S_8` action:

- there are `C(13,11) = 78` choices for the first set;
- the stabilizer `S_2 x S_6` has 1440 elements;
- the 78 choices split into four checked orbits of sizes `6, 12, 30, 30`;
- there are 2184 distinct 11-subsets among all 28 double stars;
- therefore 4 x 2184 = 8736 representative pairs are checked.

The program itself generates the stabilizer, verifies the orbit decomposition,
generates every second-set candidate, and then proves each representative
NAE-3-SAT instance unsatisfiable.

## Reproduce

```bash
g++ -O3 -std=c++20 -Wall -Wextra -pedantic \
  verify_11_obstruction.cpp -o verify_11_obstruction
./verify_11_obstruction
```

The expected first word is:

```text
UNSAT
```

CI additionally checks the exact counts `28`, `210`, `420`, `78`, `4`,
`2184`, and `8736` in the output.

## Additional unsymmetrized reproduction

During discovery, a second build enumerated all `78 x 2184 = 170352`
fixed-core pairs without quotienting the first set by its stabilizer. Four
disjoint ranges returned UNSAT:

| first-set range | pairs | immediate colour conflicts | DPLL nodes |
|---|---:|---:|---:|
| 0-19 | 43,680 | 32,516 | 12,126,257 |
| 20-39 | 43,680 | 32,778 | 10,314,289 |
| 40-59 | 43,680 | 32,956 | 10,548,414 |
| 60-77 | 39,312 | 31,416 | 7,359,496 |

These discovery runs are supporting reproduction evidence. The committed
program and the Lean theorem are the maintained verifiers.
