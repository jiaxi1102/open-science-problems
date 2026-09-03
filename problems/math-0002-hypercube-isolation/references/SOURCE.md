# Source and provenance

## Original graph problem

- Boštjan Brešar and Douglas F. Rall,
  *On the isolation numbers in graph products*.
- arXiv:2608.25752v1, submitted 2026-08-26.
- Problem 2 asks whether

  ```text
  ι(Q_n,Q_k)=γ(Q_(n-k))
  ```

  for every `0<k<n`.
- The paper proves the lower bound
  `ι(Q_n,Q_k)>=γ(Q_(n-k))` and leaves equality open.

## Coding-theory identification

- Charles J. Colbourn, Gábor Kéri, Gabriel Rivas Soriano, and Jan-Christoph
  Schlage-Puchta,
  *Covering and radius-covering arrays: Constructions and classification*,
  Discrete Applied Mathematics 158 (2010), 1158--1180.
- This paper defines radius-covering arrays, records the table entry
  `CAN_1(4,6,2)=5`, and proves the one-extra-column equality
  `CAN_r(m,m+1,2)=K_2(m,r)` in Theorem 7.3.

- Jörn Quistorff and Jan-Christoph Schlage-Puchta,
  *On generalized surjective codes*, Studia Scientiarum Mathematicarum
  Hungarica 48 (2011), 46--63.
- This paper studies the same family under the terminology of
  `s`-surjective codes with radius and provides recursive bounds and exact
  small cases.

## Repository result

The repository proves the exact graph--coding dictionary

```text
I_r(n,m)=CAN_r(m,n,2)
```

and develops structural consequences for perfect Hamming codes and fixed
codimension. The graph problem, established coding parameters,
candidate-new structural deductions, and external-review status are kept
separate in the README and novelty record.
