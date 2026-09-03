# Program for the matching upper bound

## Target

The current lower-bound construction gives

\[
R_r^{KG}(3,3)\ge 3r+3.
\]

The groundbreaking endpoint is the matching statement

\[
R_r^{KG}(3,3)=3r+3.
\]

It is enough to prove that every red/blue edge coloring of
`KG(3r+3,r)` contains a monochromatic triangle.

## Rigidity route

The project now has two complementary ingredients.

### 1. A five-point extremal family

The explicit trace coloring gives a good coloring of `KG(3r+2,r)` for every
`r`. Its finite trace gadget is verified in Lean.

### 2. One-point saturation

For every `r >= 3`, that explicit coloring cannot be extended to
`KG(3r+3,r)` while preserving its old edge colors. The proof uses short odd
closed forcing walks through one old vertex.

These imply the upper bound once one proves a suitable extremal uniqueness or
stability theorem:

> Every good coloring of `KG(3r+2,r)` is equivalent to the five-point trace
> coloring, or is close enough to inherit its one-point-saturation
> obstruction.

The required conclusion is weaker than complete classification. It suffices to
identify, inside every extremal coloring, one configuration supporting both
opposite-color odd forcing walks against an added point.

## Rank-three link structure

For `r=3`, fix a vertex `A` in a hypothetical good coloring of `KG(12,3)`.
The incident colors on the 84 triples in the nine-point complement have no
monochromatic perfect matching.

The sharp nine-point link theorem gives a five-set `S_A` and color `q_A` such
that every triple in `S_A` is joined to `A` with color `q_A`. Thus every one of
the 220 vertices carries at least one monochromatic five-cloud.

This converts the exact upper-bound problem into compatibility among local
clouds. If `B` is contained in `S_A`, then edge `AB` is forced to color `q_A`.
Any two such demands on the same edge must agree, and no triangle may have all
three edge colors forced alike.

## Computational ladder

The exact program is deliberately staged so that every negative result yields
a reusable theorem rather than only a timeout.

1. **Cloud choice.** Choose one five-cloud at every vertex and enforce mutual
   edge-color consistency.
2. **Forced triangles.** Forbid every Kneser triangle whose three colors are
   forced equal by the chosen clouds.
3. **Residual edges.** Add variables only for edges not fixed by any chosen
   cloud, with NAE constraints on residual triangles.
4. **Canonical local types.** Enumerate nine-point link colorings up to `S_9`
   and color swap, recording all five-clouds in each type.
5. **Compatibility graph.** Replace link assignments by local-type variables
   and exact overlap constraints.
6. **Certificate extraction.** If infeasible, produce a checkable SAT/ILP
   certificate and minimize it to a small family of links and triangles.
7. **Human theorem.** Translate the minimized obstruction into a stability
   lemma and formalize its finite core.

The first cloud-only model is feasible. The stronger forced-edge model has
39,160 binary variables and 243,550 constraints; a bounded HiGHS run found no
incumbent and did not prove infeasibility. Its status is unresolved.

## Theoretical ladder

Parallel to exact computation, pursue the following statements in increasing
strength.

### Link theorem A — complete five-cloud

Already established and exact: every rank-three link contains a monochromatic
`K_5^(3)`, and five is sharp.

### Link theorem B — multiple-cloud stability

Show that every admissible nine-point link either has many monochromatic
five-clouds or belongs to a small exceptional family, conjecturally including
the Fano-star type.

### Overlap theorem

Show that five-clouds belonging to disjoint Kneser vertices cannot be selected
independently. Desired forms include:

- a forced mutual containment with opposite requested colors;
- a same-color cloud triangle;
- a short alternating cloud walk that closes with odd parity;
- concentration of cloud complements onto a global distinguished set.

### Global five-point recovery

Prove that compatible local clouds align around one global five-set `P` and a
cyclic order on `P`. Recover the four trace-coloring rules from link data.
This would be an extremal reconstruction theorem for `KG(11,3)`.

### Rank lifting

Identify which parts depend only on the five-point trace gadget and matching
cardinality. Replace triples by `r`-sets and nine-point links by the relevant
`2r+3`-point local matching problem.

## Decision tree

### If `KG(12,3)` is infeasible

Then

\[
R_3^{KG}(3,3)=12.
\]

The next goal is a compact structural proof and a general stability theorem.

### If `KG(12,3)` is feasible

Then the known upper bound gives

\[
R_3^{KG}(3,3)=13.
\]

The model must be independently checked, compressed into a reproducible
certificate, and compared with the five-point lower-bound family to identify
the first genuinely new extremal mechanism.

Either outcome is mathematically valuable. The program never interprets a
solver timeout as evidence for either branch.

## Breakthrough standard

The result becomes a major theorem when at least one of the following is
achieved:

1. the exact formula `R_3^{KG}(3,3)` with an independently checkable
   certificate and a human structural explanation;
2. uniqueness or finite stability of the five-point coloring at `3r+2`;
3. the general matching upper bound `R_r^{KG}(3,3) <= 3r+3`;
4. a broader finite-link method that improves diagonal Kneser-Ramsey bounds
   for other clique orders.

The strongest endpoint is the general equality together with a reconstruction
theorem explaining why five distinguished points and an odd cycle are the
canonical extremal mechanism.

## Claim boundary

At present:

- the lower bound is a proposed theorem with a Lean-verified finite core;
- one-point saturation is a proposed rigidity theorem;
- the nine-point link theorem is exactly certified but not yet formalized in
  Lean or independently assessed for novelty;
- the matching upper bound remains open in this project;
- no exact value for `R_3^{KG}(3,3)` is claimed.
