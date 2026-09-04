# Verification record

## End-to-end lower-bound verification

- Repository: `jiaxi1102/open-science-problems`
- Branch: `math-0003-five-point-kneser`
- Theorem source commit: `56a794b76d19b01264f1d2e48c0ffdb7bceab041`
- Draft pull request: `#5`
- GitHub Actions run: `33893086539`
- Job: `101089213226`
- Conclusion: `success`
- Verified: 4 September 2026
- Runner: Ubuntu 24.04
- Lean: 4.33.1
- Mathlib release: `v4.33.1`
- Mathlib commit: `0df444a360eaa60ab8c11dca51a86af692955474`
- Finite proof mode: `decide +kernel`

## Checks performed

1. `tools/verify_kneser_five_point.py` exhaustively checked all `918` labeled
   partitions of the five distinguished points with at most two unused
   points. It independently reconstructed every Kneser edge and triangle for
   `r=1,2,3,4` and found no monochromatic triangle.
2. The source scan rejected `sorry`, `admit`, and hand-written `axiom`
   declarations across the complete formal package.
3. `lake build` explicitly built both roots:
   - `KneserFivePoint`;
   - `KneserFivePoint.LowerBound`.
4. The second root checked the arbitrary-`r` trace-cardinality bridge, the
   explicit coloring, the no-monochromatic-triangle theorem, and the final
   lower-bound witness.
5. `axiom-audit` checked declarations under `KneserFivePoint` against the
   allowlist `propext, Classical.choice, Quot.sound`.

The successful build reported:

```text
Built KneserFivePoint.LowerBound
'KneserFivePoint.finsetTraceGadget' depends on axioms:
  [propext, Classical.choice, Quot.sound]
'KneserFivePoint.kneserRamsey_three_three_lower_bound' depends on axioms:
  [propext, Classical.choice, Quot.sound]
Build completed successfully (8708 jobs).
```

The subsequent audit reported:

```text
axiom-audit: audited 11 declaration(s) under 'KneserFivePoint';
all within the allowlist [propext, Classical.choice, Quot.sound].
```

There is no `sorryAx`, no `admit`, no hand-written axiom, and no
native-computation axiom in the final lower-bound theorem.

## Final formal theorem

```lean
theorem kneserRamsey_three_three_lower_bound (r : Nat) (hr : 1 ≤ r) :
    KneserRamseyLowerBound r (3 * r + 3)
```

Here `KneserRamseyLowerBound r N` is defined in direct witness form as the
existence of a symmetric red/blue coloring of the `r`-subsets of an
`(N-1)`-point ground set with no monochromatic triple of pairwise-disjoint
vertices. Consequently, the theorem certifies the lower-bound statement

\[
R_r^{KG}(3,3)\ge 3r+3
\]

for every `r >= 1`.

## Independent executable evidence

The ordered disjoint-trace color table has SHA-256:

```text
8426231092c6081026c57f6ed1b48eaf1f766233fc4fe1191cea39d1e0a44faa
```

The verifier also recorded zero monochromatic triangles in:

| `r` | graph | vertices | Kneser triangles checked |
|---:|---|---:|---:|
| 1 | `KG(5,1)` | 5 | 10 |
| 2 | `KG(8,2)` | 28 | 420 |
| 3 | `KG(11,3)` | 165 | 15,400 |
| 4 | `KG(14,4)` | 1,001 | 525,525 |

## Remaining boundary

Logical verification of the lower-bound witness is end to end. The remaining
non-formal questions are scientific rather than proof gaps:

- whether the result and construction are new in the complete literature;
- whether independent experts agree that the formal witness matches the
  source paper's Kneser-Ramsey convention;
- whether the matching upper bound `R_r^{KG}(3,3) <= 3r+3` holds.
