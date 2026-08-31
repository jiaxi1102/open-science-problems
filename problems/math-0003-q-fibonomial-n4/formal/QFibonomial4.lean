import Mathlib

/-!
# The first-difference core for the n = 4 q-Fibonomial case

Let

  G(q) = 1 / ((1-q)(1-q^2)(1-q^3)) = sum g(n) q^n.

Then `g(n) = floor((n^2 + 6n + 12)/12)`.  For consecutive Fibonacci
lengths `x,y,x+y,x+2y`, the first-half coefficient differences of the
q-Fibonomial quotient reduce to

  g(k) - g(k-x) - g(k-y) + g(k-(2x+y)),

with terms of negative index interpreted as zero.  This file proves that
quantity is nonnegative in the full first-half range once `x >= 34` and
`3*x <= 2*y`.  The finitely many smaller Fibonacci cases are checked in a
separate theorem below.
-/

namespace QFibonomial4

/-- Quadratic numerator in the closed formula for partitions into parts 1,2,3. -/
def quad (n : ℕ) : ℕ := n * n + 6 * n + 12

/-- Number of partitions of `n` into parts of size at most three. -/
def g (n : ℕ) : ℕ := quad n / 12

/-- Integer version of the same quadratic, convenient for nonlinear arithmetic. -/
def zquad (z : ℤ) : ℤ := z * z + 6 * z + 12

/-- A shifted coefficient, with negative subscripts interpreted as zero. -/
def shiftedG (k s : ℕ) : ℤ :=
  if s ≤ k then (g (k - s) : ℤ) else 0

/-- The reduced first-difference expression. -/
def delta (x y k : ℕ) : ℤ :=
  shiftedG k 0 - shiftedG k x - shiftedG k y + shiftedG k (2 * x + y)

lemma g_division_bounds_nat (n : ℕ) :
    quad n ≤ 12 * g n + 11 ∧ 12 * g n ≤ quad n := by
  unfold g
  have hmod : quad n % 12 < 12 := Nat.mod_lt _ (by norm_num)
  have hdecomp : quad n % 12 + 12 * (quad n / 12) = quad n :=
    Nat.mod_add_div _ _
  omega

lemma g_lower_bound (n : ℕ) :
    zquad (n : ℤ) - 11 ≤ 12 * (g n : ℤ) := by
  have hNat := (g_division_bounds_nat n).1
  have hInt : (quad n : ℤ) ≤ 12 * (g n : ℤ) + 11 := by
    exact_mod_cast hNat
  simp only [quad, zquad, Nat.cast_add, Nat.cast_mul, Nat.cast_ofNat] at hInt ⊢
  omega

lemma g_upper_bound (n : ℕ) :
    12 * (g n : ℤ) ≤ zquad (n : ℤ) := by
  have hNat := (g_division_bounds_nat n).2
  have hInt : 12 * (g n : ℤ) ≤ (quad n : ℤ) := by
    exact_mod_cast hNat
  simpa only [quad, zquad, Nat.cast_add, Nat.cast_mul, Nat.cast_ofNat] using hInt

/--
The central arithmetic lemma.  The half-degree condition is written without
natural-number subtraction as `2*k + 7 <= 3*x + 4*y`.
-/
theorem delta_nonnegative_large
    (x y k : ℕ)
    (hx : 34 ≤ x)
    (hxy : 3 * x ≤ 2 * y)
    (hk : 2 * k + 7 ≤ 3 * x + 4 * y) :
    0 ≤ delta x y k := by
  have hxy' : x ≤ y := by omega
  by_cases hkx : k < x
  · have hky : k < y := lt_of_lt_of_le hkx hxy'
    have hklast : k < 2 * x + y := by omega
    simp [delta, shiftedG, Nat.not_le.mpr hkx, Nat.not_le.mpr hky,
      Nat.not_le.mpr hklast]
  · have hxk : x ≤ k := by omega
    by_cases hky : k < y
    · have hklast : k < 2 * x + y := by omega
      have hlo := g_lower_bound k
      have hhi := g_upper_bound (k - x)
      have hxZ : (34 : ℤ) ≤ (x : ℤ) := by exact_mod_cast hx
      have hxkZ : (x : ℤ) ≤ (k : ℤ) := by exact_mod_cast hxk
      rw [Nat.cast_sub hxk] at hhi
      have hprod : 0 ≤ (x : ℤ) * ((k : ℤ) - (x : ℤ)) :=
        mul_nonneg (by omega) (by omega)
      simp [delta, shiftedG, hxk, Nat.not_le.mpr hky,
        Nat.not_le.mpr hklast]
      unfold zquad at hlo hhi
      nlinarith
    · have hyk : y ≤ k := by omega
      by_cases hklast : k < 2 * x + y
      · have hlo := g_lower_bound k
        have hhix := g_upper_bound (k - x)
        have hhiy := g_upper_bound (k - y)
        have hxZ : (34 : ℤ) ≤ (x : ℤ) := by exact_mod_cast hx
        have hxyZ : 3 * (x : ℤ) ≤ 2 * (y : ℤ) := by exact_mod_cast hxy
        have hykZ : (y : ℤ) ≤ (k : ℤ) := by exact_mod_cast hyk
        have htopZ : (k : ℤ) ≤ 2 * (x : ℤ) + (y : ℤ) := by omega
        rw [Nat.cast_sub hxk] at hhix
        rw [Nat.cast_sub hyk] at hhiy
        have hprod :
            0 ≤ (2 * (x : ℤ) + (y : ℤ) - (k : ℤ)) *
              ((k : ℤ) - (y : ℤ) + 6) :=
          mul_nonneg (by omega) (by omega)
        simp [delta, shiftedG, hxk, hyk, Nat.not_le.mpr hklast]
        unfold zquad at hlo hhix hhiy
        nlinarith
      · have hlast : 2 * x + y ≤ k := by omega
        have hlo := g_lower_bound k
        have hhix := g_upper_bound (k - x)
        have hhiy := g_upper_bound (k - y)
        have hlolast := g_lower_bound (k - (2 * x + y))
        have hxZ : (34 : ℤ) ≤ (x : ℤ) := by exact_mod_cast hx
        have hkZ : 2 * (k : ℤ) + 7 ≤ 3 * (x : ℤ) + 4 * (y : ℤ) := by
          exact_mod_cast hk
        rw [Nat.cast_sub hxk] at hhix
        rw [Nat.cast_sub hyk] at hhiy
        rw [Nat.cast_sub hlast] at hlolast
        have hlastCast :
            ((2 * x + y : ℕ) : ℤ) = 2 * (x : ℤ) + (y : ℤ) := by
          norm_num
        rw [hlastCast] at hlolast
        have hbracket :
            1 ≤ 3 * (x : ℤ) + 4 * (y : ℤ) - 2 * (k : ℤ) - 6 := by
          omega
        have hprod :
            (x : ℤ) ≤ (x : ℤ) *
              (3 * (x : ℤ) + 4 * (y : ℤ) - 2 * (k : ℤ) - 6) := by
          have hnonneg :
              0 ≤ (x : ℤ) *
                ((3 * (x : ℤ) + 4 * (y : ℤ) - 2 * (k : ℤ) - 6) - 1) :=
            mul_nonneg (by omega) (by omega)
          nlinarith
        have hidentity :
            zquad (k : ℤ) - zquad ((k : ℤ) - (x : ℤ)) -
                zquad ((k : ℤ) - (y : ℤ)) +
                zquad ((k : ℤ) - (2 * (x : ℤ) + (y : ℤ))) =
              (x : ℤ) *
                (3 * (x : ℤ) + 4 * (y : ℤ) - 2 * (k : ℤ) - 6) := by
          unfold zquad
          ring
        have hscaled :
            0 ≤ 12 * (g k : ℤ) - 12 * (g (k - x) : ℤ) -
                12 * (g (k - y) : ℤ) +
                12 * (g (k - (2 * x + y)) : ℤ) := by
          linarith [hlo, hhix, hhiy, hlolast, hidentity, hprod, hxZ]
        simp [delta, shiftedG, hxk, hyk, hlast]
        linarith

/-- The Fibonacci specialization of the large-case hypotheses. -/
lemma fibonacci_large_hypotheses (m : ℕ) (hm : 8 ≤ m) :
    34 ≤ Nat.fib (m + 1) ∧
      3 * Nat.fib (m + 1) ≤ 2 * Nat.fib (m + 2) := by
  have hindex : 9 ≤ m + 1 := by omega
  have hx : Nat.fib 9 ≤ Nat.fib (m + 1) := Nat.fib_mono hindex
  have hx34 : 34 ≤ Nat.fib (m + 1) := by norm_num at hx ⊢; exact hx
  have hm0 : m ≠ 0 := by omega
  have hprev : Nat.fib (m - 1) ≤ Nat.fib m := Nat.fib_mono (Nat.sub_le m 1)
  have hxrec : Nat.fib (m + 1) = Nat.fib (m - 1) + Nat.fib m :=
    Nat.fib_add_one hm0
  have hyrec : Nat.fib (m + 2) = Nat.fib m + Nat.fib (m + 1) :=
    Nat.fib_add_two
  constructor
  · exact hx34
  · omega

/--
For every `m >= 8`, the reduced first differences in the first half of the
`n=4` q-Fibonomial polynomial are nonnegative.
-/
theorem fibonacci_delta_nonnegative_large
    (m k : ℕ)
    (hm : 8 ≤ m)
    (hk : 2 * k + 7 ≤
      3 * Nat.fib (m + 1) + 4 * Nat.fib (m + 2)) :
    0 ≤ delta (Nat.fib (m + 1)) (Nat.fib (m + 2)) k := by
  obtain ⟨hx, hxy⟩ := fibonacci_large_hypotheses m hm
  exact delta_nonnegative_large _ _ _ hx hxy hk

#print axioms fibonacci_delta_nonnegative_large

end QFibonomial4
