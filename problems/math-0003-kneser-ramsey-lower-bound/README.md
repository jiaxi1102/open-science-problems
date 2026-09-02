# A five-point construction for triangle Ramsey numbers in Kneser graphs

**ID:** `math-0003`  
**Field:** extremal combinatorics / Ramsey theory / Kneser graphs  
**Original source:** Heath, McCourt, Parker, Schwieder, and Zerbib, *Ramsey Numbers in Kneser Graphs*, arXiv:2510.25734v2  
**Problem status:** `proposed-proof`  
**Formal verification:** `finite-gadget-verified`  
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

## Formalization boundary

The Lean component verifies the finite five-point gadget: every three
pairwise-disjoint five-bit traces whose union has at least three points induce
both colors. The outer lift to `KG(3r+2,r)` currently uses the written
cardinality argument that three disjoint `r`-sets leave two points unused.

The intended next formal gate is an end-to-end Lean theorem for arbitrary
`r`, including the trace-cardinality bridge.

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
2. The current Lean boundary checks the finite gadget, not yet the complete
   arbitrary-`r` lift.
3. The matching general upper bound remains open.
4. The broader fractional-host bridge on the experimental branch remains a
   separate theorem candidate with its own novelty burden.

## Next gates

1. Complete and CI-check the Lean finite gadget.
2. Formalize the arbitrary-`r` lifting argument end to end.
3. Obtain independent review from the Kneser-Ramsey paper's authors.
4. Attack the upper bound `R_r^{KG}(3,3)<=3r+3`, using the five-point gadget
   as a guide to the extremal structure.
5. Determine whether analogous finite trace gadgets sharpen lower bounds for
   `R_r^{KG}(s,t)` beyond the triangle case.
