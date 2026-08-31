# Lean verification record

- Repository: `jiaxi1102/open-science-problems`
- Branch: `math-0002-kneser-cover`
- Verified source commit: `45a22077da284c5c88fffa19cdcacd4c308d1352`
- GitHub Actions run: `33439900366`
- Job: `99645273378`
- Conclusion: `success`
- Verified at: 31 August 2026
- Runner: Ubuntu 24.04
- Lean: 4.33.1 (`819816b2e0a3bf405af45ae5c7af2491d8f5bee6`)
- Lake: 5.0.0
- Generated `KneserCover.lean` SHA-256: `143b3fdcb75423e419eb10d1ce7c8f9fbc700f22a0cd4d55d65e27950c0667e9`
- Lean build time reported by CI: 210 seconds

The workflow regenerated the certificate, checked its hash, rejected `sorry`, `admit`, and hand-written `axiom` declarations, and completed `lake build` successfully.

Lean's `#print axioms` reported the standard logical axioms `propext`, `Classical.choice`, and `Quot.sound`, together with one generated native `bv_decide` computation axiom for each finite theorem:

- `matchingFree12_is_doubleStar._native.bv_decide.ax_1_27`
- `core01_obstruction._native.bv_decide.ax_1_47`

This is the documented Lean 4.33.1 trust boundary for `bv_decide`; see `proof.md`.
