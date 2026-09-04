# A padded five-point construction for asymmetric Kneser Ramsey numbers

**Research date:** 4 September 2026 (America/New_York).  
**Status:** proposed proof; literature priority and external review unconfirmed.  
**Primary source:** E. Heath, G. McCourt, A. Parker, C. Schwieder, S. Zerbib, *Ramsey numbers in Kneser graphs*, arXiv:2510.25734v2, 10 November 2025. https://arxiv.org/html/2510.25734v2

## 1. Main theorem

The Kneser graph KG(n,r) has the r-element subsets of an n-element ground set as vertices, with disjoint subsets adjacent. R_r^KG(s,t) is the least n for which every red/blue edge-coloring contains a red s-clique or a blue t-clique.

**Theorem A.** For all integers r >= 1 and s >= 3,

\[
R_r^{KG}(s,3)\ge s(r+1).
\]

We construct a coloring on sr+s-1 points avoiding both targets. For s=3 this recovers the earlier five-point theorem. The new content is arbitrary s and a padding construction strengthening sr+3 to sr+s.

## 2. Five-point template

Let P=Z/5Z. For disjoint traces a,b contained in P:

- empty-empty and large-large edges are red, and empty-large edges blue, where large means size at least two;
- singleton-singleton edges are red for adjacent points in the five-cycle, blue otherwise;
- singleton-empty edges are red;
- singleton {y} versus large b is red exactly when y-1 belongs to b.

The empty-empty template value is not a loop in the Kneser graph: distinct disjoint vertices can have the same empty trace.

### Four properties

**P1.** Three disjoint traces covering at least three points cannot form a monochromatic triangle.

Split by the number of singleton traces. With none, there must be both an empty and a large trace (three large traces cannot fit in five points); a same-type edge is red and a cross-type edge blue. With one singleton, either the other traces are empty and large, immediately giving both colors, or they are two pairs partitioning the four other points; exactly one contains the predecessor. With two singletons, the third trace is large. If the points are adjacent, one predecessor is the other singleton point, forcing a blue edge to the large trace. If nonadjacent, their predecessors are distinct points in the three-point complement; the large trace contains at least one, forcing a red edge. Three singletons use the standard triangle-avoiding coloring of K5.

**P2.** The blue graph on disjoint traces is triangle-free without a coverage condition. Coverage at least three is P1. At coverage at most two, either two traces are empty, giving a red edge, or the traces are empty and two singletons, also giving a red edge.

**P3.** Three nonempty disjoint traces cannot form a red triangle, by P1.

**P4.** A trace red-adjacent to an empty trace has size at most one, directly from the rule.

## 3. Padding construction

Partition a ground set of size n=sr+s-1 into disjoint sets P,D,Y with

\[
|P|=5,\qquad |D|=s-3,\qquad |Y|=sr-3.
\]

These sizes are nonnegative for r>=1, s>=3. Call an r-set tagged when it meets D, and empty-trace when it avoids both D and P.

If neither endpoint is tagged, use the five-point trace coloring. If at least one endpoint is tagged, color the edge blue exactly when the other endpoint is empty-trace; otherwise color it red. In particular tagged-tagged edges are red.

### Blue triangle exclusion

With no tagged endpoint, P2 applies. A tagged endpoint in a blue triangle forces both other endpoints to be empty-trace. Their mutual edge is red, a contradiction.

### Red s-clique exclusion

Suppose s pairwise-disjoint r-sets form a red clique. At most s-3 can be tagged: select a distinct D-point from each. At most two can be untagged with nonempty P-trace, by P3. Since (s-3)+2=s-1, at least one clique vertex is empty-trace.

Red adjacency to this vertex excludes every tagged vertex. By P4 it also forces all P-traces to have size at most one. At most two are nonempty, by P3 again. Thus the union of the s sets avoids D and uses at most two points of P. It must use at least sr-2 points of Y, but |Y|=sr-3. Contradiction.

Equivalently, the union misses all s-3 padding points and at least three cycle points, hence at least s ground points, whereas its complement has only s-1 points. This is the counting form used in Lean.

## 4. General-target corollary

**Theorem B (written proof; not included in the current Lean theorem).** For r>=1 and s,t>=3,

\[
R_r^{KG}(s,t)\ge\max(s,t)r+s+t-3.
\]

First prove sr+s+t-3. Add a disjoint set E of t-3 points to the construction on sr+s-1 points. Color every edge incident to an r-set meeting E blue; retain the original coloring on vertices avoiding E.

A red s-clique cannot contain any vertex meeting E. A blue t-clique has at most t-3 vertices meeting E, by disjointness, so at least three avoid E; these would be a blue triangle in the old construction. Thus a good coloring exists on sr+s+t-4 points. Exchange colors and s,t for the maximum.

A Lean build proving Theorem A is not claimed to formalize this additional corollary.

## 5. Comparison with the primary source

Table 2 of arXiv:2510.25734v2 gives the source bounds below. The new column substitutes r=3 in Theorem A and uses color symmetry.

| Quantity | Source lower | This construction | Source upper |
|---|---:|---:|---:|
| R_3^KG(3,3) | 11 | 12 (earlier result) | 13 |
| R_3^KG(3,4) | 13 | 16 | 22 |
| R_3^KG(3,5) | 18 | 20 | 31 |
| R_3^KG(3,6) | 22 | 24 | 42 |

This compares a specific source version, not every possible later or unpublished result. The construction does not improve every parameter pair: for example, the source's R_2^KG(3,5)>=16 is stronger than the value 15 supplied here. Stronger existing bounds must be retained.

## 6. Verification and claim boundary

The Python verifier checks the five-point properties and all unordered disjoint trace families, permitting repeated empty traces, for s=3,...,8. Universal validity is supplied by the proof above, not by extrapolation from those tests.

The formal module KneserFivePoint.Asymmetric states the complete arbitrary-r, arbitrary-s coloring witness. Its compilation and axiom output must be checked before labeling it formally verified; merely adding the source file is insufficient. The module is explicitly included in the default Lake roots.

The theorem improves the additive term of a family of lower bounds. It does not change the leading coefficient s for fixed s and growing r, prove the diagonal matching upper bound, or establish the exact formula R_r^KG(3,3)=3r+3. Literature priority and independent expert review remain unconfirmed.
