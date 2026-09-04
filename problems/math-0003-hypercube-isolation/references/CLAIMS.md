# Claim ledger

## Established inputs

- Brešar--Rall Problem 2 asks whether `ι(Q_n,Q_k)=γ(Q_(n-k))` for every `0<k<n`.
- Radius-covering arrays and generalized surjective codes are established coding-theory objects.
- Colbourn--Kéri--Rivas Soriano--Schlage-Puchta record `CAN_1(4,6,2)=5`; this numerical value is 2010 prior art.
- The binary one-column equality `CAN_r(m,m+1,2)=K_2(m,r)` is established prior art.
- Existence and parameters of binary and q-ary Hamming perfect codes, the Hamming packing bound, and the Caro--Wei inequality are standard inputs.

## Proved in the current draft

- Every graph copy of `Q_k` in `Q_n` is a coordinate subcube.
- Radius-`r` hitting of all codimension-`m` subcubes is exactly the binary radius-covering-array property:
  ```text
  I_r(n,m)=CAN_r(m,n,2).
  ```
- For fixed `m,r`, the minimum is `1` for `m<=r`, `2` for `r<m<=2r+1`, and `Θ(log n)` for `m>=2r+2`.
- Every `M`-row array in the logarithmic regime obeys the explicit normalized-column bound
  ```text
  n <= (m-1) 2^(M-1).
  ```
- A perfect-code projection obstruction yields strict extension inequalities whenever its Hamming-volume test fails.
- For binary Hamming lengths `m=2^t-1`, `t>=3`,
  ```text
  ι(Q_(m+k),Q_k)=γ(Q_m) iff k=1.
  ```
- Writing `K=2^m/(m+1)` and `M=ι(Q_(m+2),Q_2)`, the quantitative incidence argument gives
  ```text
  M-K >= ceil(3 K m(m-3) / [4(m+2)(m+1)^4]).
  ```
  Hence the additive gap is `Ω(2^m/m^4)` along binary Hamming lengths.

## Formally verified now

The Lean package verifies:

- the coordinate-copy theorem for injective edge-preserving cube maps;
- the exact distance-to-face identity and graph-to-array predicate equivalence;
- restricted-distance puncturing and full-distance lifting;
- disjoint Hamming-ball packing;
- exact-cover double counting and projected separation;
- the metric core of the perfect-code extension obstruction;
- the quantitative multiplicity estimate, deletion rescaling, Caro--Wei algebraic rearrangement, monotonicity, final pair-count combination, and exact `m=7,15,31,63` arithmetic;
- the finite `(6,2)` witness and exhaustive four-row exclusion.

GitHub Actions run `33898751152` and job `101107681395` passed at commit `fd8b7a16e90a57e8fa23fbe600cf83bb14b330f8` with Lean `4.33.1`, `lake build`, the unfinished-proof-marker gate, and bundled `leanchecker`.

The structural and quantitative theorems report only `propext`, `Classical.choice`, and `Quot.sound`. The finite exhaustive four-row exclusion separately uses a disclosed proposition-specific `native_decide` axiom.

## Not yet established

- Independent novelty confirmation for the graph--coding dictionary, perfect-code extension theorem, Hamming-family classification, or quantitative gap.
- One end-to-end Lean theorem assembling the quantitative incidence sums and the symbolic Hamming-ball cardinality formulas.
- Independent specialist review or author confirmation.
- Any claim that the work is field-changing, priority-confirmed, or publication-accepted.

The strongest justified public label is:

```text
candidate-new structural and quantitative theorem package; Lean-verified core; external review pending.
```
