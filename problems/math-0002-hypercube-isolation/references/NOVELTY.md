# Novelty and prior-art record

**Latest audit:** 2026-09-04 (America/New_York)

## Executive correction

The original graph-only search was too narrow. Two established coding/design
translations must be treated as prior art:

1. ordinary binary covering arrays are exactly transversals of fixed-dimensional
   faces of a hypercube; and
2. radius-covering arrays are exactly generalized surjective codes with an
   allowed Hamming error radius.

Consequently, the finite identity

```text
ι(Q_6,Q_2)=CAN_1(4,6,2)=5
```

is not a new covering-array value. Colbourn, Kéri, Rivas Soriano, and
Schlage-Puchta classified it in 2010. The 2011 survey of Lawrence, Kacker, Lei,
Kuhn, and Forbes also explicitly describes ordinary covering arrays as
hypercube face transversals.

The defensible candidate contribution is narrower:

- recognize closed-neighborhood subcube isolation as the radius-one version of
  the face-transversal formulation;
- apply that translation to Brešar--Rall Problem 2;
- prove the perfect-code robust-extension obstruction;
- classify equality at every binary Hamming codimension;
- prove the quantitative exponential additive gap; and
- formulate the graph-isolation constant-to-logarithmic phase transition.

None of these candidate-new statements should be described publicly as new,
first, or groundbreaking before specialist and author review.

## Primary sources checked

### The graph problem

Boštjan Brešar and Douglas F. Rall, *On the isolation numbers in graph
products*, arXiv:2608.25752v1, submitted 26 August 2026.

Problem 2 asks whether

```text
ι(Q_n,Q_k)=γ(Q_(n-k))
```

for every `0<k<n`.

### Ordinary covering arrays as face transversals

Jim Lawrence, Raghu N. Kacker, Yu Lei, D. Richard Kuhn, and Michael Forbes,
*A Survey of Binary Covering Arrays*, Electronic Journal of Combinatorics 18
(2011), P84, DOI `10.37236/571`.

The survey states that a binary covering array of strength `t`, viewed as a set
of vertices of the `k`-cube, meets every `(k-t)`-dimensional face. Section 2.1
makes the equivalence explicit: a `t`-surjective subset of `{0,1}^k` is if and
only if it is a transversal of the `(k-t)`-faces.

This establishes the radius-zero geometric dictionary. Our radius-neighborhood
statement should be presented as its natural radius-`r` extension and its
application to graph isolation, not as the first connection between covering
arrays and cube faces.

### Radius-covering arrays

C. J. Colbourn, G. Kéri, P. P. Rivas Soriano, and
J.-C. Schlage-Puchta, *Covering and radius-covering arrays: Constructions and
classification*, Discrete Applied Mathematics 158 (2010), 1158--1180, DOI
`10.1016/j.dam.2010.03.008`.

The paper:

- defines `CA_r(M;s,n,q)` and `CAN_r(s,n,q)`;
- identifies the same objects with `s`-surjective codes of radius `r`;
- proves in Theorem 7.3 that
  `CAN_r(s,s+1,2)=CAN_r(s,s,2)=K_2(s,r)`;
- records `CAN_1(4,6,2)=5` and its unique equivalence class; and
- records the stronger first Hamming-length bound
  `21<=CAN_1(7,9,2)<=24`.

### Generalized surjective codes

J. Quistorff and J.-C. Schlage-Puchta, *On generalized surjective codes*,
Studia Scientiarum Mathematicarum Hungarica 48 (2011), 75--92, DOI
`10.1556/SScMath.2009.1140`.

The paper studies

```text
σ_q(n,s;r),
```

the minimum cardinality of a `q`-ary length-`n` code that, on every `s`
coordinates, comes within Hamming radius `r` of every target. This is exactly
the radius-covering-array parameter.

## Claims separated by status

### Established prior art

1. Binary covering arrays are hypercube face transversals (`r=0`).
2. Radius-covering arrays and generalized surjective codes are equivalent.
3. `CAN_r(m,m+1,2)=K_2(m,r)`.
4. `CAN_1(4,6,2)=5`, including uniqueness up to the standard array
   equivalences.
5. `21<=CAN_1(7,9,2)<=24`.
6. Exact one-row and repetition-code regimes for generalized surjective codes.
7. Existence and parameters of binary and `q`-ary Hamming perfect codes.
8. Standard Hamming sphere-packing bounds, Caro--Wei, and monotonicity under
   adding columns.

### Independently rediscovered or reverified here

1. The five-row witness for `(n,k)=(6,2)`.
2. Exhaustive nonexistence of a four-row witness.
3. The small exact value and uniqueness after translation from the 2010 table.
4. A Lean proof that every injective edge-preserving map between binary cubes
   is a coordinate embedding.

These are valuable verification artifacts, but do not carry mathematical
priority.

### Candidate structural contribution

The repository gives self-contained proofs of the following package.

1. **Radius-neighborhood isolation formulation**
   ```text
   I_r(n,m)=CAN_r(m,n,2),
   ```
   where `I_r(n,m)` is the minimum size of a set whose radius-`r`
   neighborhood meets every copy of `Q_(n-m)` in `Q_n`.

   This is an immediate radius-`r` extension of the known face-transversal
   dictionary once one proves that every graph copy of a binary cube is a
   coordinate face. Its novelty may be expository/application-level rather
   than foundational.

2. **Perfect-code robust-extension obstruction**
   ```text
   V_q(m+ell,r+floor(ell/2))>q^ell V_q(m,r)
   ```
   prevents a perfect optimal length-`m` covering code from extending to a
   radius-covering array with `ell` extra columns and the same number of rows.

3. **Infinite Hamming-family equality classification**
   for `m=2^t-1`, `t>=3`,
   ```text
   ι(Q_(m+k),Q_k)=γ(Q_m) iff k=1.
   ```

4. **Quantitative Hamming-family gap**
   with `K=2^m/(m+1)` and every `k>=2`,
   ```text
   ι(Q_(m+k),Q_k)
     >= K + ceil(3K m(m-3)/[4(m+2)(m+1)^4]).
   ```
   Thus the additive gap is `Omega(2^m/m^4)`.

5. **Fixed-codimension phase transition**
   ```text
   ι(Q_n,Q_(n-m)) = 1, 2, or Θ_m(log n)
   ```
   according as `m=1`, `m in {2,3}`, or `m>=4`.

6. **Unbounded ratio**
   for each fixed `m>=4`,
   ```text
   ι(Q_n,Q_(n-m))/γ(Q_m)->infinity.
   ```

The phase-transition order follows quickly from established coding
terminology and may be folklore. The perfect-code and quantitative statements
are the strongest candidate-new parts.

## Search outcome

Targeted searches used graph isolation, face-transversal, radius-covering-array,
generalized-surjective-code, perfect-code extension, and multi-puncturing
terminology. They located the ordinary face-transversal equivalence and the
known finite values, but no source stating the exact perfect-code obstruction,
the all-Hamming-length `k=1` if-and-only-if classification, or the quantitative
bound above.

A negative search is not a priority certificate. The current label is

```text
candidate-new theorem package; mathematical proof substantially verified;
priority and significance not independently confirmed.
```

## Search terms used

Graph terminology:

- `"iota(Q_n,Q_k)" radius covering array`
- `"subcube isolation" hypercube covering array`
- `"Q_k-isolation" hypercube code`
- `"hypercube isolation" "covering array"`
- `"On the isolation numbers in graph products" counterexample`

Geometric terminology:

- `"face transversal" hypercube covering array`
- `"piercing" cube faces covering array`
- `"hypercube computer" covering array face`
- `"transversal of s-faces" binary cube`

Coding terminology:

- `"radius-covering array" perfect code extension`
- `"CAN_1" "m+2" Hamming code`
- `"generalized surjective code" perfect code puncturing`
- `"all puncturings" perfect code`
- `"every two-coordinate puncturing" Hamming code`
- `"robust extension" perfect code Hamming`
- `"CAN_r(s,s+2,q)" perfect`
- `"sigma_2" "m+2" radius 1`

## Required external gates

1. Verify the perfect-code obstruction and quantitative incidence argument with
   a coding theorist familiar with covering arrays and generalized surjective
   codes.
2. Verify the cube-embedding reduction and graph-isolation interpretation with
   a hypercube/product-graph specialist.
3. Ask Brešar and Rall whether the radius-covering-array translation or a
   counterexample was already known to them.
4. Ask at least one radius-covering-array author or specialist whether the
   robust-extension obstruction or quantitative bound is implicit in existing
   work.
5. Complete end-to-end Lean formalization of the quantitative counting proof.
