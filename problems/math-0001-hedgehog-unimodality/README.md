# Hedgehog plucking-polynomial unimodality

**ID:** `math-0001`
**Field:** algebraic combinatorics / knot theory
**Problem status:** `proposed-proof`
**Formal verification:** `theorem-verified`
**Novelty:** `no-prior-proof-found`
**External review:** `none`

## Problem

Conjecture 4.1 of Ibarra, Landry, Montoya-Vega, and Przytycki asks whether the plucking polynomial of a hedgehog rooted tree with delays in `{1,2}` is always unimodal.

Their Proposition 2.5 reduces the relevant family to

`Q(T,f) = p_n(q) [n-1]_q!`,

where `p_n(q)` is a zero-one polynomial supported in degrees `0,...,n-1`.

## Proposed result

We prove the stronger coefficient theorem: for every such zero-one polynomial, `p_n(q)[n-1]_q!` is unimodal. Combined with the published reduction, this gives a proposed resolution of Conjecture 4.1.

## Proof idea

First, multiplying by `[n-1]_q` produces coefficients whose adjacent differences are `a_(k+1)-a_(k-n+2)`. Every sign is forced except one central comparison, so the result is unimodal. Second, multiplication by any `[r]_q` preserves unimodality because the moving-window difference `b_(k+1)-b_k = a_(k+1)-a_(k+1-r)` changes sign at most once for a unimodal sequence. Applying this repeatedly yields the full quantum factorial.

See `proof/PROOF.md`.

## Formalization boundary

Lean verifies the complete stronger coefficient theorem and its specialization to arbitrary zero-one delay indicators. It does not yet formalize the recursive plucking-polynomial definition or reprove Proposition 2.5. Thus the new theorem is formally verified, while the final bridge to the literature conjecture remains imported from the published result.

## Reproduce

```bash
cd problems/math-0001-hedgehog-unimodality/formal
lake update
lake build
lake env lean Hedgehog.lean
```

Pinned versions: Lean 4.33.1 and mathlib v4.33.1. CI rejects unfinished proof markers, runs `leanchecker`, and performs an axiom audit.

## Remaining gates

Formalize the Proposition 2.5 bridge end-to-end, complete independent expert review, and confirm priority before changing the problem-level status beyond `proposed-proof`.