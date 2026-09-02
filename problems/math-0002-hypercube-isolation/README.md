# math-0002: Subcube isolation and radius-covering arrays

## Status matrix

| Dimension | Status |
|---|---|
| Problem | `refuted`: the universal equality fails |
| Structural result | exact equivalence with binary radius-covering arrays; infinite-family and asymptotic consequences proved |
| Formal verification | finite `(6,2)` certificate complete; structural Lean layer in progress |
| Novelty | the value `CAN_1(4,6,2)=5` is 2010 prior art; graph translation and new structural theorems require expert/author confirmation |
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
radius-covering array of strength `m`, length `n`, and radius `r`. The
central structural theorem is

```text
ι(Q_n,Q_k) = CAN_1(n-k,n,2).
```

More generally, deleting the radius-`r` neighborhood of a set so that no
codimension-`m` subcube remains has minimum size `CAN_r(m,n,2)`.

The reason is exact: every copy of a hypercube inside a hypercube is a
coordinate subcube, and the distance from a word to a face equals the
Hamming distance between its restriction to the fixed coordinates and the
face pattern.

The complete proof is in
[`proof/structural-theory.md`](proof/structural-theory.md).

## Main consequences

### Infinite Hamming-family refutation

For every `t>=3`, put `m=2^t-1`. Then

```text
ι(Q_(m+k),Q_k)=γ(Q_m)  iff  k=1.
```

The equality for `k=1` is the known parity-extension theorem for binary
radius-covering arrays. For every `k>=2`, strict inequality follows from a
new robust-extension obstruction for perfect codes: if every deletion of
two columns from an optimal-size array had covering radius one, each
projection would be a perfect Hamming code, forcing full minimum distance
at least five; the Hamming packing bound then gives a contradiction.

### Fixed-codimension phase transition

For fixed codimension `m`,

```text
ι(Q_n,Q_(n-m)) =
  1              if m=1,
  2              if m=2 or 3,
  Θ_m(log n)     if m>=4.
```

Hence, for every fixed `m>=4`,

```text
ι(Q_n,Q_(n-m)) / γ(Q_m) -> infinity.
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
ι(Q_6,Q_2)=5 > 4=γ(Q_4).
```

A minimum set is

```text
{000000,000011,000101,111001,111110}.
```

This numerical value is **not new**. The repository retains an independent
proof, Python enumeration, and Lean certificate because they make the graph
counterexample directly auditable.

## Verification

The current Lean file
[`formal/HypercubeIsolation.lean`](formal/HypercubeIsolation.lean) verifies:

1. `{0000,0001,1110,1111}` dominates `Q_4`;
2. no three vertices dominate `Q_4`;
3. the displayed five vertices isolate every coordinate square of `Q_6`;
4. no four vertices do.

The first three checks use kernel reduction. The exhaustive fourth check
uses `native_decide`, and its generated axiom is disclosed in
[`artifacts/CI.md`](artifacts/CI.md). The same finite claim is independently
reproduced by [`experiments/discover.py`](experiments/discover.py).

The next formal layer is being added on the new structural branch:

- the coordinate-face/projection distance identity;
- the equivalence between subcube isolation and radius-covering arrays;
- the length-nine Hamming packing obstruction underlying the first member
  `m=7` of the infinite family;
- kernel-checked arithmetic for the general volume inequality.

## Prior-art correction

The first pass searched only graph-isolation terminology and therefore
missed the coding-theory name of the same finite object. The corrected
record is in [`references/NOVELTY.md`](references/NOVELTY.md). In
particular:

- radius-covering arrays were defined and tabulated by
  Colbourn--Kéri--Rivas Soriano--Schlage-Puchta in 2010;
- their table records `CAN_1(4,6,2)=5`;
- their Theorem 7.3 proves `CAN_r(m,m+1,2)=K_2(m,r)`.

No priority claim should be made for the graph--coding bridge or the new
theorems until coding theorists, graph theorists, and the authors of the
2026 problem review them.

## Build

```bash
cd formal
lake build
```

Independent finite search:

```bash
python experiments/discover.py
```
