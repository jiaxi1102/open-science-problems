# Conditional theorem assembled by the two certificates

Assume both finite counterexample formulas certify UNSAT.

1. Every red/blue colouring of `E(KG(8,2))` without a monochromatic triangle has a monochromatic induced `KG(5,2)`.
2. If one colour contains such a Petersen graph on a five-set `T`, then for the complementary three-set `S` every independent set `I` in that colour satisfies
   \[
   |I|+|I\cap\binom S2|\le10.
   \]
3. Therefore the weights `1/5` on `binom(S,2)` and `1/10` elsewhere are feasible for the fractional-colouring dual and have total `31/10`.
4. Hence every triangle-free red/blue partition has one colour with fractional chromatic number at least `31/10`.
5. Any two-cover with both fractional chromatic numbers below `3` can be reduced to a triangle-free edge partition, contradicting step 4.
6. The existing two-coordinate ternary construction gives a two-cover with both fractional chromatic numbers at most `3`.

Thus the conditional conclusion is

\[
\tau_2(KG(8,2))=3.
\]

This file is a claim ledger, not evidence that the assumptions have already been certified.
