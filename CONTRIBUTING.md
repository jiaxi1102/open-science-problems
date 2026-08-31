# Research and Contribution Protocol

Each investigation should be independently understandable, reproducible, and conservative in its claims.

## Directory contract

Create `problems/<domain>-<NNNN>-<slug>/` with:

- `README.md`: canonical problem statement, provenance, status matrix, result, formalization boundary, reproduction instructions, open risks.
- `proof/`: human-readable arguments and derivations.
- `formal/`: proof-assistant project and pinned toolchain.
- `experiments/`: scripts/notebooks/searches used to discover or stress-test the result.
- `references/`: bibliography, prior-art/novelty search notes, quotations kept within fair-use limits, and source metadata.
- `artifacts/`: small generated certificates/tables/figures when useful.

Folders may be omitted when genuinely unused, but `README.md` is mandatory.

## Claim gates

### Candidate
The problem is sourced and plausibly open.

### Explored
There is substantive computation, simulation, or theory, but no complete resolution.

### Proposed proof / refutation
A complete argument or counterexample is present. Required before this label:

1. Exact original statement and citation recorded.
2. Assumptions and reductions written explicitly.
3. Known-result search performed and logged.
4. At least one independent computational or formal consistency check when feasible.

### Formally verified
A proof assistant verifies the relevant theorem. Record whether verification is:

- `partial`: auxiliary theorem(s) only;
- `theorem-verified`: the main new mathematical theorem is checked, but a bridge to the literature statement remains external;
- `end-to-end-verified`: original definitions and all reductions are formalized.

CI must reject unfinished proof markers and pin the proof-assistant/toolchain version.

### Externally validated
At least one knowledgeable independent reviewer confirms correctness, scope, and interpretation of the original problem.

### Published
Stable public archive, preprint, or peer-reviewed publication exists.

## Novelty protocol

Before claiming a new solution:

1. Search the problem title, authors, distinctive theorem statement, and proposed key lemma.
2. Search current preprints, journal records, GitHub/formalization repositories, and problem databases.
3. Record search date and queries in `references/NOVELTY.md`.
4. Distinguish `no prior proof found` from `novelty confirmed`.
5. Contact original authors or relevant experts for priority confirmation for credible new resolutions.

If a result is rediscovered, mark `closed-known` and preserve the exploration for provenance.

## Formal-proof CI standard

For Lean projects, prefer:

- pinned `lean-toolchain` and mathlib revision;
- `lake build`;
- explicit `sorry` / `admit` rejection;
- `leanchecker` where supported;
- axiom audit with an explicit allowlist;
- tests or executable certificate checks for computational components.

## Problem IDs

Use monotonically increasing IDs by broad domain, e.g. `math-0001`, `physics-0001`, `biology-0001`. The directory name should include the ID and a stable descriptive slug.