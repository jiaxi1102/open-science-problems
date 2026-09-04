# Verification record

## Maintained result

- Repository: `jiaxi1102/open-science-problems`
- Branch: `math-0002/sharp-11-set-obstruction`
- Generated `KneserCover.lean` SHA-256:
  `1f3421d0b1e03d35a588faafe0868ffac34254cce0a8e1cc93c9777cbd7215f5`
- Runner: Ubuntu 24.04
- Lean: 4.33.1 (`819816b2e0a3bf405af45ae5c7af2491d8f5bee6`)
- Lake: 5.0.0

## Cold Lean build

The first successful build with no matching GitHub cache was:

- verified source commit: `8d72f1c718dd4949a0ed2d86ef94a02201ac5737`;
- GitHub Actions run: `33902971755`;
- job: `101121137328`;
- conclusion: `success`;
- verified at: September 4, 2026;
- Lean reported: `Built KneserCover (245s)`;
- total generated target: three Lake jobs.

Before the build, CI regenerated the source, ran the finalization step, checked
the exact SHA-256 above, and rejected `sorry`, `admit`, and hand-written
`axiom` declarations.

## Full independent-verifier pipeline

The first successful run including both independent finite checks was:

- verified source commit: `d85e7a9b464f4d2010fd48743bba81cc5f205eb7`;
- GitHub Actions run: `33903367572`;
- job: `101122436530`;
- conclusion: `success`;
- verified at: September 4, 2026.

The independent sharpness checker reported:

```text
PASS sharpness_witness=PASS vertices=28 kneser_edges=210 triangles=420 red_independent_size=10 blue_independent_size=10 red_induced_edges=15 blue_induced_edges=17
```

The independent exact NAE-3-SAT verifier reported:

```text
UNSAT vertices=28 kneser_edges=210 triangles=420 A_total=78 A_orbits=4 B_total=2184 tested_orbit_pairs=8736 immediate_overlap=6596 dpll_nodes=2118286 seconds=12.6752
```

This run restored the already verified Lean build from the preceding cold-build
cache and replayed it successfully. The cold-build run above is the evidence
that the generated theorem itself was compiled from scratch.

## Lean theorem boundary

The generated and finalized source verifies:

- `ten_set_sharpness_witness`;
- `matchingFree11_is_doubleStar`;
- `core01_obstruction11`.

Lean's `#print axioms` reported:

- for `ten_set_sharpness_witness`: `propext` and the generated native
  `native_decide` computation axiom;
- for `matchingFree11_is_doubleStar`: `propext`, `Classical.choice`,
  `Quot.sound`, and the generated native `bv_decide` computation axiom;
- for `core01_obstruction11`: `propext`, `Classical.choice`, `Quot.sound`, and
  the generated native `bv_decide` computation axiom.

These generated native computation axioms are the documented Lean 4.33.1
trust boundary. No external SAT result is asserted as a user-written axiom;
Lean checks the reconstructed finite proofs under this native evaluator model.

The outer fractional-coloring reduction remains a human proof and is not yet
formalized end to end in a general graph library. See `proof.md` for the exact
boundary.
