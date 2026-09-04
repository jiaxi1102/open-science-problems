# Open Science Problems

A reproducible research workspace for exploring open problems in mathematics and science with computation, proof assistants, simulation, data analysis, and literature/novelty checks.

The repository is deliberately conservative about claims. A computational result, a formal proof, novelty, and external validation are tracked separately.

## Problem registry

| ID | Problem | Field | Status | Formal verification | External validation |
|---|---|---|---|---|---|
| `math-0001` | Hedgehog plucking-polynomial unimodality (Conjecture 4.1) | algebraic combinatorics / knot theory | `proposed-proof` | Lean 4 proof of stronger coefficient theorem | pending |
| `math-0002` | Fractional \(5/2\)-cover number of \(KG(8,2)\) | graph theory / fractional coloring | `proposed-proof` | Lean 4 verification of the finite obstruction and matching-family classification | pending |
| `math-0003` | Universal five-point lower bound for Kneser triangle Ramsey numbers | extremal combinatorics / Ramsey theory | `proposed-proof` | complete arbitrary-`r` lower-bound witness verified end to end in Lean 4.33.1 | pending |

See [`PROBLEMS.md`](PROBLEMS.md) for the registry and [`CONTRIBUTING.md`](CONTRIBUTING.md) for the required structure and claim standards.

## Repository layout

```text
problems/
  math-NNNN-short-name/
    README.md          # problem statement, provenance, status, scope
    proof/ or proof.md # human-readable proof and derivations
    formal/            # Lean/Coq/Isabelle/etc. certificate
    experiments/       # search, computation, simulation, counterexamples
    references/        # bibliographic/novelty notes and source metadata
    artifacts/         # small derived outputs when useful

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
4. Search for prior art before claiming novelty.
5. Pin software/proof-assistant versions.
6. Prefer small independently checkable certificates over opaque computation.
7. Never label a result "solved" solely because CI is green.

## Current candidate resolutions and strengthenings

### `math-0001`: hedgehog unimodality

A proposed proof of hedgehog plucking-polynomial unimodality for delays in `{1,2}`. The formal component proves a stronger zero-one coefficient theorem in Lean; the bridge to the original plucking-polynomial conjecture currently relies on the published factorization (Proposition 2.5) and is documented as such.

### `math-0002`: fractional Kneser cover

A proposed proof that the fractional \(5/2\)-cover number of \(KG(8,2)\) is exactly three, negatively answering an open two-cover question from arXiv:2607.12353v1. Lean verifies the exhaustive finite obstruction and the matching-family classification; the fractional-coloring, Tutte–Berge, symmetry, and explicit upper-bound bridge remains a written human argument pending independent review.

### `math-0003`: five-point Kneser Ramsey construction

A proposed uniform strengthening of the lower bound for diagonal triangle Ramsey numbers in Kneser graphs:

\[
R_r^{\mathrm{KG}}(3,3)\ge 3r+3\qquad(r\ge1).
\]

The construction fixes five distinguished ground points and colors each Kneser edge solely from the two traces on those points. The repository contains a complete human proof, an exhaustive independent verifier, and an end-to-end Lean 4.33.1 theorem for arbitrary `r >= 1`. Lean formalizes the trace construction, pairwise-disjointness transfer, the cardinality bridge, the explicit coloring, and the final lower-bound witness; CI rejects unfinished proof markers and hand-written axioms and audits the final theorem. The result improves the `3r+2` bound in the posted Kneser-Ramsey paper, but literature priority and external mathematical review remain pending.
