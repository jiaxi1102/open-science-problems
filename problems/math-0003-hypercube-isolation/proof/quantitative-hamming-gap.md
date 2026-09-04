# A quantitative Hamming-family gap

## Status

This note strengthens the qualitative Hamming-family obstruction in
[`structural-theory.md`](structural-theory.md). The proof is self-contained,
and its algebraic core and explicit numerical instances are checked in Lean.
The full incidence argument has not yet been independently reviewed or
formalized end to end, so the exact bound remains a **candidate theorem**, not
a confirmed priority claim.

## Theorem

Let

```text
m = 2^t - 1,       t >= 3,
K = 2^m/(m+1) = gamma(Q_m),
M = iota(Q_(m+2), Q_2) = CAN_1(m,m+2,2).
```

Then, writing `s=M-K`,

```text
s >= ceil( 3 K m(m-3) / [4(m+2)(m+1)^4] ).                 (1)
```

Equivalently,

```text
M >= K + ceil( 3 K m(m-3) / [4(m+2)(m+1)^4] ).
```

Thus the additive failure of

```text
iota(Q_(m+2),Q_2) = gamma(Q_m)
```

is exponentially large along the binary Hamming lengths:

```text
M-K = Omega(2^m/m^4).
```

The relative bound is weaker,

```text
M/K >= 1 + (3/4+o(1))/m^3,
```

but the absolute gap diverges rapidly.

Some explicit consequences are:

| `m` | `K=gamma(Q_m)` | consequence of (1) |
|---:|---:|---:|
| 7 | 16 | `M >= 17` |
| 15 | 2,048 | `M >= 2,049` |
| 31 | 67,108,864 | `M >= 67,110,127` |
| 63 | 144,115,188,075,855,872 | `M >= K + 374,653,301,052` |

The first line is weaker than the published numerical bound
`21 <= CAN_1(7,9,2) <= 24`; the point of (1) is its uniform exponential
additive separation for every Hamming length.

## Proof

Set

```text
n = m+2.
```

Take an optimal binary radius-one covering array `A` with `M` distinct rows
and `n` columns. Its rows may be assumed distinct because deleting a duplicate
row preserves every covering condition.

For a two-element set `D` of deleted coordinates, let `A_D` be the projection
onto the remaining `m` coordinates. For each `y in Q_m`, define

```text
c_D(y) = number of rows of A_D at distance at most 1 from y.
```

Because `A` has strength `m` and radius one,

```text
c_D(y) >= 1                                                     (2)
```

for every `D` and `y`.

### Step 1: covering excess in each projection

Each projected row radius-one covers exactly `m+1` words, counted with
multiplicity. Hence

```text
sum_y c_D(y) = M(m+1).
```

The Hamming length assumption gives

```text
2^m = K(m+1).
```

Therefore the covering excess of every projection is

```text
E_D := sum_y (c_D(y)-1)
     = M(m+1)-2^m
     = (m+1)s.                                                  (3)
```

### Step 2: few close row pairs in each projection

Put

```text
P_D := sum_y binom(c_D(y),2).
```

This counts, for every unordered pair of distinct rows, the size of the
intersection of their projected radius-one balls.

For fixed `y`, there are `m+1` possible projected centers at distance at most
one from `y`. Every projected center has at most four lifts to a distinct
binary row of length `m+2`, because only two coordinates were deleted. Thus

```text
c_D(y) <= 4(m+1).                                               (4)
```

Combining (2) and (4),

```text
binom(c_D(y),2)
  = c_D(y)(c_D(y)-1)/2
  <= 2(m+1)(c_D(y)-1).
```

Using (3),

```text
P_D <= 2(m+1)E_D = 2(m+1)^2 s.                                 (5)
```

Let `e_D` be the number of unordered row pairs whose projected Hamming
distance is at most two. Two binary radius-one balls whose centers are at
distance at most two have at least two common words. Therefore every pair
counted by `e_D` contributes at least two to `P_D`, and (5) gives

```text
e_D <= (m+1)^2 s.                                              (6)
```

### Step 3: transfer projection bounds to the full array

Let `e` be the number of unordered row pairs of `A` whose full Hamming
distance is at most four.

Every such pair is counted by `e_D` for at least six choices of the deleted
coordinate pair `D`:

- at full distance four, delete any two of the four disagreeing coordinates,
  giving exactly `binom(4,2)=6` guaranteed choices;
- at distance three, any deletion containing a disagreement works, giving
  `binom(n,2)-binom(n-3,2)=3n-6 >= 6` choices;
- at distance at most two, every deletion works.

Consequently, summing (6) over the `binom(n,2)` deleted pairs,

```text
6e <= sum_D e_D
   <= binom(n,2)(m+1)^2 s.                                     (7)
```

### Step 4: there must be many close row pairs

Form a graph `G` on the `M` rows of `A`, joining two rows when their Hamming
distance is at most four. It has `e` edges.

An independent set in `G` is a binary code of length `n` and minimum distance
at least five. Radius-two Hamming balls about its codewords are disjoint, so
its size is at most

```text
alpha(G) <= 2^n / V,
V := 1+n+binom(n,2).                                            (8)
```

The Caro--Wei inequality followed by Cauchy--Schwarz gives

```text
alpha(G) >= sum_v 1/(deg(v)+1)
         >= M^2/(M+2e).
```

Combining this with (8),

```text
e >= (M^2 V/2^n - M)/2.                                       (9)
```

Because `M>=K`, and because the factor below is positive for `m>=7`,

```text
M(MV/2^n-1) >= K(KV/2^n-1).
```

Now `n=m+2` and

```text
V = 1+(m+2)+binom(m+2,2),
KV/2^n - 1
  = V/[4(m+1)] - 1
  = m(m-3)/[8(m+1)].
```

Thus (9) implies

```text
e >= K m(m-3)/[16(m+1)].                                      (10)
```

### Step 5: combine the two counts

Insert (10) into (7), use

```text
binom(n,2)=binom(m+2,2)=(m+2)(m+1)/2,
```

and simplify:

```text
s >= 6e/[binom(n,2)(m+1)^2]
  >= 3K m(m-3)/[4(m+2)(m+1)^4].
```

Since `s` is an integer, taking the ceiling proves (1). ∎

## Why this is stronger than the first obstruction

The perfect-code volume obstruction proves only

```text
M >= K+1.
```

The present argument measures how much unavoidable overlap occurs in all
`binom(m+2,2)` perfect-code projections simultaneously. A near-perfect
projection has little covering excess, forcing few close pairs after that
projection. But the full row set is too large to behave like a distance-five
code: sphere packing plus the Caro--Wei bound forces many close pairs. Each
full close pair survives as a close projected pair in several deletions. The
incompatibility yields a quantitative lower bound on the excess number of
rows.

## Verification and novelty boundary

The proof uses only:

1. the exact graph/radius-covering-array dictionary;
2. the binary Hamming perfect-code identity `K(m+1)=2^m`;
3. elementary incidence double counting;
4. the radius-two Hamming packing bound;
5. the Caro--Wei inequality and Cauchy--Schwarz.

`formal/HypercubeIsolation/QuantitativeGap.lean` checks the pointwise
multiplicity estimate, the deletion-pair rescaling, the Caro--Wei algebraic
rearrangement, the required quadratic monotonicity, the final combination,
and the exact `m=7,15,31,63` arithmetic. The incidence identities and the
Caro--Wei theorem are still represented in the human proof rather than one
end-to-end Lean theorem.

Searches through radius-covering-array, generalized-surjective-code, perfect
code, puncturing, and robust-projection terminology have not located this
exact quantitative bound. That is a reason to seek specialist review, not a
priority certificate.
