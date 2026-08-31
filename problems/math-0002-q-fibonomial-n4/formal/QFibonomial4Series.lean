import QFibonomial4

/-!
# Denominator recurrence for the partition coefficients

The sequence `g n = floor((n^2 + 6n + 12)/12)` is the coefficient sequence
of `1 / ((1-q)(1-q^2)(1-q^3))`.  The key algebraic certificate is the
six-step relation and the resulting order-six denominator recurrence.
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
`(1-q)(1-q^2)(1-q^3)`.
-/
theorem g_denominator_recurrence (n : ℕ) (hn : 1 ≤ n) :
    g n + g (n - 4) + g (n - 5) =
      g (n - 1) + g (n - 2) + g (n - 6) := by
  induction n using Nat.strong_induction_on with
  | h n ih =>
      by_cases hn12 : n < 12
      · interval_cases n <;> native_decide
      · have hn12' : 12 ≤ n := by omega
        have ih6 := ih (n - 6) (by omega) (by omega)
        have h0 : g n = g (n - 6) + n := by
          have hstep := g_add_six (n - 6)
          convert hstep using 1 <;> omega
        have h1 : g (n - 1) = g (n - 7) + (n - 1) := by
          have hstep := g_add_six (n - 7)
          convert hstep using 1 <;> omega
        have h2 : g (n - 2) = g (n - 8) + (n - 2) := by
          have hstep := g_add_six (n - 8)
          convert hstep using 1 <;> omega
        have h4 : g (n - 4) = g (n - 10) + (n - 4) := by
          have hstep := g_add_six (n - 10)
          convert hstep using 1 <;> omega
        have h5 : g (n - 5) = g (n - 11) + (n - 5) := by
          have hstep := g_add_six (n - 11)
          convert hstep using 1 <;> omega
        have h6 : g (n - 6) = g (n - 12) + (n - 6) := by
          have hstep := g_add_six (n - 12)
          convert hstep using 1 <;> omega
        omega

/-- Constant coefficient of the denominator product. -/
theorem g_initial : g 0 = 1 := by native_decide

#print axioms g_add_six
#print axioms g_denominator_recurrence

end QFibonomial4
