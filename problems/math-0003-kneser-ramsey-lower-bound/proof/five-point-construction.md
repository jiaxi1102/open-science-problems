# Proof of the five-point Kneser-Ramsey lower bound

## Theorem

For every integer `r >= 1`,

\[
R_r^{\mathrm{KG}}(3,3)\ge 3r+3.
\]

Equivalently, the edges of `KG(3r+2,r)` admit a red/blue coloring with no
monochromatic triangle.

## 1. The finite trace coloring

Let

\[
P=\mathbb Z/5\mathbb Z.
\]

We first define a symmetric red/blue coloring `c(S,T)` whenever
`S,T subseteq P` are disjoint. Call a trace

- **empty** if `S=emptyset`;
- **singleton** if `|S|=1`;
- **large** if `|S|>=2`.

The color red is encoded by `1` and blue by `0`.

### Rule I: neither trace is a singleton

If neither `S` nor `T` is a singleton, set

\[
c(S,T)=1
\]

exactly when `S,T` have the same type: both empty or both large. Thus
empty--large edges are blue.

### Rule II: two singleton traces

For `S={y}` and `T={z}`, set

\[
c(S,T)=1
\quad\Longleftrightarrow\quad
z-y\equiv\pm1\pmod5.
\]

This is the red five-cycle / blue-diagonal coloring of `K_5`.

### Rule III: singleton and empty

For every `y`, set

\[
c(\{y\},\emptyset)=1.
\]

### Rule IV: singleton and large

For `S={y}` and `|T|>=2`, set

\[
c(\{y\},T)=1
\quad\Longleftrightarrow\quad
y-1\in T.
\]

The definition is symmetric because the singleton endpoint is intrinsically
distinguished from the large endpoint.

## 2. The five-point gadget lemma

### Lemma

Let `S,T,U subseteq P` be pairwise disjoint and suppose

\[
|S\cup T\cup U|\ge3.
\]

Then the three colors

\[
c(S,T),\qquad c(S,U),\qquad c(T,U)
\]

are not all equal.

### Proof

We split according to the number of singleton traces among `S,T,U`.

#### Case 0: no singleton traces

Every trace is empty or large. They cannot all be empty because their union
has size at least three. They cannot all be large because three pairwise
disjoint large subsets of a five-point set would contain at least six points.

Hence both the empty and large types occur. Two of the three traces have the
same type, so their connecting edge is red by Rule I. An edge joining the two
different types is blue. Both colors occur.

#### Case 1: exactly one singleton trace

Write the singleton as `{y}`.

If one of the other traces is empty, the third must be large because the total
union has size at least three. The singleton--empty edge is red by Rule III,
whereas the empty--large edge is blue by Rule I.

Otherwise both remaining traces are large. Pairwise disjointness gives

\[
1+|T|+|U|\le5,
\]

while largeness gives the reverse lower bound `1+2+2=5`. Therefore

\[
\{y\}\sqcup T\sqcup U=P,
\qquad |T|=|U|=2.
\]

The predecessor `y-1` belongs to exactly one of `T,U`. By Rule IV, the two
edges from `{y}` to `T,U` have opposite colors.

#### Case 2: exactly two singleton traces

Write them as `{y}` and `{z}`. The third trace `T` cannot be empty, since then
the union would have size two, so `T` is large.

If `y,z` are adjacent on the five-cycle, the singleton--singleton edge is red.
Assume, after interchanging `y,z` if needed, that `z=y+1`. Then the predecessor
of `z` is `y`, which is not in `T` by disjointness. Rule IV therefore makes
the edge from `{z}` to `T` blue.

If `y,z` are nonadjacent, their singleton--singleton edge is blue. The two
predecessors `y-1,z-1` are distinct and neither is `y` or `z`; hence both lie
in the three-point complement `P\setminus\{y,z\}`. The large trace `T` is a
subset of this complement with size at least two, so it contains at least one
of these predecessors. Rule IV gives a red edge from the corresponding
singleton to `T`.

#### Case 3: three singleton traces

The three traces are three distinct vertices of the five-cycle. Among any
three vertices of `C_5` there is an adjacent pair and a nonadjacent pair,
because both the clique number and independence number of `C_5` equal two.
Rule II therefore assigns both red and blue to the three edges.

All cases contain both colors, proving the lemma. ∎

## 3. Lifting the gadget to `KG(3r+2,r)`

Fix any five distinguished elements

\[
P\subseteq[3r+2]
\]

and identify them with `Z/5Z`. For every Kneser vertex
`A in binom([3r+2],r)`, define its trace

\[
S(A)=A\cap P.
\]

For adjacent Kneser vertices `A,B`, the sets are disjoint, so their traces are
disjoint. Color the Kneser edge `AB` by

\[
C(A,B)=c(S(A),S(B)).
\]

Now let `A,B,C` be a triangle of `KG(3r+2,r)`. The three `r`-sets are pairwise
disjoint, so

\[
|A\cup B\cup C|=3r.
\]

The ambient set has size `3r+2`, hence exactly two ground points lie outside
their union. In particular, at most two of the five distinguished points are
outside the union. Therefore

\[
|S(A)\cup S(B)\cup S(C)|
=|P\cap(A\cup B\cup C)|
\ge 5-2=3.
\]

The three traces are pairwise disjoint, so the five-point gadget lemma applies
and says that

\[
C(A,B),\qquad C(A,C),\qquad C(B,C)
\]

are not all equal. Thus no triangle of `KG(3r+2,r)` is monochromatic.

We have constructed a valid coloring of `KG(3r+2,r)`, so by the definition of
the Kneser Ramsey number,

\[
R_r^{\mathrm{KG}}(3,3)>3r+2.
\]

Since the Ramsey number is integral,

\[
\boxed{R_r^{\mathrm{KG}}(3,3)\ge3r+3.}
\]

This includes `r=1`, where the construction is the usual red-cycle /
blue-diagonal coloring of `K_5`. ∎

## 4. Verification interpretation

The full theorem has only two ingredients:

1. the finite five-point gadget lemma; and
2. the cardinality identity that three disjoint `r`-sets in a `(3r+2)`-set
   leave exactly two points unused.

The executable verifier exhausts ingredient 1 over all `918` relevant labeled
trace partitions and directly checks the lifted coloring for `r=1,2,3,4`.
The Lean file formalizes the finite gadget; formalizing ingredient 2 and the
lift for arbitrary `r` is the remaining proof-assistant boundary.
