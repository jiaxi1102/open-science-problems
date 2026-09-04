# Verification record

## Original \(5/2\) certificate

- Repository: `jiaxi1102/open-science-problems`
- Verified source commit: `45a22077da284c5c88fffa19cdcacd4c308d1352`
- GitHub Actions run: `33439900366`
- Job: `99645273378`
- Conclusion: `success`
- Verified at: 31 August 2026
- Runner: Ubuntu 24.04
- Lean: 4.33.1 (`819816b2e0a3bf405af45ae5c7af2491d8f5bee6`)
- Lake: 5.0.0
- Generated `KneserCover.lean` SHA-256:
  `143b3fdcb75423e419eb10d1ce7c8f9fbc700f22a0cd4d55d65e27950c0667e9`
- Lean build time reported by CI: 210 seconds

That workflow regenerated the certificate, checked its hash, rejected `sorry`,
`admit`, and hand-written `axiom` declarations, and completed `lake build`.

## Strengthened \(14/5\) certificate

**Current status:** branch certificate prepared; GitHub Actions verification
pending.

Artifacts prepared on 4 September 2026:

- generated `KneserCover.lean` SHA-256:
  `e21c37179741f8ddcea0cfc96911da4e50f8c336dc4aa72798acaa5f3a0e6cdb`;
- independent C++ verifier SHA-256:
  `8ce3435178190958292e87287113ff24af3aaa2a9bc5fde8aaae18a80e69f431`;
- exhaustive C++ totals: 8736 instances, 6596 direct conflicts, 2140
  solver-certified UNSAT instances, and no counterexample;
- total search nodes: 4,499,884; maximum nodes in one instance: 23,603.

The C++ verifier uses only the C++ standard library. It independently
constructs all 28 Kneser vertices, 210 Kneser edges, and 420 Kneser triangles;
checks the deletion-pair orbit sizes `12, 30, 6, 30`; runs satisfiable and
unsatisfiable solver self-tests; and fails closed on a counterexample or any
unexpected total.

The Lean branch adds:

- `matchingFree11_is_doubleStar`;
- `alpha10_center_spoke_obstruction`;
- `alpha10_same_center_obstruction`;
- `alpha10_same_leaf_obstruction`;
- `alpha10_distinct_leaves_obstruction`.

The workflow record in this section must be updated only after the branch CI
has completed successfully.

## Lean trust boundary

For the original certificate, `#print axioms` reported the standard logical
axioms `propext`, `Classical.choice`, and `Quot.sound`, together with one
generated native `bv_decide` computation axiom for each finite theorem. The
strengthened certificate uses the same mechanism. This is the documented Lean
4.33.1 trust boundary for `bv_decide`; see `proof.md`.
