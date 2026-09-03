# Local-link branch summary

This stacked branch adds the sharp nine-point link theorem and its role in the
`KG(12,3)` upper-bound program.

The primary files are:

- `proof/nine-point-link-k5.md` — theorem, exact proof boundary, sharp
  Fano-star construction, and Kneser-link corollary;
- `nine-point-link-verification.md` — successful CI and certificate record;
- `references/NINE_POINT_LINK_NOVELTY.md` — conservative priority boundary;
- `UPPER_BOUND_PROGRAM.md` — uniqueness, cloud compatibility, and rank-lifting
  program;
- `tools/verify_kneser_nine_point_link_k5.py` — pure-Python certificate
  generator, independent proof-DAG checker, and sharpness verifier;
- `.github/workflows/math-0003-nine-point-link-k5.yml` — fail-closed CI.

The branch does not claim an upper bound for `KG(12,3)`. Its new mathematical
content is the sharp finite link theorem and the resulting monochromatic
five-cloud attached to every vertex of a hypothetical counterexample.
