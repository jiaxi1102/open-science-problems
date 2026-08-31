import QFibonomial4

/-!
# Denominator recurrence for the partition coefficients

The sequence `g n = floor((n^2 + 6n + 12)/12)` is the coefficient sequence
of `1 / ((1-q)(1-q^2)(1-q^3))`.  The key algebraic certificate is the
six-step relation and the resulting order-six denominator recurrence.
Negative coefficient indices are represented by `shiftedG`, hence contribute
zero rather than being truncated by natural-number subtraction.
-/

namespace QFibonomial4

lemma quad_add_six (n : ℕ) :
    quad (n + 6) = quad n + 12 * (n + 6) := by
  unfold quad
  ring

/-- The closed formula advances by `n+6` every six steps. -/
theorem g_add_six (n : ℕ) :
    g (n + 6) = g n + n + 6 := by
  unfold g
  rw [quad_add_six]
  omega

/--
The coefficient recurrence obtained by multiplying by
`(1-q)(1-q^2)(1-q^3)`.  The shifted terms implement the convention that
coefficients of negative degree are zero.
-/
theorem g_denominator_recurrence (n : ℕ) (hn : 1 ≤ n) :
    (g n : ℤ) + shiftedG n 4 + shiftedG n 5 =
      shiftedG n 1 + shiftedG n 2 + shiftedG n 6 := by
  induction n using Nat.strong_induction_on with
  | h n ih =>
      by_cases hn12 : n < 12
      · interval_cases n <;> norm_num [g, quad, shiftedG]
      · have hn12' : 12 ≤ n := by omega
        have ih6 := ih (n - 6) (by omega) (by omega)
        simp [shiftedG, Nat.sub_sub,
          show 1 ≤ n - 6 by omega, show 2 ≤ n - 6 by omega,
          show 4 ≤ n - 6 by omega, show 5 ≤ n - 6 by omega,
          show 6 ≤ n - 6 by omega] at ih6
        have h0Nat : g n = g (n - 6) + n := by
          have hstep := g_add_six (n - 6)
          have hidx : n - 6 + 6 = n := by omega
          rw [hidx] at hstep
          omega
        have h1Nat : g (n - 1) = g (n - 7) + (n - 1) := by
          have hstep := g_add_six (n - 7)
          have hidx : n - 7 + 6 = n - 1 := by omega
          rw [hidx] at hstep
          omega
        have h2Nat : g (n - 2) = g (n - 8) + (n - 2) := by
          have hstep := g_add_six (n - 8)
          have hidx : n - 8 + 6 = n - 2 := by omega
          rw [hidx] at hstep
          omega
        have h4Nat : g (n - 4) = g (n - 10) + (n - 4) := by
          have hstep := g_add_six (n - 10)
          have hidx : n - 10 + 6 = n - 4 := by omega
          rw [hidx] at hstep
          omega
        have h5Nat : g (n - 5) = g (n - 11) + (n - 5) := by
          have hstep := g_add_six (n - 11)
          have hidx : n - 11 + 6 = n - 5 := by omega
          rw [hidx] at hstep
          omega
        have h6Nat : g (n - 6) = g (n - 12) + (n - 6) := by
          have hstep := g_add_six (n - 12)
          have hidx : n - 12 + 6 = n - 6 := by omega
          rw [hidx] at hstep
          omega
        have h0 : (g n : ℤ) = (g (n - 6) : ℤ) + (n : ℤ) := by
          exact_mod_cast h0Nat
        have h1 : (g (n - 1) : ℤ) = (g (n - 7) : ℤ) + (n - 1 : ℕ) := by
          exact_mod_cast h1Nat
        have h2 : (g (n - 2) : ℤ) = (g (n - 8) : ℤ) + (n - 2 : ℕ) := by
          exact_mod_cast h2Nat
        have h4 : (g (n - 4) : ℤ) = (g (n - 10) : ℤ) + (n - 4 : ℕ) := by
          exact_mod_cast h4Nat
        have h5 : (g (n - 5) : ℤ) = (g (n - 11) : ℤ) + (n - 5 : ℕ) := by
          exact_mod_cast h5Nat
        have h6 : (g (n - 6) : ℤ) = (g (n - 12) : ℤ) + (n - 6 : ℕ) := by
          exact_mod_cast h6Nat
        simp [shiftedG, show 1 ≤ n by omega, show 2 ≤ n by omega,
          show 4 ≤ n by omega, show 5 ≤ n by omega, show 6 ≤ n by omega]
        omega

/-- Constant coefficient of the denominator product. -/
theorem g_initial : g 0 = 1 := by norm_num [g, quad]

#print axioms g_add_six
#print axioms g_denominator_recurrence

end QFibonomial4
