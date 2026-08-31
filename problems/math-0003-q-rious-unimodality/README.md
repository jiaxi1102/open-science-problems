# math-0003: A proposed counterexample to q-rious unimodality

## Status

- **Problem status:** `proposed-refutation`
- **Formal verification:** `theorem-verified`
- **Novelty:** `no-prior-counterexample-found; provisional`
- **External review:** `none`

The exact arithmetic and formal statement are verified, but novelty and the
match to the authors' intended scope have not yet been confirmed by the
authors or an independent specialist. Until that happens, describe this as a
**proposed counterexample**, not as an externally established resolution.

## Source problem

S. Ole Warnaar and Wadim Zudilin, *q-rious unimodality*,
[arXiv:2502.03993](https://arxiv.org/abs/2502.03993), Conjecture 5.

For tuples of positive integers \(\mathbf a\) and \(\mathbf b\) satisfying
Landau's criterion, the conjecture states that

\[
(1+q)D(\mathbf a,\mathbf b;q),\qquad
D(\mathbf a,\mathbf b;q)=
\frac{\prod_i[a_i]!}{\prod_j[b_j]!},
\]

is unimodal.

## Candidate

Take

\[
\mathbf a=(12,5,3,2),\qquad
\mathbf b=(9,6,4,1,1,1).
\]

The pair is balanced with common sum 22, has height 2 and gcd 1, and has no
cancellable common tuple entry. Its Landau step function is nonnegative for
every real input.

The q-factorial ratio is

\[
D(q)=\frac{[12]![5]![3]![2]!}{[9]![6]![4]![1]!^3}
     =\frac{[2][10][11][12]}{[4][6]}
     =\Phi_2\Phi_5\Phi_{10}\Phi_{11}\Phi_{12}.
\]

Its coefficient sequence is

```text
1, 2, 2, 2, 3, 4, 5, 6, 7, 8, 8, 7,
7, 8, 8, 7, 6, 5, 4, 3, 2, 2, 2, 1
```

and the coefficient sequence of \((1+q)D(q)\) is

```text
1, 3, 4, 4, 5, 7, 9, 11, 13, 15, 16, 15, 14,
15, 16, 15, 13, 11, 9, 7, 5, 4, 4, 3, 1
```

The values at degrees 10, 12, and 14 are \(16,14,16\), which preclude any
weakly unimodal mode.

This refutes Conjecture 5 as written. It does **not** refute the original
q-rious positivity conjecture: every coefficient of \(D(q)\) here is
nonnegative.

## Verification layers

### Lean

`formal/QRiousCounterexample.lean` proves all three required components:

1. the Landau floor inequality for every real \(x\);
2. the exact cross-multiplied q-factorial polynomial identity;
3. non-unimodality from the certified coefficients at degrees 10, 12, and 14.

The CI workflow rejects unfinished proof markers, builds the project, invokes
Lean's environment checker, and audits the declaration dependencies.

### Independent exact computation

`experiments/verify_candidate.py` uses only the Python standard library. It
constructs q-factorials by dense integer convolution, performs exact monic
polynomial long division, checks all 180 Landau residue classes, and verifies
the complete coefficient vectors.

### Discovery search

`experiments/search_factorial_ratios.py` exhaustively scans a declared finite
scope. Within balanced partition pairs of total sum 2 through 22, positive
height at most 6, gcd 1, no common entries, and degree at most 1000, it checks
995,484 eligible pairs, of which 32,230 satisfy Landau's criterion. The pair
above is the only non-unimodal example in that scope and first occurs at total
sum 22. This is a scoped computational statement, not an unrestricted
minimality theorem.

## Reproduce

```bash
python3 experiments/verify_candidate.py

python3 -m venv .venv
source .venv/bin/activate
pip install -r experiments/requirements-search.txt
python3 experiments/search_factorial_ratios.py \
  --max-sum 22 --max-height 6 --max-degree 1000

cd formal
lake build
lake env lean QRiousCounterexample.lean
```

## Files

- `proof/PROOF.md`: human mathematical proof.
- `formal/QRiousCounterexample.lean`: formal certificate.
- `experiments/verify_candidate.py`: independent standard-library verifier.
- `experiments/search_factorial_ratios.py`: exhaustive discovery search.
- `artifacts/certificate.json`: machine-readable exact witness.
- `references/NOVELTY.md`: prior-art and status audit.

## Remaining gates

1. Send the candidate and certificate to Warnaar and Zudilin for statement and
   priority confirmation.
2. Obtain an independent review of the Landau reduction and q-factorial
   expansion.
3. Re-run broader literature and code searches after public disclosure.
4. Replace `proposed-refutation` by `externally-validated` only after those
   checks succeed.
