# Fractional-cover threshold and a sharp Ramsey obstruction for \(KG(8,2)\)

**ID:** `math-0002`  
**Field:** graph theory / fractional coloring / Kneser graphs  
**Original source:** Gujgiczer–Marits–Ozeki, arXiv:2607.12353v1 (July 2026)  
**Problem status:** `proposed-proof`  
**Formal verification:** `partial-theorem-verified`  
**Novelty:** `search-incomplete`  
**External review:** `none`

## Original questions

Let

\[
\mathcal C_\beta=\{H:\chi_f(H)\le \beta\},
\]

and let \(c_{\mathcal C_\beta}(G)\) be the least number of members of this
class whose edge sets cover \(E(G)\). The source paper asks:

1. can \(KG(8,2)\) be covered by two graphs in \(\mathcal C_{5/2}\)?
2. what is the smallest rational \(\beta\) for which a two-graph cover exists?

The 28 vertices of \(KG(8,2)\) are the two-element subsets of an eight-element
set; two vertices are adjacent when the corresponding pairs are disjoint.

## Candidate results

### The original \(5/2\) question

\[
\boxed{c_{\mathcal C_{5/2}}(KG(8,2))=3.}
\]

Thus the proposed answer to the first question is **no**. Combined with the
source paper's construction for \(KG(7,2)\), this gives

\[
KG(n,2)\text{ has a two-graph }5/2\text{-fractional cover}
\iff n\le 7.
\]

### A sharper Ramsey theorem

For a triangle-free red-blue edge coloring of \(KG(8,2)\), let \(R\) and
\(B\) be the two color graphs. The strengthened finite result is

\[
\boxed{
\max_{\substack{E(KG(8,2))=E(R)\sqcup E(B)\\R,B\text{ triangle-free}}}
\min\{\alpha(R),\alpha(B)\}=10.
}
\]

The upper bound is the 11-set obstruction: every such coloring has
\(\alpha(R)\le10\) or \(\alpha(B)\le10\). The lower bound is an explicit
coloring with a 10-vertex independent set in each color, checked in Lean.

Consequently, if \(\beta_2(KG(8,2))\) denotes the smallest fractional-chromatic
threshold at which two covering graphs become possible, then

\[
\boxed{\frac{14}{5}\le \beta_2(KG(8,2))\le3.}
\]

The lower bound follows from \(\chi_f(H)\ge |V(H)|/\alpha(H)\); the upper bound
comes from a proper six-coloring and two three-colorable covering graphs.
This narrows the source paper's quantitative open question, but does not yet
determine its exact answer.

## Proof architecture

A hypothetical two-cover can be reduced to a red-blue edge partition. If both
covering graphs have fractional chromatic number below 3, both color graphs are
triangle-free because \(\chi_f(K_3)=3\).

Suppose both color graphs had independent sets of size 11. Viewing the 28
Kneser vertices as the edges of \(K_8\), each independent 11-set becomes an
11-edge family with matching number at most two: a three-edge matching would
create a monochromatic Kneser triangle in the opposite color.

A Tutte-Berge argument shows that every 11-edge graph on eight vertices with
matching number at most two is contained in a 13-edge double star

\[
D_{xy}=\{e\in E(K_8):e\cap\{x,y\}\ne\varnothing\}.
\]

The remaining finite obstruction rules out two oppositely monochromatic
11-subsets of double stars in a triangle-free coloring of all 210 Kneser
edges. The first double-star core is fixed to \(\{0,1\}\) using the transitive
\(S_8\)-action; the first set, second core, second set, and all 210 colors
remain universally quantified in the Lean theorem.

See [`proof.md`](proof.md) for the complete written argument.

## Independent verification

Two independently implemented exact checks support the finite core:

- Lean bit-blasts the universal statements and verifies SAT refutations;
- a standalone C++ NAE-3-SAT/DPLL checker reconstructs the graph, verifies the
  stabilizer-orbit decomposition, and exhausts all representative pairs.

The C++ checker verifies:

- 28 Kneser vertices;
- 210 Kneser edges;
- 420 triangle constraints;
- 78 possible 11-subsets of a fixed double star;
- four stabilizer orbits of sizes \(6,12,30,30\);
- 2184 distinct second-set candidates;
- 8736 representative set pairs.

See [`computations/README.md`](computations/README.md).

## Lean formalization

Lean verifies the following delicate finite statements:

- `matchingFree11_is_doubleStar`: every matching-free 11-subset of the 28
  edges of \(K_8\) is contained in a double star;
- `core01_obstruction11`: after fixing one core by symmetry, no choices of two
  opposite 11-sets and the 210 edge colors satisfy all constraints;
- `ten_set_sharpness_witness`: an explicit triangle-free coloring has a
  10-vertex independent set in each color.

The outer bridge is currently human-checked rather than formalized end to end.
It includes fractional-chromatic monotonicity, the inequality
\(\chi_f(H)\ge |V(H)|/\alpha(H)\), conversion of an edge cover to a partition,
Tutte-Berge, the symmetry reduction, and the upper-bound constructions.

The finite proofs use Lean's `bv_decide`; no `sorry`, `admit`, or hand-written
`axiom` declarations occur in the generated source.

## Reproduce

```bash
cd problems/math-0002-kneser-fractional-cover/computations
g++ -O3 -std=c++20 -Wall -Wextra -pedantic \
  verify_11_obstruction.cpp -o verify_11_obstruction
./verify_11_obstruction

cd ../formal
python generate_lean.py
python finalize_lean.py
lake build
```

Pinned environment:

- Lean 4.33.1
- Lake 5.0.0
- generated `KneserCover.lean` SHA-256:
  `1f3421d0b1e03d35a588faafe0868ffac34254cce0a8e1cc93c9777cbd7215f5`

The CI and trust-boundary details are recorded in
[`verification-record.md`](verification-record.md).

## Novelty boundary

The July 2026 source explicitly states both the \(5/2\) question and the exact
threshold question as open. Searches performed through September 4, 2026 have
not located a later resolution or the sharp independence theorem above. The
source authors have not yet confirmed priority. See
[`references/NOVELTY.md`](references/NOVELTY.md).

## Remaining risks and next gates

The main remaining risks are a mismatch between the finite encoding and the
intended graph-theoretic reduction, an overlooked prior result, or an error in
the human outer bridge. Green CI certifies the stated finite theorems under the
documented trust model; it does not certify novelty.

The next mathematical target is the exact value of \(\beta_2(KG(8,2))\):
either construct a two-cover at \(14/5\), improve the lower bound beyond
\(14/5\), or prove the upper endpoint 3 is necessary. In parallel, the result
needs independent graph-theory review, end-to-end formalization, and author
confirmation before manuscript submission.
