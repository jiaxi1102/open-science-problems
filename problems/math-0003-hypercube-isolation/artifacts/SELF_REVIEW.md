# Mathematical self-review

**Audit date:** 2026-09-04 (America/New_York)

## Scope

This audit checks the internal logic of the graph--coding dictionary, the fixed-codimension phase transition, the perfect-code extension obstruction, and the quantitative Hamming-family gap. It does not establish novelty or replace independent specialist review.

## Results of the audit

### Coordinate-copy and dictionary theorem

- The edge-color propagation argument uses the fact that every four-cycle in a hypercube alternates two coordinate directions.
- Distinct intrinsic directions map to distinct ambient coordinates because their incident edges at a vertex have distinct endpoints.
- The distance from a word to a coordinate face is exactly its number of disagreements on the fixed coordinates.
- Therefore radius-neighborhood face hitting is equivalent, in both directions, to the radius-covering-array predicate.

No missing induced-subgraph assumption is used: an injective edge-preserving copy of `Q_k` is forced to be coordinate by the four-cycle/common-neighbor structure.

### Fixed-codimension phase transition

The normalized-column count was rechecked carefully. After complementing each column to make the first row zero, there are `2^(M-1)`, not `2^M`, possible column types. In the regime `m>=2r+2`, a type repeated `m` times leaves only the two constant projected rows, while a target of weight `r+1` lies farther than `r` from both. Hence

```text
n <= (m-1) 2^(M-1).
```

The random upper bound uses exactly `2^m binom(n,m)` bad events and miss probability `(1-B(m,r)/2^m)^M` per event.

### Perfect-code extension obstruction

- Exact covering-volume equality forces projected radius-`r` balls to be pairwise disjoint.
- Disjoint radius-`r` balls force projected minimum distance at least `2r+1`.
- Deleting `ell` coordinates can reduce full Hamming distance by at most `ell`, so full-row distance is at least `2r+1+ell`.
- Radius `r+floor(ell/2)` balls around the full rows are therefore disjoint.
- The resulting packing inequality is exactly the negation of the stated volume-gap hypothesis.

For the binary radius-one, two-extra-column specialization,

```text
V_2(m+2,2)-4V_2(m,1)=m(m-3)/2.
```

### Quantitative Hamming-family gap

Let `K=2^m/(m+1)`, `M=K+s`, and delete any two coordinates.

1. The projected covering excess is exactly `(m+1)s`.
2. A target has at most `4(m+1)` covering full rows: `m+1` possible projected centers and four lifts per center.
3. Therefore the unordered ball-overlap count is at most `2(m+1)^2s`.
4. Every projected row pair at distance at most two has at least two common radius-one neighbors, so `e_D <= (m+1)^2s`.
5. A full pair at distance at most four is counted by at least six coordinate deletions; hence
   ```text
   6e <= binom(m+2,2)(m+1)^2s.
   ```
6. An independent set in the distance-at-most-four graph is a distance-five code. Radius-two packing and Caro--Wei/Cauchy--Schwarz give
   ```text
   e >= (M^2 V/2^(m+2)-M)/2.
   ```
7. This quadratic expression is increasing for `M>=K` when `m>=7`, and substitution at `M=K` yields
   ```text
   e >= K m(m-3)/(16(m+1)).
   ```
8. Combining the two estimates gives
   ```text
   s >= 3 K m(m-3)/[4(m+2)(m+1)^4].
   ```

The exact rational and integral evaluations for `m=7,15,31,63` were recomputed independently and agree with the Lean module.

## Formal verification cross-check

GitHub Actions run `33898751152`, job `101107681395`, passed at branch commit `fd8b7a16e90a57e8fa23fbe600cf83bb14b330f8` with Lean `4.33.1`. The structural, packing, perfect-projection, and quantitative modules use only Mathlib's standard logical axioms (`propext`, `Classical.choice`, and `Quot.sound`). The separate finite exhaustive `(6,2)` theorem still has the disclosed proposition-specific `native_decide` axiom.

## Remaining risks

1. The quantitative incidence sums and Hamming-ball cardinality formulas are not yet assembled into a single end-to-end Lean theorem.
2. The phase-transition and perfect-code arguments need independent coding-theory review.
3. No search can certify novelty; different terminology may hide an equivalent theorem.
4. The manuscript should remain a working draft until the original authors and at least one radius-covering-array specialist respond.
