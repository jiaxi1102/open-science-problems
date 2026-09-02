# Novelty and source boundary for one-point saturation

**Search date:** 2 September 2026  
**Status:** targeted search negative; author and expert confirmation pending.

## Claimed contribution

For the explicit five-point coloring `c_r` of `KG(3r+2,r)`, the accompanying
proof proposes that, for every `r >= 3`, no good coloring of
`KG(3r+3,r)` can restrict to `c_r` on the original ground set. We call this
**one-point saturation of the coloring**.

This is a rigidity theorem for a particular extremal coloring. It is not the
matching upper bound `R_r^KG(3,3) <= 3r+3`, because a coloring of
`KG(3r+3,r)` could in principle reorganize the old edges rather than extend
`c_r`.

## Original Kneser-Ramsey source

The investigation starts from:

- Heath, McCourt, Parker, Schwieder, and Zerbib, *Ramsey Numbers in Kneser
  Graphs*, arXiv:2510.25734v2.

The posted paper proves the weaker uniform lower bound `3r+2`, determines the
`r=2` case, and reports a computational upper bound in the `r=3` case. The
search performed for this repository did not find the five-point coloring or
its one-point rigidity theorem in that source.

## Weighted odd-cycle ingredient

The anonymous-filler step uses the integer decomposition property of the
stable-set polytope of an odd cycle. A convenient source is:

- Yohann Benchetrit, *Integer round-up property for the chromatic number of
  some h-perfect graphs*, Mathematical Programming 164 (2017), 261-281;
  arXiv:1406.0757.

The paper defines weighted coloring by multisets of stable sets and proves the
integer round-up property for t-perfect claw-free graphs. It states the
equivalent polyhedral formulation that the stable-set polytope has the integer
decomposition property. Odd cycles are claw-free and their stable-set
polytope is given by nonnegativity, edge, and odd-hole inequalities, exactly
the inequalities checked in the proof.

The imported theorem is standard prior mathematics and is not claimed as a
new contribution here. The new part is the pair of periodic five-point trace
cycles and their use as signed forcing obstructions for every rank.

## Searches performed

Targeted searches included combinations of:

- `Kneser Ramsey one-point saturated coloring`;
- `Kneser graph coloring extension monochromatic triangle`;
- `KG(3r+2,r) coloring triangle`;
- `star-critical Ramsey Kneser`;
- `critical coloring Kneser Ramsey`;
- the exact displayed lower-bound and saturation statements.

No Kneser-specific result matching the proposed theorem was located.

## Nearby terminology that is not the same result

There is a literature on **Ramsey-saturated colorings**, **star-critical
Ramsey numbers**, and extensions of colorings of complete graphs. Those
notions usually ask when adding a vertex, a star, or selected host edges to a
classical complete-graph Ramsey coloring forces a monochromatic target. The
present setting is different in two ways:

1. the host is a Kneser graph whose vertex set itself changes when one ground
   point is added;
2. the theorem preserves all old edge colors and studies the simultaneously
   created family of new Kneser vertices.

Those nearby terms should be cited for context if the result is written as a
paper, but they do not by themselves establish priority for this Kneser
construction.

## Remaining novelty work

Before claiming priority publicly:

1. ask the authors of arXiv:2510.25734 whether they know this construction or
   rigidity statement;
2. ask an independent extremal-combinatorics researcher to audit both the
   search and the reduction;
3. search MathSciNet, zbMATH, and citation chains for critical/extremal
   colorings of Kneser graphs;
4. compare against unpublished computational classifications for
   `KG(11,3)` and `KG(12,3)`;
5. search later versions and follow-up papers after the current arXiv source.

Until those steps are complete, the appropriate label is
`no-prior-proof-found`, not `novelty-confirmed`.
