# Novelty and statement audit

**Audit date:** 2026-08-31

## Source statement

Primary source reviewed:

- S. Ole Warnaar and Wadim Zudilin, *q-rious unimodality*,
  [arXiv:2502.03993](https://arxiv.org/abs/2502.03993).

Conjecture 5 states, without an irreducibility or height-one restriction, that
if a pair of positive-integer tuples satisfies Landau's criterion, then
\((1+q)D(\mathbf a,\mathbf b;q)\) is unimodal. The candidate in this directory
uses positive entries, is balanced and coprime, has height two, has no common
entry to cancel, and satisfies the stronger all-real version of Landau's
criterion.

The paper proves the conjecture for Bober's 52 sporadic height-one pairs and
one classified two-parameter family, and reports substantial computational
checks for several known families. Those checks are not an exhaustive scan of
all balanced pairs of height two.

## Searches performed

The following exact or near-exact searches were run across general web search,
arXiv-indexed results, scholarly metadata pages, and GitHub code search:

```text
"q-rious unimodality" counterexample
"q-rious unimodality" refutation
"Conjecture 5" "q-rious unimodality"
Warnaar Zudilin counterexample
"12, 5, 3, 2" "9, 6, 4, 1, 1, 1"
"12,5,3,2" "9,6,4,1,1,1" factorial ratio
"[12]![5]![3]![2]!" "[9]![6]![4]!"
"[2][10][11][12]" "[4][6]"
"Phi_2" "Phi_5" "Phi_10" "Phi_11" "Phi_12" unimodal
"16,15,14,15,16" "q-rious"
```

No matching prior counterexample, proof of failure, or occurrence of the exact
pair was found. Searches also found the original preprint still presenting the
claim as a conjecture and current open-problem indexes still describing the
q-rious unimodality program as unresolved.

## What this audit does not establish

A negative literature search is not a priority proof. In particular, it may
miss:

- an unpublished or privately circulated observation;
- a recent manuscript not yet indexed;
- a result stated in different notation;
- author knowledge not reflected in the public version;
- an intended convention not explicit in the printed statement.

The three denominator entries equal to 1 deserve explicit attention. They are
allowed positive integers and affect Landau's criterion and the scaled
factorial ratios, although \([1]!=1\) in the single polynomial at \(n=1\).
The source statement does not exclude them. Author confirmation should check
that this matches the intended scope.

## Current novelty assessment

`no-prior-counterexample-found; provisional`

The result should remain labelled **proposed counterexample** until the authors
or independent experts confirm both the statement match and priority.
