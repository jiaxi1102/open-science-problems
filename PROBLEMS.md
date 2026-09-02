# Problem Registry

This is the canonical index of investigations in this repository. Status labels describe the strongest justified claim **today**, not the intended endpoint.

| ID | Short name | Original source | Field | Status | Formal status | Novelty status | Next gate |
|---|---|---|---|---|---|---|---|
| `math-0001` | Hedgehog unimodality | Ibarra–Landry–Montoya-Vega–Przytycki, Conj. 4.1 | algebraic combinatorics / knot theory | `proposed-proof` | stronger coefficient theorem verified in Lean 4 | prior-art search negative so far; priority not author-confirmed | formalize Proposition 2.5 bridge + independent expert review |
| `math-0002` | Fractional \(5/2\)-cover of \(KG(8,2)\) | Gujgiczer–Marits–Ozeki, arXiv:2607.12353v1 open question | graph theory / fractional coloring | `proposed-proof` | matching-family classification and finite coloring obstruction verified in Lean 4; outer bridge human | source states open in July 2026; later-literature search and author confirmation pending | independent graph-theory audit + end-to-end formalization + novelty confirmation |
| `math-0003` | Five-point Kneser Ramsey lower bound | Heath–McCourt–Parker–Schwieder–Zerbib, diagonal triangle case | extremal combinatorics / Ramsey theory | `proposed-proof` | finite five-point gadget verified in Lean 4 by kernel reduction; arbitrary-`r` lift human | posted source contains weaker `3r+2` bound; exhaustive priority review pending | author/expert review + formalize arbitrary-`r` lift + attack matching upper bound |

## Required status dimensions

Every problem README should report these separately:

- **Problem status:** candidate / explored / proposed-proof / refuted / closed-known / externally-validated / published.
- **Formal verification:** none / partial / theorem-verified / end-to-end-verified.
- **Novelty:** unchecked / search-incomplete / no-prior-proof-found / independently-confirmed / not-new.
- **External review:** none / requested / in-review / confirmed / disputed.

A proof assistant can establish logical correctness of a formal statement; it cannot establish that the formal statement exactly matches the literature problem, nor that the result is novel.
