# Structural Lean verification

**Verified date:** 2026-09-04

## Checked revision

- Repository: `jiaxi1102/open-science-problems`
- Branch: `result/math-0002-radius-covering-phase-transition`
- Verified formal commit: `64b1de088dcd5adf7c0cbc0f10c82f16be5a69e2`
- GitHub Actions workflow run: `33894374692`
- Verification job: `101093456647`
- Toolchain: Lean `4.33.1`
- Mathlib revision: `0df444a360eaa60ab8c11dca51a86af692955474`

The later commits through the current documentation head modify Markdown only; this record deliberately names the exact formal-code commit checked by CI.

## Successful gates

- recursive unfinished-proof-marker scan: passed;
- `lake build`: passed (`3011` jobs);
- bundled `leanchecker`: passed;
- workflow conclusion: `success`.

## Structural theorems checked

### Coordinate-copy theorem

```text
HypercubeIsolation.CubeCopies.CubeEmbedding.is_coordinate_copy
```

Every injective edge-preserving map from a binary cube to a binary cube is represented by one base vertex and an injection of intrinsic coordinate directions into ambient coordinate directions.

Reported axioms:

```text
[propext, Classical.choice, Quot.sound]
```

### Coordinate-face/radius-covering-array dictionary

```text
HypercubeIsolation.StructuralTheory.hitsAllCodimFaces_iff_radiusCoveringArray
```

For a finite row set, meeting the radius-`r` neighborhood of every coordinate face of fixed codimension is equivalent to the binary radius-covering-array condition on every fixed-coordinate projection.

Reported axioms:

```text
[propext, Classical.choice, Quot.sound]
```

Together with the coordinate-copy theorem, this formalizes the structural bridge from arbitrary graph copies of `Q_k` to coordinate faces and then to radius-covering arrays.

### Perfect-code volume arithmetic

```text
HypercubeIsolation.StructuralTheory.binary_two_column_volume_obstruction
```

The binary two-column volume gap reduces to `m(m-3)` and is positive for `m>=4`.

Reported axioms:

```text
[propext, Classical.choice, Quot.sound]
```

### Quantitative-gap algebra

```text
HypercubeIsolation.QuantitativeGap.quantitative_gap_from_pair_counts
HypercubeIsolation.QuantitativeGap.hamming31_gap_coefficient
HypercubeIsolation.QuantitativeGap.hamming63_gap_coefficient
```

Lean verifies the algebraic implication from the two pair-count inequalities to the quantitative Hamming-family gap, as well as the exact displayed coefficients for selected Hamming lengths.

Reported axioms:

```text
[propext, Classical.choice, Quot.sound]
```

## Remaining trust boundary

The older finite theorem

```text
HypercubeIsolation.counterexample_certificate
```

still reports

```text
[propext, noFourVertexQ2IsolatingQ6._native.native_decide.ax_1_1]
```

because exhaustive exclusion of all four-row candidates in `Q_6` uses `native_decide`. The witness and smaller checks use kernel reduction, and an independent Python implementation reproduces the exhaustive result.

The **general quantitative theorem is not yet end-to-end formalized**. CI checks its final algebra and numerical instances, but the covering-multiplicity incidence count, close-pair deletion count, Caro--Wei step, and Hamming sphere-packing step remain human proofs in `proof/quantitative-hamming-gap.md`.
