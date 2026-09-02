# Verification record

## Clean review branch

- Repository: `jiaxi1102/open-science-problems`
- Branch: `math-0003-five-point-kneser`
- Verified source commit: `2cc6f5a2a91ba0e096977669cfb7b400f870a4bd`
- Draft pull request: `#5`
- GitHub Actions run: `33684568921`
- Job: `100428818987`
- Conclusion: `success`
- Verified: 2 September 2026
- Runner: Ubuntu 24.04
- Lean: 4.33.1
- Proof mode: `decide +kernel`

The same theorem sources had previously passed on the exploratory branch at
commit `6877b53a52e03d53baf817457ae95f9953457c40`, run `33683038605`, job
`100423855952`. The clean PR run independently checked the focused 12-file
review package.

## Checks performed

1. `tools/verify_kneser_five_point.py` exhaustively checked all `918` labeled
   partitions of the five distinguished points with at most two unused
   points. It also reconstructed every Kneser edge and triangle for
   `r=1,2,3,4` and found no monochromatic triangle.
2. The source scan rejected `sorry`, `admit`, and hand-written `axiom`
   declarations.
3. `lake build` checked the Lean theorems `red_symm` and `fivePointGadget`.

Lean reported:

```text
'KneserFivePoint.red_symm' depends on axioms: [propext, Quot.sound]
'KneserFivePoint.fivePointGadget' depends on axioms: [propext, Quot.sound]
```

There is no native-computation axiom in this certificate. The finite truth
of the five-point gadget was reduced by the Lean kernel.

The executable verifier fixes the ordered disjoint-trace color table with
SHA-256:

```text
8426231092c6081026c57f6ed1b48eaf1f766233fc4fe1191cea39d1e0a44faa
```

## Boundary

The finite gadget is machine checked. The outer statement

\[
R_r^{KG}(3,3)\ge 3r+3
\]

also uses the written observation that three pairwise-disjoint `r`-sets in a
`(3r+2)`-element ground set leave exactly two points unused, so their traces
on the five distinguished points cover at least three points. That lift is
short and elementary but is not yet encoded end to end in Lean.
