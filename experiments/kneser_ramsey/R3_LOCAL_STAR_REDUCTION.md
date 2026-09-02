# The local-star reduction for `KG(12,3)`

**Status:** proved structural equivalence; exact global compatibility problem still
open.  
**Purpose:** replace the opaque 9,240-variable edge-SAT instance by a local
matching-coloring problem with an explicit gluing law.

## 1. Setup

Let

\[
G=KG(12,3).
\]

Its vertices are the triples of `[12]`, and two triples are adjacent when they
are disjoint. A red/blue edge-coloring `c` of `G` is **good** when it contains
no monochromatic triangle.

For a vertex `A`, its neighborhood is

\[
N_G(A)=\binom{[12]\setminus A}{3},
\]

and hence the graph induced by the neighborhood is canonically

\[
G[N_G(A)]\cong KG(9,3).
\]

Define the **star coloring at `A`** by

\[
\sigma_A(B)=c(AB),\qquad B\in N_G(A).
\]

Thus `sigma_A` is a red/blue coloring of the 84 triples in the nine-point
complement of `A`.

## 2. The nine-point perfect-matching hypergraph

For a nine-element set `X`, let `P(X)` be the 3-uniform hypergraph whose
vertices are the triples in `X` and whose hyperedges are the unordered
partitions

\[
\{B,C,D\},\qquad X=B\mathbin{\dot\cup}C\mathbin{\dot\cup}D,
\]

into three triples.

The hypergraph `P(X)` has

- `binom(9,3)=84` vertices;
- `9!/(3!^3 3!)=280` hyperedges.

Equivalently, its hyperedges are the perfect matchings of the complete
3-uniform hypergraph on `X`.

There is also a useful graph interpretation. The graph `KG(9,3)` has 840
edges, and every edge belongs to exactly one triangle: if `B` and `C` are
disjoint triples, their six-point union has a unique complementary triple
`D`. Consequently, the 280 triangles of `KG(9,3)` partition its 840 edges.
It follows immediately that every cut of `KG(9,3)` has at most

\[
2\cdot 280=560
\]

edges. Equality holds precisely when every partition triangle has vertices
on both sides of the cut, i.e. precisely when the corresponding two-coloring
of `P(X)` is proper.

## 3. Local-star equivalence theorem

### Theorem

A red/blue edge-coloring `c` of `KG(12,3)` is good if and only if, for every
triple `A`, its star coloring `sigma_A` is a proper two-coloring of

\[
P([12]\setminus A).
\]

Equivalently, for every partition

\[
[12]=A\mathbin{\dot\cup}B\mathbin{\dot\cup}C\mathbin{\dot\cup}D
\]

into four triples, the three colors

\[
c(AB),\ c(AC),\ c(AD)
\]

are not all equal, and the analogous condition holds at each of `B,C,D`.

### Proof: good coloring implies proper stars

Fix `A`, and let `B,C,D` partition `[12] minus A`. Suppose for contradiction
that

\[
c(AB)=c(AC)=c(AD)=\gamma.
\]

Because `ABC`, `ABD`, and `ACD` are triangles and the coloring is good, the
three opposite edges `BC`, `BD`, and `CD` must all have color different from
`gamma`. They therefore form a monochromatic triangle `BCD`, a contradiction.
Thus every hyperedge `{B,C,D}` of the local perfect-matching hypergraph is
bichromatic under `sigma_A`.

### Proof: proper stars imply good coloring

Suppose instead that `ABC` is a monochromatic triangle, say all three of its
edges have color `gamma`. Let

\[
D=[12]\setminus(A\cup B\cup C),
\]

which is a triple. Properness of the star at `A` applied to the partition
`{B,C,D}` forces `AD` to have the opposite color. Properness at `B` similarly
forces `BD` to have the opposite color, and properness at `C` forces `CD` to
have the opposite color. But then the star at `D` is monochromatic on the
partition `{A,B,C}`, contradicting its properness. Hence no monochromatic
triangle exists.

## 4. Exact compatibility formulation

For each triple `A`, let `Sigma(A)` be the set of all proper two-colorings of
`P([12] minus A)`. The exact decision problem is:

> Choose one local state `sigma_A in Sigma(A)` for every one of the 220
> triples `A`, subject to the pairwise gluing equations
>
> \[
> \sigma_A(B)=\sigma_B(A)
> \]
>
> for every disjoint pair `A,B`.

The theorem above proves that solutions of this compatibility system are in
bijection with good red/blue edge-colorings of `KG(12,3)`.

This changes the interpretation of the computation. The original CNF has
9,240 edge-color variables and 123,200 NAE clauses. The local formulation has
220 highly structured local objects, each living on an 84-vertex,
280-hyperedge perfect-matching system, coupled by explicit overlap equations.
The difficult part is not local feasibility—many proper local colorings
exist—but global gluing.

## 5. Canonical `K4` normalization

Every partition of `[12]` into four triples induces a `K4` in `KG(12,3)`.
Up to relabeling its four vertices and globally swapping the two colors, a
red/blue coloring of `K4` with no monochromatic triangle has exactly two
types:

1. **matching type:** one color induces a two-edge perfect matching and the
   other a four-cycle;
2. **path type:** each color induces a three-edge path.

Therefore it is sufficient for the exact SAT decision to fix one canonical
four-triple partition and solve these two branches. This is the origin of the
`matching` and `path` seed cases in the certified exact-search workflow.

## 6. Structural invariants to extract

A proper local coloring is a partition

\[
\binom{X}{3}=R_A\mathbin{\dot\cup}B_A
\]

such that neither color class contains a perfect matching. The following
invariants should be computed for every local orbit encountered:

1. color-class sizes;
2. point-degree multisets in both colors;
3. matching and covering numbers;
4. sets of omitted points;
5. automorphism-group order;
6. restrictions to each eight-, seven-, and six-point subset;
7. the color pattern on pairs of complementary triples after deleting three
   points;
8. compatibility profiles with a neighboring local state.

The first target is not a complete raw enumeration of all local colorings.
It is a quotient by `S_9` and color swap, followed by a compatibility graph on
local orbit representatives. Unsatisfiability of that finite gluing graph
would be both a certificate for

\[
R_3^{KG}(3,3)=12
\]

and a source of human-readable obstruction lemmas.

## 7. General-r analogue

For a hypothetical good coloring of `KG(3r+3,r)` and a fixed `r`-set `A`,
the star at `A` colors all `r`-sets in a `(2r+3)`-point complement. Whenever
three of those sets partition a `3r`-subset, their star colors cannot all be
equal by the same opposite-triangle argument.

Thus the exact `r=3` reduction is the smallest instance of a more general
local matching-avoidance principle. What is special at `r=3` is that the
entire complement has size `3r=9`, so every relevant triple of neighbors is a
perfect matching of the whole complement and the local graph edges decompose
into triangles. A successful classification at `r=3` should therefore be
mined for a statement that remains meaningful when three unused points are
present for general `r`.

## 8. Concrete proof program

1. Finish the symmetry-broken exact decision in both canonical `K4` branches.
2. If satisfiable, validate the model against all 61,600 original triangles
   and mine it for a six- or seven-point trace construction improving the
   lower bound.
3. If unsatisfiable, rerun with proof logging and independently check the
   proof certificate.
4. Enumerate local proper-coloring orbits only as needed by the global solver,
   using canonical augmentation rather than listing all labeled states.
5. Extract a minimal incompatible family of local orbit types.
6. Translate the minimal obstruction into a human lemma and formalize it.
7. Test the resulting lemma in `KG(15,4)` and then formulate the general
   `3r+3` upper-bound induction or stability theorem.

The goal is not merely a one-off SAT result. The computational certificate is
being used as a microscope for the compatibility obstruction that a general
proof must explain.
