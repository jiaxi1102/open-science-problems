# Exact two-cover threshold research

**Status:** active certified search; no exact-threshold theorem is claimed in
this branch until every required UNSAT result has an independently checked
proof trace.

## Target invariant

For a finite graph `G`, write

\[
\tau_2(G)=\min_{E(G)\subseteq E(H_1)\cup E(H_2)}
           \max\{\chi_f(H_1),\chi_f(H_2)\}.
\]

The merged result and the strengthened parent branch give

\[
\frac{14}{5}\le \tau_2(KG(8,2))\le3.
\]

This branch tests a structural route to the exact value

\[
\tau_2(KG(8,2))=3.
\]

## Two finite statements

### A. Monochromatic Petersen lemma

Every red/blue edge-colouring of `KG(8,2)` with no monochromatic triangle
contains a monochromatic induced `KG(5,2)`, equivalently a monochromatic
Petersen graph supported on the ten two-subsets of some five ground points.

The `petersen` CNF is satisfiable exactly when this statement has a
counterexample. It has 210 variables and 953 clauses.

### B. Petersen-to-dual-template lemma

Fix a red Petersen graph on ground set

\[
T=\{3,4,5,6,7\},\qquad S=[8]\setminus T=\{0,1,2\}.
\]

For a red-independent family `I` of Kneser vertices, the candidate lemma is

\[
|I|+\left|I\cap\binom S2\right|\le10.
\]

The `petersen-template` CNF is satisfiable exactly when a triangle-free
colouring with the fixed red Petersen graph violates this inequality. It has
838 variables and 2,256 clauses. Ground-set symmetry and colour
complementation turn one fixed UNSAT certificate into the general statement.

The inequality makes the following fractional-colouring dual weights feasible
for the red graph:

\[
y_e=\begin{cases}
1/5,&e\in\binom S2,\\
1/10,&e\notin\binom S2.
\end{cases}
\]

Indeed every red-independent set has total weight at most one, while

\[
\sum_e y_e=3\cdot\frac15+25\cdot\frac1{10}=\frac{31}{10}.
\]

Thus statement B implies that the colour containing the Petersen graph has
fractional chromatic number at least `31/10`.

## Consequence if both statements certify UNSAT

Any edge partition with both colour graphs of fractional chromatic number
strictly below three is triangle-free. Statement A then supplies a
monochromatic Petersen graph, and statement B supplies a `31/10` dual lower
bound for that colour, a contradiction. The existing two-coordinate ternary
construction gives the matching upper bound three. Consequently,

\[
\tau_2(KG(8,2))=3.
\]

The intermediate theorem would be stronger and more structural:

> Every triangle-free red/blue edge partition of `KG(8,2)` has one colour of
> fractional chromatic number at least `31/10`.

This `31/10` statement is only about triangle-free partitions; it does not
contradict the known two-cover upper bound three, whose covering graphs may
contain triangles.

## Reproduction and trust boundary

```bash
python exact_threshold_search.py self-test
python exact_threshold_search.py generate petersen results
python exact_threshold_search.py generate petersen-template results
```

The generator reconstructs `KG(8,2)` from definitions. A SAT solver result is
not accepted by status alone:

- SAT must include a full assignment that the Python verifier checks directly
  against all graph, triangle, Petersen, independence, and weight conditions;
- UNSAT must include a DRAT trace independently accepted by pinned
  `drat-trim` with the exact success line `s VERIFIED`.

Canonical hashes for this branch:

```text
06d8f8df57e7d029581091a2130456386843afc17af349b62265d4c7ac028585  exact_threshold_search.py
f1e846f3bb2c6a05a997d3d6f85102f5d365176c990bb8ec9a1633a01b8803be  petersen.cnf
5d5a01be5ae121790323393b554e3fb1e8978f87f62a5943bb43e3c616027d36  petersen.json
3119d5c5b04f8a7c8c3a096bf31af04f40e71fec1de985256a55d34d388628c8  petersen-template.cnf
8d05d7c6a0269851535609bde99ceea0e351d7558552d4d54bb303453844979c  petersen-template.json
```

The much larger `template` mode is retained as a monolithic independent
cross-check, but it is not needed if the two modular certificates succeed.

## Claim boundary

The formulas and their semantic mappings are research artifacts. Neither a
solver timeout nor an unverified `UNSATISFIABLE` line proves anything. Even
verified finite certificates leave literature priority and the written bridge
to fractional colouring subject to independent specialist review.
