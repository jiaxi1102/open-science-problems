# Nine-point link verification record

- Repository: `jiaxi1102/open-science-problems`
- Branch: `math-0003-local-link-k5`
- Verified commit: `216fa09bd6b555f1d2c50320530f875b8446d5f8`
- GitHub Actions run: `33699675062`
- Job: `100476040518`
- Conclusion: `success`
- Verified: 3 September 2026
- Runner: Ubuntu 24.04
- Python: 3.12.14
- Artifact: `9873052699`
- Artifact archive SHA-256: `fc0a2a4aed81402d2c86a5e3559514a1543ad3bef04c805af9ea6d8f9be7b28b`

## Verified finite theorem

Every red/blue coloring of the triples of a nine-point set with no
monochromatic perfect matching contains a monochromatic `K_5^(3)`.
Equivalently, for complementary 3-graphs on nine vertices with matching
numbers at most two, one color has transversal number at most four.

The workflow performed four checks:

1. rejected unfinished markers and third-party decision dependencies;
2. regenerated the canonical 813-clause finite formulation;
3. generated and traversed the deterministic unit-propagation DPLL proof DAG;
4. serialized, decompressed, and independently rechecked the complete proof
   certificate, then compared the two result records byte for byte.

The verified certificate statistics were:

```text
Boolean variables:             84
Perfect-matching constraints:  280
Five-set constraints:          126
CNF clauses:                   813
DPLL internal nodes:           9,536
Conflict leaves:               9,537
Proof references:              19,073
Canonical raw proof bytes:     589,720
```

The canonical hashes were:

```text
CNF SHA-256:
0db7c378b5fdf09326e5190ad6697e64b2a508ce39075864bcb3cd4918b84314

Raw proof-certificate SHA-256:
30a35dcd239712ee87e4f65ddb5ab71a0965facf63d5595fd237ad95e9c6223d
```

The compressed certificate is treated only as a transport representation;
its bytes may vary across Python and zlib builds. Verification decompresses it
and checks the canonical raw payload hash.

## Sharpness check

The same workflow exhaustively checked the Fano-star coloring on nine points:

- red triples: all triples through one distinguished point plus the seven Fano
  lines on seven other points;
- blue triples: the complement;
- monochromatic perfect matchings: zero;
- red transversal number: four;
- blue transversal number: five;
- monochromatic blue copies of `K_5^(3)`: seven;
- monochromatic copies of `K_6^(3)`: zero.

Therefore five is exactly the largest complete 3-graph order guaranteed by the
finite theorem's hypotheses.

## Boundary

This record certifies the finite nine-point theorem and its sharpness example.
It does not establish the existence or nonexistence of a good coloring of
`KG(12,3)`, does not prove the general Kneser-Ramsey upper bound, and does not
establish novelty. A human structural proof, Lean formalization, literature
audit, and global five-cloud compatibility argument remain separate gates.
