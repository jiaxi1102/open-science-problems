# Proposed proof of q-Fibonomial unimodality for n = 4

## 1. Rational form

Set

\[
x=F_{m+1},\qquad y=F_{m+2}.
\]

Using `F_(m+3)=x+y`, `F_(m+4)=x+2y`, and `F_2,F_3,F_4=1,2,3`, the `n=4` q-Fibonomial is

\[
Q_m(q)=\frac{[x]_q[y]_q[x+y]_q[x+2y]_q}{[2]_q[3]_q}.
\]

Its degree is

\[
D=3x+4y-7.
\]

Since `[r]_q=(1-q^r)/(1-q)`,

\[
(1-q)Q_m(q)=
\frac{(1-q^x)(1-q^y)(1-q^{x+y})(1-q^{x+2y})}
     {(1-q)(1-q^2)(1-q^3)}.
\tag{1}
\]

Let

\[
G(q)=\frac1{(1-q)(1-q^2)(1-q^3)}=\sum_{t\ge0}g(t)q^t.
\]

The coefficient is the classical restricted-partition formula

\[
g(t)=\left\lfloor\frac{t^2+6t+12}{12}\right\rfloor,
\tag{2}
\]

with `g(t)=0` for negative `t`. In the Lean development, (2) is connected to `G` by the exact six-step denominator recurrence, not taken as an oracle.

## 2. First differences

Writing `A=q^x` and `B=q^y`, the numerator of (1) expands as

\[
(1-A)(1-B)(1-AB)(1-AB^2)
=1-A-B+A^2B+AB^3-A^3B^3-A^2B^4+A^3B^4.
\tag{3}
\]

If `c_k=[q^k]Q_m(q)`, then `[q^k](1-q)Q_m=c_k-c_{k-1}`. For `2k\le D`, every term in (3) beginning at exponent `x+3y` or later vanishes. Indeed,

\[
2k+7\le3x+4y
\]

and `x<=y` imply `k<x+3y`. Therefore

\[
c_k-c_{k-1}=\delta(x,y,k),
\tag{4}
\]

where

\[
\delta(x,y,k)=g(k)-g(k-x)-g(k-y)+g(k-(2x+y)).
\]

It remains to prove `delta>=0` in the first half.

## 3. Uniform floor bounds

Put

\[
P(t)=t^2+6t+12.
\]

From (2),

\[
P(t)-11\le12g(t)\le P(t).
\tag{5}
\]

For `m>=8`, Fibonacci monotonicity and the recurrence give

\[
x\ge34,\qquad 3x\le2y.
\tag{6}
\]

We now split according to which shifted terms in (4) are active.

### Case I: k < x

All shifted terms vanish, so `delta=g(k)>=0`.

### Case II: x <= k < y

Only the first shift is active. By (5),

\[
12\delta\ge P(k)-11-P(k-x)
=x(2k-x+6)-11>0.
\]

### Case III: y <= k < 2x+y

Here

\[
12\delta\ge E(k)-11,
\qquad
E(k)=P(k)-P(k-x)-P(k-y).
\]

A direct identity gives

\[
E(k)-E(2x+y)=(2x+y-k)(k-y+6)\ge0.
\]

At the right endpoint,

\[
E(2x+y)=-x^2+2xy-6x-12
\ge2x^2-6x-12>11,
\]

using `2y>=3x` and `x>=34`. Thus `delta>=0`.

### Case IV: 2x+y <= k and 2k <= D

All four terms in (4) are active. By (5),

\[
\begin{aligned}
12\delta
&\ge P(k)-P(k-x)-P(k-y)+P(k-2x-y)-22\\
&=x(3x+4y-2k-6)-22.
\end{aligned}
\]

The first-half inequality `2k+7<=3x+4y` makes the parenthesis at least `1`. Hence

\[
12\delta\ge x-22\ge12>0.
\]

This proves first-half monotonicity for every `m>=8`.

## 4. Finite initial range

For `m=0,...,7`, the first-half ranges are finite; the largest requires only `k<=96`. The Lean theorem `fibonacci_delta_nonnegative_small` exhausts these cases using explicit interval splitting and kernel-checked arithmetic. No external SAT/SMT certificate or native-code axiom is used.

Consequently, for every `m>=0` and every `k` with `2k<=D`,

\[
c_k-c_{k-1}\ge0.
\]

## 5. Symmetry finishes the proof

The q-Fibonomial coefficient sequence is algebraically symmetric, as recorded in the source literature. Therefore an increase through the midpoint reflects to a decrease after the midpoint. Thus `Q_m(q)` is unimodal for every `m`.

The general reflection step is formalized as `symmetric_firstHalf_unimodal`, and the complete specialization as `fibQCoeff_unimodal_of_symmetry`.
