# Fractional covers of \(KG(8,2)\): a \(14/5\) lower bound

**Status:** candidate new result, strengthened 4 September 2026. The finite
core has been checked in Lean and by an independent exhaustive solver. The
outer reduction has not yet undergone external peer review.

## 1. Definitions and statements

For a graph class \(\mathcal P\), let \(c_{\mathcal P}(G)\) be the least
number of members of \(\mathcal P\) whose edge sets cover \(E(G)\). For
\(\beta\ge2\), put

\[
\mathcal C_\beta=\{H:\chi_f(H)\le\beta\}.
\]

The vertices of \(KG(8,2)\) are the 28 two-element subsets of \([8]\), and
two vertices are adjacent exactly when the corresponding pairs are disjoint.

The source paper asks whether two members of \(\mathcal C_{5/2}\) cover
\(KG(8,2)\), and also asks for the least threshold

\[
\beta_2(KG(8,2))=
\min\{\beta:c_{\mathcal C_\beta}(KG(8,2))\le2\}.
\]

We propose the following two results.

### Theorem A

\[
\boxed{c_{\mathcal C_{5/2}}(KG(8,2))=3.}
\]

### Theorem B

\[
\boxed{\frac{14}{5}\le\beta_2(KG(8,2))\le3.}
\]

The central finite statement is stronger than what is needed merely to exclude
\(5/2\).

### Finite Ramsey statement

For every red-blue coloring of \(E(KG(8,2))\), at least one of the following
holds:

1. there is a monochromatic triangle; or
2. one of the two color graphs has independence number at most ten.

Theorem B follows immediately from this statement. A monochromatic triangle
forces fractional chromatic number at least three. Otherwise, for the color
graph \(H\) with \(\alpha(H)\le10\),

\[
\chi_f(H)\ge\frac{|V(H)|}{\alpha(H)}
\ge\frac{28}{10}=\frac{14}{5}.
\]

## 2. Three bipartite graphs suffice

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

\[
\{\{6,7\},\{6,8\},\{7,8\}\},
\]

whose members also intersect pairwise.

Assign the six colors distinct three-bit strings. For each bit position
\(t\), let \(H_t\) contain every Kneser edge whose endpoint codewords differ
in bit \(t\). Each \(H_t\) is bipartite, using that bit as the bipartition.
Every Kneser edge joins different proper colors, whose codewords differ in at
least one position. Therefore

\[
E(KG(8,2))=E(H_1)\cup E(H_2)\cup E(H_3),
\]

and each \(\chi_f(H_t)\le2\). Hence three members of every
\(\mathcal C_\beta\) with \(\beta\ge2\) suffice; in particular,

\[
c_{\mathcal C_{5/2}}(KG(8,2))\le3,
\qquad
\beta_2(KG(8,2))\le3.
\]

## 3. Reduction of a two-cover to a coloring

Suppose two graphs \(R\) and \(B\) cover all Kneser edges. If an edge belongs
to both, assign it arbitrarily to one of them, and delete it from the other.
Fractional chromatic number is monotone under taking subgraphs, so it is enough
to analyze red-blue **partitions** of \(E(KG(8,2))\).

If either color graph contains a triangle, then that graph contains \(K_3\)
and has fractional chromatic number at least three. We may therefore restrict
the hard case to colorings with no monochromatic triangle.

Assume, toward the finite Ramsey statement, that both color graphs have an
independent set of size eleven. Let

- \(A\) be an 11-set independent in red; and
- \(C\) be an 11-set independent in blue.

Every Kneser edge induced by \(A\) is blue, and every Kneser edge induced by
\(C\) is red.

Interpret the 28 Kneser vertices as the 28 edges of \(K_8\). A triangle in
\(KG(8,2)\) is exactly a matching of three edges in \(K_8\). If \(A\)
contained a three-edge matching, its three Kneser vertices would induce a blue
triangle. Thus the 11-edge graph \(A\subseteq E(K_8)\) has matching number at
most two. The same is true of \(C\).

## 4. Structure of large matching-free families

For distinct \(x,y\in[8]\), define the 13-edge double star

\[
D_{xy}=\{e\in E(K_8):e\cap\{x,y\}\ne\varnothing\}.
\]

### Lemma

Every graph \(F\) on eight vertices with

\[
|E(F)|\ge11
\qquad\text{and}\qquad
\nu(F)\le2
\]

is contained in some double star \(D_{xy}\).

### Proof

By the Tutte-Berge formula, there is a set \(S\subseteq V(F)\) such that

\[
o(F-S)-|S|=8-2\nu(F)\ge4,
\]

where \(o(F-S)\) is the number of odd components of \(F-S\). Write
\(s=|S|\). Since \(o(F-S)\le8-s\),

\[
8-s-s\ge4,
\]

so \(s\le2\).

If \(s=0\), at least four odd components partition the eight vertices. The
maximum possible number of internal edges is obtained by the partition
\(5+1+1+1\), giving at most

\[
\binom52=10
\]

edges. This contradicts \(|E(F)|\ge11\).

If \(s=1\), the seven vertices outside \(S\) contain at least five odd
components. At most three edges lie entirely outside \(S\), attained by the
component-size partition \(3+1+1+1+1\). At most seven edges meet the one
vertex of \(S\). Thus again \(|E(F)|\le10\), a contradiction.

Therefore \(s=2\). The six vertices of \(F-S\) form at least six odd
components, so every one is an isolated singleton. Every edge of \(F\) meets
\(S\), and hence

\[
F\subseteq D_S.
\]

This proves the lemma. \(\square\)

Applying the lemma to \(A\) and \(C\), both are 11-element subsets of double
stars.

## 5. The exact finite obstruction

It remains to rule out a red-blue coloring of the 210 edges of \(KG(8,2)\)
satisfying all of the following:

1. all 420 Kneser triangles are non-monochromatic;
2. all Kneser edges induced by an 11-subset \(A\) of one double star are
   blue; and
3. all Kneser edges induced by an 11-subset \(C\) of another double star are
   red.

The symmetric group \(S_8\) acts transitively on the 28 two-vertex cores.
Relabel the ground set so that the core containing \(A\) is \(\{0,1\}\).
This does not restrict \(A\) within its 13-edge double star, the second core,
\(C\), or the 210 edge colors.

The Lean theorem `core01_obstruction_11` proves that the resulting universal
finite proposition is false. The theorem `matchingFree11_is_doubleStar`
independently proves the exact 11-edge matching-family classification used in
the reduction.

A separately written C++ verifier reaches the same conclusion without using
the Lean generator. It enumerates

\[
\binom{13}{11}\cdot28\binom{13}{11}
=78\cdot2184
=170{,}352
\]

candidate pairs. Of these, 129,666 have an immediate forced-color clash. For
every remaining pair it performs a complete DPLL search on the 420
not-all-equal triangle clauses. The deterministic search explores 40,027,816
nodes and returns `UNSAT`.

Therefore the assumed pair \(A,C\) cannot exist. Every triangle-free red-blue
coloring has one color graph with independence number at most ten. This proves
the finite Ramsey statement and the lower bound

\[
\beta_2(KG(8,2))\ge\frac{14}{5}.
\]

Since \(5/2<14/5\), two members of \(\mathcal C_{5/2}\) cannot cover the
Kneser graph. Combining this with Section 2 proves Theorem A.

## 6. Consequence for the family \(KG(n,2)\)

The source paper supplies a two-graph \(5/2\)-fractional cover of
\(KG(7,2)\). Restricting that cover handles every \(n\le7\). Conversely,
\(KG(8,2)\) is an induced subgraph of \(KG(n,2)\) for every \(n\ge8\).
Thus the proposed result determines the complete cutoff:

\[
KG(n,2)\text{ is coverable by two }5/2\text{-fractionally colorable graphs}
\iff n\le7.
\]

## 7. Lean correspondence

`formal/generate_lean.py` deterministically generates the complete finite
source.

- `BV28 := BitVec 28` represents a family of edges of \(K_8\).
- `BV210 := BitVec 210` represents a red-blue coloring of the Kneser edges.
- `matchingFree` is the conjunction excluding all 420 three-edge matchings.
- `triangleFree` is the conjunction excluding both monochromatic assignments
  on all 420 Kneser triangles.
- `blueOn` and `redOn` impose the two oppositely monochromatic induced
  subgraphs.
- `matchingFree11_is_doubleStar` checks the structure lemma at the exact
  cardinality needed.
- `core01_obstruction_11` checks the complete transitivity-reduced finite
  obstruction.

Run:

```bash
cd formal
python generate_lean.py
lake build
```

The generated source has SHA-256

```text
2a51c43c1f9ec8e0f2bbfa76cf7333dc1dcc53ded85a67ff5212a863647b68a9
```

### Trust boundary

The finite proofs use Lean's native `bv_decide`. The generated proof terms are
checked within the Lean environment, but native reflective computation means
the Lean compiler/native evaluator is part of the trusted computing base.
`#print axioms` reports the standard logical axioms `propext`,
`Classical.choice`, and `Quot.sound`, plus one generated native-computation
axiom for each `bv_decide` theorem. There are no `sorry`, `admit`, or
hand-written axioms.

## 8. What is and is not formalized

The delicate finite core is machine-checked twice. The following outer facts
remain human-checked:

- monotonicity of fractional chromatic number under edge deletion;
- \(\chi_f(H)\ge |V(H)|/\alpha(H)\);
- the Tutte-Berge derivation above;
- transitivity of the \(S_8\)-action on double-star cores; and
- the three-bit bipartite upper-bound construction.

These are standard or elementary, but an end-to-end theorem in a graph library
is still a separate formalization milestone.

## 9. Exact-threshold work

The interval \([14/5,3]\) remains. An exact SAT experiment searches for two
maps from \(KG(8,2)\) to \(KG(14,5)\) whose coordinate edge sets cover every
Kneser edge. A satisfying assignment would prove equality
\(\beta_2=14/5\). An unsatisfiable result at this single denominator would
only rule out that particular unscaled representation; it would not exclude a
homomorphism to \(KG(14t,5t)\) for \(t>1\).
