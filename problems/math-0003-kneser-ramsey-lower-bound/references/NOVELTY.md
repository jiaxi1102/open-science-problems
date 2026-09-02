# Novelty and prior-art record

**Last searched:** 2 September 2026  
**Status:** `search-incomplete`; no priority claim established.

## Closest primary source

Emily Heath, Grace McCourt, Alex Parker, Coy Schwieder, and Shira Zerbib,
*Ramsey Numbers in Kneser Graphs*, arXiv:2510.25734v2.

The posted paper:

- defines `R_r^{KG}(s,t)`;
- proves `R_r^{KG}(3,3) >= 3r+2` for `r>=2` by coloring
  `KG(3r+1,r)`;
- proves `R_2^{KG}(3,3)=9`;
- reports `R_3^{KG}(3,3)<=13` computationally; and
- supplies an explicit good coloring of `KG(8,2)`.

The proof of its uniform lower bound partitions Kneser vertices according to
membership in two distinguished ground points. It is different from the
five-point trace gadget here, which colors `KG(3r+2,r)` and gains one further
ground point uniformly in `r`.

The paper's `KG(8,2)` appendix coloring has the same coarse split into traces
of size `0,1,2` relative to a five-element ground part, but its listed
completion is not the same trace-only rule used here. The present theorem was
found independently by first extracting an explicit `KG(11,3)` rule from a
SAT witness and then observing that the rule only needs five distinguished
points and extends to arbitrary `r`.

## Searches performed

Web/arXiv searches included the following combinations:

- `Kneser Ramsey 3r+3`;
- `R_r^{KG}(3,3) 3r+3`;
- `KG(3r+2,r) monochromatic triangle coloring`;
- `Kneser graph edge coloring no monochromatic triangle C5`;
- `five-cycle trace coloring Kneser graph`;
- searches around the cited MathOverflow question on Ramsey theory for
  Kneser graphs; and
- inspection of the full HTML text and appendices of arXiv:2510.25734v2.

These searches recovered the Heath et al. paper and secondary summaries of
it, all stating the weaker posted bound `3r+2`. They did not recover a source
stating the theorem

\[
R_r^{KG}(3,3)\ge3r+3
\]

or the five-point construction.

## What remains before a novelty claim

1. Search MathSciNet and zbMATH by formula and terminology.
2. Search Google Scholar cited-by and citing chains for the Heath et al.
   paper, including manuscripts not indexed by arXiv search.
3. Check later revisions, conference abstracts, slides, and authors' pages.
4. Ask the authors of arXiv:2510.25734 directly whether they know this
   construction or an unpublished strengthening.
5. Obtain an independent subject-matter review of the proof.

Until those steps are complete, repository and manuscript language must use
`proposed new theorem`, `candidate strengthening`, or equivalent wording—not
`first`, `novel`, or `solved` without qualification.
