# Novelty and prior-art record

**Corrected search date:** 2026-09-02 (America/New_York)

## Executive correction

The first search pass used graph-isolation terminology only. That was not
enough. Under the exact coding-theory translation,

```text
ι(Q_n,Q_k) = CAN_1(n-k,n,2),
```

the finite value originally presented as a candidate discovery is

```text
ι(Q_6,Q_2) = CAN_1(4,6,2) = 5.
```

Colbourn, Kéri, Rivas Soriano, and Schlage-Puchta tabulated
`CAN_1(4,6,2)=5` in 2010. The numerical value and its radius-covering-array
interpretation are therefore prior art. It remains a valid counterexample
to the 2026 graph-theory question, but it must not be advertised as a newly
computed covering-array number.

## Primary sources checked

### The graph problem

Boštjan Brešar and Douglas F. Rall, *On the isolation numbers in graph
products*, arXiv:2608.25752v1, submitted 26 August 2026.

Problem 2 asks whether

```text
ι(Q_n,Q_k)=γ(Q_(n-k))
```

for every `0<k<n`.

### Radius-covering arrays

C. J. Colbourn, G. Kéri, P. P. Rivas Soriano, and
J.-C. Schlage-Puchta, “Covering and radius-covering arrays:
Constructions and classification,” *Discrete Applied Mathematics* 158
(2010), 1158--1180, DOI 10.1016/j.dam.2010.03.008.

The paper:

- defines `CA_r(M;s,n,q)` and `CAN_r(s,n,q)`;
- proves in Theorem 7.3 that
  `CAN_r(s,s+1,2)=CAN_r(s,s,2)=K_2(s,r)`;
- records `CAN_1(4,6,2)=5` in its binary table.

### Generalized surjective codes

J. Quistorff and J.-C. Schlage-Puchta, “On generalized surjective
codes,” *Studia Scientiarum Mathematicarum Hungarica* 48 (2011).

This is an equivalent coding formulation and supplies monotonicity and
small-row results relevant to the phase diagram.

## Claims now separated by status

### Established prior art

1. The radius-covering-array definition.
2. `CAN_r(m,m+1,2)=K_2(m,r)`.
3. `CAN_1(4,6,2)=5`.
4. Standard existence and parameters of q-ary Hamming perfect codes.
5. Standard Hamming sphere-packing bounds.
6. Basic monotonicity of `CAN_r(m,n,q)` in the number of columns.

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
   prevents a perfect optimal length-`m` covering code from extending to a
   radius-covering array with `ell` additional columns and the same number
   of rows.

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

5. **Unbounded separation**
   for each fixed `m>=4`,
   ```text
   ι(Q_n,Q_(n-m))/γ(Q_m) -> infinity.
   ```

These proofs are in `proof/structural-theory.md`.

### Novelty status

Targeted searches did not locate a paper stating the exact
subcube-isolation/radius-covering-array equivalence, the robust-extension
obstruction above, or its Hamming-family classification consequence.

That supports the status

```text
candidate-new structural result; priority not independently confirmed.
```

It does **not** justify “first,” “new,” or “groundbreaking” in a public
claim. Those words require review by specialists and, ideally, written
confirmation from the authors of the 2026 problem and researchers in
radius-covering arrays.

## Search queries

Graph terminology:

- `"iota(Q_n,Q_k)" radius covering array`
- `"subcube isolation" hypercube covering array`
- `"Q_k-isolation" hypercube code`
- `"hypercube isolation" "covering array"`
- `"On the isolation numbers in graph products" counterexample`
- `"Brešar" "Rall" "Problem 2" hypercube`

Coding terminology:

- `"radius-covering array" hypercube subcube`
- `"generalized surjective code" subcube`
- `"CAN_1" "m+2" perfect code`
- `"radius-covering array" perfect code extension`
- `"all puncturings" perfect code`
- `"every puncturing" Hamming code`
- `"robust extension" perfect code Hamming`
- `"two-coordinate puncturing" perfect code`
- `"CAN_r(s,s+2,q)" perfect`

Repositories and scholarly indexes were also searched for exact formulas
and terminology. No direct match was found as of the date above.

## Required external gates

1. Verify the graph-to-coding dictionary with a hypercube/product-graph
   specialist.
2. Verify Theorem 3.1 with a coding theorist familiar with covering arrays
   and perfect codes.
3. Ask Brešar and Rall whether the bridge or counterexample was already
   known to them.
4. Ask at least one radius-covering-array author or specialist whether the
   robust-extension obstruction is implicit in existing literature.
5. Complete the structural Lean formalization and independent proof audit.
