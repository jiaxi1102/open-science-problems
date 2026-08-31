# Hedgehog plucking-polynomial unimodality

**ID:** `math-0001`  
**Field:** algebraic combinatorics / knot theory  
**Problem status:** `proposed-proof`  
**Formal verification:** `end-to-end-specialized-verified`  
**Novelty:** `no-prior-proof-found`  
**External review:** `none`

## Problem

Conjecture 4.1 of Ibarra, Landry, Montoya-Vega, and Przytycki asks whether the delayed plucking polynomial of every hedgehog rooted tree whose leaf delays lie in `{1,2}` is unimodal.

For an `n`-leaf hedgehog, their Proposition 2.5 gives

```text
Q(T,f) = p_n(q) [n-1]_q!,
p_n(q) = ε_0 + ε_1 q + ... + ε_(n-1) q^(n-1),
ε_i ∈ {0,1}.
```

The exponent is the position of a leaf counted from right to left, and `ε_i = 1` exactly when that leaf has delay `1` and is eligible for the first pluck.

## Proposed result

We prove the stronger coefficient theorem

```text
for every zero-one polynomial p_n supported in degrees 0,...,n-1,
p_n(q) [n-1]_q! is unimodal.
```

We also formalize the specialized plucking recursion for the hedgehog family, derive the displayed factorization from that recursion, and combine it with the coefficient theorem. The final Lean theorem is:

```lean
Hedgehog.recursiveDelayedStar_unimodal
```

Thus the current package is no longer conditional on importing Proposition 2.5 as an unformalized bridge.

## Proof idea

Multiplying `p_n(q)` by `[n-1]_q` produces coefficients whose adjacent differences are

```text
a_(k+1) - a_(k-n+2).
```

Every sign is forced except one central comparison, so this first product is unimodal. More generally, multiplying any unimodal coefficient sequence by `[r]_q` forms a moving window, with adjacent difference

```text
b_(k+1) - b_k = a_(k+1) - a_(k+1-r).
```

For a unimodal input, the two window endpoints can reverse order at most once. Therefore multiplication by `[r]_q` preserves unimodality. Repeating this for `[n-2]_q,...,[1]_q` proves the result.

See [`proof/PROOF.md`](proof/PROOF.md) for the paper proof and [`proof/FORMALIZATION.md`](proof/FORMALIZATION.md) for the exact correspondence with the recursive semantics.

## Formalization layers

- `formal/Hedgehog.lean` proves the general zero-one quantum-factorial coefficient theorem.
- `formal/HedgehogStar.lean` formalizes the first-pluck rule for a `{1,2}`-delayed star and derives the factorization at coefficient level.
- `formal/HedgehogRecursive.lean` independently defines the ordinary-star recursion, proves that it equals the q-factorial coefficients, defines the delayed-star recursion, derives Proposition 2.5 for this family, and proves unimodality.

The formal model is specialized to the star/hedgehog family in Conjecture 4.1. It is not a generic library for arbitrary plane rooted trees. This specialization is mathematically sufficient for the conjecture, but exact statement matching should still be checked by independent subject-matter review.

## Independent finite cross-check

`experiments/crosscheck.py` uses separate exact-integer polynomial code. For every one of the `8,191` Boolean delay patterns through 12 leaves it verifies:

1. the recursively defined ordinary star equals `[n]_q!`;
2. the recursively defined delayed star equals `p_n(q)[n-1]_q!`;
3. the resulting coefficient sequence is weakly unimodal.

This computation is a regression test for conventions and implementation mistakes, not a substitute for the proof.

## Reproduce

```bash
python3 problems/math-0001-hedgehog-unimodality/experiments/crosscheck.py \
  --max-leaves 12

cd problems/math-0001-hedgehog-unimodality/formal
lake update
lake build
lake env lean HedgehogRecursive.lean
```

Pinned versions: Lean `4.33.1` and mathlib `v4.33.1`. CI rejects `sorry` and `admit`, runs the independent cross-check, builds the complete dependency chain, invokes Lean's official `leanchecker`, and audits axioms against the standard allowlist.

## Remaining gates

- independent mathematical review of the moving-window argument;
- independent confirmation that the specialized recursive semantics exactly matches the authors' conventions;
- author or expert confirmation of novelty and priority;
- preparation of a concise paper-quality note.

Until those gates are passed, the result remains labeled `proposed-proof`, despite the successful formal verification.