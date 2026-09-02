# Proof that `ι(Q₆,Q₂)=5>4=γ(Q₄)`

## Reduction to projected dominating codes

Identify `Q_n` with `{0,1}^n`. Every subgraph of `Q_n` isomorphic to `Q_2` is a coordinate square: traversing a four-cycle flips two coordinates in alternating order. Such a square is specified by two free coordinates and a binary assignment on the other `n-2` coordinates.

For `D⊆Q_6` and a four-coordinate set `J`, write `π_J(D)` for the projection of `D` onto `J`. A coordinate square whose fixed coordinates are `J` and whose fixed pattern is `x∈Q_4` meets `N[D]` exactly when some `d∈D` has `d_H(π_J(d),x)≤1`. Consequently,

> `D` is `Q_2`-isolating in `Q_6` iff `π_J(D)` dominates `Q_4` for every four-coordinate set `J`.

## The comparison value `γ(Q₄)=4`

Every closed neighborhood in `Q_4` has size five. Three centers cover at most fifteen of the sixteen vertices, so `γ(Q_4)≥4`. The set

```text
{0000,0001,1110,1111}
```

dominates `Q_4`, hence `γ(Q_4)=4`.

## Lower bound: four vertices cannot isolate every square

Assume, for contradiction, that `C={c₀,c₁,c₂,c₃}⊆Q_6` is `Q_2`-isolating. Every four-coordinate projection of `C` therefore dominates `Q_4`.

### Balanced-column lemma

In any four-center dominating code in `Q_4`, every coordinate column has two zeros and two ones.

Fix a coordinate, and suppose `t` of the four centers have bit zero there. In the zero slice, each zero-bit center covers at most four vertices, while each one-bit center covers at most one. Thus the four centers cover at most

```text
4t+(4-t)=3t+4
```

of the eight zero-slice vertices, forcing `t≥2`. Applying the same argument to the one slice gives `t≤2`. Hence `t=2`.

Every coordinate of `C` belongs to some four-coordinate projection, so the lemma says that every one of the six columns of the `4×6` binary matrix of `C` is balanced.

Translate the cube by `c₀` (bitwise XOR), which preserves Hamming distance and coordinate squares. The first row is now `000000`. A balanced column is therefore one of precisely three types on the other rows:

```text
A = (1,1,0),   B = (1,0,1),   C = (0,1,1).
```

Any four selected columns must give a dominating four-center code in `Q_4`.

* A symbol cannot occur at least four times. Four identical columns yield only two distinct projected rows, which cannot dominate `Q_4`.
* Two different symbols cannot both occur at least twice. Choosing two columns of each type gives, up to row and coordinate permutations,

  ```text
  {0000,1111,1100,0011}.
  ```

  The vertex `1010` is at Hamming distance two from all four centers.

Thus at most one symbol occurs more than once, and it occurs at most three times. The six columns would then number at most `3+1+1=5`, contradiction. Therefore `ι(Q_6,Q_2)≥5`.

## Upper bound: a five-vertex witness

Let

```text
D={000000,000011,000101,111001,111110}.
```

Reading the six columns across these five rows gives three equal columns and three distinct remaining columns. Hence, up to cube automorphisms, a four-coordinate projection has one of three multiplicity forms. Representative projected center sets are:

| Type | Centers in `Q₄` |
|---|---|
| `AAAB` | `{0000,0001,1110,1111}` |
| `AABC` | `{0000,0010,0011,1101,1110}` |
| `ABCE` | `{0000,0101,0110,1011,1100}` |

A direct radius-one check shows that each set dominates all sixteen vertices of `Q_4`. The Lean theorem `isolatingWitnessQ6_valid` checks all fifteen coordinate projections and all sixteen fixed patterns. Therefore `ι(Q_6,Q_2)≤5`.

Combining the two bounds gives `ι(Q_6,Q_2)=5`, while `γ(Q_4)=4`. This refutes the proposed universal equality.
