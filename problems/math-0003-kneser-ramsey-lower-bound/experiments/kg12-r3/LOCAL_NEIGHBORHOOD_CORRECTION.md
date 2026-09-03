# Correction: the 342-pattern local classification is false

## Rejected hypothesis

An early exploratory script conjectured that every red/blue coloring of the
3-subsets of a nine-point set with no monochromatic partition into three
triples came from one of 342 indicator-threshold patterns. This is false.
The script and any dependent UNSAT search must not be used as a completeness
argument.

## General weighted construction

Let real weights `w_1,...,w_9` have total `W`, and suppose no triple has
weight sum exactly `W/3`. Color a triple `T` red when

```text
3 * sum_{i in T} w_i > W
```

and blue otherwise.

For every partition of the nine points into three triples `A,B,C`, the three
triple sums add to `W`. They therefore cannot all exceed `W/3`, and they
cannot all lie below `W/3`. Thus every such partition contains both colors.

This produces many more local colorings than the proposed 342 patterns. For
example, the weights

```text
1, 2, 4, 8, 16, 32, 64, 128, 256
```

have total 511, so no triple can equal the nonintegral average `511/3`. The
resulting coloring is valid but is not an indicator-threshold pattern from a
subset of size 1, 2, or 4.

## Consequence for the exact `KG(12,3)` search

A satisfying model produced under the old local-type restriction would still
be a valid full coloring once independently checked. An UNSAT result under
that restriction says only that the restricted ansatz fails. It cannot decide
the unrestricted Ramsey problem.

The corrected research direction is to search broader local weighted
representations, while retaining the original unrestricted SAT/DRAT route as
the only decisive UNSAT path.
