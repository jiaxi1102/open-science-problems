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

## Rigidity of the construction

A second theorem candidate explains why the construction stops exactly where
it does. For every `r >= 3`, the explicit five-point coloring `c_r` of
`KG(3r+2,r)` is **one-point saturated**:

> no good coloring of `KG(3r+3,r)` can restrict to `c_r` on the original
> `3r+2` ground points.

The proof produces two periodic signed forcing cycles through the same old
Kneser vertex. One rules out coloring a selected new edge red; the other
rules out coloring it blue. Anonymous filler points are supplied by the
integer decomposition theorem for the stable-set polytope of an odd cycle.

At `r=3`, the entire one-point extension decomposes into 55 independently
checkable monotone 2-SAT instances. Exactly 10 individual new vertices can be
added, while the other 45 are obstructed. Symmetry reduces the 45 failures to
two explicit signed odd bicycles consisting of only four short alternating
paths.

See:

- [`proof/r3-one-point-saturation.md`](proof/r3-one-point-saturation.md) for
  the complete finite theorem and human certificates;
- [`proof/uniform-one-point-saturation.md`](proof/uniform-one-point-saturation.md)
  for the periodic all-r construction;
- [`references/ONE_POINT_SATURATION.md`](references/ONE_POINT_SATURATION.md)
  for the imported odd-cycle theorem and novelty boundary.

This rigidity result still does not prove the matching upper bound: a good
coloring at `3r+3`, if one exists, could reorganize the old edge colors rather
than extend `c_r`. Its value is structural—it identifies a uniform local
mechanism that any stability or uniqueness proof must confront.

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

The complete lower-bound proof is in
[`proof/five-point-construction.md`](proof/five-point-construction.md).

The deterministic verifier

```bash
python tools/verify_kneser_five_point.py
```

checks all `918` possible labeled trace partitions and independently rebuilds
and verifies every Kneser triangle for `r=1,2,3,4`. It uses only the Python
standard library.

The rigidity checks are:

```bash
python tools/verify_kneser_r3_one_point_saturation.py
python tools/verify_kneser_general_saturation_templates.py
```

The first reconstructs all 55 finite extension instances, validates every
positive assignment, and checks the short negative certificates. The second
checks both periodic trace blocks, every alternating edge color, and the
weighted odd-cycle inequalities through `r=1000` as a regression sweep. The
universal proof is the displayed algebra plus the cited integer-decomposition
theorem, not an inference from the finite sweep.

## Formalization boundary

The Lean component verifies the finite five-point gadget: every three
pairwise-disjoint five-bit traces whose union has at least three points induce
both colors. The outer lift to `KG(3r+2,r)` currently uses the written
cardinality argument that three disjoint `r`-sets leave two points unused.

The one-point-saturation proof is presently human-checked plus independently
executable verification. Its weighted odd-cycle filler lemma and periodic
trace recurrences have not yet been encoded in Lean.

The intended next formal gates are:

1. an end-to-end Lean theorem for the arbitrary-`r` lower-bound lift;
2. a Lean proof of the weighted odd-cycle filler lemma;
3. a formal composition of the two periodic forcing cycles into the
   one-point-saturation theorem.

## Novelty / prior art

A targeted search through September 2, 2026 found the posted Kneser-Ramsey
paper with the weaker bound `3r+2`, but did not find this five-point trace
construction, the displayed `3r+3` theorem, or the one-point rigidity
statement. See [`references/NOVELTY.md`](references/NOVELTY.md) and
[`references/ONE_POINT_SATURATION.md`](references/ONE_POINT_SATURATION.md).

This is not yet an exhaustive priority determination. The authors of the
original paper and independent extremal-combinatorics experts should be asked
to check both novelty and correctness before public priority claims.

## Risks and unresolved items

1. Neither theorem has yet been peer reviewed or independently reproduced.
2. The current Lean boundary checks the finite lower-bound gadget, not the
   complete arbitrary-`r` lift or the rigidity theorem.
3. The one-point theorem imports the integer decomposition property for odd
   cycle stable-set polytopes; that application needs independent audit.
4. The matching general upper bound remains open.
5. The broader fractional-host bridge on the experimental branch remains a
   separate theorem candidate with its own novelty burden.

## Next gates

1. Formalize the arbitrary-`r` lower-bound lift end to end.
2. Obtain independent review from the Kneser-Ramsey paper's authors.
3. Formalize the weighted odd-cycle filler lemma and both periodic forcing
   cycles.
4. Attack `R_r^{KG}(3,3)<=3r+3` through stability: show that every extremal
   coloring at `3r+2` is equivalent or close enough to the five-point family
   to inherit a signed-cycle obstruction.
5. Decide the exact `r=3` one-apex subproblem with a checkable SAT/UNSAT
   certificate; this is strictly smaller than the full `KG(12,3)` instance.
6. Determine whether analogous finite trace gadgets and saturation mechanisms
   sharpen other Kneser-Ramsey parameters.
