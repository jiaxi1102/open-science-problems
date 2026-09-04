# Novelty and prior-art record

**Problem:** `math-0002` — fractional covers and a sharp Ramsey obstruction for \(KG(8,2)\)  
**Status:** `search-incomplete`  
**Last updated:** September 4, 2026

## Original source

Gujgiczer, Marits, and Ozeki, arXiv:2607.12353v1 (July 2026), explicitly ask:

1. whether \(KG(8,2)\) can be covered by two graphs of fractional chromatic number at most \(5/2\);
2. for the smallest rational \(\beta\) at which such a two-cover becomes possible.

The present candidate result answers the first question negatively, proves the
cover number is three, establishes the sharp triangle-free independence
parameter 10, and narrows the second question to

\[
14/5\le\beta_2(KG(8,2))\le3.
\]

Stable source: https://arxiv.org/abs/2607.12353

## Searches completed

The following searches were repeated on September 4, 2026:

- exact arXiv identifier `2607.12353`;
- exact paper title, with and without author names;
- `KG(8,2)` together with `fractional chromatic`, `fractional cover`,
  `two-cover`, `5/2`, `14/5`, and `smallest beta`;
- exact phrases from the paper's open questions;
- GitHub code and repository searches for `KG(8,2)` fractional-cover
  certificates or subsequent implementations.

The arXiv record still showed version 1, submitted July 17, 2026. No later
preprint, published paper, repository, or indexed web result was found that
claims either the negative \(5/2\) answer, the exact cover number three, the
sharp independence parameter 10, or the \(14/5\) lower bound.

This is negative search evidence, not proof of priority.

## Closely related prior work

The source paper supplies the definitions, a two-graph \(5/2\)-fractional
cover of \(KG(7,2)\), and a triangle-free two-cover of \(KG(8,2)\). It also
notes that previously known triangle-free colorings do not settle the
fractional question. Those results are inputs and context, not rediscoveries
claimed here.

The structural use of Tutte-Berge is standard. The potentially novel content
is the combination of:

- the 11-edge double-star reduction;
- the exact opposite-11-set obstruction in triangle-free colorings;
- the resulting sharp Ramsey parameter 10;
- the fractional threshold lower bound \(14/5\);
- the application resolving the source paper's \(5/2\) question.

## Checks still required before a priority claim

1. Search MathSciNet, zbMATH, Google Scholar, and specialist citation indexes
   with institutional access.
2. Inspect every later version and citing work for arXiv:2607.12353.
3. Contact the source authors with the exact statements, written proof,
   independent checker, and Lean certificate.
4. Obtain independent graph-theory review of the reduction, the sharpness
   witness, and both finite encodings.
5. Search older literature on Ramsey colorings of Kneser graphs for an
   equivalent independence-number statement under different notation.

Until these checks are complete, the correct wording remains **candidate new
result** or **proposed resolution**, not an established first proof.
