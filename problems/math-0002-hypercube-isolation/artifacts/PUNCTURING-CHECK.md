# Puncturing-rigidity Lean check

**Checked:** 2026-09-02 (America/New_York)

On a fresh clone of branch `result/math-0002-hypercube-isolation`, the
following checks completed with exit code zero under the pinned Lean
`4.33.1` / Mathlib `v4.33.1` environment:

```bash
cd problems/math-0002-hypercube-isolation/formal
lake build
lake env lean HypercubeIsolation/Puncturing.lean
```

A recursive scan of the formal tree found no `sorry` or `admit` markers.

The checked module proves:

```text
if deleting every ell-set of coordinates leaves distance at least d>0,
then the full Hamming distance is at least d+ell.
```

It also proves the radius form with `d=2r+1`, which is the rigidity step in
the perfect-code robust-extension obstruction.

The local logs are retained as session artifacts. GitHub Actions remains the
public reproducibility gate for the branch.
