# A five-point construction for triangle Ramsey numbers in Kneser graphs

**ID:** `math-0003`  
**Field:** extremal combinatorics / Ramsey theory / Kneser graphs  
**Original source:** Heath, McCourt, Parker, Schwieder, and Zerbib, *Ramsey Numbers in Kneser Graphs*, arXiv:2510.25734v2  
**Problem status:** `proposed-proof`  
**Formal verification:** `end-to-end-verified`  
**Novelty:** `search-incomplete`  
**External review:** `none`

## Original problem

For integers `r,s,t >= 1`, the `r`-Kneser Ramsey number

\[
R_r^{\mathrm{KG}}(s,t)
\]

is the least integer `n` such that every red/blue coloring of the edges of
`KG(n,r)` contains a red `K_s` or a blue `K_t`.

For the diagonal triangle case, Heath et al. proved

\[
R_r^{\mathrm{KG}}(3,3)\ge 3r+2\qquad(r\ge2),
\]

proved `R_2^{KG}(3,3)=9`, and obtained the computational upper bound
`R_3^{KG}(3,3)<=13`. Their posted version does not contain the stronger
uniform lower bound below.

## Proposed result

### Theorem

For every integer `r >= 1`,

\[
\boxed{R_r^{\mathrm{KG}}(3,3)\ge 3r+3.}
\]

Equivalently, `KG(3r+2,r)` has a red/blue edge coloring with no monochromatic
triangle.

The coloring uses only the traces of Kneser vertices on five distinguished
ground points. The remaining `3r-3` points are completely anonymous.

## Why it matters

This proves the full lower-bound side of the natural candidate formula

\[
R_r^{\mathrm{KG}}(3,3)=3r+3.
\]

It improves the previously posted general lower bound by one for every
`r>=2`, gives the new bounds

\[
R_3^{\mathrm{KG}}(3,3)\ge12,
\qquad
R_4^{\mathrm{KG}}(3,3)\ge15,
\]

and replaces the initially discovered SAT witnesses at `r=3,4` by one
closed-form construction valid for all `r`.

The theorem does **not** prove the matching upper bound. Establishing
`R_r^{KG}(3,3)<=3r+3` for all `r` remains the central route to an exact
family theorem.

## Construction in one paragraph

Fix five ground points identified with `Z/5Z`. For an `r`-set `A`, let
`S(A)` be its trace on those five points. Classify a trace as empty,
singleton, or large (size at least two). For two disjoint vertices:

- empty--empty and large--large edges are red; empty--large edges are blue;
- singleton--singleton edges inherit the red five-cycle / blue-diagonal
  coloring of `K_5`;
- singleton--empty edges are red;
- the edge between singleton `{y}` and a large trace `T` is red exactly when
  `y-1` belongs to `T`.

Three pairwise-disjoint `r`-sets in `[3r+2]` leave exactly two ground points
unused, so their traces cover at least three of the five distinguished
points. A four-case analysis by the number of singleton traces shows that the
three induced edge colors cannot be equal.

## Argument / evidence

The complete proof is in [`proof/five-point-construction.md`](proof/five-point-construction.md).

The deterministic verifier

```bash
python tools/verify_kneser_five_point.py
```

checks all `918` possible labeled trace partitions and independently rebuilds
and verifies every Kneser triangle for `r=1,2,3,4`. It uses only the Python
standard library.

## End-to-end Lean formalization

The Lean 4.33.1 package now verifies the complete lower-bound chain for an
arbitrary natural number `r >= 1`:

1. Kneser vertices are represented as `r`-element finsets of `Fin n`.
2. The five distinguished points are embedded into `Fin (3*r+2)`.
3. Each vertex is mapped to its five-point trace.
4. Pairwise-disjoint Kneser vertices are proved to have pairwise-disjoint
   traces.
5. A cardinality theorem proves that three disjoint `r`-sets in `3*r+2`
   points have traces covering at least three distinguished points.
6. The kernel-checked five-point gadget rules out a monochromatic triangle.
7. The explicit coloring is packaged as a witness for
   `KneserRamseyLowerBound r (3*r+3)`.

The final theorem is:

```lean
theorem kneserRamsey_three_three_lower_bound (r : Nat) (hr : 1 ≤ r) :
    KneserRamseyLowerBound r (3 * r + 3)
```

CI builds both `KneserFivePoint` and `KneserFivePoint.LowerBound`, rejects
`sorry`, `admit`, and hand-written axioms, and performs an axiom audit. The
final theorem depends only on:

```text
[propext, Classical.choice, Quot.sound]
```

There is no `sorryAx` and no native-computation axiom. See
[`verification-record.md`](verification-record.md) for the reproducible run.

### Formal statement boundary

The formal file defines the lower bound in its direct witness form: a
symmetric two-coloring of all `r`-subsets of a `(3r+2)`-point set such that
every triple of pairwise-disjoint vertices receives both colors. This is the
mathematical content needed to conclude `R_r^{KG}(3,3) >= 3r+3`. It does not
separately formalize the source paper's least-integer operator and prove an
API-level equivalence to that notation.

## Novelty / prior art

A targeted search through September 2, 2026 found the posted Kneser-Ramsey
paper with the weaker bound `3r+2`, but did not find this five-point trace
construction or the displayed `3r+3` theorem. See
[`references/NOVELTY.md`](references/NOVELTY.md).

This is not yet an exhaustive priority determination. The authors of the
original paper and independent extremal-combinatorics experts should be asked
to check both novelty and correctness before public priority claims.

## Risks and unresolved items

1. The result has not yet been peer reviewed or independently reproduced.
2. Literature priority remains incomplete despite the targeted negative
   search.
3. The matching general upper bound remains open.
4. The broader fractional-host bridge on the exploratory branch remains a
   separate theorem candidate with its own novelty burden.

## Next gates

1. Obtain independent review from the Kneser-Ramsey paper's authors and an
   unrelated Ramsey-theory expert.
2. Formalize an optional equivalence to a least-`n` Kneser-Ramsey-number
   definition, without changing the already verified witness theorem.
3. Attack the upper bound `R_r^{KG}(3,3)<=3r+3`, using the five-point gadget
   as a guide to the extremal structure.
4. Determine whether analogous finite trace gadgets sharpen lower bounds for
   `R_r^{KG}(s,t)` beyond the triangle case.
