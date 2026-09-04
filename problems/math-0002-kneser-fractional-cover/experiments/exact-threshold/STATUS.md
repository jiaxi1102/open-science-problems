# Exact-threshold search status

- Parent milestone: draft PR #12 (`14/5` lower bound, Lean finite core).
- Research branch: `research/math-0002-exact-threshold`.
- Current claims: none beyond the parent milestone.
- Decisive jobs:
  1. `petersen`: counterexample search for the monochromatic-Petersen lemma.
  2. `petersen-template`: counterexample search for the fixed Petersen-to-`31/10` dual lemma.
- Promotion rule: an UNSAT conclusion is recorded only after `drat-trim` reports the exact line `s VERIFIED`; a SAT conclusion is recorded only after direct semantic replay of the model.
- Exact-threshold promotion requires both jobs to return `UNSAT_DRAT_VERIFIED`, followed by a written proof audit and literature review.
