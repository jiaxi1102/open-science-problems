import Mathlib.Tactic

namespace HypercubeIsolation.QuantitativeGap

/-!
Kernel-checked arithmetic for the quantitative Hamming-family gap.

The combinatorial proof produces two inequalities.  If `e` is the number of
row pairs at full distance at most four, `K` is the perfect-code size, and
`s = M-K` is the excess number of rows, they can be written as

  K*m*(m-3) ≤ 16*(m+1)*e
  12*e ≤ (m+2)*(m+1)^3*s.

The first comes from sphere packing plus the Caro--Wei inequality; the second
comes from summing projected covering excess over all two-coordinate deletions.
The theorem below checks that these imply the advertised quantitative bound.
-/

/-- Algebraic combination of the lower and upper pair-count estimates. -/
theorem quantitative_gap_from_pair_counts
    (K m s e : ℚ)
    (hm : 0 ≤ m + 1)
    (hlower : K * m * (m - 3) ≤ 16 * (m + 1) * e)
    (hupper : 12 * e ≤ (m + 2) * (m + 1) ^ 3 * s) :
    3 * K * m * (m - 3) ≤ 4 * (m + 2) * (m + 1) ^ 4 * s := by
  calc
    3 * K * m * (m - 3) = 3 * (K * m * (m - 3)) := by ring
    _ ≤ 3 * (16 * (m + 1) * e) :=
      mul_le_mul_of_nonneg_left hlower (by norm_num)
    _ = (4 * (m + 1)) * (12 * e) := by ring
    _ ≤ (4 * (m + 1)) * ((m + 2) * (m + 1) ^ 3 * s) :=
      mul_le_mul_of_nonneg_left hupper (mul_nonneg (by norm_num) hm)
    _ = 4 * (m + 2) * (m + 1) ^ 4 * s := by ring

/-- Exact coefficient in the first Hamming case `m=7`. -/
theorem hamming7_gap_coefficient :
    (3 * (16 : ℚ) * 7 * (7 - 3)) /
        (4 * (7 + 2) * (7 + 1) ^ 4) = 7 / 768 := by
  norm_num

/-- Exact coefficient at Hamming length `m=15`. -/
theorem hamming15_gap_coefficient :
    (3 * (2048 : ℚ) * 15 * (15 - 3)) /
        (4 * (15 + 2) * (15 + 1) ^ 4) = 135 / 544 := by
  norm_num

/-- At Hamming length `m=31`, the excess lower bound lies strictly between 1262 and 1263. -/
theorem hamming31_gap_coefficient :
    (3 * (67108864 : ℚ) * 31 * (31 - 3)) /
        (4 * (31 + 2) * (31 + 1) ^ 4) = 13888 / 11 ∧
      (1262 : ℚ) < 13888 / 11 ∧ 13888 / 11 < 1263 := by
  norm_num

/-- At Hamming length `m=63`, the integer excess is at least 374,653,301,052. -/
theorem hamming63_gap_coefficient :
    (3 * (144115188075855872 : ℚ) * 63 * (63 - 3)) /
        (4 * (63 + 2) * (63 + 1) ^ 4) = 4870492913664 / 13 ∧
      (374653301051 : ℚ) < 4870492913664 / 13 ∧
      4870492913664 / 13 < 374653301052 := by
  norm_num

#print axioms quantitative_gap_from_pair_counts
#print axioms hamming31_gap_coefficient
#print axioms hamming63_gap_coefficient

end HypercubeIsolation.QuantitativeGap
