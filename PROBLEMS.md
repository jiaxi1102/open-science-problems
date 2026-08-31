# Problem Registry

This is the canonical index of investigations in this repository. Status labels describe the strongest justified claim **today**, not the intended endpoint.

| ID | Short name | Original source | Field | Status | Formal status | Novelty status | Next gate |
|---|---|---|---|---|---|---|---|
| `math-0001` | Hedgehog unimodality | Ibarra–Landry–Montoya-Vega–Przytycki, Conj. 4.1 | algebraic combinatorics / knot theory | `proposed-proof` | stronger coefficient theorem verified in Lean 4 | prior-art search negative so far; priority not author-confirmed | formalize Proposition 2.5 bridge + independent expert review |
| `math-0002` | Hypercube `Q_k`-isolation equality | Brešar–Rall, Problem 2, arXiv:2608.25752v1 | domination theory / hypercubes | `refuted` (proposed counterexample) | theorem-verified finite certificate; graph-model bridge external | no prior proof found as of 2026-08-31; priority not author-confirmed | independent expert review + author contact + kernel-only formalization |

## Required status dimensions

Every problem README should report these separately:

- **Problem status:** candidate / explored / proposed-proof / refuted / closed-known / externally-validated / published.
- **Formal verification:** none / partial / theorem-verified / end-to-end-verified.
- **Novelty:** unchecked / search-incomplete / no-prior-proof-found / independently-confirmed / not-new.
- **External review:** none / requested / in-review / confirmed / disputed.

A proof assistant can establish logical correctness of a formal statement; it cannot establish that the formal statement exactly matches the literature problem, nor that the result is novel.
