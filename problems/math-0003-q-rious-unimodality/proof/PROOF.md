# Proposed counterexample to q-rious unimodality

Let

\[
\mathbf a=(12,5,3,2),\qquad
\mathbf b=(9,6,4,1,1,1).
\]

Write

\[
D(\mathbf a,\mathbf b;q)
 =\frac{[12]![5]![3]![2]!}
 {[9]![6]![4]![1]!^3},
\qquad [n]=1+q+\cdots+q^{n-1}.
\]

The goal is to verify that the pair satisfies Landau's criterion while
\((1+q)D(\mathbf a,\mathbf b;q)\) is not unimodal.

## 1. Balance, height, and coprimality

Both tuples have sum 22:

\[
12+5+3+2=9+6+4+1+1+1=22.
\]

The height is \(6-4=2\). The gcd of all ten entries is 1, and the two
tuples have no common entry.

## 2. Landau's criterion

Define

\[
F(x)=\lfloor12x\rfloor+\lfloor5x\rfloor+
\lfloor3x\rfloor+\lfloor2x\rfloor-
\lfloor9x\rfloor-\lfloor6x\rfloor-
\lfloor4x\rfloor-3\lfloor x\rfloor.
\]

Since the pair is balanced, \(F(x+1)=F(x)\). More directly, because every
entry divides 180, put \(k=\lfloor180x\rfloor\). The identity

\[
\left\lfloor\frac y d\right\rfloor
 =\left\lfloor\frac{\lfloor y\rfloor}{d}\right\rfloor
\quad(d\in\mathbb Z_{>0})
\]

gives

\[
F(x)=G(k),
\]

where integer division is used in

\[
G(k)=
\left\lfloor\frac{k}{15}\right\rfloor+
\left\lfloor\frac{k}{36}\right\rfloor+
\left\lfloor\frac{k}{60}\right\rfloor+
\left\lfloor\frac{k}{90}\right\rfloor-
\left\lfloor\frac{k}{20}\right\rfloor-
\left\lfloor\frac{k}{30}\right\rfloor-
\left\lfloor\frac{k}{45}\right\rfloor-
3\left\lfloor\frac{k}{180}\right\rfloor.
\]

Balance also gives \(G(k+180)=G(k)\). It is therefore enough to inspect
\(k=0,\ldots,179\). Exact integer evaluation gives only the values 0, 1,
and 2, occurring 68, 44, and 68 times respectively. In particular,
\(F(x)\ge 0\) for every real \(x\), which is Landau II and hence is stronger
than the nonnegative-\(x\) condition required by Conjecture 5.

The Lean proof performs this reduction symbolically and closes the 180
finite residue cases in the kernel.

## 3. Exact q-factorial quotient

Cancel consecutive q-factorials:

\[
\begin{aligned}
D(q)
&=\frac{[12]![5]![3]![2]!}{[9]![6]![4]!}\\
&=[10][11][12]\,[5]\,\frac{[3]![2]!}{[6]!}\\
&=\frac{[2][10][11][12]}{[4][6]}.
\end{aligned}
\]

Factoring q-integers into cyclotomic polynomials gives

\[
D(q)=\Phi_2(q)\Phi_5(q)\Phi_{10}(q)\Phi_{11}(q)\Phi_{12}(q).
\]

Thus \(D(q)\in\mathbb Z[q]\). Exact expansion yields

\[
\begin{aligned}
D(q)= {}&1+2q+2q^2+2q^3+3q^4+4q^5+5q^6+6q^7+7q^8+8q^9\\
&+8q^{10}+7q^{11}+7q^{12}+8q^{13}+8q^{14}+7q^{15}\\
&+6q^{16}+5q^{17}+4q^{18}+3q^{19}+2q^{20}+2q^{21}+2q^{22}+q^{23}.
\end{aligned}
\]

The Lean certificate does not rely on polynomial division: it proves the
cross-multiplied identity

\[
[9]![6]![4]![1]!^3D(q)=[12]![5]![3]![2]!
\]

directly in \(\mathbb Z[q]\).

## 4. Non-unimodality

Multiplication by \(1+q\) adds adjacent coefficients. The full sequence is

\[
(1,3,4,4,5,7,9,11,13,15,16,15,14,15,16,15,13,11,9,7,5,4,4,3,1).
\]

In particular,

\[
[q^{10}](1+q)D=16,\qquad
[q^{12}](1+q)D=14,\qquad
[q^{14}](1+q)D=16.
\]

Suppose the sequence had a mode \(m\). If \(m\le12\), the sequence would be
nonincreasing from 12 to 14, forcing \(14\ge16\). If \(m>12\), it would be
nondecreasing from 10 to 12, forcing \(16\le14\). Both are impossible.
Therefore \((1+q)D(q)\) is not unimodal.

## 5. Consequence and scope

This pair satisfies the hypotheses of Warnaar--Zudilin Conjecture 5 but not
its conclusion, so it is a counterexample to the q-rious **unimodality**
conjecture as stated.

It is not a counterexample to the original q-rious positivity conjecture:
all coefficients of \(D(q)\) displayed above are nonnegative.
