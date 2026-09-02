# An explicit triangle-free two-colouring of `KG(11,3)`

**Status:** proposed new lower-bound construction; independently executable, not yet externally reviewed.  
**Consequence:**

\[
R^{\mathrm{KG}}_3(3,3)\ge 12.
\]

This improves the lower endpoint `11` reported by Heath--McCourt--Parker--Schwieder--Zerbib. Their computational upper bound remains `13`, so this construction narrows the published interval to

\[
12\le R^{\mathrm{KG}}_3(3,3)\le 13.
\]

## Construction

Partition the eleven ground elements as

\[
[11]=X\sqcup Y,\qquad |X|=6,\qquad Y=\mathbb Z/5\mathbb Z.
\]

For a vertex `A` of `KG(11,3)`, put

\[
w(A)=|A\cap X|.
\]

Two vertices are adjacent precisely when the corresponding triples are disjoint. Colour every such edge `AB` red or blue as follows.

### Neither endpoint is central

If `w(A),w(B) != 2`, colour `AB` red exactly when both weights are at most one or both weights equal three. Equivalently, low--low and high--high edges are red, while low--high edges are blue.

### Exactly one endpoint is central

Suppose `w(A)=2`, so `A cap Y={y}`.

- If `w(B)=3`, colour `AB` red.
- If `w(B)<=1`, colour `AB` red exactly when `y-1` belongs to `B cap Y`; otherwise colour it blue.

Use the symmetric rule when `B` is central.

### Both endpoints are central

If `A cap Y={y}` and `B cap Y={z}`, colour `AB` red exactly when `y` and `z` are adjacent on the five-cycle:

\[
z-y\equiv \pm1\pmod 5.
\]

Otherwise colour it blue.

No information about the internal geometry of the six-element part `X` is required.

## Proof that no triangle is monochromatic

Let `A,B,C` be three pairwise disjoint triples. Since they use nine of the eleven ground elements and `|Y|=5`,

\[
4\le w(A)+w(B)+w(C)\le6.
\]

After sorting, the only possible weight patterns are

\[
\begin{array}{lll}
(0,1,3),&(0,2,2),&(1,1,2),\\
(0,2,3),&(1,1,3),&(1,2,2),\\
(0,3,3),&(1,2,3),&(2,2,2).
\end{array}
\]

We check them in four groups.

### No central vertex

The possible patterns are `(0,1,3)`, `(1,1,3)`, and `(0,3,3)`. In each case there is at least one same-side pair and at least one low--high pair. Hence the triangle contains both a red and a blue edge.

### Exactly one central vertex

The possible patterns are `(1,1,2)`, `(0,2,3)`, and `(1,2,3)`.

For `(0,2,3)` and `(1,2,3)`, the central--high edge is red and the low--high edge is blue.

For `(1,1,2)`, let the central triple meet `Y` at `y`. The two low triples each use two elements of `Y`; together with `y` they partition the five-cycle. Therefore `y-1` belongs to exactly one of the two low triples. The two central--low edges consequently have opposite colours.

### Exactly two central vertices

The possible patterns are `(0,2,2)` and `(1,2,2)`. Let the two central triples meet `Y` at `y` and `z`.

If `y,z` are adjacent, their mutual edge is red. One of `y-1,z-1` is the other central point, so the corresponding edge from a central vertex to the low vertex is blue.

If `y,z` are nonadjacent, their mutual edge is blue. The predecessors `y-1` and `z-1` are two distinct elements of the three-point complement of `{y,z}` in the five-cycle. In pattern `(0,2,2)` the low vertex contains all three complementary points; in pattern `(1,2,2)` it contains two of them. In either case it contains at least one predecessor, producing a red central--low edge.

### Three central vertices

For pattern `(2,2,2)`, the three central triples determine three distinct points of the five-cycle. Among any three vertices of `C_5` there is both an adjacent pair and a nonadjacent pair, because `C_5` has clique number and independence number two. Thus the three Kneser edges include both colours.

Every possible triangle is therefore nonmonochromatic. This proves the construction.

## Deterministic verification

Run

```bash
python tools/verify_kneser_r3_explicit.py
```

The verifier checks all `4,620` Kneser edges and all `15,400` Kneser triangles using only the Python standard library. The lexicographically ordered edge-colour bitset has SHA-256

```text
e32129b5e64783311ab3443e3e3e492887bcb8025b9efaf4cd9182c7f113788b
```

The rule was reverse-engineered from an exact SAT witness constrained by a ground-set automorphism of cycle type `(6)(5)`, but the statement and proof above no longer depend on SAT.

## Why this matters for the larger project

The construction exposes a reusable mechanism. For `KG(3r+2,r)`, split the ground set into parts of sizes `2r` and `r+2`, and let

\[
c=\left\lfloor\frac{2r}{3}\right\rfloor.
\]

If neither endpoint of an edge lies in the central layer `|A cap X|=c`, the same low--low/high--high versus low--high rule automatically makes every triangle avoiding that layer nonmonochromatic. Only edges touching one critical layer require additional design. This **boundary-layer reduction** is now being tested at `r=4`; a validated `(8)(6)`-symmetric SAT witness already exists on `KG(14,4)`.
