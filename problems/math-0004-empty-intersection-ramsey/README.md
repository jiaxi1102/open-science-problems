# Half-density empty-intersection Ramsey theorem

**ID:** `math-0004`  
**Field:** extremal combinatorics / Ramsey theory / set systems  
**Source:** Heath–McCourt–Parker–Schwieder–Zerbib, arXiv:2510.25734v2, Problem 4 and Theorem 5  
**Problem status:** `proposed-proof`  
**Formal verification:** `theorem-verified` for the finite and arbitrary-q family statements  
**Novelty:** `search-incomplete`  
**External review:** `none`

## Result

For every positive integer q, every red/blue coloring of the COMPLETE graph on all 3q-element subsets of a 6q-element set contains distinct A,B,C with all three edges the same color and

\[
A\cap B\cap C=\varnothing.
\]

This supplies beta ≤ 2 for the empty-intersection ratio problem. The source paper's Theorem 5 supplies beta ≤ 7/3. The comparison is to that source version, not independently confirmed priority.

This is a related question, NOT a theorem about pairwise-disjoint Kneser triangles. It does not determine beta exactly or settle the earlier Kneser-Ramsey leading constant.

## Proof and formal scope

The finite base comprises the twenty three-element subsets of a six-element set. There are 190 colored edges and 480 triples with empty three-way intersection. A 960-clause Boolean formula describes an avoiding coloring; an explicit resolution certificate refutes it. The generated Lean proof reconstructs ordinary proof terms, rather than treating a solver or native evaluator as an axiom.

The block lift sends S to S×[q]. Lean proves cardinality, injectivity, preservation of empty intersection, and the transfer to arbitrary positive q. The final theorem is `EmptyIntersection.uniformHalfIntersectionRamsey` in `formal/Lift.lean`. Its ground set is `Fin 6 × Fin q`; `ground_card` proves its size is 6*q.

The combinatorial theorem is verified. The extremal real parameter beta is not separately defined as a Lean infimum. Substitution k=3q gives beta≤2; no optimality claim is made.

Complete proof: [proof/half-density.md](proof/half-density.md).

## Reproduction

The verified artifact includes exact generated Lean sources, the RUP certificate, pinned configuration, dependency manifest, build log, commit, and hashes. For an extracted artifact:

```bash
sha256sum -c SHA256SUMS
python experiments/verify_certificate.py formal/rup-certificate.json
cd formal
lake exe cache get
lake build
```

Lean is 4.33.1; Mathlib is pinned to `0df444a360eaa60ab8c11dca51a86af692955474` (v4.33.1). Finite geometric checks use `decide +kernel`; the resolution proof uses ordinary logical inference. Final dependencies are only `propext`, `Classical.choice`, and `Quot.sound`.

The repository retains generators rather than the large expanded resolution source. To regenerate from the repository root:

```bash
python -m pip install z3-solver==4.13.3.0
python problems/math-0004-empty-intersection-ramsey/experiments/build_structured.py \
  --out problems/math-0004-empty-intersection-ramsey/formal
python problems/math-0004-empty-intersection-ramsey/experiments/verify_certificate.py \
  problems/math-0004-empty-intersection-ramsey/formal/rup-certificate.json
cd problems/math-0004-empty-intersection-ramsey/formal
MATHLIB_NO_CACHE_ON_UPDATE=1 lake update
lake exe cache get
lake build
```

Z3 is needed to rediscover the derivation, not to check the already generated Lean source or certificate. Every generated source must still pass Lean. The first full build used about 12 GB peak resident memory.

## Independent evidence and unresolved work

The standard-library replay reconstructs geometry independently and checks 1,898 derived clauses and 74,719 propagation steps. A separate SciPy/HiGHS model also reported infeasibility; that solver result is supplementary, not formal evidence.

Bounded unrestricted CaDiCaL searches for (n,k)=(9,5) and (11,6) both returned UNKNOWN after 240 seconds. A timeout is neither a counterexample nor an impossibility proof. The harder strict-majority problem on 2k−1 points, the optimal beta, and the general Kneser-Ramsey asymptotic gap remain unresolved by this work.

Independent mathematical and priority review are still required. A conceptual replacement for the finite resolution certificate would improve understanding. See [references/NOVELTY.md](references/NOVELTY.md) and [verification-record.md](verification-record.md).
