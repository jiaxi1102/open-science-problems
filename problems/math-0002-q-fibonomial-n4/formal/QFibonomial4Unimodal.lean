import QFibonomial4All

/-!
# From the first-difference theorem to unimodality

This file isolates the final order-theoretic step.  A coefficient sequence
that is symmetric in degree `D` and nondecreasing through the midpoint is
unimodal.  It then specializes that fact to any sequence satisfying the
q-Fibonomial first-difference law proved in the other modules.
-/

namespace QFibonomial4

/-- Symmetry of a coefficient sequence supported in degrees `0,...,D`. -/
def SymmetricAtDegree (c : ℕ → ℤ) (D : ℕ) : Prop :=
  ∀ k, k ≤ D → c k = c (D - k)

/-- Standard weak unimodality on the finite coefficient interval `0,...,D`. -/
def UnimodalAtDegree (c : ℕ → ℤ) (D : ℕ) : Prop :=
  ∃ M, M ≤ D ∧
    (∀ k, k < M → c k ≤ c (k + 1)) ∧
    (∀ k, M ≤ k → k < D → c (k + 1) ≤ c k)

/-- Symmetry reflects first-half increases into second-half decreases. -/
theorem symmetric_firstHalf_unimodal
    {c : ℕ → ℤ} {D : ℕ}
    (hsym : SymmetricAtDegree c D)
    (hinc : ∀ k, 2 * (k + 1) ≤ D → c k ≤ c (k + 1)) :
    UnimodalAtDegree c D := by
  refine ⟨D / 2, by omega, ?_, ?_⟩
  · intro k hk
    exact hinc k (by omega)
  · intro k hkMid hkD
    by_cases hcenter : 2 * k < D
    · have hs := hsym k (by omega)
      have hidx : D - k = k + 1 := by omega
      rw [hidx] at hs
      exact le_of_eq hs.symm
    · let j : ℕ := D - k - 1
      have hjinc : c j ≤ c (j + 1) := by
        apply hinc
        dsimp [j]
        omega
      have hsNext := hsym (k + 1) (by omega)
      have hsHere := hsym k (by omega)
      have hj0 : D - (k + 1) = j := by
        dsimp [j]
        omega
      have hj1 : D - k = j + 1 := by
        dsimp [j]
        omega
      calc
        c (k + 1) = c (D - (k + 1)) := hsNext
        _ = c j := by rw [hj0]
        _ ≤ c (j + 1) := hjinc
        _ = c (D - k) := by rw [hj1]
        _ = c k := hsHere.symm

/-- Degree of the `n=4` q-Fibonomial polynomial. -/
def qFib4Degree (m : ℕ) : ℕ :=
  3 * Nat.fib (m + 1) + 4 * Nat.fib (m + 2) - 7

/--
Any symmetric coefficient sequence satisfying the derived q-Fibonomial
first-difference formula is unimodal.  The published symmetry theorem supplies
`hsym` for the actual q-Fibonomial coefficients.
-/
theorem qFib4_unimodal_of_symmetry_and_difference
    (m : ℕ) (c : ℕ → ℤ)
    (hsym : SymmetricAtDegree c (qFib4Degree m))
    (hdiff : ∀ k, 1 ≤ k →
      c k - c (k - 1) =
        delta (Nat.fib (m + 1)) (Nat.fib (m + 2)) k) :
    UnimodalAtDegree c (qFib4Degree m) := by
  apply symmetric_firstHalf_unimodal hsym
  intro k hk
  have hkDelta :
      2 * (k + 1) + 7 ≤
        3 * Nat.fib (m + 1) + 4 * Nat.fib (m + 2) := by
    unfold qFib4Degree at hk
    omega
  have hnonneg := fibonacci_delta_nonnegative m (k + 1) hkDelta
  have hd := hdiff (k + 1) (by omega)
  have hsub : k + 1 - 1 = k := by omega
  rw [hsub] at hd
  omega

#print axioms symmetric_firstHalf_unimodal
#print axioms qFib4_unimodal_of_symmetry_and_difference

end QFibonomial4
