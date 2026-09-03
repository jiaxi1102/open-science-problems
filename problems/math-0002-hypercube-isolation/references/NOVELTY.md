# Novelty and prior-art check

**Latest search date:** 2026-09-02 (America/New_York)

## Claims checked

The investigation now separates four statements that initially appeared to
be one claim.

1. The numerical value `ι(Q_6,Q_2)=5`.
2. The exact identity between hypercube subcube-isolation numbers and binary
   radius-covering-array numbers.
3. The perfect-code robust-extension obstruction and its infinite Hamming
   family.
4. The fixed-codimension constant/logarithmic phase transition.

## Corrected status of the small value

The finite parameter is not new. Colbourn, Kéri, Rivas Soriano, and
Schlage-Puchta, *Covering and radius-covering arrays: Constructions and
classification* (2010), tabulate

```text
CAN_1(4,6,2)=5.
```

The exact graph--coding identity therefore turns this old table entry into

```text
ι(Q_6,Q_2)=5.
```

The initial graph-only search missed the established coding-theory term.
The repository preserves the balanced-column proof, Python enumeration, and
Lean certificate as independent verification, but makes no novelty claim
for the value.

The same source proves in Theorem 7.3 that

```text
CAN_r(m,m+1,2)=K_2(m,r),
```

which supplies the positive one-extra-column case used in the structural
classification.

Its exact-value table also gives, for example, a lower bound strictly above
`K_2(7,1)=16` for `CAN_1(7,9,2)`. Thus the first binary Hamming instance is
already numerically visible in prior art. The candidate contribution is the
uniform perfect-code proof and its graph-theoretic interpretation, not that
individual parameter value.

## Candidate contribution

The current candidate-new contribution is the package consisting of:

```text
I_r(n,m)=CAN_r(m,n,2),
```

where `I_r(n,m)` is radius-`r` isolation of codimension-`m` subcubes;

an obstruction saying that a perfect radius-`r` code of length `m` cannot
extend to an `m+ell` column radius-covering array with the same number of
rows whenever

```text
V_q(m+ell,r+floor(ell/2)) > q^ell V_q(m,r);
```

and, for binary Hamming lengths `m=2^t-1`, `t>=3`, the classification

```text
ι(Q_(m+k),Q_k)=γ(Q_m)  iff  k=1.
```

The fixed-codimension consequence is

```text
ι(Q_n,Q_(n-m)) = 1            for m=1,
                 2            for m=2,3,
                 Θ_m(log n)   for m>=4.
```

## Search scope

Searches covered graph-isolation terminology, covering-array terminology,
generalized surjective codes, perfect-code extensions, puncturing, robust
covering codes, and exact parameter notation. Representative queries
included:

- `"iota(Q_6,Q_2)"`
- `"isolation number" hypercube subcube`
- `"radius-covering array" hypercube isolation`
- `"CAN_1(4,6,2)"`
- `"CAN_1(7,9,2)"`
- `"CAN_1(m,m+2,2)" Hamming code`
- `"perfect code" "radius-covering array"`
- `"generalized surjective code" perfect code`
- `"puncturing" "generalized surjective code"`
- `"robust" puncturing perfect Hamming code covering radius`

The primary sources inspected were:

- Brešar--Rall, *On the isolation numbers in graph products*,
  arXiv:2608.25752v1 (2026), especially Problem 2;
- Colbourn--Kéri--Rivas Soriano--Schlage-Puchta (2010), definitions, exact
  tables, and Theorem 7.3;
- Quistorff--Schlage-Puchta, *On generalized surjective codes* (2011), which
  studies the same coding object under `s`-surjective-with-radius notation
  and includes recursive bounds and exact small cases.

## Outcome

No source located in these searches states the graph--coding identity in the
form above, the general perfect-code volume obstruction, or the resulting
binary Hamming-codimension `iff k=1` classification. This is evidence for
further expert review, not a priority certificate. The structural proof is
short enough that it may be an unpublished folklore consequence of coding
and covering-array theory.

## Required external gate

Before any publication-level novelty claim:

1. obtain review from a radius-covering-array or coding-theory expert;
2. obtain review from a graph theorist familiar with subgraph isolation;
3. send the corrected result to Brešar and Rall;
4. ask specifically whether the exact dictionary or perfect-code
   obstruction is known under alternate terminology;
5. complete or clearly delimit the Lean formalization of the full packing
   argument.

Current novelty label:

```text
small numerical result: not new
structural package: no prior source located; priority unconfirmed
```
