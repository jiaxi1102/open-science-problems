# Verification record

## Verified result

The finite core establishes that a triangle-free red-blue coloring of
`E(KG(8,2))` cannot have an independent 11-set in both color graphs. Together
with the human outer reduction, this yields

\[
\beta_2(KG(8,2))\ge \frac{14}{5}
\]

and, in particular,

\[
c_{\{\chi_f\le5/2\}}(KG(8,2))=3.
\]

## Canonical CI run

- Repository: `jiaxi1102/open-science-problems`
- Branch: `math-0002-strengthen-beta-lower-bound`
- Verified source commit: `e114dadfdb9cad0330bc944cacb40df53aa1e4ca`
- GitHub Actions run: `33899078059`
- Job: `101108622554`
- Conclusion: `success`
- Verified at: 4 September 2026
- Runner: Ubuntu 24.04
- Lean: 4.33.1 (`819816b2e0a3bf405af45ae5c7af2491d8f5bee6`)
- Lake: 5.0.0

## Independent exhaustive verification

A separately written C++20 verifier generated `KG(8,2)` from first principles,
fixed only the first double-star core using the documented `S_8` symmetry, and
checked all

\[
\binom{13}{11}\cdot 28\binom{13}{11}=170{,}352
\]

candidate pairs of oppositely monochromatic 11-subsets.

Its deterministic terminal record was:

```text
UNSAT k=11 tested=170352 overlap=129666 nodes=40027816 seconds=247.032
```

Thus:

- 170,352 candidate pairs were considered;
- 129,666 had an immediate forced-color conflict;
- all remaining cases were rejected by a complete DPLL search over the 420
  not-all-equal triangle constraints;
- the search explored 40,027,816 deterministic DPLL nodes.

The workflow compiled the verifier with:

```text
g++ -O3 -std=c++20 -Wall -Wextra -pedantic
```

and required the exact counts above before proceeding to Lean.

## Lean certificate

`formal/generate_lean.py` deterministically generated a 127,901-byte Lean
source file with SHA-256:

```text
2a51c43c1f9ec8e0f2bbfa76cf7333dc1dcc53ded85a67ff5212a863647b68a9
```

CI checked the hash, rejected `sorry`, `admit`, and hand-written `axiom`
declarations, and completed `lake build` successfully. The two finite theorems
are:

- `KneserCover.matchingFree11_is_doubleStar`;
- `KneserCover.core01_obstruction_11`.

Lean reported a 238-second build for the generated source.

## Trust boundary

Lean's `#print axioms` reported the standard logical axioms `propext`,
`Classical.choice`, and `Quot.sound`, together with one generated native
`bv_decide` computation axiom for each finite theorem:

- `matchingFree11_is_doubleStar._native.bv_decide.ax_1_27`;
- `core01_obstruction_11._native.bv_decide.ax_1_47`.

This is the documented native-`bv_decide` trust boundary in Lean 4.33.1. No
external solver result is imported into Lean as an axiom.

## Formalization boundary

The finite obstruction is independently checked twice. The outer bridge is
still human-checked rather than end-to-end formalized: fractional-chromatic
monotonicity, `χ_f(H) ≥ |V(H)|/α(H)`, Tutte-Berge, the `S_8` transitivity
argument, and the explicit three-bipartite-graph upper bound remain to be
encoded in a general graph library.
