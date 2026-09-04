# Reproduce the finite instances

From this directory:

```bash
python exact_threshold_search.py self-test
rm -rf results
python exact_threshold_search.py generate petersen results/petersen
python exact_threshold_search.py generate petersen-template results/petersen-template
```

Expected dimensions and hashes:

| mode | variables | clauses | CNF SHA-256 |
|---|---:|---:|---|
| `petersen` | 210 | 953 | `f1e846f3bb2c6a05a997d3d6f85102f5d365176c990bb8ec9a1633a01b8803be` |
| `petersen-template` | 838 | 2,256 | `3119d5c5b04f8a7c8c3a096bf31af04f40e71fec1de985256a55d34d388628c8` |

A solver's `UNSATISFIABLE` status is not sufficient. Replay its proof with the independently built checker:

```bash
cadical --no-binary instance.cnf proof.drat
drat-trim instance.cnf proof.drat
```

The required checker verdict is exactly:

```text
s VERIFIED
```

For a SAT result, pass the complete solver output to the generator's `verify` subcommand; it reconstructs every semantic condition rather than merely evaluating the emitted auxiliary CNF.
