# Novelty / prior-art record

**Problem:** `math-0001` Hedgehog plucking-polynomial unimodality

## Current assessment

`no-prior-proof-found` — not `independently-confirmed`.

The source paper presents the `{1,2}`-delay unimodality statement as Conjecture 4.1. Initial searches did not identify a later proof of the conjecture or the stronger zero-one quantum-factorial theorem used here.

## Distinctive result searched

For every zero-one polynomial

`p(q) = ε_0 + ε_1 q + ... + ε_(n-1) q^(n-1)`, with `ε_i ∈ {0,1}`,

the product `p(q)[n-1]_q!` has a unimodal coefficient sequence.

## Search checklist

- original paper and versions of the problem statement;
- title/author searches around plucking polynomials with delay functions;
- searches for the exact hedgehog/unimodality conjecture;
- searches for equivalent zero-one polynomial times quantum-factorial statements;
- public formalization/problem repositories for an existing proof.

## Important distinction

A negative search is evidence only. Priority should be treated as unresolved until the original authors or independent subject-matter experts confirm that the proof is not already known or implicit in prior literature.

## Known false start retained outside this problem

During exploration, OEIS A248802 Conjecture 5 was independently refuted and Lean-verified, but the identical counterexample was then found in the public LeanOpenProblems-results repository. That result is therefore not being represented here as a new discovery. This is the reason the master repository separates formal correctness from novelty status.