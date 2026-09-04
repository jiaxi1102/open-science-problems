# Result states

Each matrix job terminates in exactly one research status:

- `UNSAT_DRAT_VERIFIED`: the counterexample formula is unsatisfiable and the proof trace passed independent replay;
- `SAT_MODEL_VERIFIED`: a counterexample assignment passed direct semantic reconstruction;
- `TIMEOUT_NO_CLAIM`: no mathematical conclusion;
- `SOLVER_ERROR_NO_CLAIM`: no mathematical conclusion.

Only the first two are certificate-bearing outcomes. The exact-threshold theorem requires `UNSAT_DRAT_VERIFIED` for both modular jobs.
