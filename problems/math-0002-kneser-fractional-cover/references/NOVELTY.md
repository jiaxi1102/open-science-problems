# Novelty and prior-art record

**Problem:** `math-0002` — fractional covers of \(KG(8,2)\)  
**Status:** `targeted-search-negative; confirmation pending`  
**Last updated:** 4 September 2026

## Original source

Gujgiczer, Marits, and Ozeki, *Cover numbers by graph families bounded by
certain graph parameters*, arXiv:2607.12353v1, submitted 14 July 2026.

Stable source: https://arxiv.org/abs/2607.12353

The paper explicitly asks whether \(KG(8,2)\) can be covered by two graphs of
fractional chromatic number at most \(5/2\). It separately asks for the exact
smallest fractional threshold \(\beta\) permitting a two-cover and records only

\[
2<\beta\le3.
\]

## Candidate contributions in this repository

1. A negative answer to the \(5/2\) two-cover question, equivalently

   \[
   c_{\mathcal C_{5/2}}(KG(8,2))=3.
   \]

2. The stronger quantitative bound

   \[
   \frac{14}{5}\le\beta_2(KG(8,2))\le3.
   \]

3. The complete \(5/2\)-threshold cutoff for the family \(KG(n,2)\): the
   source construction for \(n=7\), combined with the proposed obstruction at
   \(n=8\), gives a two-cover exactly when \(n\le7\).

## Searches completed

Targeted searches were repeated on 4 September 2026 using combinations of:

- the exact source title and author names;
- `KG(8,2)` with `fractional chromatic`, `fractional cover`, `5/2`, and
  `14/5`;
- the exact-threshold wording from the paper; and
- GitHub code/repository searches for the same identifiers.

The searches found the July 2026 source and unrelated Kneser/fractional-coloring
papers, but no later paper or public code claiming either the negative
\(5/2\) result or the \(14/5\) lower bound. The arXiv record inspected on that
date still exposed version 1 only.

This is evidence against obvious prior publication, not a proof of priority.
Search-engine indexing can lag, private or in-progress work is invisible, and
not every journal/citation database has been exhaustively checked.

## Required checks before a priority claim

1. Search MathSciNet, zbMATH, Google Scholar, and citation indexes using an
   institutional account.
2. Inspect any later versions and all citing papers for arXiv:2607.12353.
3. Send the exact theorem, proof reduction, Lean commit, and independent
   verifier to the source authors and ask about known concurrent work.
4. Obtain independent review from a graph theorist familiar with fractional
   coloring and Kneser graphs.
5. Preserve dated commits and verification logs while avoiding public claims
   stronger than `candidate new result` until those checks are complete.

## Wording policy

Until author or independent expert confirmation, use **proposed resolution**
for the \(5/2\) question and **candidate new lower bound** for \(14/5\). Do not
call either result the established first proof or a published theorem.
