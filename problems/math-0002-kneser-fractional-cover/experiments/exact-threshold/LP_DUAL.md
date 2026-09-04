# Fractional-colouring dual used by the certificate

For a graph `H`, the fractional chromatic number is at least the value of any nonnegative vertex weighting `y` satisfying `sum_{v in I} y_v <= 1` for every independent set `I`.

For a three-set `S`, assign weight `1/5` to the three Kneser vertices in `binom(S,2)` and `1/10` to the other 25 vertices. The total is `31/10`. Multiplying every independent-set inequality by ten shows that dual feasibility is exactly

```text
|I| + |I ∩ binom(S,2)| <= 10.
```

The `petersen-template` formula searches for a violating independent set of weighted size at least eleven.
