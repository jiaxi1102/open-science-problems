# Puncturing rigidity for robust covering arrays

## Theorem

Let `x,y` be words of length `N`, and let `d>0`. Suppose that after deleting
**every** set of `ell` coordinates, the two punctured words remain at Hamming
distance at least `d`. Then

```text
d_H(x,y) >= d + ell.
```

## Proof

Let `Delta` be the set of coordinates on which `x` and `y` disagree, and put
`h=|Delta|=d_H(x,y)`.

If `ell<=h`, delete any `ell` coordinates from `Delta`. The punctured distance
is exactly `h-ell`, so the hypothesis gives

```text
d <= h-ell,
```

and hence `h>=d+ell`.

If `ell>h`, extend `Delta` to an `ell`-set of coordinates and delete that set.
All disagreements disappear, so the punctured distance is zero, contradicting
`d>0`. Therefore the first case is the only possible one. ∎

## Role in the perfect-code obstruction

Suppose an `M x (m+ell)` radius-covering array has the minimum number
`M=K_q(m,r)` of rows and that a perfect radius-`r` code of length `m` exists.
Every `m`-column projection must then be a perfect code, so distinct projected
rows are separated by at least

```text
d=2r+1.
```

Applying the theorem to every pair of full rows gives minimum distance at
least

```text
2r+1+ell.
```

Consequently balls of radius `r+floor(ell/2)` around the full rows are
disjoint. This is the bridge from local perfection under every puncturing to
the global Hamming packing contradiction.

## Formal status

[`formal/HypercubeIsolation/Puncturing.lean`](../formal/HypercubeIsolation/Puncturing.lean)
formalizes the theorem for binary words and its radius-`r` corollary. The file
is included as an explicit root of the pinned Lean build.
