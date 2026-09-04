# Subcube isolation as radius-covering arrays

## 1. Definitions

Write `Q_n` for the graph on `{0,1}^n` in which two words are adjacent when
they differ in one coordinate. For `r>=0`, let `N_r[D]` be the set of vertices
at Hamming distance at most `r` from a set `D`.

For integers `0<=m<=n`, define

```text
I_r(n,m)=min{|D| : Q_n-N_r[D] contains no copy of Q_(n-m)}.
```

Thus the parameter in Brešar--Rall Problem 2 is

```text
iota(Q_n,Q_k)=I_1(n,n-k).
```

Let `CA_r(M;m,n,q)` be a radius-covering array: an `M×n` array over a
`q`-symbol alphabet such that every restriction to `m` columns has covering
radius at most `r`. Let `CAN_r(m,n,q)` be the least possible number of rows.

## 2. Exact graph--coding equivalence

### Theorem 2.1

For every `0<=m<=n` and `r>=0`,

```text
I_r(n,m)=CAN_r(m,n,2).
```

In particular,

```text
iota(Q_n,Q_k)=CAN_1(n-k,n,2).
```

### Proof

First, every subgraph of `Q_n` isomorphic to `Q_j` is a coordinate
`j`-subcube. Label each ambient edge by the unique coordinate that it flips.
Every four-cycle in a hypercube alternates two labels, so opposite edges have
the same label. In `Q_j`, all edges in one intrinsic coordinate direction are
connected through a sequence of opposite-edge relations in four-cycles.
Hence an embedding assigns one fixed ambient coordinate to each intrinsic
direction. The labels at one vertex are distinct, and following paths from
that vertex shows that the image is exactly the face obtained by freeing those
`j` ambient coordinates.

Now let `S` be an `m`-set of coordinates and `a∈{0,1}^S`. The
codimension-`m` face

```text
F(S,a)={x∈{0,1}^n : x|_S=a}
```

is a copy of `Q_(n-m)`. For every `d∈Q_n`,

```text
dist(d,F(S,a))=d_H(d|_S,a),
```

because the free coordinates can be chosen to agree with `d`, while every
disagreement on `S` is unavoidable.

Consequently `F(S,a)` meets `N_r[D]` exactly when some row `d∈D` has
`d_H(d|_S,a)<=r`. Requiring this for every `S` and `a` says precisely that
the binary array whose rows are the elements of `D` is a
`CA_r(|D|;m,n,2)`. Taking minima proves the theorem. ∎

### Consequence for the 2026 conjecture

A dominating set in `Q_m` is the same as a binary radius-one covering code,
so

```text
gamma(Q_m)=K_2(m,1)=CAN_1(m,m,2).
```

Brešar--Rall's proposed equality is therefore equivalent to

```text
CAN_1(m,m+k,2)=K_2(m,1)       for all m,k>=1.
```

Colbourn--Kéri--Rivas Soriano--Schlage-Puchta proved the equality for one
extra binary column:

```text
CAN_r(m,m+1,2)=CAN_r(m,m,2)=K_2(m,r).
```

Thus `k=1` is always an equality case. The question is whether an optimal
covering code can remain optimal under two or more robust coordinate
extensions.

## 3. A robust-extension obstruction for perfect codes

For a `q`-ary Hamming space, write

```text
V_q(N,R)=sum_{i=0}^R binom(N,i)(q-1)^i
```

for the volume of a radius-`R` ball.

### Theorem 3.1 — perfect-code obstruction

Assume a perfect `q`-ary radius-`r` covering code of length `m` exists, so

```text
K_q(m,r)V_q(m,r)=q^m.
```

Let `ell>=1`. If

```text
V_q(m+ell,r+floor(ell/2))>q^ell V_q(m,r),
```

then

```text
CAN_r(m,m+ell,q)>K_q(m,r).
```

### Proof

Suppose an array `A` with exactly `M=K_q(m,r)` rows existed. Project `A`
onto any `m` columns. Those `M` projected words radius-`r` cover all `q^m`
words. The sum of their ball sizes is

```text
M V_q(m,r)=q^m.
```

Since their union already has size `q^m`, the balls are pairwise disjoint.
Thus every `m`-column projection is a perfect code and has minimum distance at
least `2r+1`.

Take two distinct full rows at distance `d`. Delete `ell` coordinates
containing as many disagreements as possible. The remaining distance must
still be at least `2r+1`, so

```text
d>=2r+1+ell.
```

Therefore radius-`r+floor(ell/2)` balls around the full rows are pairwise
disjoint in the length-`m+ell` Hamming space. The Hamming packing bound gives

```text
M V_q(m+ell,r+floor(ell/2))<=q^(m+ell).
```

Substituting `M=q^m/V_q(m,r)` contradicts the displayed strict inequality. ∎

### Corollary 3.2 — q-ary Hamming lengths

Let `q` be a prime power and

```text
m=(q^t-1)/(q-1),       t>=3.
```

Then

```text
CAN_1(m,m+2,q)>K_q(m,1).
```

Indeed the `q`-ary Hamming code is perfect, and

```text
V_q(m+2,2)-q^2V_q(m,1)
  =((q-1)^2 m(m+1-2q))/2>0.
```

### Corollary 3.3 — complete equality classification at binary Hamming codimensions

Let `m=2^t-1` with `t>=3`. Then, for every `k>=1`,

```text
iota(Q_(m+k),Q_k)=gamma(Q_m)    iff    k=1.
```

For `k=1`, this is the known parity-extension theorem for binary
radius-covering arrays. For `k>=2`, Corollary 3.2 gives strict inequality at
two extra columns, and monotonicity under adding columns preserves strictness.
This supplies an infinite, structurally explained family of counterexamples
to Problem 2.

### Quantitative strengthening

The separate note
[`quantitative-hamming-gap.md`](quantitative-hamming-gap.md) proves the
candidate bound

```text
iota(Q_(m+k),Q_k)
 >= K + ceil(3K m(m-3)/[4(m+2)(m+1)^4])
```

for `m=2^t-1`, `t>=3`, `k>=2`, and `K=2^m/(m+1)`. Thus the additive gap is
`Omega(2^m/m^4)`, not merely at least one.

## 4. Fixed-codimension phase transition

Put

```text
B(m,r)=sum_{j=0}^r binom(m,j).
```

### Theorem 4.1

For fixed binary `m` and `r`, as `n→∞`,

```text
CAN_r(m,n,2)=
  1                    if m<=r,
  2                    if r<m<=2r+1,
  Theta_(m,r)(log n)   if m>=2r+2.
```

### Proof

If `m<=r`, one row covers every projected word. If `r<m<=2r+1`, one row
does not suffice, while the two complementary constant rows cover every word:
every binary word is within distance `floor(m/2)<=r` of one of them.

Now assume `m>=2r+2`, and let an `M×n` array be radius-covering. Complement
columns independently so that the first row becomes all zero. This preserves
the radius-covering property and leaves only `2^(M-1)` possible normalized
column types.

No type can occur `m` times. If it did, selecting those columns would leave
only the two constant projected rows `0^m` and `1^m`. A word of weight `r+1`
is farther than `r` from both, because `m-(r+1)>=r+1`. Therefore every type
occurs at most `m-1` times, and

```text
n<=(m-1)2^(M-1),
M>=1+log_2(n/(m-1)).
```

For the upper bound, take `M` independent uniformly random binary rows. For a
fixed choice of `m` columns and a fixed target word, one row lands within
radius `r` with probability `B(m,r)/2^m`. By the union bound, a
radius-covering array exists whenever

```text
2^m binom(n,m)(1-B(m,r)/2^m)^M<1.
```

This gives `M=O_(m,r)(log n)`, completing the proof. ∎

### Corollary 4.2 — phase transition for ordinary subcube isolation

For the closed-neighborhood problem,

```text
iota(Q_n,Q_(n-m))=
  1              if m=1,
  2              if m=2 or 3,
  Theta_m(log n) if m>=4.
```

In particular, for every fixed `m>=4`,

```text
iota(Q_n,Q_(n-m))/gamma(Q_m)→∞.
```

A completely explicit sufficient condition for strict inequality is

```text
n>(m-1)2^(gamma(Q_m)-1).
```

## 5. The small case `(n,k)=(6,2)`

The 2010 radius-covering-array tables contain

```text
CAN_1(4,6,2)=5.
```

By Theorem 2.1 this yields

```text
iota(Q_6,Q_2)=5>4=gamma(Q_4).
```

The five-row witness in this repository and its Lean certificate remain useful
as an independently checkable illustration, but the numerical value must not
be presented as new.

## 6. Formal and novelty boundary

Lean now verifies:

1. every injective edge-preserving binary cube map is a coordinate embedding;
2. the exact distance-to-face identity;
3. the coordinate-face/radius-covering-array equivalence;
4. the arithmetic core of the two-column perfect-code obstruction;
5. the algebra and selected coefficients in the quantitative gap;
6. the finite `(6,2)` certificate.

The full minimization statement and the incidence-counting proof of the
quantitative theorem are not yet assembled end to end in Lean.

The following external inputs are explicitly identified:

1. radius-covering-array terminology and published small tables;
2. `CAN_r(m,m+1,2)=K_2(m,r)`;
3. existence and perfectness of Hamming codes;
4. standard sphere-packing and Caro--Wei inequalities.

The small value is known after translation. Public searches have not located
the exact graph/coding dictionary, perfect-code extension theorem, or
quantitative Hamming-family bound. That supports expert review; it is not a
priority certificate.
