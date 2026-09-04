# A sharp triangle-free Ramsey obstruction in \(KG(8,2)\)

**Status:** candidate new result, strengthened September 4, 2026. The proof and
formal certificate have not yet undergone independent expert review. The
source paper Gujgiczer–Marits–Ozeki, arXiv:2607.12353v1 (July 2026), explicitly
asks whether two \(5/2\)-fractionally-colorable graphs cover \(KG(8,2)\) and,
more generally, asks for the least possible fractional threshold.

## 1. Definitions and results

For a graph class \(\mathcal P\), let \(c_{\mathcal P}(G)\) be the least number
of subgraphs from \(\mathcal P\) whose edge sets cover \(E(G)\). Put

\[
\mathcal C_\beta=\{H:\chi_f(H)\le\beta\}.
\]

The vertices of \(KG(8,2)\) are the 28 two-element subsets of \([8]\), with
adjacency when the corresponding pairs are disjoint.

### Theorem A: answer to the \(5/2\) question

\[
\boxed{c_{\mathcal C_{5/2}}(KG(8,2))=3.}
\]

### Theorem B: sharp finite Ramsey parameter

For every red-blue partition

\[
E(KG(8,2))=E(R)\sqcup E(B)
\]

in which both \(R\) and \(B\) are triangle-free,

\[
\min\{\alpha(R),\alpha(B)\}\le10.
\]

Moreover, equality is attainable. Equivalently,

\[
\boxed{
\max_{\substack{E(KG(8,2))=E(R)\sqcup E(B)\\R,B\text{ triangle-free}}}
\min\{\alpha(R),\alpha(B)\}=10.
}
\]

### Corollary: quantitative threshold interval

Let \(\beta_2(KG(8,2))\) be the least rational \(\beta\) for which two graphs
of fractional chromatic number at most \(\beta\) cover \(KG(8,2)\). Then

\[
\boxed{\frac{14}{5}\le\beta_2(KG(8,2))\le3.}
\]

The lower endpoint strengthens the earlier \(28/11\) bound. The exact value
inside this interval remains open.

## 2. Two elementary upper bounds

### 2.1 Three bipartite covering graphs

Color a vertex \(\{i,j\}\), with \(i<j\), by

\[
\kappa(\{i,j\})=
\begin{cases}
i,&i\le5,\\
6,&i\ge6.
\end{cases}
\]

This is a proper six-coloring. For colors 1 through 5, every pair in a color
class contains the color label. The sixth class is
\(\{\{6,7\},\{6,8\},\{7,8\}\}\), whose members also intersect pairwise.

Assign the six colors distinct three-bit strings. For bit position \(t\), let
\(H_t\) contain the edges whose endpoint strings differ in bit \(t\). Each
\(H_t\) is bipartite, and every Kneser edge lies in at least one \(H_t\).
Thus three members of \(\mathcal C_{5/2}\) suffice.

### 2.2 Two three-colorable covering graphs

Map the six proper colors injectively into \([3]\times[3]\). Let \(G_1\)
contain every Kneser edge whose endpoint colors differ in the first coordinate,
and define \(G_2\) analogously using the second coordinate. Each \(G_i\) is
3-colorable. Distinct code pairs differ in at least one coordinate, so
\(G_1\cup G_2\) covers every Kneser edge. Therefore

\[
\beta_2(KG(8,2))\le3.
\]

## 3. The 11-set obstruction

Assume that \(R\) and \(B\) form a triangle-free red-blue partition and that
both have an independent set of size 11. Choose

\[
A\subseteq V(KG(8,2)),\quad |A|=11,\quad A\text{ independent in }R,
\]

and

\[
C\subseteq V(KG(8,2)),\quad |C|=11,\quad C\text{ independent in }B.
\]

Every Kneser edge induced by \(A\) is blue, while every Kneser edge induced by
\(C\) is red.

### 3.1 Matching interpretation

Identify the 28 Kneser vertices with the 28 edges of \(K_8\). A triangle in
\(KG(8,2)\) is exactly a matching of three edges of \(K_8\).

If the 11-edge family \(A\) contained a three-edge matching, the corresponding
three Kneser vertices would induce a blue triangle, contradicting that \(B\)
is triangle-free. Hence \(\nu(A)\le2\). Similarly, \(\nu(C)\le2\).

### 3.2 Structure lemma

**Lemma.** Every graph \(F\) on eight vertices with at least 11 edges and
\(\nu(F)\le2\) is contained in a 13-edge double star

\[
D_{xy}=\{e\in E(K_8):e\cap\{x,y\}\ne\varnothing\}.
\]

**Proof.** The Tutte-Berge formula gives a set \(S\subseteq V(F)\) such that

\[
o(F-S)-|S|=8-2\nu(F)\ge4.
\]

Write \(s=|S|\). Since \(o(F-S)\le8-s\), we obtain \(s\le2\).

If \(s=0\), the graph has at least four odd components. Among all partitions
of eight vertices with at least four odd parts, the sum of the possible
within-component edges is at most

\[
\binom52=10,
\]

attained by component sizes \(5,1,1,1\).

If \(s=1\), the seven vertices outside \(S\) have at least five odd
components. They span at most three edges, attained by component sizes
\(3,1,1,1,1\), while at most seven edges meet \(S\). Again
\(|E(F)|\le10\).

Both cases contradict \(|E(F)|\ge11\). Therefore \(s=2\). Now \(F-S\) has
six vertices and at least six odd components, so every component is a singleton.
No edge has both endpoints outside \(S\); hence every edge meets the two-vertex
set \(S\), and \(F\subseteq D_S\). ∎

Thus both \(A\) and \(C\) are 11-subsets of double stars.

### 3.3 Exact finite obstruction

It remains to rule out a coloring of the 210 Kneser edges satisfying:

1. every one of the 420 Kneser triangles is non-monochromatic;
2. all Kneser edges induced by an 11-subset \(A\) of one double star are blue;
3. all Kneser edges induced by an 11-subset \(C\) of another double star are red.

The group \(S_8\) is transitive on the 28 double-star cores, so the first core
can be relabeled to \(\{0,1\}\). The Lean theorem `core01_obstruction11`
checks the resulting universal statement: the first 11-set, the second core,
the second 11-set, and all 210 colors remain quantified variables.

The separate Lean theorem `matchingFree11_is_doubleStar` checks the complete
28-bit matching-family classification. A standalone C++ implementation
independently reconstructs the NAE-3-SAT instances and exhausts all four
stabilizer orbits of the first 11-set against all 2184 possible second sets.
Both verifiers return UNSAT.

This contradiction proves Theorem B's upper bound
\(\min\{\alpha(R),\alpha(B)\}\le10\).

## 4. Sharpness of the finite theorem

For completeness, the formal package contains an explicit triangle-free
red-blue coloring and two independent 10-sets. Vertices are indexed by the
lexicographic list of pairs from \(\{0,\ldots,7\}\); Kneser edges are then
indexed lexicographically.

The red-independent 10-set, written as edges of \(K_8\), is

\[
\{05,02,03,67,06,26,16,56,36,46\},
\]

and the blue-independent 10-set is

\[
\{17,34,46,67,07,24,45,47,27,57\}.
\]

The 210 coloring bits are stored in `formal/generate_lean.py`. The theorem
`ten_set_sharpness_witness` checks that:

- both displayed sets have cardinality 10;
- every Kneser edge induced by the first set is blue;
- every Kneser edge induced by the second set is red;
- all 420 Kneser triangles are non-monochromatic.

Hence both color graphs have independence number at least 10. Combined with
the 11-set obstruction, this proves equality in Theorem B.

## 5. Fractional-cover consequences

Consider any two covering graphs \(H_1,H_2\) with
\(\chi_f(H_i)<3\). Intersect them with \(KG(8,2)\) and assign each covered edge
to one graph, obtaining a triangle-free red-blue partition \(R,B\) with
\(R\subseteq H_1\) and \(B\subseteq H_2\).

Theorem B gives, after possibly swapping colors, \(\alpha(R)\le10\). The
standard fractional bound yields

\[
\chi_f(R)\ge\frac{|V(R)|}{\alpha(R)}\ge\frac{28}{10}=\frac{14}{5}.
\]

Monotonicity under taking subgraphs then gives
\(\chi_f(H_1)\ge\chi_f(R)\ge14/5\). Therefore every two-cover below 3 has one
member of fractional chromatic number at least \(14/5\), proving the lower
endpoint of the interval.

In particular, two members of \(\mathcal C_{5/2}\) cannot cover. Together with
the three-bipartite-graph construction, this proves Theorem A.

The source paper constructs a two-graph \(5/2\)-fractional cover of
\(KG(7,2)\). Restriction handles all \(n\le7\), while \(KG(8,2)\) is an induced
subgraph of \(KG(n,2)\) for every \(n\ge8\). Consequently,

\[
KG(n,2)\text{ is coverable by two }5/2\text{-fractionally-colorable graphs}
\iff n\le7.
\]

## 6. Verification and trust boundary

The formal package uses Lean 4.33.1 and its standard bit-vector decision
procedure.

- `BV28` represents a family of edges of \(K_8\).
- `BV210` represents a red-blue coloring of \(E(KG(8,2))\).
- `matchingFree` expands all 420 three-edge matchings.
- `triangleFree` expands all 420 Kneser triangles as NAE constraints.
- `blueOn` and `redOn` impose the two monochromatic induced-subgraph conditions.
- `matchingFree11_is_doubleStar` proves the structure classification.
- `core01_obstruction11` proves the universal finite obstruction.
- `ten_set_sharpness_witness` verifies the concrete lower-bound coloring.

The proofs use `bv_decide`, which bit-blasts the propositions, invokes CaDiCaL,
and checks reconstructed LRAT evidence. Lean 4.33.1 uses native reflective
computation in this process, so the Lean compiler/native evaluator is part of
the documented trust boundary. There are no `sorry`, `admit`, or hand-written
axioms.

The outer reduction uses standard graph-theoretic facts and remains a written
proof rather than an end-to-end formalization in a general fractional-coloring
library. The result therefore remains a candidate until independent experts
audit the reduction, reproduce the checks, and confirm novelty.
