# A sharp nine-point link theorem

## Statement

Let the triples of a nine-point set be colored red or blue. A **perfect
matching** is a partition of the nine points into three triples.

> **Nine-point link theorem.** If neither color contains a perfect matching,
> then one color contains every triple of some five-point set; that is, there
> is a monochromatic copy of \(K_5^{(3)}\).

Equivalently, let \(\mathcal R\) and \(\mathcal B\) be complementary
3-uniform hypergraphs on nine vertices. If

\[
\nu(\mathcal R),\nu(\mathcal B)\le 2,
\]

then

\[
\min\{\tau(\mathcal R),\tau(\mathcal B)\}\le 4.
\]

Indeed, a four-point transversal of one color has a five-point complement
containing only triples of the other color.

The order five is best possible: there is a coloring with no monochromatic
perfect matching and no monochromatic \(K_6^{(3)}\).

## Exact proof certificate

The theorem is presently established by a small, independently checked finite
refutation. Associate a Boolean variable \(x_T\) to each of the
\(\binom 93=84\) triples, with `true` meaning red.

The negation consists of:

1. for each of the 280 partitions of the nine points into three triples, one
   clause forbidding all blue and one clause forbidding all red;
2. for each of the 126 five-point sets, one ten-literal clause requiring a red
   triple and one ten-literal clause requiring a blue triple;
3. one unit clause removing the global red/blue swap.

Thus the canonical formula has

\[
560+252+1=813
\]

clauses. Its SHA-256 digest is

```text
0db7c378b5fdf09326e5190ad6697e64b2a508ce39075864bcb3cd4918b84314
```

`tools/verify_kneser_nine_point_link_k5.py` constructs a deterministic DPLL
refutation using only unit propagation and binary branching. The proof is a
DAG with 9,536 internal nodes, 9,537 conflict leaves, and 19,073 checked
references. The script then traverses the DAG independently: at every node it
recomputes the unit-propagation closure, verifies the branch variable is
unassigned, and verifies both children or the indicated conflicting clause.
Every node must be reachable and the graph must be acyclic.

The deterministic proof payload has hashes

```text
raw JSON:  30a35dcd239712ee87e4f65ddb5ab71a0965facf63d5595fd237ad95e9c6223d
gzip:      f63cad91fd91a94f6fba484de031e6d480c0236f54709fd0ecd7ab5063c3f40b
```

No external SAT solver or Python package is trusted by this verification.

## Sharpness: the Fano-star coloring

Take a Fano plane on points \(0,\ldots,6\), an ordinary point \(7\), and a
special point \(8\). Color red

- every triple containing \(8\), and
- the seven Fano lines on \(0,\ldots,6\).

Color every remaining triple blue.

There is no blue perfect matching because no blue triple contains point 8. A
red perfect matching would use one red triple through 8 and would then require
two disjoint Fano lines, but every two Fano lines intersect. Hence neither
color has a perfect matching.

The verifier exhaustively establishes

\[
\tau(\mathcal R)=4,\qquad \tau(\mathcal B)=5.
\]

It finds seven blue copies of \(K_5^{(3)}\), no red copy, and no monochromatic
\(K_6^{(3)}\). Consequently five is exactly the largest complete 3-graph order
forced by the theorem's hypotheses.

## Corollary for \(KG(12,3)\)

Suppose an edge coloring of \(KG(12,3)\) has no monochromatic triangle. Fix a
Kneser vertex \(A\), a triple. Its neighbors are the 84 triples in the
nine-point complement \([12]\setminus A\). Color such a neighboring triple
\(B\) by the color of the Kneser edge \(AB\).

This local coloring has no monochromatic perfect matching. To see this, let
\(B,C,D\) partition \([12]\setminus A\). If the three edges from \(A\) to
\(B,C,D\) had one color, avoiding a monochromatic triangle through \(A\)
would force all three edges among \(B,C,D\) to have the opposite color. Those
three edges would themselves form a monochromatic triangle.

The nine-point link theorem therefore gives a five-set

\[
S_A\subseteq [12]\setminus A
\]

and a color \(q_A\) such that

\[
c(A,B)=q_A\qquad\text{for every }B\in\binom{S_A}{3}.
\]

We call \((S_A,q_A)\) a **monochromatic five-cloud in the link of \(A\)**.
Thus every hypothetical counterexample on \(KG(12,3)\) carries 220 coupled
five-clouds.

This is the first nontrivial stability constraint on an arbitrary candidate
coloring. It is stronger than the false preliminary conjecture that one local
color must have a two-point transversal: admissible local colorings with
transversal numbers 4 and 5 exist, and the Fano-star example is canonical.

## Role in the upper-bound program

The current route to the matching upper bound is:

1. prove one-point saturation of the explicit five-point coloring at
   \(3r+2\);
2. prove uniqueness or sufficient stability of extremal good colorings at
   \(3r+2\);
3. conclude that a coloring at \(3r+3\) cannot exist.

For \(r=3\), the theorem above converts each local 84-variable link into a
five-set and a color. The remaining problem is global compatibility: cloud
choices at adjacent triples must force the same shared edge color, and the
forced colors cannot complete a monochromatic Kneser triangle.

## Verification and claim boundary

- The finite nine-point theorem and sharpness construction are exactly
  verified by a deterministic standard-library program.
- The result is not yet formalized in Lean.
- A human structural proof and a complete prior-art audit remain open.
- The theorem alone does **not** prove that \(KG(12,3)\) is Ramsey.
- No claim of \(R_3^{KG}(3,3)=12\), or of the general equality
  \(R_r^{KG}(3,3)=3r+3\), is made here.
