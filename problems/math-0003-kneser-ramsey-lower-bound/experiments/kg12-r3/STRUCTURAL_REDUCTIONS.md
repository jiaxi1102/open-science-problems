# Structural reductions for the exact `r=3` problem

## 1. The one-unit gap

The five-point construction gives a red/blue edge coloring of
`KG(11,3)` without a monochromatic triangle. Consequently

\[
R_3^{\mathrm{KG}}(3,3)\ge 12.
\]

The published computational upper bound is

\[
R_3^{\mathrm{KG}}(3,3)\le 13.
\]

Thus the exact value is determined by one finite question:

> Does `KG(12,3)` admit a red/blue edge coloring with no monochromatic
> triangle?

A satisfying coloring proves the value is `13`; a checked impossibility proof
proves it is `12`.

## 2. Exact instance counts

The vertices are the 3-subsets of a twelve-point ground set. Hence there are

\[
\binom{12}{3}=220
\]

vertices. A fixed triple is disjoint from \(\binom{9}{3}=84\) triples, so the
number of Kneser edges is

\[
\frac12\binom{12}{3}\binom{9}{3}=9240.
\]

A Kneser triangle consists of three pairwise-disjoint triples. Choose its
nine-point union and partition that union into three unordered triples:

\[
\binom{12}{9}\frac{9!}{(3!)^3 3!}=61600.
\]

With one Boolean color variable per edge, every Kneser triangle contributes
exactly two not-all-equal clauses.

## 3. Four-block partitions and the canonical dichotomy

A partition of the twelve points into four triples induces a `K4` in the
Kneser graph. There are

\[
\frac{12!}{(3!)^4 4!}=15400
\]

such partitions.

Consider any red/blue coloring of the six edges of `K4` with no monochromatic
triangle. The red graph and its complement are both triangle-free. A direct
classification gives exactly 18 labeled colorings:

- three red perfect matchings, whose blue complements are four-cycles;
- three red four-cycles, whose blue complements are perfect matchings;
- twelve red copies of `P4`, whose blue complements are also copies of `P4`.

Therefore, after a permutation of the four blocks and one global color swap,
every admissible coloring lies in exactly one of two canonical types:

1. **matching/C4:** red edges `AB,CD`;
2. **P4/P4:** red edges `AB,BD,CD`.

This is the justification for splitting the exact search into two primary
branches. It is a symmetry reduction, not an extra hypothesis.

## 4. The redundant star lemma

In any admissibly colored `K4`, no three-edge star is monochromatic.
Indeed, suppose `AB,AC,AD` are all red. The triangles `ABC`, `ABD`, and
`ACD` force `BC,BD,CD` blue, making `BCD` a blue triangle. The other color is
identical by symmetry.

Thus each four-block partition supplies four additional NAE constraints, one
at each center. These constraints follow from the four triangle constraints,
so adding them preserves the set of solutions while improving SAT
propagation. Across all four-block partitions this adds

\[
15400\times4=61600
\]

three-variable NAE constraints, or 123200 CNF clauses.

## 5. An exhaustive 36-cube cover

Fix the primary partition

```text
012 | 345 | 678 | 9ab
```

to one of the two canonical types above. Next use the overlapping partition

```text
036 | 149 | 27a | 58b.
```

Its six edge colors must be one of the 18 admissible labeled `K4` patterns.
Accordingly, each primary branch is the union of 18 exact cubes, and the full
problem is the union of

\[
2\times18=36
\]

cubes.

The coverage argument is elementary and complete:

- every global coloring restricts to one of the two primary canonical types;
- after the primary type is fixed, its restriction to the secondary `K4` is
  one of all 18 explicitly enumerated admissible patterns;
- no additional symmetry assumption is imposed on the secondary partition.

Therefore:

- one independently checked SAT model in any cube settles the exact value as
  `13`;
- checked UNSAT certificates for all 36 cubes settle the exact value as `12`.

A timeout, a solver-only assertion, or an UNSAT result from a restricted
ansatz does not enter this implication.

## 6. Local neighborhood obstruction

Fix a Kneser vertex `A`. Its 84 neighbors are the triples of the nine-point
complement of `A`. Color such a triple `B` by the color of edge `AB`.

Neither local color class can contain three pairwise-disjoint triples. If
`B,C,D` were three pairwise-disjoint neighbors all joined to `A` in red, then
`BC,BD,CD` would all be forced blue, producing a blue triangle. Thus each
local color class has matching number at most two.

This observation is valid and useful, but it does **not** imply a finite list
of 342 local colorings.

## 7. The corrected weighted local family

Let real weights \(w_1,\ldots,w_9\) have total \(W\), and suppose no triple
has sum exactly \(W/3\). Color a triple `T` red exactly when

\[
3\sum_{i\in T}w_i>W.
\]

For any partition of the nine points into triples `A,B,C`, their three sums
add to `W`. They cannot all exceed `W/3`, and they cannot all be below
`W/3`. Hence the partition contains both colors.

This gives a large family of valid local colorings and refutes the discarded
342-pattern completeness hypothesis. Searches using bounded local integer
weights are therefore constructive ansatzes only: SAT is decisive after full
verification, while INFEASIBLE is not an unrestricted theorem.

## 8. Uniform pure-trace gadgets

Fix `m` distinguished points and target `KG(3r+c,r)` with `r>=m`. Every
`r`-set has an arbitrary trace on the distinguished points. Three disjoint
`r`-sets have pairwise-disjoint traces `S,T,U`, and the number of distinguished
points outside their union is at most `c`. Equivalently,

\[
|S\cup T\cup U|\ge m-c.
\]

Suppose the unordered pairs of disjoint traces can be red/blue colored so
that every such trace triple has both edge colors. Coloring a Kneser edge by
its two traces then yields a valid coloring of `KG(3r+c,r)` for every `r>=m`.
It follows that

\[
R_r^{\mathrm{KG}}(3,3)\ge 3r+c+1.
\]

The repeated empty trace must be included: distinct Kneser vertices can both
avoid all distinguished points. The finite SAT quotient in
`tools/general_trace_gadget_sat.py` handles this case explicitly.

For `c=3`, a verified finite gadget would improve the current construction to

\[
R_r^{\mathrm{KG}}(3,3)\ge 3r+4
\]

for every sufficiently large `r`. A checked UNSAT quotient only rules out the
specified pure-trace architecture.

## 9. Certificate hierarchy

The project uses the following claim order:

1. **Full SAT model:** independently expand and check all 9240 edges and all
   61600 triangles.
2. **Full UNSAT:** independently check the complete DRAT/LRAT certificate.
3. **Exhaustive cube UNSAT:** independently check every cube certificate and
   mechanically verify the 36-cube cover.
4. **Restricted ansatz UNSAT:** record only as a structural negative result.
5. **Heuristic failure or timeout:** record no mathematical conclusion.

Novelty, source-statement matching, and formal verification remain separate
from the computational certificate itself.
