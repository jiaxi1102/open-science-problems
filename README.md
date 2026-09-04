# Open Science Problems

A reproducible research workspace for exploring open problems in mathematics and science with computation, proof assistants, simulation, data analysis, and literature/novelty checks.

The repository is deliberately conservative about claims. A computational result, a formal proof, novelty, and external validation are tracked separately.

## Problem registry

| ID | Problem | Field | Status | Formal verification | External validation |
|---|---|---|---|---|---|
| `math-0001` | Hedgehog plucking-polynomial unimodality (Conjecture 4.1) | algebraic combinatorics / knot theory | `proposed-proof` | Lean 4 proof of stronger coefficient theorem | pending |
| `math-0002` | Hypercube `Q_k`-isolation equality (Problem 2) | domination theory / covering arrays | `refuted`; structural theorem package proposed | Lean 4 coordinate-copy theorem, graph/coding bridge, quantitative algebra, and finite certificate | pending |

See [`PROBLEMS.md`](PROBLEMS.md) for the registry and [`CONTRIBUTING.md`](CONTRIBUTING.md) for the required structure and claim standards.

## Repository layout

```text
problems/
  math-0001-hedgehog-unimodality/
  math-0002-hypercube-isolation/
    README.md          # problem statement, provenance, status, scope
    paper/             # manuscript draft
    proof/             # human-readable proofs and derivations
    formal/            # Lean/Coq/Isabelle/etc. certificate
    experiments/       # search, computation, simulation, counterexamples
    references/        # bibliographic/novelty notes and source metadata
    artifacts/         # verification records and small derived outputs

templates/
  problem/             # starter files for new explorations

.github/workflows/     # reproducibility and formal-verification CI
```

## Status vocabulary

- `candidate`: selected as worth investigating; no substantive result yet.
- `explored`: computational/theoretical exploration exists, but no complete claimed resolution.
- `proposed-proof`: a complete argument is present, but novelty and/or expert review remain pending.
- `formally-verified`: the relevant theorem has been checked by a proof assistant; this does **not** by itself establish novelty or that all reductions to the original problem were formalized.
- `externally-validated`: independent subject-matter review has confirmed the result and scope.
- `published`: publicly archived or peer-reviewed with stable bibliographic record.
- `closed-known`: investigation rediscovered a previously known result; retained for provenance but not claimed as new.
- `refuted`: the conjecture is disproved by a validated counterexample.

## Reproducibility principles

1. Preserve the original problem statement and source.
2. Separate conjecture-level claims from stronger/weaker auxiliary theorems.
3. Record the formalization boundary explicitly.
4. Search for prior art across neighboring fields before claiming novelty.
5. Pin software/proof-assistant versions.
6. Prefer small independently checkable certificates over opaque computation.
7. Never label a result "solved" solely because CI is green.
8. Correct the public record when a terminology bridge reveals prior art.

## Current results

`math-0001` contains a proposed proof of hedgehog plucking-polynomial unimodality for delays in `{1,2}`. The formal component proves a stronger zero-one coefficient theorem in Lean; the bridge to the original plucking-polynomial conjecture currently relies on the published factorization (Proposition 2.5) and is documented as such.

`math-0002` identifies hypercube subcube isolation exactly with binary radius-covering arrays:

```text
ι(Q_n,Q_k)=CAN_1(n-k,n,2).
```

This translation refutes the universal equality in Brešar–Rall Problem 2 and yields an infinite Hamming-family obstruction, a quantitative exponential additive gap, and a fixed-codimension constant-to-logarithmic phase transition. The smallest value `ι(Q_6,Q_2)=5` is not new: it was already present in 2010 radius-covering-array tables under different terminology. The candidate-new structural package has substantial Lean verification but still awaits independent specialist review and priority confirmation.
