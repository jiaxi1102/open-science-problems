# A half-density empty-intersection Ramsey theorem

## Abstract

For every positive integer q, every red/blue edge-coloring of the complete graph whose vertices are the 3q-element subsets of a 6q-element ground set contains a monochromatic triangle A,B,C satisfying A ∩ B ∩ C = ∅. The proof consists of a finite obstruction on the twenty three-element subsets of a six-element set, followed by uniform block replication. Both parts have been checked in Lean. Literature priority and independent external review remain pending.

This supplies beta ≤ 2 in Problem 4 of Heath, McCourt, Parker, Schwieder and Zerbib, *Ramsey Numbers in Kneser Graphs*, arXiv:2510.25734v2. Their Theorem 5 supplies beta ≤ 7/3. This is a comparison with that specific source version, not a complete claim of priority.

## 1. Definition and scope

Write P(n,k) for the property that every two-coloring of all unordered pairs of distinct members of binom([n],k) has distinct A,B,C whose three pair colors agree and whose three-way intersection is empty.

The host graph is COMPLETE. Pairwise disjointness is NOT required. In particular, this is not a claim that KG(6q,3q) is triangle-Ramsey; that Kneser graph has no triangles.

## 2. Finite obstruction

### Lemma

P(6,3) holds.

### Exact encoding and proof certificate

List the twenty members V_0,...,V_19 of binom({0,...,5},3) lexicographically. Give each unordered index pair a<b a Boolean variable x_ab. There are binom(20,2)=190 variables.

For every a<b<c satisfying V_a ∩ V_b ∩ V_c = ∅, impose

    (x_ab OR x_ac OR x_bc)
    AND (NOT x_ab OR NOT x_ac OR NOT x_bc).

The first clause excludes an all-false triangle; the second excludes an all-true triangle. There are exactly 480 relevant triples and 960 clauses. There are no additional symmetry or color-fixing assumptions.

The supplied resolution certificate derives the empty clause from these clauses. It contains 1,898 derived clauses including the final empty clause. Each derivation is justified by reverse unit propagation: negate the target clause, propagate consequences of already established clauses, and obtain a contradiction. The independent standard-library checker reconstructs the set geometry and verifies all 74,719 recorded propagation steps.

The formal proof reconstructs these inferences as ordinary Lean proof terms using disjunction elimination, contradiction, and False elimination. Z3 discovers the derivation but is not a trusted axiom. `EmptyIntersection.impossible` proves the formula unsatisfiable; `EmptyIntersection.finiteIntersectionRamsey` connects it to the geometric statement through kernel-checked row validity, edge lookup, and Boolean-clause equivalences.

The Lean representation retains 34,649 propagation steps after discarding unused dependencies. The independent replay checks the larger unpruned derivation. Both lead to the same empty clause.

This is a computer-assisted proof of the finite lemma, not a claimed short human case analysis. The generated sources can be checked without running the discovery solver.

## 3. Uniform block replication

### Theorem

P(6q,3q) holds for every positive integer q.

### Proof

Take the ground set X={0,...,5}×{0,...,q−1}, of size 6q. For each base three-set S, put

    L(S) = S × {0,...,q−1}.

Each L(S) has 3q elements. Because q>0, distinct base sets have distinct images. For any base A,B,C,

    L(A) ∩ L(B) ∩ L(C) = L(A ∩ B ∩ C).

Given a coloring of the complete graph on all 3q-subsets of X, restrict to the twenty vertices L(S) and transfer the colors to their base sets S. The finite lemma yields distinct A,B,C with equal pair colors and empty three-way intersection. Their images remain distinct, have the same pair colors, and have empty three-way intersection. QED.

Lean uses ground set `Fin 6 × Fin q`. The subtype `HalfVertex q` consists of its finite subsets of size 3*q. The lemmas `ground_card`, `liftVertex_injective`, and `liftVertex_empty` establish the required properties. The final theorem is `uniformHalfIntersectionRamsey`.

## 4. Density consequence

Put k=3q and n=6q=2k. Since q can be arbitrarily large, the smallest admissible beta, or its infimum if a minimum is not attained, is at most 2. The formal theorem is the uniform combinatorial statement, not a separately defined real-valued infimum named beta.

A further written consequence covers every rational alpha in (0,1/2]. Choose k=3q so n=k/alpha is integral, and restrict to a fixed 2k-element portion of the n-point ground set. Thus there are arbitrarily large admissible n with the empty-intersection monochromatic-triangle property at density alpha. This monotonicity corollary is not separately formalized in the current Lean module.

## 5. Exactness of the finite base threshold

P(5,3) is false. Fix x in [5] and split the three-subsets according to whether they contain x. Color within classes red and across classes blue. There is no blue triangle. A red triangle in the first class shares x; in the second class it consists of three three-subsets of a four-element set, whose common intersection has size at least one.

Together with P(6,3), this proves that the least ground-set size for fixed k=3 is six. This does not establish optimality of beta=2 when k varies. The countercoloring is a written argument, not an additional Lean theorem in this package.

## 6. Unresolved questions

No equality beta=2 is claimed. The source's stronger strict-majority question P(2k−1,k) remains unresolved here. Bounded unrestricted SAT searches for P(9,5) and P(11,6) returned UNKNOWN after their wall-clock limits, not SAT or UNSAT.

The previous project's Kneser-Ramsey equality candidate R_r^KG(3,3)=3r+3 and its leading asymptotic coefficient are also not settled by this theorem. This is a separate, related problem.

## Reference

Emily Heath, Grace McCourt, Alex Parker, Coy Schwieder, Shira Zerbib.
*Ramsey Numbers in Kneser Graphs*. arXiv:2510.25734v2, 10 November 2025.
Problems 3–4, Theorem 5.
https://arxiv.org/html/2510.25734v2
