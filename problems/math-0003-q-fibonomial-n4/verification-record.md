# Verification record

## Current verified package

- Repository: `jiaxi1102/open-science-problems`
- Branch: `proof/math-0003-q-fibonomial-n4`
- Verified commit: `743ab29218accc01546f406481786bd4aec4aeb6`
- GitHub Actions run: `33448188481`
- Job: `99671889121`
- Completed: 2026-08-31 22:56 UTC
- Result: `success`

## Checks passed

- unfinished-proof declaration scan;
- Lean 4.33.1 / mathlib 4.33.1 build of all six modules;
- official compiled-environment `leanchecker` over all modules;
- axiom audit over 33 declarations under namespace `QFibonomial4`.

The axiom audit admitted only:

```text
propext
Classical.choice
Quot.sound
```

No `sorry`, `admit`, user-declared `axiom`, `native_decide`, external SMT result, or generated opaque proof certificate remains in the formal source.

## Verification scope

The verified package includes the exact rational power-series model, the numerator expansion, the full and first-half coefficient-difference formulas, the infinite symbolic inequality, the complete finite initial range, and the general implication from symmetry plus first-half monotonicity to unimodality.

The final theorem presently takes the standard algebraic symmetry of the q-Fibonomial coefficient sequence as a hypothesis. The elementary rewriting from the source paper's factorial notation to the displayed `n=4` rational expression also remains documented mathematically rather than re-proved inside Lean. These two boundaries are why the registry uses `theorem-verified`, not `end-to-end-verified`.

## Historical pre-migration run

The same formal source previously passed on the temporary path at commit `be9821a1e5812062cc5ceabd42c114db611dd189`, run `33447332968`, job `99669255232`.
