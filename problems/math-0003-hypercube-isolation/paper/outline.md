# Manuscript outline

## Working title

**Subcube isolation in hypercubes is radius-covering: a coding-theoretic dictionary, perfect-code obstruction, and a phase transition**

## Abstract skeleton

Brešar and Rall asked whether the minimum number of vertices whose closed neighborhoods destroy every `Q_k` in `Q_n` always equals `γ(Q_(n-k))`. We identify the invariant exactly with the binary radius-covering-array number `CAN_1(n-k,n,2)`. This both corrects the status of the smallest counterexample, whose numerical value is established covering-array prior art, and yields structural consequences not visible in the graph formulation. We prove a sharp fixed-codimension transition, with constant behavior in codimensions at most three and logarithmic growth from codimension four onward. We also derive a perfect-code projection obstruction. For every binary Hamming length `m=2^t-1`, it implies `ι(Q_(m+k),Q_k)=γ(Q_m)` exactly when `k=1`, giving infinitely many strict inequalities with `Q_2` fixed. Lean verifies the coordinate-copy theorem, the graph-to-array bridge, and the arithmetic core; full formalization of the packing obstruction remains in progress.

## Sections

1. Introduction and corrected provenance
2. Every cube copy is a coordinate cube
3. Exact radius-covering-array dictionary
4. Fixed-codimension phase transition
5. Perfect projections and robust extension obstruction
6. Binary and q-ary Hamming families
7. The smallest graph-language example
8. Formal verification and trust boundary
9. Open problems: sharp asymptotic constants and equality classification

## Main theorem package

### Dictionary

`ι_r(Q_n,Q_(n-m)) = CAN_r(m,n,2)`.

### Phase transition

For fixed `m,r` as `n -> infinity`:

- `1` when `m<=r`;
- `2` when `r<m<=2r+1`;
- `Θ(log n)` when `m>=2r+2`.

### Perfect-code obstruction

If a perfect `q`-ary radius-`r` code of length `m` exists and

`K_q(m,r) V_q(m+ell,r+floor(ell/2)) > q^(m+ell)`,

then `CAN_r(m,m+ell,q)>K_q(m,r)`.

### Binary Hamming corollary

For `m=2^t-1`, `t>=3`, and `k>=1`:

`ι(Q_(m+k),Q_k)=γ(Q_m)` iff `k=1`.

## Review gates

- Green Lean CI for the coordinate-copy and bridge modules.
- End-to-end formal packing theorem, or an explicitly bounded formalization claim.
- Coding-theory review of the perfect-code obstruction.
- Graph-theory review of the exact dictionary.
- Author confirmation and expanded MathSciNet/Zentralblatt/Google Scholar prior-art search before any novelty claim.
