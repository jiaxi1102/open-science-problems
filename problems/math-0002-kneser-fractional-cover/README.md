# Fractional \(5/2\)-cover number of \(KG(8,2)\)

**ID:** `math-0002`  
**Field:** graph theory / fractional coloring / Kneser graphs  
**Original source:** Gujgiczer–Marits–Ozeki, arXiv:2607.12353v1 (July 2026)  
**Problem status:** `proposed-proof`  
**Formal verification:** `partial-theorem-verified`  
**Novelty:** `search-incomplete`  
**External review:** `none`

## Original problem

Let \(\mathcal C_{5/2}=\{H:\chi_f(H)\le 5/2\}\), and let \(c_{\mathcal C_{5/2}}(G)\) be the least number of members of this class whose edge sets cover \(E(G)\). The source paper asks whether the Kneser graph \(KG(8,2)\) can be covered by two graphs in \(\mathcal C_{5/2}\).

The 28 vertices of \(KG(8,2)\) are the two-element subsets of an eight-element set; two vertices are adjacent when the corresponding pairs are disjoint.

## Why it matters

The question separates ordinary triangle-free covers from covers controlled by fractional chromatic number. The source paper gives a two-graph triangle-free cover but leaves open whether the stronger fractional threshold \(5/2\) can still be achieved. Resolving the first unknown Kneser instance also determines the full cutoff for the family \(KG(n,2)\) at this threshold.

## Result

The candidate theorem is

\[
c_{\mathcal C_{5/2}}(KG(8,2))=3.
\]

Thus the proposed answer to the original two-cover question is **no**. Combined with the source paper's construction for \(KG(7,2)\), the argument gives

\[
KG(n,2)\text{ has a two-graph }5/2\text{-fractional cover}\iff n\le 7.
\]

The finite core proves the stronger Ramsey-type statement that every red–blue coloring of \(E(KG(8,2))\) without a monochromatic triangle has at least one color graph with independence number at most 11. Consequently, the two-cover fractional threshold is at least \(28/11>5/2\).

## Argument / evidence

The upper bound of three uses an explicit proper six-coloring of \(KG(8,2)\), three-bit codes for the six colors, and one bipartite covering graph per bit.

For the lower bound, a hypothetical two-cover can be reduced to a red–blue edge partition. Since \(\chi_f(K_3)=3\), both color graphs are triangle-free. The inequality \(\chi_f(H)\ge |V(H)|/\alpha(H)\) forces a 12-vertex independent set in each color graph.

Viewing the vertices of \(KG(8,2)\) as the edges of \(K_8\), each such 12-set is a 12-edge family with matching number at most two. A Tutte–Berge argument places every such family inside a 13-edge double star. The remaining finite obstruction—two oppositely monochromatic 12-subsets of double stars in a triangle-free red–blue coloring—is checked exhaustively in Lean after fixing one double-star core by the transitive \(S_8\)-action.

See [`proof.md`](proof.md) for the complete written argument.

## Formalization boundary

Lean verifies the two delicate finite statements:

- `matchingFree12_is_doubleStar`: every matching-free 12-subset of the 28 edges of \(K_8\) is contained in a double star;
- `core01_obstruction`: after fixing one core by symmetry, no choice of the second core, the two 12-subsets, and the 210 edge colors satisfies all required constraints.

The outer mathematical bridge is currently human-checked rather than formalized end to end. It includes fractional-chromatic monotonicity, \(\chi_f(H)\ge |V|/\alpha\), the reduction from a cover to an edge partition, Tutte–Berge, the symmetry reduction, and the explicit three-graph upper-bound construction.

The finite proofs use Lean's `bv_decide`. In Lean 4.33.1 this includes native reflective computation, so the compiler/native evaluator is part of the trusted computing base. There are no `sorry`, `admit`, or hand-written `axiom` declarations.

## Reproduce

```bash
cd problems/math-0002-kneser-fractional-cover/formal
python generate_lean.py
python finalize_lean.py
lake build
```

Pinned environment:

- Lean 4.33.1
- Lake 5.0.0
- generated `KneserCover.lean` SHA-256: `143b3fdcb75423e419eb10d1ce7c8f9fbc700f22a0cd4d55d65e27950c0667e9`

The successful CI run and trust-boundary details are recorded in [`verification-record.md`](verification-record.md).

## Novelty / prior art

The July 2026 source explicitly states the two-cover question as open. A comprehensive post-publication literature and citation search has not yet been completed, and the source authors have not yet confirmed priority. See [`references/NOVELTY.md`](references/NOVELTY.md).

## Risks and unresolved items

The strongest remaining risks are a mismatch between the encoded finite obstruction and the intended graph-theoretic reduction, an overlooked issue in the human outer argument, or an independent resolution appearing after the cited preprint. Green CI establishes the generated finite Lean theorems under the stated trust model; it does not establish novelty or complete formal equivalence to the literature question.

## Next gates

1. Independent graph-theory audit of the reduction and the generated enumeration.
2. Reproduction of the Lean build on a separate machine.
3. Comprehensive novelty search and contact with the source authors.
4. End-to-end Lean formalization of the outer fractional-coloring and symmetry bridge.
5. Prepare a concise manuscript only after the preceding gates are documented.
