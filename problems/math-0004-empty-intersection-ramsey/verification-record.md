# Verification record: half-density empty-intersection theorem

## First complete successful build

- Repository: `jiaxi1102/open-science-problems`
- Branch: `math-0004-empty-intersection-ramsey`
- Verified source commit: `8a8ea48db87f8c01d623f1eb85f64fbe58aeb475`
- Workflow run: `33945082400`
- Job: `101249593987`
- Conclusion: `success`
- Verified artifact: `9963123342`, `empty-intersection-verified`
- Artifact creation timestamp: `2026-09-05T04:42:56Z`
- Lean: `4.33.1`
- Mathlib: `0df444a360eaa60ab8c11dca51a86af692955474` (v4.33.1)

Run: https://github.com/jiaxi1102/open-science-problems/actions/runs/33945082400

Archive SHA-256:

```
4de61e10c3c5c7a6c53b154c70d0e1107a9fa7e4a754787237b5cb60059bad8f
```

The downloaded archive digest and all 15 manifested files were checked locally. Those counts refer to the first verified artifact, not the later documentation package.

## Actual Lean output

```
Built CoreData (8.0s)
Built Resolution (89s)
'EmptyIntersection.impossible' depends on axioms:
  [propext, Classical.choice, Quot.sound]
Built Finite (646ms)
'EmptyIntersection.finiteIntersectionRamsey' depends on axioms:
  [propext, Classical.choice, Quot.sound]
Built Lift (37s)
'EmptyIntersection.uniformHalfIntersectionRamsey' depends on axioms:
  [propext, Classical.choice, Quot.sound]
Build completed successfully (8710 jobs).
Exit status: 0
```

All four modules are explicit Lake roots. The workflow requires the actual named theorem outputs and rejects dependencies outside the standard allowlist. The project proofs use no placeholders, hand-written axioms, native_decide, or bv_decide. Geometric table lemmas use `decide +kernel`; resolution uses ordinary proof terms.

The build used about 12 GB peak resident memory. There are 8710 build jobs including dependencies, NOT 8710 new theorems. Lean was run in GitHub Actions, not the local runtime.

## Independent replay

The exact downloaded certificate passed `experiments/verify_certificate.py` locally. It independently reconstructs all geometry and uses only the Python standard library:

- 20 vertices, 190 variables, 480 relevant triples, 960 initial clauses;
- 1898 derived clauses ending in the empty clause;
- 74719 propagation steps checked;
- certificate SHA-256 `d097fb214e2cb9d0168fb8c769ed2d9c75c73c6851b9e45f161ce10acf14547e`;
- resolution-source SHA-256 `baa94b8644b83f38cc5a33b76f6190cba508ebc8b1bea54b1a786757be8c7061`.

The Lean representation keeps 34649 propagation steps after pruning unused dependencies. A separate set-based SciPy/HiGHS integer-programming model reported infeasibility. That result is supplementary, not part of the formal proof.

## Boundary

The final theorem quantifies over every positive q and every Boolean pair coloring on all 3q-element subsets of `Fin 6 × Fin q`, and produces three distinct monochromatic vertices with empty three-way intersection. `ground_card` proves ground-set size 6q.

The real-valued extremal beta is not separately defined in Lean. Substituting k=3q gives beta≤2. Optimality, the strict-majority question, and the original Kneser-Ramsey leading constant are not proved. Written smaller-density and P(5,3) countercoloring corollaries are not additional formal theorems.

Earlier failed runs are not presented as successful verification: the monolithic proof was interrupted by a runner shutdown; subsequent split-proof builds exposed a finite-order interface and then two block-lift interfaces. The successful source above fixes them. Bounded strict-majority searches returned UNKNOWN for both (9,5) and (11,6).

Novelty remains `search-incomplete`; external review is `none`.
