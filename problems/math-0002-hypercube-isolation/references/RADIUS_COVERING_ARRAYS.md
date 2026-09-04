# Radius-covering-array dictionary and prior art

**Audit date:** 2026-09-04 (America/New_York)

## Exact parameter match

The hypercube problem uses the established parameter under two equivalent names:

```text
ι(Q_n,Q_k)=CAN_1(n-k,n,2)=σ_2(n,n-k;1).
```

Here:

- `CA_r(M;s,n,q)` is an `M×n` radius-`r` covering array of strength `s`;
- `CAN_r(s,n,q)` is its minimum number of rows;
- `σ_q(n,s;r)` is the minimum size of an `s`-surjective `q`-ary code of radius `r`.

The equivalence follows because a `Q_k` in `Q_n` is a coordinate `k`-face, and a closed neighborhood meets the face exactly when the fixed-coordinate projection is within Hamming distance one of its fixed pattern.

## Primary sources

### Colbourn–Kéri–Rivas Soriano–Schlage-Puchta (2010)

C. J. Colbourn, G. Kéri, P. P. Rivas Soriano, and J.-C. Schlage-Puchta, *Covering and radius-covering arrays: Constructions and classification*, Discrete Applied Mathematics 158 (2010), 1158–1180.

DOI: `10.1016/j.dam.2010.03.008`

Relevant content:

- definition of `CA_r(M;s,n,q)` and `CAN_r(s,n,q)`;
- classification of small radius-covering arrays in Table 6;
- numerical bounds and exact values in the Section 8 tables;
- Theorem 7.3: `CAN_r(s,s+1,2)=CAN_r(s,s,2)=K_2(s,r)`.

For the present problem, Table 6 reports the number of equivalence classes of binary strength-four, radius-one arrays:

| rows `M` | maximum classified columns `n` with an array | number at that maximum |
|---:|---:|---:|
| 4 | 5 | 1 |
| 5 | 6 | 1 |
| 6 | 8 | 1 |
| 7 | 9 | 33 |

The same classification has zero arrays at `(M,n)=(4,6),(5,7),(6,9),(7,10)`. Together with the numerical table, this yields

```text
CAN_1(4,n,2)=4,5,6,6,7,8 for n=5,6,7,8,9,10.
```

In particular, `CAN_1(4,6,2)=5` and the five-row array is unique up to row permutation, column permutation, and independent binary-symbol permutations in columns. These operations correspond exactly to reordering a vertex set and applying a hypercube automorphism.

### Quistorff–Schlage-Puchta (2011)

J. Quistorff and J.-C. Schlage-Puchta, *On generalized surjective codes*, Studia Scientiarum Mathematicarum Hungarica 48 (2011), 75–92.

DOI: `10.1556/SScMath.2009.1140`

Definition 3 calls a code `C⊂Q^n` `s`-surjective with radius `r` when every target on every `s` coordinates agrees with some codeword in at least `s-r` positions, and denotes the minimum cardinality by `σ_q(n,s;r)`. Thus their definition is identical to the radius-covering-array formulation.

## Consequences for the 2026 graph problem

Brešar and Rall prove

```text
ι(Q_n,Q_k)≥γ(Q_{n-k})
```

and ask whether equality always holds. Under the dictionary, setting `m=n-k` gives

```text
CAN_1(m,n,2)≥CAN_1(m,m,2)=K_2(m,1)=γ(Q_m).
```

So their lower bound is the usual monotonicity under adding columns, and their question asks whether that monotonicity is always equality.

The 2010 table already answers the universal question negatively at `(n,k)=(6,2)`, although it is expressed in coding/design language rather than isolation language.

## Corrected novelty assessment

The previous file `NOVELTY.md` recorded no prior proof after graph-terminology searches. That conclusion was too narrow. The exact finite value was known under radius-covering-array terminology.

Current assessment:

- `ι(Q_6,Q_2)=5`: **known after translation**;
- uniqueness of the minimum set up to cube automorphism: **known after translation**;
- the explicit witness and Lean/Python checks: **independent verification, not mathematical priority**;
- the exact identity with `CAN_1`/`σ_2`, its explicit application to Brešar–Rall Problem 2, and the fixed-codimension phase-transition formulation: **candidate new, priority not yet confirmed**.

## Search terms that must be included going forward

- `radius-covering array`
- `generalized surjective code`
- `s-surjective code radius`
- `CAN_r(s,n,q)`
- `sigma_q(n,s;r)`
- `covering array with radius`
- `covering code projection`

The terminology bridge is now part of the required prior-art protocol for this problem.
