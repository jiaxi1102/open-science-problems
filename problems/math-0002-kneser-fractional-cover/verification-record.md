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

- Branch: `math-0002-alpha10-strengthening`
- Verified source commit: `39bc3335b158a1492365bbfb65b74f4c35bcbdf8`
- Pull request: `#12`
- GitHub Actions run: `33892016237`
- Job: `101085705498`
- Conclusion: `success`
- Verified at: 4 September 2026
- Runner: Ubuntu 24.04.4, image `ubuntu-24.04` version `20260831.293.1`
- Lean: 4.33.1 (`819816b2e0a3bf405af45ae5c7af2491d8f5bee6`)
- Lake: 5.0.0
- Generated `KneserCover.lean` SHA-256:
  `e21c37179741f8ddcea0cfc96911da4e50f8c336dc4aa72798acaa5f3a0e6cdb`
- Independent C++ verifier SHA-256:
  `8ce3435178190958292e87287113ff24af3aaa2a9bc5fde8aaae18a80e69f431`
- Independent verifier time reported by CI: 31.9637 seconds
- Lean build time reported by CI: 607 seconds

The clean pull-request workflow regenerated and hash-checked the final Lean
source, rejected `sorry`, `admit`, and hand-written `axiom` declarations, and
completed `lake build`. The independent C++ verifier reconstructed all 28
Kneser vertices, 210 Kneser edges, and 420 Kneser triangles; checked the four
deletion-pair orbit sizes `12, 30, 6, 30`; passed satisfiable and unsatisfiable
solver self-tests; and exhaustively returned:

```text
center_spoke              2184 cases: 1819 direct, 365 solved UNSAT
same_center_spokes        2184 cases: 1622 direct, 562 solved UNSAT
opposite_same_leaf        2184 cases: 1478 direct, 706 solved UNSAT
opposite_distinct_leaves  2184 cases: 1677 direct, 507 solved UNSAT
TOTAL                     8736 cases: 6596 direct, 2140 solved UNSAT
```

It explored 4,499,884 search nodes, with at most 23,603 nodes in one instance,
and found no counterexample.

The Lean branch verifies:

- `matchingFree12_is_doubleStar`;
- `matchingFree11_is_doubleStar`;
- `core01_obstruction`;
- `alpha10_center_spoke_obstruction`;
- `alpha10_same_center_obstruction`;
- `alpha10_same_leaf_obstruction`;
- `alpha10_distinct_leaves_obstruction`.

## Lean trust boundary

For each finite theorem, `#print axioms` reported the standard logical axioms
`propext`, `Classical.choice`, and `Quot.sound`, together with one theorem-local
generated native `bv_decide` computation axiom. The generated axiom names are:

- `matchingFree12_is_doubleStar._native.bv_decide.ax_1_27`;
- `matchingFree11_is_doubleStar._native.bv_decide.ax_1_27`;
- `core01_obstruction._native.bv_decide.ax_1_47`;
- `alpha10_center_spoke_obstruction._native.bv_decide.ax_1_47`;
- `alpha10_same_center_obstruction._native.bv_decide.ax_1_47`;
- `alpha10_same_leaf_obstruction._native.bv_decide.ax_1_47`;
- `alpha10_distinct_leaves_obstruction._native.bv_decide.ax_1_47`.

This is the documented Lean 4.33.1 trust boundary for `bv_decide`; see
`proof.md`. No compiler-independent kernel-only claim is made.
