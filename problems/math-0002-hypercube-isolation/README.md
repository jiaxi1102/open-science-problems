# math-0002: Counterexample to the hypercube isolation equality

## Status matrix

| Dimension | Status |
|---|---|
| Problem | `refuted` (proposed counterexample with complete proof) |
| Formal verification | `theorem-verified` computational certificate; literature-to-model bridge is human-checked |
| Novelty | `no-prior-proof-found` as of 2026-08-31; not independently confirmed |
| External review | `none` |

## Original question

Brešar and Rall asked in Problem 2 of *On the isolation numbers in graph products* (arXiv:2608.25752v1, 26 August 2026) whether

```text
ι(Q_n,Q_k)=γ(Q_{n-k})
```

for every `0<k<n`.

## Result

The equality is false. The first genuinely new square-isolation case gives

```text
ι(Q_6,Q_2)=5 > 4 = γ(Q_4).
```

A minimum `Q_2`-isolating set is

```text
{000000,000011,000101,111001,111110}.
```

The human proof is in [`proof/proof.md`](proof/proof.md).

## Why the finite model is exact

Every copy of `Q_2` in a hypercube is a coordinate square. For each choice of four fixed coordinates in `Q_6`, projecting an isolating set to those coordinates must dominate `Q_4`, and this condition is also sufficient. Thus the finite certificate checks the original graph-theoretic property, not a heuristic relaxation.

## Verification

The Lean file [`formal/HypercubeIsolation.lean`](formal/HypercubeIsolation.lean) verifies:

1. `{0000,0001,1110,1111}` dominates `Q_4`;
2. no three vertices dominate `Q_4`;
3. the displayed five vertices isolate every coordinate square of `Q_6`; and
4. no one of the `635376` four-vertex subsets does.

The first three facts use kernel reduction. The exhaustive fourth fact uses Lean's `native_decide`, so it carries one explicit generated native-computation axiom whose proposition is auditable. The same enumeration is independently implemented in Python in [`experiments/discover.py`](experiments/discover.py). This formalization is therefore classified as `theorem-verified`, not `end-to-end-verified`: the elementary lemma that every `Q_2` copy is a coordinate square is documented in the human proof rather than formalized in a graph library.

The green workflow run, checked commit, and exact axiom report are recorded in [`artifacts/CI.md`](artifacts/CI.md).

Build:

```bash
cd formal
lake build
```

Independent search:

```bash
python experiments/discover.py
```

## Formalization boundary and open risks

- The Lean model encodes vertices as six-bit naturals and coordinate squares through all fifteen four-coordinate projections.
- `native_decide` trusts Lean's compiler for the exhaustive lower-bound computation; the generated axiom is not hidden, and an independent Python implementation reproduces it.
- Public prior-art search was negative, but novelty is not author-confirmed or independently reviewed.
- The result refutes the universal equality only; it does not characterize all pairs `(n,k)`.

## Next gates

1. Independent graph-theory review of the projection reduction and balanced-column proof.
2. Send the counterexample and certificate to Brešar and Rall for priority/correctness confirmation.
3. Replace the native exhaustive lower bound with a kernel-only Lean formalization of the short balanced-column proof.
4. Study the gap `ι(Q_n,Q_k)-γ(Q_{n-k})` and determine the next values.
