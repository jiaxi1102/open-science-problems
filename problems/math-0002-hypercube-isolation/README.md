# math-0002: Subcube isolation and radius-covering arrays

## Status matrix

| Dimension | Status |
|---|---|
| Problem | `refuted`: the universal equality fails |
| Structural result | exact equivalence with radius-covering arrays; infinite Hamming-family, quantitative-gap, and phase-transition theorems proved on paper |
| Formal verification | coordinate-copy theorem and graph/coding bridge kernel-checked; local quantitative algebra checked; finite `(6,2)` certificate complete |
| Novelty | ordinary face-transversal and radius-covering-array formulations are prior art; the perfect-code obstruction and quantitative graph-isolation package are candidate new |
| External review | none yet |

## Original question

Brešar and Rall ask in Problem 2 of *On the isolation numbers in graph
products* (arXiv:2608.25752v1, 26 August 2026) whether

```text
ι(Q_n,Q_k)=γ(Q_(n-k))
```

for every `0<k<n`.

## Exact translation

Let `CAN_r(m,n,2)` denote the minimum number of rows in a binary
radius-covering array of strength `m`, length `n`, and radius `r`. The central
structural identity is

```text
ι(Q_n,Q_k)=CAN_1(n-k,n,2).
```

More generally, deleting the radius-`r` neighborhood of a set so that no
codimension-`m` subcube remains has minimum size `CAN_r(m,n,2)`.

The reason is exact: every copy of a hypercube inside a hypercube is a
coordinate subcube, and the distance from a word to a face equals the Hamming
distance between its restriction to the fixed coordinates and the face
pattern.

The radius-zero version of this geometry is established prior art: ordinary
binary covering arrays have long been described as transversals of cube faces.
The contribution here is therefore not the first covering-array/cube-face
connection. It is the radius-neighborhood formulation for graph isolation and
the structural consequences drawn from it.

The full manuscript is in [`paper/draft.md`](paper/draft.md), with modular
proofs in [`proof/structural-theory.md`](proof/structural-theory.md) and
[`proof/quantitative-hamming-gap.md`](proof/quantitative-hamming-gap.md).

## Main consequences

### Infinite Hamming-family classification

For every `t>=3`, put `m=2^t-1`. Then

```text
ι(Q_(m+k),Q_k)=γ(Q_m)  iff  k=1.
```

The equality for `k=1` is the known parity-extension theorem for binary
radius-covering arrays. For every `k>=2`, strict inequality follows from a
perfect-code extension obstruction: if every deletion down to `m` columns
were an optimal covering code, all those projections would be perfect, forcing
full minimum distance incompatible with sphere packing.

### Quantitative exponential additive gap

Writing

```text
K=γ(Q_m)=2^m/(m+1),
```

the candidate quantitative theorem gives, for every `k>=2`,

```text
ι(Q_(m+k),Q_k)
  >= K + ceil(3K m(m-3)/[4(m+2)(m+1)^4]).
```

Hence the additive gap is `Omega(2^m/m^4)`. At `m=31` the theorem already
forces at least `1,263` extra vertices; at `m=63`, at least
`374,653,301,052` extra vertices.

### Fixed-codimension phase transition

For fixed codimension `m`,

```text
ι(Q_n,Q_(n-m)) =
  1              if m=1,
  2              if m=2 or 3,
  Θ_m(log n)     if m>=4.
```

Consequently, for every fixed `m>=4`,

```text
ι(Q_n,Q_(n-m))/γ(Q_m) -> infinity.
```

This turns the original equality failure into an unbounded asymptotic
separation.

### Smallest table-based illustration

The 2010 radius-covering-array tables contain

```text
CAN_1(4,6,2)=5.
```

The exact translation gives

```text
ι(Q_6,Q_2)=5>4=γ(Q_4).
```

A minimum set is

```text
{000000,000011,000101,111001,111110}.
```

This numerical value is **not new**. The repository retains an independent
proof, Python enumeration, and Lean certificate because they make the graph
counterexample directly auditable.

## Lean verification

The formal package contains:

- [`CubeCopies.lean`](formal/HypercubeIsolation/CubeCopies.lean): every
  injective edge-preserving map `Q_k→Q_n` is a coordinate embedding;
- [`StructuralTheory.lean`](formal/HypercubeIsolation/StructuralTheory.lean):
  the exact distance-to-face identity, the coordinate-face/radius-covering
  equivalence, and perfect-code volume arithmetic;
- [`QuantitativeGap.lean`](formal/HypercubeIsolation/QuantitativeGap.lean):
  the pointwise overlap estimate, deletion-count rescaling, packing
  rearrangement, quadratic monotonicity, final algebra, and exact coefficients
  for `m=7,15,31,63`;
- [`HypercubeIsolation.lean`](formal/HypercubeIsolation.lean): the finite
  `(6,2)` witness and exhaustive lower bound.

The structural theorems are kernel-checked and report only standard
classical/extensionality axioms from Mathlib. The exhaustive finite lower bound
still uses `native_decide`; its generated axiom is explicitly disclosed, and
an independent Python search reproduces the result.

The remaining end-to-end formalization target is the finite incidence
machinery joining the local multiplicity lemmas to the global pair counts and
the graph independence bound.

## Prior-art correction

The first pass searched only graph-isolation terminology and therefore missed
both the coding-theory name of the radius-one object and the older ordinary
face-transversal formulation. The corrected records are in
[`references/NOVELTY.md`](references/NOVELTY.md) and
[`references/RADIUS_COVERING_ARRAYS.md`](references/RADIUS_COVERING_ARRAYS.md).
In particular:

- Lawrence--Kacker--Lei--Kuhn--Forbes describe binary covering arrays as
  hypercube face transversals;
- Colbourn--Kéri--Rivas Soriano--Schlage-Puchta define and classify
  radius-covering arrays;
- their tables record `CAN_1(4,6,2)=5`;
- their Theorem 7.3 proves `CAN_r(m,m+1,2)=K_2(m,r)`.

No priority claim should be made for the perfect-code obstruction or new
structural consequences until coding theorists, graph theorists, and the
authors of the 2026 problem review them.

## Build

```bash
cd formal
lake build
```

Independent finite search:

```bash
python experiments/discover.py
```
