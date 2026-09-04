# Exact two-cover fractional threshold of KG(7,2)

**Result:** tau_2(KG(7,2)) = 5/2, where tau_2 minimizes the larger fractional chromatic number in a two-graph edge cover.

**Provenance:** The KG(7,2) part of the second small-case question in Section 7 of Gujgiczer–Marits–Ozeki, *Cover numbers by graph families bounded by certain graph parameters*, arXiv:2607.12353v1. The upper construction is already Theorem 4.2 of that paper. The contribution is the matching lower bound.

**Claim status:** candidate resolution; independent expert review and priority confirmation are pending. Consult the actual workflow result and axiom output for formal execution status. No general asymptotic problem is claimed solved.

## Proof

Every red-blue coloring of KG(7,2) contains a monochromatic triangle or pentagon. A sufficient induced subgraph has vertices 03, 04, 05, 06, 12, 14, 15, 16, 23, 24, 25, 34, 36, 45, 46, where 03 denotes {0,3}. It has 50 edges, 40 triangles and 1,104 pentagons. The finite Ramsey certificate asserts that these 1,144 cycles cannot all be non-monochromatic.

Given any two-cover, assign each edge a color corresponding to a graph containing it. A monochromatic C3 or C5 forces one covering graph to have fractional chromatic number at least 5/2: in a p-color, q-fold coloring of C5, each color occurs at most twice, so 5q <= 2p. C3 gives the stronger bound 3q <= p. These bounds also follow directly for real fractional weights by summing the vertex covering inequalities.

For the matching upper bound, partition vertices into H (pairs on {0,...,4}), A (pairs containing 5), and B (pairs containing 6 but not 5). The first covering graph consists of edges within H and between A and B. Assign two colors to each vertex from {0,...,4}: its own pair on H, {0,1} on A, and {2,3} on B. This is a valid 5:2 coloring. The remaining edges form a bipartite graph between H and A union B. Thus the optimal maximum fractional chromatic number is exactly 5/2.

## Formal boundary

`KG7.lean` verifies the complete vertex/edge encoding, every witness cycle, the universal Ramsey assertion for `BitVec 105`, and the explicit upper-bound palettes. `CycleBound.lean` proves the counting inequality for arbitrary natural palette size p and multiplicity q, by induction rather than a bounded search.

The outer conversion between graph covers, their restrictions to the certified cycles, and the usual real-valued definition of fractional chromatic number remains the written argument above, not one end-to-end theorem about a library definition of tau_2. Native reflective evaluation in Lean 4.33.1 is part of the `bv_decide` trust boundary. Machine verification does not establish novelty or expert acceptance.

An independent, standard-library C++ exact verifier regenerates the graph and cycles, includes SAT/UNSAT self-tests, and returns UNSAT in 7,159 search nodes.

## Reproduce

```sh
cd formal
python3 generate.py
lean CycleBound.lean
lean KG7.lean
```

Lean is pinned to 4.33.1; Mathlib is not required. The workflow preserves generated sources, cycle manifest, compiler/axiom logs, and checksums. For the independent check, compile `experiments/verify_independent.cpp` with C++20 and run the resulting executable.

Source: https://arxiv.org/html/2607.12353v1
