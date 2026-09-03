# A robustness dichotomy for binary perfect codes

## 1. Robust extensions

For a binary radius-`r` covering code of length `m`, an `ell`-column robust
extension is an array with the same rows and `m+ell` columns such that deletion
of any `ell` columns leaves a radius-`r` covering code of length `m`. In
radius-covering-array notation, an optimal-size robust extension would give

```text
CAN_r(m,m+ell,2)=K_2(m,r).
```

The perfect-code obstruction in `structural-theory.md` implies that such an
extension cannot exist whenever

```text
V_2(m+ell,r+floor(ell/2)) > 2^ell V_2(m,r).
```

Here `V_2(N,R)=sum_{i=0}^R binom(N,i)`.

## 2. Repetition parameters are indefinitely robust

Let `m=2r+1`. The two constant rows

```text
0^n, 1^n
```

form a binary radius-covering array of strength `m`, radius `r`, and every
length `n>=m`. Indeed, any target word on `m` selected columns has weight `w`,
and

```text
min(w,m-w) <= floor(m/2)=r.
```

One row cannot cover all words because `m>r`. Therefore

```text
CAN_r(m,n,2)=2=K_2(m,r)                 for every n>=m.
```

Thus binary repetition perfect codes admit arbitrarily many robust extension
columns without increasing the number of rows.

## 3. Nontrivial Hamming parameters fail after two columns

For a binary Hamming length

```text
m=2^t-1,  t>=3,
```

a perfect radius-one code exists and `V_2(m,1)=m+1`. For two extra columns,

```text
2 V_2(m+2,2) - 8 V_2(m,1) = m(m-3) > 0.
```

Equivalently,

```text
V_2(m+2,2) > 4 V_2(m,1).
```

The perfect-code obstruction gives

```text
CAN_1(m,m+2,2) > K_2(m,1).
```

Monotonicity in the number of columns then gives strict inequality for every
larger extension. The exceptional Hamming length `m=3` is exactly the
repetition case `m=2r+1` and is indefinitely robust.

## 4. The binary Golay parameters also fail after two columns

The binary Golay perfect-code parameters are

```text
m=23, r=3, K_2(23,3)=4096,
V_2(23,3)=1+23+253+1771=2048.
```

For two extra columns, the packing radius in the obstruction is four, and

```text
V_2(25,4)
  = 1+25+300+2300+12650
  = 15276
  > 8192
  = 4 V_2(23,3).
```

Therefore

```text
CAN_3(23,25,2) > 4096.
```

Again, the same strict inequality persists for every number of extension
columns at least two.

## 5. Dichotomy

Using the standard classification of binary perfect-code parameter sets, the
preceding calculations give the following statement.

### Theorem (binary perfect-code robustness dichotomy)

Among binary perfect-code parameter families:

1. repetition parameters `m=2r+1`, with two codewords, admit optimal-size
   radius-covering arrays of arbitrary length;
2. every nontrivial Hamming parameter set and the binary Golay parameter set
   admit the known one-column extension where applicable, but no two-column
   robust extension with the perfect-code number of rows.

In particular, nontrivial binary perfect codes are *locally optimal but
maximally fragile*: requiring robustness to deletion of any two columns forces
strictly more codewords.

## 6. Ternary Golay check

The same general obstruction is not intrinsically binary. For the ternary
Golay parameters `m=11,r=2`,

```text
V_3(11,2)=1+22+220=243,
V_3(13,3)=1+26+312+2288=2627,
9 V_3(11,2)=2187.
```

Hence

```text
CAN_2(11,13,3) > K_3(11,2)=729.
```

This supplies a second sporadic perfect-code instance and shows that the
robust-extension principle extends naturally beyond binary hypercubes.

## 7. Formalization boundary

The general puncturing rigidity step is formalized in
[`formal/HypercubeIsolation/Puncturing.lean`](../formal/HypercubeIsolation/Puncturing.lean).
The Hamming-family polynomial identity is formalized in
[`formal/HypercubeIsolation/StructuralTheory.lean`](../formal/HypercubeIsolation/StructuralTheory.lean).
The finite Golay volume evaluations and the abstract disjoint-ball packing
lemma are the next Lean targets.

The parameter classification and existence of the Hamming/Golay perfect codes
are external coding-theory inputs and must be cited rather than reproved.
Novelty of the robustness dichotomy remains subject to coding-theory review.
