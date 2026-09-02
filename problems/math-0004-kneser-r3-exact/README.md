# Exact diagonal triangle Kneser Ramsey number for `r = 3`

**ID:** `math-0004`  
**Field:** extremal combinatorics / computational Ramsey theory  
**Status:** `exact-search-running`  
**Dependency:** proposed universal lower bound in PR #5

## Decision target

The source paper proves

\[
R^{\mathrm{KG}}_3(3,3)\le 13.
\]

The five-point construction in PR #5 gives

\[
R^{\mathrm{KG}}_3(3,3)\ge 12.
\]

It remains to decide whether the edges of `KG(12,3)` can be colored red and
blue without a monochromatic triangle.

- A satisfying coloring proves `R^{KG}_3(3,3) = 13` when combined with the
  published upper bound.
- An unsatisfiability certificate proves `R^{KG}_3(3,3) = 12` when combined
  with the five-point lower bound.

Either outcome determines the exact value.

## Exact encoding

`tools/search_kneser_r3_exact.py` constructs the full instance directly from
the definition.

- 220 vertices: the three-subsets of a 12-point ground set;
- 9,240 Kneser edges: unordered pairs of disjoint triples;
- 61,600 Kneser triangles: unordered triples of pairwise-disjoint triples;
- one Boolean variable per Kneser edge;
- two NAE clauses per triangle, forbidding all-red and all-blue triangles.

The encoding has 9,240 variables and 123,203 clauses. Three unit clauses fix a
canonical triangle to colors `0,0,1`. This is without loss of generality:
`S_12` is transitive on Kneser triangles and their three vertices can be
permuted, while global color complementation exchanges the two nonmonochromatic
patterns.

The generated DIMACS file has expected SHA-256

```text
dc03e235ff1e4105b306a3ebfa1e1bc734287916533ac8eb68e26e6178858004
```

## Verification boundary

A SAT result is accepted only after the independent model checker reconstructs
all 61,600 triangles and confirms that none is monochromatic. The eventual
coloring will then be converted into a compact reproducible certificate and a
Lean theorem.

An UNSAT status is not accepted by itself. It must be accompanied by a proof
trace checked by an independent verifier and, ultimately, a Lean-checkable or
similarly small trusted certificate.

The exploratory workflow pins the official Kissat 4.0.4 Linux binary by its
published SHA-256. Solver output, generated metadata, hashes, and any model are
uploaded as workflow artifacts.
