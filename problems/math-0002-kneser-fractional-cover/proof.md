# The fractional \(5/2\)-cover number of \(KG(8,2)\) is three

**Status:** candidate new result, prepared 31 August 2026. The argument and Lean certificate have not yet undergone peer review. Gujgiczer–Marits–Ozeki, arXiv:2607.12353v1 (July 2026), explicitly listed the two-cover question as open.

## 1. Problem and answer

For a graph class \(\mathcal P\), let \(c_{\mathcal P}(G)\) be the least number of subgraphs from \(\mathcal P\) whose edge sets cover \(E(G)\). Put

\[
\mathcal C_{5/2}=\{H:\chi_f(H)\le 5/2\}.
\]

The open question was whether \(KG(8,2)\) can be covered by two members of \(\mathcal C_{5/2}\). Here the vertices of \(KG(8,2)\) are the 28 two-element subsets of \([8]\), and two vertices are adjacent when the corresponding pairs are disjoint.

## Main theorem

\[
\boxed{c_{\mathcal C_{5/2}}(KG(8,2))=3.}
\]

Therefore the answer to the two-cover question is **no**.

A stronger finite statement proved along the way is:

> In every red–blue coloring of \(E(KG(8,2))\) with no monochromatic triangle, at least one color graph has independence number at most 11.

Consequently, if \(\beta_2\) denotes the smallest fractional-chromatic threshold at which two covering graphs become possible, then

\[
\beta_2(KG(8,2))\ge \frac{28}{11}>\frac52.
\]

## 2. Upper bound: three bipartite graphs suffice

Color the vertex \(\{i,j\}\), with \(i<j\), by

\[
\kappa(\{i,j\})=
\begin{cases}
i,&i\le5,\\
6,&i\ge6.
\end{cases}
\]

This is a proper six-coloring. For colors 1 through 5, every pair in a color class contains the color label. The sixth class is
\(\{\{6,7\},\{6,8\},\{7,8\}\}\), whose members also intersect pairwise.

Assign the six colors distinct three-bit strings. For bit position \(t\), let \(H_t\) contain the edges whose endpoint color strings differ in bit \(t\). Each \(H_t\) is bipartite, using that bit as its bipartition. Every Kneser edge joins distinct colors, whose codewords differ in at least one bit, so every edge lies in some \(H_t\). Hence

\[
c_{\mathcal C_{5/2}}(KG(8,2))\le3.
\]

## 3. Lower bound: two graphs cannot suffice

Assume for contradiction that the Kneser edges are covered by two graphs \(R,B\) satisfying

\[
\chi_f(R),\chi_f(B)\le\frac52.
\]

Because fractional chromatic number does not increase on taking subgraphs, assign each covered edge to one of the two graphs; thus the cover may be treated as a red–blue edge partition.

### 3.1 Both color graphs are triangle-free

A triangle has fractional chromatic number 3. Therefore neither \(R\) nor \(B\) contains a triangle, so every one of the 420 triangles of \(KG(8,2)\) is non-monochromatic.

### 3.2 Each color graph has an independent 12-set

For every finite graph \(H\),

\[
\chi_f(H)\ge\frac{|V(H)|}{\alpha(H)}.
\]

Since \(|V(KG(8,2))|=28\),

\[
\alpha(R),\alpha(B)\ge
\left\lceil\frac{28}{5/2}\right\rceil=12.
\]

Choose a 12-set \(A\) independent in red and a 12-set \(C\) independent in blue. Every Kneser edge induced by \(A\) is blue; every Kneser edge induced by \(C\) is red.

Interpret the 28 Kneser vertices as the 28 edges of \(K_8\). A Kneser triangle is exactly a matching of three edges in \(K_8\). If \(A\) contained such a matching, its three Kneser edges would form a blue triangle. Thus the 12-edge graph \(A\subseteq E(K_8)\) has matching number at most two. The same holds for \(C\).

### 3.3 Structure lemma

**Lemma.** Every 12-edge graph \(F\) on eight vertices with \(\nu(F)\le2\) is contained in a 13-edge double star

\[
D_{xy}=\{e\in E(K_8):e\cap\{x,y\}\ne\varnothing\}.
\]

**Proof.** The Tutte–Berge formula gives a set \(S\subseteq V(F)\) such that

\[
o(F-S)-|S|\ge4.
\]

Write \(s=|S|\). Since \(o(F-S)\le8-s\), we have \(s\le2\).

If \(s=0\), at least four odd components partition eight vertices; convexity of \(\binom{x}{2}\) shows that at most \(\binom52=10\) edges are possible. If \(s=1\), the seven vertices outside \(S\) have at least five odd components, hence at most three internal edges, while at most seven edges meet \(S\); again there are at most ten edges. Both contradict \(|E(F)|=12\).

Thus \(s=2\). The six vertices of \(F-S\) form at least six odd components, so they are all isolated. Every edge of \(F\) meets \(S\), proving \(F\subseteq D_S\). ∎

Therefore \(A\) and \(C\) are each 12-element subsets of a double star.

### 3.4 Exact finite obstruction

It remains to rule out a red–blue coloring of the 210 Kneser edges satisfying all of the following:

1. all 420 Kneser triangles are non-monochromatic;
2. all Kneser edges induced by a 12-subset \(A\) of one double star are blue;
3. all Kneser edges induced by a 12-subset \(C\) of another double star are red.

The symmetric group \(S_8\) acts transitively on the 28 double-star cores. Relabeling the ground set therefore fixes the first core as \(\{0,1\}\) without restricting the second core or the edge coloring. The Lean theorem `core01_obstruction` checks precisely this universal fixed-core statement: both 12-sets and all 210 colors remain quantified variables, and the second double-star core remains an arbitrary 28-way choice.

The theorem `matchingFree12_is_doubleStar` independently checks the complete 28-bit classification used in the structure lemma. Together with the elementary relabeling argument, the Lean certificate proves the full finite obstruction.

This contradicts the sets \(A,C\), so two \(5/2\)-fractionally-colorable graphs do not suffice. Combining the lower and upper bounds proves

\[
c_{\mathcal C_{5/2}}(KG(8,2))=3.
\]

## 4. Further corollary

The cited paper constructs a two-graph \(5/2\)-fractional cover of \(KG(7,2)\). Restricting that construction handles every \(KG(n,2)\) with \(n\le7\). Conversely, \(KG(8,2)\) is an induced subgraph of \(KG(n,2)\) for every \(n\ge8\). Hence:

\[
KG(n,2)\text{ is coverable by two }5/2\text{-fractionally-colorable graphs}
\iff n\le7.
\]

## 5. Lean verification

The formal package uses Lean 4.33.1 and only Lean's standard library.

- `BV28 := BitVec 28` represents a family of edges of \(K_8\).
- `BV210 := BitVec 210` represents a red–blue coloring of \(E(KG(8,2))\).
- `matchingFree` expands all 420 three-edge matchings.
- `triangleFree` expands all 420 Kneser triangles as not-all-equal constraints.
- `blueOn` and `redOn` impose the two monochromatic induced-subgraph conditions.
- `matchingFree12_is_doubleStar` verifies the 12-edge structure classification.
- `core01_obstruction` verifies the universal transitivity-reduced coloring obstruction.

Run:

```bash
cd formal
python generate_lean.py
python finalize_lean.py
lake build
```

The generated source has SHA-256

```text
143b3fdcb75423e419eb10d1ce7c8f9fbc700f22a0cd4d55d65e27950c0667e9
```

### Trust boundary

The proofs use Lean's `bv_decide`. It bit-blasts the finite propositions, invokes CaDiCaL, and checks the resulting LRAT refutations with a checker proved sound in Lean. In Lean 4.33.1 the final reflective computation is native, so the Lean compiler/native evaluator is part of the trusted computing base and a generated native-computation axiom appears in `#print axioms`. There are no `sorry`, `admit`, or hand-written axioms in the source. This is a standard Lean machine certificate, but not a compiler-independent kernel-only certificate.

## 6. Verification scope and research status

Lean verifies the delicate exhaustive finite obstruction and the matching-family classification. The outer reduction uses standard graph-theoretic facts—the fractional chromatic bound \(\chi_f\ge |V|/\alpha\), monotonicity, Tutte–Berge, and the explicit three-bit construction—and is written above as a human proof rather than encoded in a general graph/fractional-coloring library.

This should be treated as a candidate resolution until independent experts reproduce the build, audit the reduction and enumeration, and confirm literature novelty.
