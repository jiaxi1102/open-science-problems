# A cyclic certificate for `KG(14,4)`

**Status:** proposed new computational lower bound; deterministically verified, not yet externally reviewed.  
**Consequence:**

\[
\boxed{R^{\mathrm{KG}}_4(3,3)\ge 15.}
\]

Heath--McCourt--Parker--Schwieder--Zerbib prove the general bound
\(R_r^{\mathrm{KG}}(3,3)\ge 3r+2\), which gives only `14` when `r=4`.
The certificate here colours every edge of `KG(14,4)` red or blue without a
monochromatic triangle, improving that lower bound by one in the first case
beyond the published exact and near-exact computations.

## Symmetry reduction

Partition the fourteen ground points into an eight-cycle and a six-cycle. Let

\[
\sigma=(0\ 1\ 2\ 3\ 4\ 5\ 6\ 7)
       (8\ 9\ 10\ 11\ 12\ 13).
\]

The permutation has order `lcm(8,6)=24` and acts on the edges of `KG(14,4)`.
The certificate is constant on every orbit of this action.

The full graph has:

- `1,001` vertices;
- `105,105` edges;
- `525,525` triangles;
- `4,475` edge orbits under `sigma`.

Thus the colouring is represented by only `4,475` bits, or `560` bytes. The
stored orbit bitset has SHA-256

```text
057d4833da5e4aef547ff836ff8591428c3e00fd52f0041caa046cf986a9bf79
```

Of the orbit representatives, `2,237` are red. After expanding the orbits,
the graph has `52,062` red edges and `53,043` blue edges.

## Verification

Run

```bash
python tools/verify_kneser_r4_orbit_certificate.py
```

The verifier uses only the Python standard library. It:

1. reconstructs all `1,001` four-subsets of `[14]`;
2. reconstructs all `105,105` disjointness edges;
3. reconstructs the `4,475` edge orbits under `sigma`;
4. verifies the orbit-bitset hash;
5. expands the colouring to every edge; and
6. checks all `525,525` Kneser triangles directly.

The resulting triangle counts are:

- `270,120` triangles with one red edge;
- `255,405` triangles with two red edges;
- `0` monochromatic triangles.

The verifier does not call a SAT solver and does not trust a stored list of
triangles. It reconstructs the entire finite object from the concise orbit
certificate.

## Discovery provenance

The certificate was found by reducing the NAE-SAT instance to edge orbits
under `sigma` and solving the resulting `44,026` distinct triangle clauses
with CaDiCaL. The discovered assignment was then separated from the solver
and converted into the deterministic certificate above.

A second experiment shows that a broad analytic normal form also exists:
choose a fixed eight-element part `X`, put `w(A)=|A cap X|`, and analytically
colour all edges whose endpoints avoid the central layer `w=2` by the
low--low/high--high versus low--high rule. Only the `69,300` edges touching
the central layer need remain free; that reduced problem is satisfiable and
also validates all `525,525` triangles. This boundary-layer lemma is general,
but its `r=4` completion cannot simultaneously retain the full cyclic
symmetry used by the compact certificate.

## Interpretation and limits

This is stronger than an unstructured SAT witness: it is a short,
reconstructible object with a transparent group action and an independent
exhaustive verifier. It is not yet a closed-form family construction. The
next decisive test is whether the analogous cycle type `(10)(7)` gives a good
colouring of `KG(17,5)`, and whether the orbit assignments for `r=3,4,5` can
be compressed into a uniform rule.

Until independent combinatorics experts reproduce the certificate and check
literature priority, the result should be cited as a proposed new
computational lower bound rather than an established theorem.
