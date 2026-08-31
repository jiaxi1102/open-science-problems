import QFibonomial4Series

/-!
# Formal power-series bridge

This file proves that the closed formula `g n` is exactly the coefficient
sequence of

  1 / ((1-X)(1-X^2)(1-X^3)).

It therefore removes the generating-function identification as an informal
step in the q-Fibonomial argument.
-/

namespace QFibonomial4

open PowerSeries

/-- The partition generating series with coefficients `g n`. -/
noncomputable def partitionSeries : PowerSeries ℤ :=
  PowerSeries.mk fun n => (g n : ℤ)

@[simp]
theorem coeff_partitionSeries (n : ℕ) :
    PowerSeries.coeff n partitionSeries = (g n : ℤ) := by
  simp [partitionSeries]

/-- The denominator `(1-X)(1-X^2)(1-X^3)`. -/
noncomputable def partitionDenominator : PowerSeries ℤ :=
  (1 - X) * (1 - X ^ 2) * (1 - X ^ 3)

lemma partitionDenominator_expansion :
    partitionDenominator =
      1 - X ^ 1 - X ^ 2 + X ^ 4 + X ^ 5 - X ^ 6 := by
  unfold partitionDenominator
  ring

lemma coeff_partitionSeries_mul_X_pow (n s : ℕ) :
    PowerSeries.coeff n (partitionSeries * X ^ s) = shiftedG n s := by
  rw [PowerSeries.coeff_mul_X_pow']
  simp [partitionSeries, shiftedG]

lemma partition_product_expansion :
    partitionSeries * partitionDenominator =
      partitionSeries - partitionSeries * X ^ 1 - partitionSeries * X ^ 2 +
        partitionSeries * X ^ 4 + partitionSeries * X ^ 5 -
          partitionSeries * X ^ 6 := by
  rw [partitionDenominator_expansion]
  ring

/-- The closed formula is the inverse of the partition denominator. -/
theorem partitionSeries_mul_denominator :
    partitionSeries * partitionDenominator = 1 := by
  rw [partition_product_expansion]
  ext n
  by_cases hn : n = 0
  · subst n
    norm_num [partitionSeries, shiftedG, g, quad,
      PowerSeries.coeff_mul_X_pow']
  · have hr := g_denominator_recurrence n (Nat.one_le_iff_ne_zero.mpr hn)
    simp only [map_sub, map_add, coeff_partitionSeries,
      coeff_partitionSeries_mul_X_pow, coeff_one]
    simp [hn]
    omega

#print axioms partitionSeries_mul_denominator

end QFibonomial4
