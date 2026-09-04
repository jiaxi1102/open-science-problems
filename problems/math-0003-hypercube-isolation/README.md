# math-0003: Subcube isolation and radius-covering arrays

## Status matrix

| Dimension | Status |
|---|---|
| Problem | `refuted`: the universal equality fails |
| Structural result | exact equivalence with binary radius-covering arrays; fixed-codimension phase transition; perfect-code rigidity; candidate exponential additive gap |
| Formal verification | coordinate-copy theorem, graph-to-array bridge, perfect-projection metric core, packing core, and quantitative arithmetic in Lean; finite `(6,2)` certificate complete |
| Novelty | the value `CAN_1(4,6,2)=5` is 2010 prior art; the graph translation and structural/quantitative theorem package require specialist confirmation |
| External review | none yet |

## Original question

Brešar and Rall ask in Problem 2 of *On the isolation numbers in graph products* (arXiv:2608.25752v1, 26 August 2026) whether

```text
ι(Q_n,Q_k)=γ(Q_(n-k))
```

for every `0<k<n`.

## Exact translation

Let `CAN_r(m,n,2)` denote the minimum number of rows in a binary radius-covering array of strength `m`, length `n`, and radius `r`. The central structural theorem is

```text
ι(Q_n,Q_k) = CAN_1(n-k,n,2).
```

More generally, deleting the radius-`r` neighborhood of a set so that no codimension-`m` subcube remains has minimum size `CAN_r(m,n,2)`.

The proof has two exact ingredients: every graph copy of a hypercube inside a hypercube is a coordinate subcube, and the distance from a word to a coordinate face equals the Hamming distance on its fixed coordinates. Both ingredients now have a Lean structural layer. The complete mathematical argument is in [`proof/structural-theory.md`](proof/structural-theory.md).

## Infinite fixed-`Q_2` family

For every `t>=3`, put `m=2^t-1`. Then

```text
ι(Q_(m+k),Q_k)=γ(Q_m)  iff  k=1.
```

The equality for `k=1` is the known binary parity-extension theorem. For every `k>=2`, strict inequality follows from a robust-extension obstruction for perfect codes. At `k=2`, every `m`-column projection of an optimal-size array would have to be a perfect Hamming code. That forces the full rows to have minimum distance at least five, but the radius-two Hamming packing bound rules out that many length-`m+2` rows. Monotonicity then handles every `k>=2`.

This gives infinitely many counterexamples while the forbidden surviving subcube remains two-dimensional.

## Quantitative Hamming-family separation

Writing

```text
K = γ(Q_m) = 2^m/(m+1),
M = ι(Q_(m+2),Q_2),
m = 2^t-1,
```

the candidate quantitative theorem proves

```text
M-K >= ceil(3 K m(m-3) / [4(m+2)(m+1)^4]).
```

Therefore

```text
ι(Q_(m+2),Q_2)-γ(Q_m) = Ω(2^m/m^4)
```

along the Hamming lengths. The explicit lower bounds on the excess are `1` at `m=7`, `1` at `m=15`, `1263` at `m=31`, and `374,653,301,052` at `m=63`. The full incidence proof is in [`proof/quantitative-hamming-gap.md`](proof/quantitative-hamming-gap.md); Lean checks its algebraic core and exact numerical instances.

## Fixed-codimension phase transition

For fixed codimension `m`,

```text
ι(Q_n,Q_(n-m)) =
  1              if m=1,
  2              if m=2 or 3,
  Θ_m(log n)     if m>=4.
```

The normalized-column argument gives the explicit lower constraint

```text
n <= (m-1) 2^(M-1)
```

for every `M`-row array in the logarithmic regime. Hence, for every fixed `m>=4`,

```text
ι(Q_n,Q_(n-m)) / γ(Q_m) -> infinity.
```

Thus the proposed equality can fail by an unbounded multiplicative factor as well as by an exponentially growing additive amount along the Hamming family.

## Smallest table-based illustration

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

This numerical value is **not new**. The repository retains an independent proof, Python enumeration, and Lean certificate because they make the graph counterexample directly auditable.

## Lean verification

The formal package currently contains:

1. `CubeCopies.lean`: every injective edge-preserving map `Q_k -> Q_n` is a coordinate embedding;
2. `StructuralTheory.lean`: the exact distance-to-face identity and the equivalence between radius-neighborhood face hitting and the binary radius-covering-array predicate;
3. `ProjectionDistance.lean`: puncturing/projection distance lemmas;
4. `Packing.lean`: disjoint Hamming balls and an abstract packing bound;
5. `PerfectProjection.lean`: exact projected covers force separation, which lifts to full-row separation and packing;
6. `QuantitativeGap.lean`: kernel-checked multiplicity, deletion, Caro--Wei algebra, monotonicity, final gap combination, and explicit `m=7,15,31,63` arithmetic;
7. `HypercubeIsolation.lean`: the finite `(6,2)` witness and exhaustive four-row exclusion.

The finite exhaustive lower bound still uses `native_decide`; its generated axiom is disclosed. The structural and quantitative modules use ordinary kernel-checked reasoning with Mathlib and contain no `sorry`, `admit`, or hand-written axioms. The remaining end-to-end formalization gate is to prove the Hamming-ball cardinality specializations and assemble the quantitative incidence sums into one final theorem.

## Prior-art correction

The first search pass used graph-isolation terminology and missed the established coding-theory name. The corrected record is in [`references/NOVELTY.md`](references/NOVELTY.md). In particular:

- radius-covering arrays were defined and tabulated by Colbourn--Kéri--Rivas Soriano--Schlage-Puchta;
- their table records `CAN_1(4,6,2)=5`;
- their Theorem 7.3 proves `CAN_r(m,m+1,2)=K_2(m,r)`.

Searches through 4 September 2026 have not located the graph--coding dictionary, the perfect-projection obstruction, the Hamming-family equality classification, or the quantitative gap theorem. That is not a priority certificate. No public novelty claim should be made until coding theorists, graph theorists, and the authors of the 2026 problem review the work.

## Reproduce

```bash
cd problems/math-0003-hypercube-isolation/formal
lake build
python ../experiments/discover.py
```

The publication draft is [`paper/main.tex`](paper/main.tex).
