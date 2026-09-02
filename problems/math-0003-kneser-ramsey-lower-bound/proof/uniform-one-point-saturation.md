# Uniform one-point saturation of the five-point construction

**Status:** proposed elementary proof for every `r >= 3`; the periodic trace
blocks, explicit anonymous fillers, and forcing contradictions are verified in
CI.

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

This is a rigidity theorem for the construction. It does not by itself prove
that a completely different coloring of `KG(3r+3,r)` cannot exist.

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

It is enough to exhibit one `P` for which the incident edges of `X_P` cannot
be colored. Choose

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
cyclic trace words with the required colors and then add anonymous fillers so
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

## 6. An elementary cyclic-interval filler lemma

We now give a direct construction of the anonymous fillers. No polyhedral or
weighted-coloring theorem is required.

### Lemma

Let `L=2q+1` be odd, let `m` be positive, and let

\[
d_0,d_1,\ldots,d_{L-1}
\]

be nonnegative integers satisfying, with indices modulo `L`,

\[
d_i+d_{i+1}\le m
\]

and

\[
\sum_i d_i\le qm.
\]

Then there are subsets

\[
F_i\subseteq\mathbb Z/m\mathbb Z
\]

such that

\[
|F_i|=d_i,
\qquad
F_i\cap F_{i+1}=\varnothing
\]

for every `i`.

### Proof

Define the available gap after position `i` by

\[
c_i=m-d_i-d_{i+1}\ge0
\]

and the total gap that we need by

\[
G=qm-\sum_i d_i\ge0.
\]

There is enough gap capacity, because

\[
\sum_i c_i-G
=(2q+1)m-2\sum_i d_i-\left(qm-\sum_i d_i\right)
=(q+1)m-\sum_i d_i
\ge m.
\]

Hence we may choose integers

\[
0\le g_i\le c_i,
\qquad
\sum_i g_i=G.
\]

For example, fill the capacities greedily until the remaining required gap is
zero.

Set `s_0=0` in `Z/mZ` and recursively define

\[
s_{i+1}=s_i+d_i+g_i\pmod m.
\]

Because

\[
\sum_i(d_i+g_i)=qm,
\]

we have `s_L=s_0`. Now take the cyclic interval

\[
F_i=\{s_i,s_i+1,\ldots,s_i+d_i-1\}\pmod m.
\]

The interval `F_{i+1}` begins after `F_i` and a gap of size `g_i`. Moreover,

\[
d_i+g_i+d_{i+1}\le d_i+c_i+d_{i+1}=m,
\]

so the two adjacent cyclic intervals do not overlap. The closing edge is
covered by the same calculation because `s_L=s_0`. This proves the lemma.

## 7. Applying the filler lemma

Consider either trace cycle

\[
S_0,S_1,\ldots,S_{L-1},
\qquad L=2q+1.
\]

At position `i`, an actual old `r`-set needs

\[
d_i=r-|S_i|
\]

anonymous filler points. Apply the lemma with

\[
m=|U|=2r-2.
\]

Adjacent traces are disjoint and have combined size at least two. Therefore

\[
d_i+d_{i+1}
=2r-(|S_i|+|S_{i+1}|)
\le 2r-2=m.
\]

Also, if `w=sum_i |S_i|`, then

\[
\sum_i d_i=Lr-w.
\]

Since `q=(L-1)/2`, the inequality

\[
\sum_i d_i\le q(2r-2)
\]

is equivalent to

\[
w\ge L+r-1,
\]

which was arranged explicitly for both periodic families in Sections 4 and
5.

Identify `U` with `Z/(2r-2)Z` and let the lemma produce `F_i`. Then

\[
A_i=S_i\cup F_i
\]

is an old `r`-set, is disjoint from `P`, and is disjoint from `A_{i+1}`. Its
old edge color to `A_{i+1}` is exactly the prescribed trace color.

The interval construction starts with `s_0=0`. Both trace families have the
same base trace `01`, hence the same base demand `r-2`. It therefore gives the
same initial filler set

\[
F_0=\{0,1,\ldots,r-3\}
\]

for both cycles. The lifted red- and blue-defect cycles pass through the same
old set

\[
A_0=\{0,1\}\cup F_0.
\]

## 8. Conclusion

Let `X_P={x} union P`. If `X_PA_0` is red, the lifted red-defect cycle forces
that same edge blue. If it is blue, the lifted blue-defect cycle forces it
red. Both choices are impossible, so even the single new vertex `X_P` cannot
be added. Therefore the entire one-point extension to `KG(3r+3,r)` is
impossible.

This proves one-point saturation for every `r >= 3`.

## 9. Executable verification boundary

The repository verifier checks:

1. every trace in the two base cycles and repeat blocks;
2. every cyclic disjointness relation;
3. every red/blue edge in the alternating words;
4. the exact length and total-trace-weight formulas;
5. every gap-capacity and total-gap inequality;
6. the explicit cyclic intervals and all resulting old `r`-sets;
7. the closing forcing contradiction for both colors;
8. equality of the two base old vertices;
9. every admissible demand vector for palette sizes through five and odd
   cycle lengths through seven;
10. the full construction for all ranks `3 <= r <= 1000` as a regression
    sweep.

The finite sweep is not being substituted for the universal proof. The proof
for arbitrary `r` is the displayed algebra and the constructive interval
lemma above. The remaining formalization target is to encode that elementary
lemma, the periodic trace recurrences, and their composition in Lean.

## 10. Why this matters

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
