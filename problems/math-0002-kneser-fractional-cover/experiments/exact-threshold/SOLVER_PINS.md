# Solver and checker pins

The certificate workflow builds the following upstream revisions from source:

- CaDiCaL: `c60730422e758ef1cebe7aeddf2dda31c996bf04`
- drat-trim: `2e3b2dc0ecf938addbd779d42877b6ed69d9a985`

CaDiCaL produces the search verdict and proof trace. `drat-trim` is compiled independently and must replay an UNSAT trace to the exact verdict `s VERIFIED`. Binary hashes and source revision identifiers are retained in each workflow artifact.
