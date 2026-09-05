# Five-point constructions and padding for Kneser Ramsey numbers

**ID:** `math-0003`  
**Field:** extremal combinatorics / Ramsey theory / Kneser graphs  
**Original source:** Heath, McCourt, Parker, Schwieder, and Zerbib, *Ramsey Numbers in Kneser Graphs*, arXiv:2510.25734v2  
**Problem status:** `proposed-proof`  
**Formal verification:** diagonal and asymmetric coloring witnesses verified end to end; general-target corollary written only  
**Novelty:** `search-incomplete`  
**External review:** `none`

## Problem and results

The Kneser graph KG(n,r) has the r-subsets of an n-element set as vertices,
with two vertices adjacent exactly when disjoint. The number R_r^KG(s,t)
is the least n such that every red/blue edge-coloring of KG(n,r) contains a
red s-clique or a blue t-clique.

### A. Verified diagonal lower bound

For every r >= 1,

\[
R_r^{KG}(3,3)\ge3r+3.
\]

The construction on KG(3r+2,r) uses only five distinguished points.
The [original complete proof](proof/five-point-construction.md) and
[original verification record](verification-record.md) are retained.

### B. New verified asymmetric extension

For every r >= 1 and s >= 3,

\[
\boxed{R_r^{KG}(s,3)\ge s(r+1).}
\]

A five-point cycle together with s-3 padding points yields a coloring of
KG(sr+s-1,r) with no red s-clique and no blue triangle. The old diagonal
result is its s=3 case. This theorem has an arbitrary-r, arbitrary-s Lean
proof, not an extrapolation from finite examples.

### C. General-target corollary (written proof, not yet Lean-verified)

For r >= 1 and s,t >= 3,

\[
R_r^{KG}(s,t)\ge\max(s,t)r+s+t-3.
\]

A second padding step extends B to arbitrary t. Its complete written proof
is included but is not covered by the current final Lean theorem.

## The new construction

Partition the ground set into P,D,Y with |P|=5, |D|=s-3, |Y|=sr-3.
Identify P with a cyclically ordered five-point set. An r-set is tagged if
it meets D. Vertices avoiding D use the original five-point trace coloring.
Edges involving a tagged vertex are red, except edges to an untagged vertex
with empty P-trace, which are blue.

There is no blue triangle. In a hypothetical red s-clique, at most s-3
vertices are tagged and at most two are untagged with nonempty traces.
Hence one vertex has an empty trace and is untagged. Red adjacency to it
excludes every tagged vertex and forces all traces to have size at most one.
At most two cycle points can then be covered. The union must miss all s-3
padding points and at least three cycle points: at least s unused points,
contradicting the available s-1 unused points.

See [the complete asymmetric proof](proof/asymmetric-padding.md).

## Concrete comparison with the source paper

Table 2 of arXiv:2510.25734v2 gives the source bounds below. These are
comparisons with that particular source version, not a certified exhaustive
survey of all later or unpublished work.

| Quantity | Source lower | Construction lower | Source upper |
|---|---:|---:|---:|
| R_3^KG(3,3) | 11 | 12 (earlier result) | 13 |
| R_3^KG(3,4) | 13 | 16 | 22 |
| R_3^KG(3,5) | 18 | 20 | 31 |
| R_3^KG(3,6) | 22 | 24 | 42 |

This construction need not beat every existing bound. For example, the
source gives R_2^KG(3,5)>=16, stronger than the value 15 from theorem B.
The best justified bound is the maximum of applicable results.

## Lean verification

The final asymmetric theorem is:

```lean
theorem kneserRamsey_asymmetric_lower_bound
    (r s : Nat) (hr : 1 ≤ r) (hs : 3 ≤ s) :
    KneserAsymmetricAvoiding (s*(r+1)-1) r s
```

`KneserAsymmetricAvoiding` explicitly requires a symmetric Boolean coloring
of all r-element finsets of `Fin n`, with no red s-clique of pairwise-disjoint
vertices and no blue triangle of pairwise-disjoint vertices. For r>=1 these
vertices are distinct. This is the direct witness formulation needed for
the Ramsey lower bound; a separate least-integer operator is not formalized.

The default Lake roots include all three modules:

```text
KneserFivePoint
KneserFivePoint.LowerBound
KneserFivePoint.Asymmetric
```

Lean 4.33.1 and Mathlib v4.33.1 are pinned. The successful build and a separate
explicit audit of the actual final declarations report only:

```text
[propext, Classical.choice, Quot.sound]
```

There is no `sorryAx`, native-computation axiom, or hand-written axiom in
the final theorem dependencies. Finite lemmas use `decide +kernel` and the
universal part uses ordinary cardinality and injection proofs.

The exact successful source commit, run, job, output, and reproduction
instructions are in [asymmetric-verification.md](asymmetric-verification.md).

## Executable regressions

From the repository root:

```bash
python tools/verify_kneser_five_point.py
python tools/verify_kneser_padding.py
cd problems/math-0003-kneser-ramsey-lower-bound/formal
lake exe cache get
lake build
lake env lean Audit.lean
```

The original verifier checks 918 relevant trace partitions and all Kneser
triangles directly for r=1,2,3,4. The padding verifier checks the unrestricted
five-point properties and, for s=3,...,8, a total of 820,706 s-trace families
and 233,970 triangle-trace families, deliberately including repeated empty
traces. None violate the required conditions. These are independently
implemented finite checks, not substitutes for the universal proof.

## Scientific status and remaining work

The theorem witnesses are verified; priority and external expert review are
not. The [original novelty record](references/NOVELTY.md) and
[asymmetric search record](references/ASYMMETRIC-NOVELTY.md) describe the
searches and missing checks. No author confirmation or peer review has been
obtained.

The stronger diagonal equality R_r^KG(3,3)=3r+3 is a conjectural target, not
a result. Its matching upper bound remains unproved. These new lower bounds
improve additive terms, not the leading asymptotic coefficient for fixed
clique sizes. The general-target corollary still needs Lean formalization.

The highest-value mathematical goal remains a structural upper-bound
argument, while the current constructive results are ready for independent
correctness and priority review. The separate fractional-host bridge on the
exploratory branch has its own proof and novelty obligations.
