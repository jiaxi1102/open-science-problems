# Novelty and prior-art record

**Corrected and extended search date:** 2026-09-04 (America/New_York)

## Executive correction

The first search pass used graph-isolation terminology only. That was not sufficient. Under the exact coding-theory translation

```text
ι(Q_n,Q_k) = CAN_1(n-k,n,2),
```

the finite value originally presented as a candidate discovery is

```text
ι(Q_6,Q_2) = CAN_1(4,6,2) = 5.
```

Colbourn, Kéri, Rivas Soriano, and Schlage-Puchta tabulated `CAN_1(4,6,2)=5` in 2010. The numerical value and its radius-covering-array interpretation are therefore prior art. It remains a valid counterexample to the 2026 graph-theory question, but it must not be advertised as a newly computed covering-array number.

The same tables give the stronger first Hamming-length numerical interval

```text
21 <= CAN_1(7,9,2) <= 24.
```

Thus the `m=7` member of the Hamming-family theorem is not a new numerical lower bound. The candidate contribution is the exact graph--coding dictionary, a uniform proof for every Hamming length, the fixed-codimension phase theorem, and the quantitative all-length additive-gap estimate.

## Primary sources checked

### The graph problem

Boštjan Brešar and Douglas F. Rall, *On the isolation numbers in graph products*, arXiv:2608.25752v1, submitted 26 August 2026.

Problem 2 asks whether

```text
ι(Q_n,Q_k)=γ(Q_(n-k))
```

for every `0<k<n`.

### Radius-covering arrays

C. J. Colbourn, G. Kéri, P. P. Rivas Soriano, and J.-C. Schlage-Puchta, “Covering and radius-covering arrays: Constructions and classification,” *Discrete Applied Mathematics* 158 (2010), 1158--1180, DOI `10.1016/j.dam.2010.03.008`.

The paper:

- defines `CA_r(M;s,n,q)` and `CAN_r(s,n,q)`;
- proves in Theorem 7.3 that `CAN_r(s,s+1,2)=CAN_r(s,s,2)=K_2(s,r)`;
- records `CAN_1(4,6,2)=5`;
- records `21 <= CAN_1(7,9,2) <= 24`.

### Generalized surjective codes

J. Quistorff and J.-C. Schlage-Puchta, “On generalized surjective codes,” *Studia Scientiarum Mathematicarum Hungarica* 48 (2011).

This gives an equivalent coding formulation and supplies monotonicity, recursive inequalities, and exact small-row regimes relevant to the phase diagram.

### Standard coding and extremal inputs

The current proof also uses established facts about Hamming perfect codes, Hamming sphere packing, and the Caro--Wei lower bound for graph independence number. These are inputs, not claimed contributions.

## Claims separated by status

### Established prior art

1. Radius-covering arrays and generalized surjective codes.
2. `CAN_r(m,m+1,2)=K_2(m,r)`.
3. `CAN_1(4,6,2)=5`.
4. `21 <= CAN_1(7,9,2) <= 24`.
5. Exact one-row and two-row generalized-surjective-code regimes.
6. Existence and parameters of q-ary Hamming perfect codes.
7. Hamming sphere-packing bounds.
8. The Caro--Wei inequality.
9. Monotonicity of `CAN_r(m,n,q)` in the number of columns.

### Self-contained results proved in this repository

1. **Exact graph--coding equivalence**
   ```text
   I_r(n,m)=CAN_r(m,n,2),
   ```
   where `I_r(n,m)` is radius-`r` isolation of codimension-`m` subcubes.

2. **Perfect-code robust-extension obstruction**
   ```text
   V_q(m+ell,r+floor(ell/2)) > q^ell V_q(m,r)
   ```
   prevents a perfect optimal length-`m` covering code from extending to a radius-covering array with `ell` extra columns and the same number of rows.

3. **Infinite Hamming-family classification**
   for `m=2^t-1`, `t>=3`,
   ```text
   ι(Q_(m+k),Q_k)=γ(Q_m) iff k=1.
   ```

4. **Fixed-codimension phase transition**
   ```text
   ι(Q_n,Q_(n-m)) = 1, 2, or Θ_m(log n)
   ```
   according as `m=1`, `m in {2,3}`, or `m>=4`.

5. **Unbounded multiplicative separation**
   for each fixed `m>=4`,
   ```text
   ι(Q_n,Q_(n-m))/γ(Q_m) -> infinity.
   ```

6. **Quantitative binary Hamming-family gap**
   with `K=2^m/(m+1)` and `m=2^t-1`, `t>=3`,
   ```text
   CAN_1(m,m+2,2)-K
     >= ceil(3 K m(m-3) / [4(m+2)(m+1)^4]).
   ```
   Consequently the additive gap is `Ω(2^m/m^4)`.

Items 1--6 are presently candidate-new formulations or consequences. Their proofs are self-contained in the repository, but priority has not been independently confirmed.

## Searches for the structural and quantitative package

Targeted searches through 4 September 2026 used graph, coding, puncturing, robust-projection, perfect-code, and quantitative terminology. Representative queries included:

- `"subcube isolation" hypercube covering array`
- `"Q_k-isolation" hypercube code`
- `"hypercube isolation" "covering array"`
- `"radius-covering array" hypercube subcube`
- `"generalized surjective code" subcube`
- `"CAN_1" "m+2" perfect code`
- `"radius-covering array" perfect code extension`
- `"perfect-code extension" covering array`
- `"robust extension" "covering code" Hamming`
- `"all puncturings" "perfect code" Hamming`
- `"every puncturing" "covering code"`
- `"two-coordinate puncturing" perfect code`
- `"CAN_r(s,s+2,q)" perfect`
- `"generalized surjective code" Hamming family`
- `"radius-covering array" Caro-Wei`
- `"covering array" quantitative gap perfect code`
- `"CAN_1(m,m+2,2)" lower bound`

The searches recovered the foundational radius-covering-array literature, generalized-surjective-code literature, ordinary punctured/shortened Hamming-code papers, and the 2026 graph paper. They did not locate the exact graph dictionary, the displayed robust-extension criterion, the all-Hamming-length equality classification, or the displayed quantitative gap formula.

This is evidence for requesting expert review, not a novelty certificate. The fixed-codimension logarithmic order may be folklore once the coding translation is noticed. The quantitative theorem may also exist under a different extremal-set or robust-covering-code terminology.

## Current novelty label

```text
candidate-new structural and quantitative theorem package;
known finite seed corrected to prior art;
priority not independently confirmed.
```

The words “first,” “new,” and “groundbreaking” should not appear in a public claim until specialists confirm priority and the argument survives independent review.

## Required external gates

1. Verify the coordinate-copy and graph-to-coding dictionary with a hypercube/product-graph specialist.
2. Verify the perfect-code obstruction and quantitative incidence proof with a coding theorist familiar with generalized surjective codes.
3. Ask Brešar and Rall whether the bridge or counterexample was already known to them.
4. Ask at least one radius-covering-array author or specialist whether the robust-extension obstruction or quantitative gap is implicit in existing literature.
5. Complete the end-to-end Lean incidence/cardinality assembly.
6. Preserve the known-value correction prominently in every abstract, README, and submission draft.
