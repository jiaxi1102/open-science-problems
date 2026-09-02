# One-point saturation of the five-point `KG(11,3)` coloring

**Status:** proved for the explicit coloring; deterministic verification and
short human certificates included.  
**Scope:** this does **not** prove that every good coloring of `KG(11,3)` is
nonextendable, nor does it settle whether `KG(12,3)` has a good coloring.

## 1. Statement

Let `c_5` be the explicit five-point red/blue coloring of

\[
KG(11,3)
\]

used to prove the lower bound

\[
R_3^{KG}(3,3)\ge 12.
\]

Then `c_5` is **one-point saturated**:

> There is no good coloring of `KG(12,3)` whose restriction to the triples of
> the first eleven points is `c_5`.

In other words, the five-point construction cannot be extended by adjoining a
twelfth ground point while preserving its old edge colors.

This is stronger than observing that a particular heuristic extension fails.
Every possible coloring of every new edge is ruled out.

## 2. Why the extension problem decouples

Call the new ground point `x`. The old vertices remain the triples of `[11]`.
The new vertices are

\[
X_P=\{x\}\cup P,
\qquad P\in\binom{[11]}2.
\]

There are `binom(11,2)=55` such vertices. Any two contain `x`, so they are
never adjacent in the Kneser graph. Therefore no triangle contains two new
vertices, and the extension choices for distinct `X_P` are independent.

Fix a pair `P`. The old neighbors of `X_P` are the triples

\[
T\in\binom{[11]\setminus P}{3},
\]

of which there are `binom(9,3)=84`. Introduce one Boolean variable

\[
y_T=c(X_PT)
\]

for each such triple, with red=`true` and blue=`false`.

For disjoint old triples `T,U`, let their already-fixed old edge color be
`gamma=c_5(TU)`. The triangle `X_P,T,U` is nonmonochromatic exactly when

\[
(y_T\ne\gamma)\lor(y_U\ne\gamma).
\]

Thus each old red edge contributes

\[
\neg y_T\lor\neg y_U,
\]

and each old blue edge contributes

\[
y_T\lor y_U.
\]

The extension problem at `X_P` is therefore a monotone 2-SAT instance with
84 variables and 840 clauses. The whole one-point extension problem is the
conjunction of 55 independent instances of this form.

## 3. Complete classification of the 55 new vertices

The deterministic verifier gives:

| Type of `P` | Number | Individually extendable? |
|---|---:|---|
| two distinguished cycle points | 10 | yes |
| one distinguished and one anonymous point | 30 | no |
| two anonymous points | 15 | no |

Hence exactly 10 of the 55 individual new vertices admit incident-edge
colorings, while 45 do not. Since a full `KG(12,3)` extension would have to
add all 55 vertices, it is impossible.

The positive instances are accompanied by full 84-bit assignments and are
rechecked against all 840 original triangles. The negative instances are
proved by strongly connected components in their implication graphs and,
more importantly, by the explicit short certificates below.

## 4. The forcing rule

Suppose `TU` is an old edge of color `gamma`. If the new edge `X_PT` also has
color `gamma`, then the triangle `X_P,T,U` forces `X_PU` to have the opposite
color.

Consequently, along an old path whose successive edge colors alternate with
the currently forced new-edge color, a starting color propagates
uniquely. A path that returns to its starting triple with the opposite forced
color is a contradiction.

To prove an instance unsatisfiable, it suffices to give one such closed
forcing path beginning with red and another beginning with blue. We call the
pair a **signed odd bicycle**.

## 5. Anonymous–anonymous obstruction

By permuting the six anonymous points, it suffices to take

\[
P=\{5,6\},\qquad A=\{0,1,7\}.
\]

### Red is impossible

The old edges on

\[
A,\ \{2,8,9\},\ \{3,4,10\},\ A
\]

have colors

\[
\text{red},\ \text{blue},\ \text{red}.
\]

If `X_PA` is red, the first triangle forces the next new edge blue, the
second forces the next red, and the third forces `X_PA` blue. Contradiction.

### Blue is impossible

The old edges on

\[
A,
\{3,8,9\},
\{0,1,2\},
\{4,7,8\},
\{3,9,10\},
A
\]

have colors

\[
\text{blue},\ \text{red},\ \text{blue},\ \text{red},\ \text{blue}.
\]

Starting with `X_PA` blue propagates around this path and forces `X_PA` red.
Contradiction. Thus `X_{\{5,6\}}` cannot be added.

## 6. Distinguished–anonymous obstruction

The five-point coloring is invariant under the dihedral group on the five
cycle points and under arbitrary permutations of the six anonymous points.
It therefore suffices to take

\[
P=\{0,5\},\qquad A=\{1,6,7\}.
\]

### Red is impossible

The old path

\[
A,
\{2,8,9\},
\{3,4,6\},
\{1,2,7\},
\{8,9,10\},
A
\]

has edge colors

\[
\text{red},\ \text{blue},\ \text{red},\ \text{blue},\ \text{red}.
\]

Starting with `X_PA` red returns with `X_PA` forced blue.

### Blue is impossible

The old path

\[
A,
\{2,3,8\},
\{4,9,10\},
A
\]

has edge colors

\[
\text{blue},\ \text{red},\ \text{blue}.
\]

Starting with `X_PA` blue returns with `X_PA` forced red.

Thus no mixed pair can be added. Together with the preceding case, all 45
pairs involving at least one anonymous point are ruled out by two symmetry
orbits and four tiny paths.

## 7. Machine verification

`tools/verify_kneser_r3_one_point_saturation.py` performs all of the following
without third-party libraries:

1. reconstructs the explicit `KG(11,3)` coloring and checks all 15,400 old
   triangles;
2. constructs all 55 local 2-SAT instances;
3. solves each by an independently implemented SCC algorithm;
4. directly checks all 840 triangles for each of the 10 positive instances;
5. confirms that the remaining 45 instances are contradictory;
6. verifies every disjointness and color assertion in the four forcing paths;
7. verifies color invariance under generators of `D_5 x S_6`.

The output records a digest of the full 55-instance status and witness table,
so any change in the construction or variable ordering is visible.

## 8. What this teaches us

The result explains why the lower-bound construction does not casually grow
to `KG(12,3)`. The obstruction is already local: for most possible new
vertices, the old coloring presents two incompatible odd forcing cycles.
Any good coloring of `KG(12,3)`, should one exist, must therefore reorganize
many old edges rather than merely append a boundary layer.

This also gives a new search language. Instead of treating the exact problem
as a flat SAT instance, we can search for or rule out **signed odd bicycles**
in local neighborhoods and use them as small, human-readable conflict
certificates.

## 9. General-r extension principle

The decoupling is not special to `r=3`. Starting from any good coloring of

\[
KG(3r+2,r),
\]

adding a new ground point creates vertices

\[
X_P=\{x\}\cup P,
\qquad P\in\binom{[3r+2]}{r-1},
\]

with no edges among themselves. For each fixed `P`, extension is again a
monotone 2-SAT problem on old `r`-sets disjoint from `P`; every old edge
contributes one same-color-forbidding clause.

Therefore a uniform signed odd bicycle for even one orbit of `P` would prove
one-point saturation of the five-point construction for all `r`. Establishing
that general family is the next theoretical target. It would convert the
present `r=3` phenomenon into a structural theorem explaining the sharp
boundary at `3r+2` for the explicit construction.
