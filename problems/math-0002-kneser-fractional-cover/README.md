# Two-cover fractional threshold of \(KG(8,2)\)

**ID:** `math-0002`  
**Field:** graph theory / fractional coloring / Kneser graphs  
**Original source:** Gujgiczer–Marits–Ozeki, arXiv:2607.12353v1 (July 2026)  
**Problem status:** `proposed-proof`  
**Formal verification:** `partial-theorem-verified`  
**Novelty:** `search-incomplete`  
**External review:** `none`

## Source problem

For a graph \(G\), define its two-cover fractional threshold by

\[
\tau_2(G)=
\min_{E(G)\subseteq E(H_1)\cup E(H_2)}
\max\{\chi_f(H_1),\chi_f(H_2)\}.
\]

Because deleting edges cannot increase fractional chromatic number, the minimum
may equivalently be taken over red–blue partitions of \(E(G)\).

The source paper asks whether \(KG(8,2)\) can be covered by two graphs of
fractional chromatic number at most \(5/2\). It also asks for the exact smallest
fractional threshold permitting a two-cover. The 28 vertices of \(KG(8,2)\)
are the two-element subsets of an eight-element set; two vertices are adjacent
when the corresponding pairs are disjoint.

## Results under review

The original candidate resolution remains:

\[
\boxed{c_{\{\chi_f\le 5/2\}}(KG(8,2))=3.}
\]

The strengthened candidate theorem is:

> In every red–blue coloring of \(E(KG(8,2))\) with no monochromatic triangle,
> at least one color graph has independence number at most \(10\).

It implies the quantitative bound

\[
\boxed{\frac{14}{5}\le \tau_2(KG(8,2))\le 3.}
\]

Indeed, if a color graph contains a triangle then its fractional chromatic
number is at least \(3\). Otherwise both color graphs are triangle-free, the
strengthened finite theorem gives \(\alpha\le10\) in one color, and
\(\chi_f(H)\ge |V(H)|/\alpha(H)\) yields
\(\chi_f(H)\ge28/10=14/5\).

The upper bound \(3\) follows from an explicit proper six-coloring of
\(KG(8,2)\): encode its six colors by six distinct pairs in \([3]^2\), and for
each coordinate take the graph formed by edges whose endpoint codes differ in
that coordinate. The two graphs are 3-partite and cover every Kneser edge.

Thus the exact-threshold problem is reduced to the remaining interval

\[
\frac{14}{5}\le\tau_2(KG(8,2))\le3.
\]

## Why the strengthening is structural

Identify the vertices of \(KG(8,2)\) with the 28 edges of \(K_8\). A Kneser
triangle is then exactly a three-edge matching in \(K_8\).

If both color graphs had independent sets of size 11, those sets would become
11-edge families in \(K_8\), each with matching number at most two. A
Tutte–Berge argument shows that every such family is contained in a 13-edge
double star

\[
D_{xy}=\{e\in E(K_8):e\cap\{x,y\}\ne\varnothing\}.
\]

After mapping the first double-star core to \(\{0,1\}\), any 11-subset is
obtained by deleting two of its 13 edges. Under the stabilizer of the unordered
core, the deletion pair has exactly four orbit types:

1. the center edge and one spoke;
2. two spokes at the same center;
3. opposite spokes with the same leaf;
4. opposite spokes with distinct leaves.

The remaining statement is therefore a finite four-orbit obstruction, not an
unstructured search over all red–blue colorings.

See [`proof.md`](proof.md) for the complete written reduction.

## Machine verification

Lean 4.33.1 checks the research-critical finite propositions:

- `matchingFree12_is_doubleStar`: the structure statement used by the original
  \(5/2\) proof;
- `matchingFree11_is_doubleStar`: every 11-edge family of \(K_8\) with no
  three-edge matching is contained in a double star;
- `core01_obstruction`: the original 12-set obstruction;
- `alpha10_center_spoke_obstruction`;
- `alpha10_same_center_obstruction`;
- `alpha10_same_leaf_obstruction`;
- `alpha10_distinct_leaves_obstruction`.

The four `alpha10_*` theorems fix one representative first 11-set, while the
second 11-set, its double-star core, and all 210 edge colors remain universally
quantified.

A separate standard-library C++ program independently constructs
\(KG(8,2)\), checks the four deletion-pair orbit counts, and solves all

\[
4\cdot28\cdot\binom{13}{2}=8736
\]

symmetry-reduced instances with an exact branch-and-propagate NAE-3 solver.
It includes satisfiable and unsatisfiable self-tests and fails closed if it
finds a counterexample or unexpected enumeration total.

## Formalization boundary

The Lean certificate verifies the matching-family classifications and the five
finite coloring obstructions. The following bridges remain written rather than
formalized end to end:

- fractional-chromatic monotonicity and \(\chi_f(H)\ge |V(H)|/\alpha(H)\);
- reduction from an overlapping two-cover to an edge partition;
- the Tutte–Berge derivation of the double-star structure;
- the \(S_8\) core reduction and four stabilizer-orbit classification;
- the explicit two-graph 3-partite upper-bound construction.

The finite proofs use Lean's `bv_decide`. In Lean 4.33.1, native reflective
computation remains part of the trusted computing base. There are no `sorry`,
`admit`, or hand-written `axiom` declarations.

## Reproduce

```bash
cd problems/math-0002-kneser-fractional-cover

g++ -O3 -std=c++20 -Wall -Wextra -Werror -pedantic \
  experiments/verify_alpha10.cpp -o /tmp/verify_alpha10
/tmp/verify_alpha10

cd formal
python generate_lean.py
python finalize_lean.py
lake build
```

Pinned formal environment:

- Lean 4.33.1;
- Lake 5.0.0;
- generated `KneserCover.lean` SHA-256:
  `e21c37179741f8ddcea0cfc96911da4e50f8c336dc4aa72798acaa5f3a0e6cdb`.

The CI run and trust-boundary details are recorded in
[`verification-record.md`](verification-record.md).

## Novelty and claim boundary

The July 2026 source explicitly poses the \(5/2\) two-cover question and the
exact-threshold problem. A comprehensive post-publication citation and
literature audit has not yet been completed, and the source authors have not
yet confirmed priority. Machine verification establishes finite logical
claims under the documented trust model; it does not establish novelty,
correct translation to the literature problem, or peer acceptance.

## Next gates

1. Obtain independent graph-theory review of the reduction and orbit argument.
2. Reproduce both the Lean and C++ checks on an independent machine.
3. Complete the literature audit and contact the source authors.
4. Determine whether the lower bound \(14/5\) is sharp or can be raised to the
   exact value \(3\) using rational LP dual certificates.
5. Formalize the outer graph/fractional-coloring bridge end to end in Lean.
