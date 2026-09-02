# Uniform one-point saturation of the five-point construction

**Status:** proposed proof for every `r >= 3`; finite trace blocks and all
arithmetic conditions are verified in CI. The only imported ingredient is the
standard integer-decomposition theorem for weighted colorings of odd cycles.

## 1. The theorem

Let `c_r` be the five-point coloring of

\[
KG(3r+2,r)
\]

used in `math-0003`. For every `r >= 3`, `c_r` is one-point saturated:

> No good red/blue coloring of `KG(3r+3,r)` restricts to `c_r` on the first
> `3r+2` ground points.

Thus the explicit lower-bound family cannot be enlarged by even one ground
point while preserving its old edges.

This statement is about the rigidity of the construction. It does not by
itself prove that some completely different coloring of `KG(3r+3,r)` cannot
exist.

## 2. Decoupling after one new ground point

Write the old ground set as

\[
D\mathbin{\dot\cup}W,
\qquad |D|=5,\quad |W|=3r-3,
\]

where `D={0,1,2,3,4}` carries its cyclic order and the coloring depends only
on traces in `D`.

Adjoin a new point `x`. Every new Kneser vertex has the form

\[
X_P=\{x\}\cup P,
\qquad P\in\binom{D\cup W}{r-1}.
\]

Any two new vertices contain `x`, so they are nonadjacent. Consequently, the
extension problem separates by `P` exactly as in the `r=3` analysis.

It is enough to exhibit a single pair `P` for which the incident edges of
`X_P` cannot be colored. Choose

\[
P\in\binom{W}{r-1}.
\]

There remain

\[
U=W\setminus P,
\qquad |U|=2r-2
\]

anonymous points available to build old neighbors of `X_P`.

## 3. Forcing cycles

Let `A_0,A_1,...,A_{L-1}` be old `r`-sets disjoint from `P`, with consecutive
sets disjoint cyclically. Their old edge colors form a word of length `L`.

If that word is

\[
RBRB\cdots R
\]

of odd length and the new edge `X_PA_0` is red, triangle avoidance forces the
new-edge colors alternately around the cycle and returns to `A_0` with blue.
This is a contradiction. We call this a **red-defect cycle**. A
blue-defect cycle has word

\[
BRBR\cdots B
\]

and rules out blue in the same way.

Two such cycles through the same old set `A_0` make both possible colors of
`X_PA_0` impossible.

Because `c_r` depends only on five-point traces, it suffices first to build
cyclic trace words with the required colors, then add anonymous fillers so
successive old sets become disjoint `r`-sets.

## 4. Red-defect trace family

Use the notation `01={0,1}`, `234={2,3,4}`, and so on. Start with the cyclic
trace list

\[
\mathcal R_0=(01,234,1,034,2).
\]

Its five edge colors are

\[
R,B,R,B,R,
\]

and the sum of its trace sizes is 10.

The final red edge `2--01` may be replaced successively by

\[
2,1,234,01,
\]

then

\[
234,0,23,01,
\]

then

\[
23,04,2,01.
\]

Each replacement turns one red edge into the color word `RBR`. Performing all
three returns the terminal trace to `2`. Therefore the six-trace block

\[
\mathcal B_R=(1,234,0,23,04,2)
\]

can be repeated arbitrarily.

After `t_R` repetitions, the red cycle has

\[
L_R=5+6t_R,
\qquad
w_R=10+10t_R,
\]

where `w_R` is the total trace size. Choose

\[
t_R=\max\left(0,\left\lceil\frac{r-6}{4}\right\rceil\right).
\]

Then

\[
6+4t_R\ge r,
\]

which is equivalent to

\[
w_R\ge L_R+r-1.
\]

## 5. Blue-defect trace family

Start with

\[
\mathcal Q_0=(01,3,012,4,3).
\]

Its edge colors are

\[
B,R,B,R,B,
\]

and its total trace size is 8.

The final blue edge `3--01` can be expanded by

\[
3,0,4,01,
\]

and the resulting final edge `4--01` by

\[
4,012,3,01.
\]

Together these substitutions return the terminal trace to `3`. Hence the
four-trace block

\[
\mathcal B_B=(0,4,012,3)
\]

may be repeated. After `t_B` repetitions,

\[
L_B=5+4t_B,
\qquad
w_B=8+6t_B.
\]

Take

\[
t_B=\max\left(0,\left\lceil\frac{r-4}{2}\right\rceil\right).
\]

Then

\[
4+2t_B\ge r,
\]

or equivalently

\[
w_B\ge L_B+r-1.
\]

## 6. Anonymous fillers from weighted odd-cycle coloring

Consider either trace cycle

\[
S_0,S_1,\ldots,S_{L-1},
\qquad L=2q+1.
\]

At position `i`, an actual old `r`-set needs

\[
d_i=r-|S_i|
\]

anonymous filler points. We seek subsets `F_i subseteq U` with

\[
|F_i|=d_i,
\qquad F_i\cap F_{i+1}=\varnothing.
\]

This is exactly a weighted coloring of the odd cycle `C_L` with `|U|=2r-2`
colors: an anonymous point may occur at any independent set of cycle
positions.

For an odd cycle, the stable-set polytope is defined by nonnegativity, its
edge inequalities, and the single odd-cycle inequality. Its stable-set
polytope has the integer decomposition property. Consequently, the required
filler sets exist whenever

\[
d_i+d_{i+1}\le 2r-2
\]

for every edge and

\[
\sum_i d_i\le q(2r-2).
\]

For our trace cycles, adjacent traces are disjoint and have total size at
least two. Hence

\[
d_i+d_{i+1}
=2r-(|S_i|+|S_{i+1}|)
\le 2r-2.
\]

Also

\[
\sum_i d_i=Lr-w.
\]

Because `q=(L-1)/2`, the odd-cycle inequality is equivalent to

\[
w\ge L+r-1,
\]

which was arranged explicitly in Sections 4 and 5.

Thus both trace cycles lift to cycles of actual old `r`-sets using the
`2r-2` points of `U`.

The two weighted colorings may initially use different filler subsets at the
common base trace `01`. Both base demands equal `r-2`; a permutation of the
anonymous palette `U` maps one base filler set to the other. Relabel the
second cycle by that permutation. The lifted red- and blue-defect cycles now
pass through the same old set

\[
A_0=\{0,1\}\cup F_0.
\]

## 7. Conclusion

Let `X_P={x} union P`. If `X_PA_0` is red, the lifted red-defect cycle forces
that same edge blue. If it is blue, the lifted blue-defect cycle forces it
red. Both choices are impossible, so the single new vertex `X_P` cannot be
added. Therefore the entire one-point extension to `KG(3r+3,r)` is impossible.

This proves one-point saturation for every `r >= 3`.

## 8. Imported theorem and verification boundary

The filler step uses the integer decomposition property for stable-set
polytopes of odd cycles. One convenient modern source is:

- Yohann Benchetrit, *Integer round-up property for the chromatic number of
  some h-perfect graphs*, Mathematical Programming 164 (2017), 261-281;
  arXiv:1406.0757. Theorem 4 proves the integer round-up property for
  t-perfect claw-free graphs, and the paper explicitly identifies this with
  the integer decomposition property of the stable-set polytope. Odd cycles
  are the basic non-perfect h-perfect graphs and are claw-free.

The repository verifier checks:

1. every trace in the two base cycles and repeat blocks;
2. every disjointness relation;
3. every red/blue edge in the alternating words;
4. the exact length and total-trace-weight formulas;
5. both weighted-cycle inequalities;
6. all ranks `3 <= r <= 1000` as a regression sweep.

The finite sweep is not being substituted for the universal proof. The proof
for arbitrary `r` is the displayed algebra plus the cited integer-decomposition
theorem. An end-to-end Lean formalization of the weighted odd-cycle filler
lemma remains a separate formalization target.

## 9. Why this matters

The lower-bound construction is not merely a collection of isolated finite
witnesses. It is a uniform family sitting exactly at a local extension
barrier. At every rank, a new ground point immediately creates a vertex whose
incident edge colors are obstructed by two odd forcing cycles.

This identifies a concrete structural mechanism behind the `+3` lower bound:

> five-point trace control creates a globally triangle-free coloring at
> `3r+2`, while alternating signed cycles make that same coloring maximally
> rigid against one-point growth.

The matching upper-bound problem is therefore not likely to yield to a greedy
extension argument. A proof of

\[
R_r^{KG}(3,3)\le 3r+3
\]

must show that **every** good coloring at `3r+2` has an obstruction of this
kind, or derive a different universal incompatibility at `3r+3`.
