# math-0003 — q-Fibonomial unimodality for n = 4

## Status

- **Problem status:** `proposed-proof`
- **Formal verification:** `theorem-verified` for the complete first-difference argument and its exact rational power-series model; not yet end-to-end from the paper's factorial definition
- **Novelty:** `no-prior-proof-found` in a targeted search; priority not independently or author-confirmed
- **External review:** `none`

This directory contains a proposed proof of the first case left open by Connelly, Ito, Martinez, Shevchenko, and Yang: unimodality of the q-Fibonomial coefficient with lower index `4`, for every upper offset `m`.

## Statement

Let `F_j` be the Fibonacci numbers and `[r]_q = 1 + q + ... + q^(r-1)`. For every `m >= 0`, define

```text
Q_m(q) = [F_(m+1)]_q [F_(m+2)]_q [F_(m+3)]_q [F_(m+4)]_q
         --------------------------------------------------- .
                         [F_2]_q [F_3]_q [F_4]_q
```

Since `F_2 = 1`, `F_3 = 2`, and `F_4 = 3`, this is the q-Fibonomial

```text
[ m+4 ]
[  4  ]_F.
```

**Proposed theorem.** The coefficient sequence of `Q_m(q)` is unimodal for every `m >= 0`.

## Main reduction

Put `x = F_(m+1)` and `y = F_(m+2)`. Then the numerator lengths are

```text
x, y, x+y, x+2y,
```

and the degree is `D = 3x + 4y - 7`. If `c_k` is the coefficient of `q^k`, then throughout the first half, `2k <= D`,

```text
c_k - c_(k-1)
  = g(k) - g(k-x) - g(k-y) + g(k-(2x+y)),

g(t) = floor((t^2 + 6t + 12)/12),
```

where `g(t)=0` for negative indices. The proof establishes that this difference is nonnegative for every `m` and every first-half `k`. Algebraic symmetry of q-Fibonomials then supplies the decreasing second half.

See [`proof/PROOF.md`](proof/PROOF.md) for the complete argument.

## Formalization

The Lean project proves:

- the floor bounds for `g` and the infinite symbolic inequality;
- every exceptional Fibonacci case below the symbolic threshold by explicit kernel-checked arithmetic;
- the denominator recurrence for `g`;
- the power-series identity `G(q)(1-q)(1-q^2)(1-q^3)=1`;
- the exact eight-term numerator expansion and coefficient first-difference formula;
- symmetry plus first-half monotonicity implies unimodality;
- the Fibonacci-specialized coefficient sequence is unimodal once the standard algebraic symmetry theorem is supplied.

The formal series is characterized by the exact rational identity for the `n=4` q-Fibonomial expression. The remaining end-to-end formalization work is to connect this model to the paper's factorial notation inside Lean and reprove its general algebraic symmetry theorem rather than importing that theorem mathematically.

## Reproduce

Pinned versions: Lean `4.33.1`, mathlib `v4.33.1`.

```bash
cd problems/math-0003-q-fibonomial-n4/formal
lake build
```

CI additionally rejects unfinished proof declarations, runs Lean's compiled-environment checker, and audits axioms against the standard allowlist.

## Research caution

A passing proof assistant establishes the formal theorems in this directory. It does not by itself establish priority, complete literature coverage, or acceptance of the paper-to-formal-statement bridge. Treat this as a proposed result until independent experts and the original authors review it.
