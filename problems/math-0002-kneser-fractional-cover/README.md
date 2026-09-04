# Fractional covers of \(KG(8,2)\)

**ID:** `math-0002`  
**Field:** graph theory / fractional coloring / Kneser graphs  
**Original source:** Gujgiczer–Marits–Ozeki, arXiv:2607.12353v1 (14 July 2026)  
**Problem status:** `proposed-proof + new-bound`  
**Formal verification:** `finite-core-theorem-verified`  
**Novelty:** `no-prior-result-found; author confirmation pending`  
**External review:** `none`

## Source questions

For \(\beta\ge2\), let

\[
\mathcal C_\beta=\{H:\chi_f(H)\le\beta\},
\]

and let \(c_{\mathcal C_\beta}(G)\) be the least number of members of this
class whose edge sets cover \(E(G)\). The source paper asks:

1. whether \(KG(8,2)\) can be covered by two members of
   \(\mathcal C_{5/2}\); and
2. for the smallest threshold

   \[
   \beta_2(KG(8,2)):=
   \min\{\beta:c_{\mathcal C_\beta}(KG(8,2))\le2\}.
   \]

The paper records only \(2<\beta_2(KG(8,2))\le3\).

## Results

The proposed answer to the first question is exact:

\[
\boxed{c_{\mathcal C_{5/2}}(KG(8,2))=3.}
\]

The strengthened finite theorem also gives a new quantitative answer to the
second question:

\[
\boxed{\frac{14}{5}\le\beta_2(KG(8,2))\le3.}
\]

The lower bound follows from this Ramsey-type statement:

> Every red-blue coloring of \(E(KG(8,2))\) either contains a monochromatic
> triangle or has a color graph with independence number at most ten.

Indeed, a monochromatic triangle has fractional chromatic number three. In
the other case, the standard inequality
\(\chi_f(H)\ge |V(H)|/\alpha(H)\) gives

\[
\chi_f(H)\ge\frac{28}{10}=\frac{14}{5}.
\]

This improves the earlier internal bound \(28/11\) and rules out every
threshold strictly below \(14/5\), not just \(5/2\).

## Proof architecture

The 28 vertices of \(KG(8,2)\) are the edges of \(K_8\), with adjacency given
by disjointness.

1. A hypothetical two-cover may be reduced to a red-blue edge partition.
2. If both color graphs are triangle-free and both have independent
   11-sets, those sets become 11-edge subgraphs of \(K_8\) with matching
   number at most two.
3. Every 11-edge graph on eight vertices with matching number at most two is
   contained in a 13-edge double star. This follows from Tutte-Berge; it is
   also verified exhaustively in Lean.
4. The remaining finite obstruction—oppositely monochromatic 11-subsets of
   double stars in a triangle-free coloring—is impossible. Lean verifies the
   complete fixed-core statement, and an independent C++ DPLL verifier checks
   all 170,352 candidate pairs.
5. Three bipartite graphs cover \(KG(8,2)\): use an explicit proper
   six-coloring, assign the six colors distinct three-bit strings, and take
   one cut graph per bit.

See [`proof.md`](proof.md) for the complete written argument.

## Formal and independent verification

The generated Lean 4 file proves:

- `matchingFree11_is_doubleStar`; and
- `core01_obstruction_11`.

The independent verifier enumerates all
\(\binom{13}{11}\cdot28\binom{13}{11}=170{,}352\) fixed-core candidate pairs
and performs a complete not-all-equal SAT search on the 420 triangles of
\(KG(8,2)\). It returns `UNSAT` after 40,027,816 deterministic DPLL nodes.

Reproduce with:

```bash
cd problems/math-0002-kneser-fractional-cover

g++ -O3 -std=c++20 verification/nae_independence_obstruction.cpp \
  -o /tmp/nae_independence_obstruction
/tmp/nae_independence_obstruction

cd formal
python generate_lean.py
lake build
```

Pinned environment:

- Lean 4.33.1;
- Lake 5.0.0;
- generated `KneserCover.lean` SHA-256:
  `2a51c43c1f9ec8e0f2bbfa76cf7333dc1dcc53ded85a67ff5212a863647b68a9`.

The finite Lean theorems use native `bv_decide`; the compiler/native evaluator
is therefore part of the documented trust boundary. There are no `sorry`,
`admit`, or hand-written `axiom` declarations.

## Formalization boundary

Lean verifies the two delicate finite claims. The outer bridge remains a
human proof: monotonicity under edge deletion, the fractional bound
\(\chi_f\ge |V|/\alpha\), the Tutte-Berge derivation, the relabeling of the
first double-star core, and the explicit three-graph construction have not yet
all been encoded in a general graph library.

## Additional corollary

The source paper gives a two-graph \(5/2\)-fractional cover of \(KG(7,2)\).
Together with induced-subgraph monotonicity, the proposed result yields

\[
KG(n,2)\text{ has a two-graph }5/2\text{-fractional cover}
\iff n\le7.
\]

## Ongoing exact-threshold search

An exact SAT experiment is testing whether two explicit \(14/5\)-colorings
already suffice, by searching for two maps to \(KG(14,5)\). A positive result
would prove \(\beta_2=14/5\). A negative result at this denominator would not
settle equality, because a \(14/5\)-fractional coloring may require a scaled
target \(KG(14t,5t)\) with \(t>1\).

## Remaining gates

1. Independent graph-theory review of the outer reduction.
2. Comprehensive citation-index search and confirmation from the source
   authors.
3. End-to-end Lean formalization of the graph/fractional-coloring bridge.
4. Resolve, or further narrow, the exact interval \([14/5,3]\).
5. Prepare a short manuscript only after the first three gates are recorded.
