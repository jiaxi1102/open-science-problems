# Verification record: asymmetric padding theorem

Verified on 4 September 2026, America/New_York (5 September UTC).

## Theorem and scope

For all r >= 1 and s >= 3, the construction witnesses

\[
R_r^{KG}(s,3)\ge s(r+1).
\]

The final formal statement is:

```lean
theorem kneserRamsey_asymmetric_lower_bound
    (r s : Nat) (hr : 1 ≤ r) (hs : 3 ≤ s) :
    KneserAsymmetricAvoiding (s*(r+1)-1) r s
```

`KneserAsymmetricAvoiding n r s` requires a symmetric Boolean coloring of all
r-element subsets of `Fin n`, with no red clique of s pairwise-disjoint
vertices and no blue triangle of pairwise-disjoint vertices. Since r >= 1,
those disjoint vertices are distinct. This is the direct coloring-witness
form of the Ramsey lower bound, not a separate formalization of a least-n
Ramsey-number operator.

The general-target corollary
`R_r^KG(s,t) >= max(s,t)*r+s+t-3` has a complete written proof in
`proof/asymmetric-padding.md`, but is NOT part of the current Lean theorem.

## Reproducible successful run

- Repository: `jiaxi1102/open-science-problems`
- Branch: `math-0003-five-point-kneser`
- Pull request: `#5` (unmerged)
- Verified source commit: `31b9ff6a01a584785737a5c9f175aa54d8179889`
- Workflow run: `33931702669`
- Job: `101211454095`
- Event: `push`
- Conclusion: `success`
- Run URL: https://github.com/jiaxi1102/open-science-problems/actions/runs/33931702669
- Lean: `4.33.1`
- Mathlib: `v4.33.1`, commit `0df444a360eaa60ab8c11dca51a86af692955474`

The build explicitly included `KneserFivePoint`, `KneserFivePoint.LowerBound`,
and `KneserFivePoint.Asymmetric`. At 00:05:21 UTC the log reported:

```text
Built KneserFivePoint.Asymmetric (22s)
'KneserFivePoint.padding_blue_triangle_free' depends on axioms:
  [propext, Classical.choice, Quot.sound]
'KneserFivePoint.kneserRamsey_asymmetric_lower_bound' depends on axioms:
  [propext, Classical.choice, Quot.sound]
Build completed successfully (8709 jobs).
```

The finite template lemmas use `decide +kernel`; the arbitrary-r,s part uses
ordinary finite-set, injection, cardinality, and arithmetic proofs.

## Exact-declaration axiom audit

The legacy namespace audit reports only 11 declarations and is not used as
sole evidence for auditing the additional modules. The new `Audit.lean`
imports `KneserFivePoint.Asymmetric` explicitly. CI runs
`lake env lean Audit.lean`, requires output for each named theorem, and checks
the complete reported dependency set against the allowlist.

At 00:06:06 UTC, all three explicit checks passed:

```text
PASS KneserFivePoint.kneserRamsey_three_three_lower_bound
  ['Classical.choice', 'Quot.sound', 'propext']
PASS KneserFivePoint.padding_blue_triangle_free
  ['Classical.choice', 'Quot.sound', 'propext']
PASS KneserFivePoint.kneserRamsey_asymmetric_lower_bound
  ['Classical.choice', 'Quot.sound', 'propext']
```

There is no `sorryAx`, native-computation axiom, or hand-written axiom in
these theorem dependencies. Source scans also rejected unfinished proof
markers. The final audit step and the entire job concluded successfully.

## Independent executable checks

`tools/verify_kneser_padding.py` uses only the Python standard library.
It checks all 1024 ordered disjoint five-point trace triples, the 32 empty
interfaces, symmetry, and the following unordered disjoint trace families.
Repeated empty traces are deliberately included.

| s | distinguished points | s-trace families | triangle-trace families |
|---:|---:|---:|---:|
| 3 | 5 | 187 | 187 |
| 4 | 6 | 855 | 715 |
| 5 | 7 | 4,111 | 2,795 |
| 6 | 8 | 21,110 | 11,051 |
| 7 | 9 | 115,929 | 43,947 |
| 8 | 10 | 678,514 | 175,275 |

Totals: 820,706 s-trace families and 233,970 triangle-trace families.
No blue triangle or red s-family covering three distinguished points was
found. These are finite regressions; the general theorem is established by
the proof, not extrapolation from the computations.

The original diagonal verifier also passed all 918 coverage-qualified trace
partitions and direct Kneser-triangle checks for r=1,2,3,4.

The new verifier's table SHA-256 is:

```text
45432382d1c35f10fd37e994ae52662bc47b51678ebdd43c54830fc0d0dc0290
```

Encoding: one raw byte 0/1 per ordered disjoint five-bit-mask pair, in
lexicographic order. The hash differs from the earlier verifier's hash
because the encoding differs; it does not represent a changed coloring.

## Reproduction

```bash
git clone https://github.com/jiaxi1102/open-science-problems.git
cd open-science-problems
git checkout 31b9ff6a01a584785737a5c9f175aa54d8179889
python tools/verify_kneser_five_point.py
python tools/verify_kneser_padding.py
cd problems/math-0003-kneser-ramsey-lower-bound/formal
lake exe cache get
lake build
lake env lean Audit.lean
```

## Scientific boundary

Theorem A is formally verified in direct witness form. Literature priority
is `search-incomplete`; external review is `none`. Theorem B has a written
proof but no Lean verification yet. The diagonal matching upper bound and
an exact general formula remain unproved. No compilation success settles
novelty, importance, or the entire research program.
