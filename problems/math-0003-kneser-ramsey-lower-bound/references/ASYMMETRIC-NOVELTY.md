# Novelty and source-comparison record: asymmetric padding

Search date: 4 September 2026, America/New_York. Results were checked via
live web search and the original arXiv HTML, not only search summaries.

## Exact claims under investigation

- Theorem A: R_r^KG(s,3) >= s(r+1), for r>=1 and s>=3.
- Written corollary B: R_r^KG(s,t) >= max(s,t)r+s+t-3, for s,t>=3.
- Construction: five cycle points, s-3 red padding points, and a blue
  padding step for the second clique parameter.

## Primary comparator

Emily Heath, Grace McCourt, Alex Parker, Coy Schwieder, Shira Zerbib,
*Ramsey numbers in Kneser graphs*, arXiv:2510.25734v2, 10 November 2025.
https://arxiv.org/html/2510.25734v2
https://arxiv.org/abs/2510.25734

Definition 1 matches the witness interpretation: clique vertices are
pairwise-disjoint r-sets. Proposition 10 gives R(s,t)+2r-2. The general
trivial lower bound is r*max(s,t). Theorem 11 gives 3r+2 in the diagonal
triangle case, while Theorem 12 includes the exact r=2 value 9.
Table 2 gives lower bounds 13,18,22 for R_3^KG(3,4), R_3^KG(3,5),
R_3^KG(3,6), respectively. Theorem A gives 16,20,24.

The arXiv record retrieved in this search points to v2. This does not
exclude an unindexed paper, a differently phrased result, or unpublished
work by the authors or others.

## Queries used

- "Kneser Ramsey" "s(r"
- "Kneser" "Ramsey" "sr+s"
- "Ramsey Numbers in Kneser Graphs" lower bounds
- "Kneser" "Ramsey" "s(r+1)"
- "Kneser Ramsey" "padding"
- "Kneser" "Ramsey" "16" "3,4"

The searches did not identify the displayed construction or theorem in
another primary source. Unrelated anti-Ramsey results, induced-host Ramsey
variants, and secondary machine-written literature summaries were not
used as evidence for the theorem or its novelty.

## Status and missing checks

Novelty status: search-incomplete. External review: none.
No priority claim or publication claim is justified by this record alone.
The source-paper authors and an independent Ramsey theorist have not yet
confirmed the result. A complete bibliographic/citation-chain search,
including MathSciNet or zbMATH, has not been performed.

## Scope guard

These bounds improve additive constants in a family of lower bounds.
They do not establish the matching diagonal upper bound, an exact formula
for the whole family, or a better leading asymptotic coefficient. For
parameter pairs where a previous bound is larger, retain that previous
bound rather than replace it with the weaker new formula.
