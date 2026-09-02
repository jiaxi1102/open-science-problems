# Exact computation for `R_3^KG(3,3)`

## Decisive finite question

The five-point construction proves

\[
R_3^{\mathrm{KG}}(3,3)\ge 12.
\]

The posted Heath–McCourt–Parker–Schwieder–Zerbib paper gives

\[
R_3^{\mathrm{KG}}(3,3)\le 13.
\]

Therefore one finite instance decides the exact value:

- if `KG(12,3)` has a red/blue edge coloring with no monochromatic triangle,
  then `R_3^KG(3,3)=13`;
- if no such coloring exists, then `R_3^KG(3,3)=12`.

## SAT encoding

`tools/kg12_r3_sat.py` deterministically enumerates:

- `220` vertices, the 3-subsets of `[12]`;
- `9240` Kneser edges, one Boolean variable per edge;
- `61600` Kneser triangles;
- `123200` not-all-equal clauses, two per triangle;
- three additional unit clauses for a justified symmetry normalization.

For each triangle with edge variables `x,y,z`, the clauses

```text
 x  y  z
-x -y -z
```

forbid all-blue and all-red respectively.

The symmetry normalization fixes the canonical triangle

```text
A = {0,1,2}, B = {3,4,5}, C = {6,7,8}
```

to colors red, blue, blue on `AB,AC,BC`. This loses no solution: every valid
coloring makes the triangle nonmonochromatic; a global color swap makes its
minority color red, and a permutation of the twelve ground points maps the
unique red edge to `AB`.

## Certificate policy

The workflow uses the pinned Kissat 4.0.4 Linux binary, checks the release
asset SHA-256, and treats the two outcomes differently:

- **SAT:** the complete model is reconstructed and independently checked
  against all `61600` triangles by the standard-library Python verifier;
- **UNSAT:** Kissat emits a DRAT proof, which is independently checked by a
  pinned build of `drat-trim`.

Neither a solver exit code nor a log message alone is accepted as the result.
The CNF, enumeration hashes, solver output, model or proof, checker output, and
checksums are retained as a workflow artifact.

## Status

This directory is an active research experiment. No exact-value claim should
be made until one of the two certificate paths completes and the resulting
artifact is independently reproduced.
