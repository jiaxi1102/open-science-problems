import QFibonomial4

/-!
# Complete Fibonacci specialization of the reduced first-difference theorem

The symbolic argument in `QFibonomial4.lean` handles every `m >= 8`.
The eight smaller values are finite and are checked here by explicit bounded
case analysis and `norm_num`, so the resulting theorem is checked by Lean's
kernel without native code evaluation.  Combining the two gives the reduced
first-difference inequality for every Fibonacci index.
-/

namespace QFibonomial4

/-- Exact kernel-checked verification of the eight cases below the threshold. -/
theorem fibonacci_delta_nonnegative_small
    (m k : ℕ) (hm : m < 8)
    (hk : 2 * k + 7 ≤
      3 * Nat.fib (m + 1) + 4 * Nat.fib (m + 2)) :
    0 ≤ delta (Nat.fib (m + 1)) (Nat.fib (m + 2)) k := by
  have hk96 : k ≤ 96 := by
    interval_cases m <;> norm_num [Nat.fib] at hk ⊢ <;> omega
  interval_cases m
  all_goals interval_cases k
  all_goals norm_num [Nat.fib] at hk
  all_goals norm_num [Nat.fib, delta, shiftedG, g, quad]

/--
For every Fibonacci index, all reduced first differences through the center
are nonnegative.
-/
theorem fibonacci_delta_nonnegative
    (m k : ℕ)
    (hk : 2 * k + 7 ≤
      3 * Nat.fib (m + 1) + 4 * Nat.fib (m + 2)) :
    0 ≤ delta (Nat.fib (m + 1)) (Nat.fib (m + 2)) k := by
  by_cases hm : 8 ≤ m
  · exact fibonacci_delta_nonnegative_large m k hm hk
  · exact fibonacci_delta_nonnegative_small m k (by omega) hk

#print axioms fibonacci_delta_nonnegative_small
#print axioms fibonacci_delta_nonnegative

end QFibonomial4
