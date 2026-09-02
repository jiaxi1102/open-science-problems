# Claim ledger

## Established inputs

- Brešar--Rall Problem 2 asks whether `ι(Q_n,Q_k)=γ(Q_(n-k))` for every `0<k<n`.
- Radius-covering arrays are established coding-theory objects.
- The 2010 tables record `CAN_1(4,6,2)=5`; this numerical value is prior art.
- The binary one-column equality `CAN_r(m,m+1,2)=K_2(m,r)` is established prior art.

## Proved in the current draft

- Every graph copy of `Q_k` in `Q_n` is a coordinate subcube.
- Radius-`r` hitting of all codimension-`m` subcubes is exactly the binary radius-covering-array property.
- For fixed `m,r`, the minimum is `1` for `m<=r`, `2` for `r<m<=2r+1`, and `Θ(log n)` for `m>=2r+2`.
- A perfect-code projection obstruction yields strict two-column extension inequalities whenever its Hamming-volume test fails.
- In particular, binary Hamming lengths `m=2^t-1`, `t>=3`, give `ι(Q_(m+k),Q_k)=γ(Q_m)` exactly for `k=1`.

## Formally verified now

- The coordinate-copy theorem.
- The exact face-distance identity and graph-to-array predicate equivalence.
- The arithmetic core of the binary two-column volume obstruction.
- The finite `(6,2)` witness and exhaustive four-row exclusion, with `native_decide` explicitly disclosed.

## Not yet established

- Independent novelty confirmation for the graph--coding dictionary or perfect-code extension theorem.
- End-to-end Lean verification of the perfect-code projection/packing argument.
- Independent specialist review or author confirmation.
- Any claim that the work is field-changing or publication-accepted.
