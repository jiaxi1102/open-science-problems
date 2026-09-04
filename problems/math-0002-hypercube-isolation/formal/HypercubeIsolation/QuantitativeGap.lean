import Mathlib.Tactic

namespace HypercubeIsolation.QuantitativeGap

/-!
Kernel-checked arithmetic for the quantitative Hamming-family gap.

The combinatorial proof produces two inequalities. If `e` is the number of
row pairs at full distance at most four, `K` is the perfect-code size, and
`s = M-K` is the excess number of rows, they can be written as

  K*m*(m-3) ≤ 16*(m+1)*e
  12*e ≤ (m+2)*(m+1)^3*s.

The first comes from sphere packing plus the Caro--Wei inequality; the second
comes from summing projected covering excess over all two-coordinate deletions.
The theorems below verify the pointwise overlap estimate, the deletion-count
rescaling, the packing rearrangement, the required quadratic monotonicity, and
the final advertised bound.
-/

/--
If a covered target has multiplicity `c`, with
`1 ≤ c ≤ 4(m+1)`, then its contribution to the unordered overlap count is at
most `2(m+1)` times its covering excess.
-/
theorem multiplicity_pair_bound
    (m c : ℚ)
    (hc1 : 1 ≤ c)
    (hcmax : c ≤ 4 * (m + 1)) :
    c * (c - 1) / 2 ≤ 2 * (m + 1) * (c - 1) := by
  have hnonneg : 0 ≤ c - 1 := sub_nonneg.mpr hc1
  have hhalf : c / 2 ≤ 2 * (m + 1) := by linarith
  calc
    c * (c - 1) / 2 = (c / 2) * (c - 1) := by ring
    _ ≤ (2 * (m + 1)) * (c - 1) :=
      mul_le_mul_of_nonneg_right hhalf hnonneg

/--
Rescale the natural two-deletion incidence inequality to the polynomial form
used by the final theorem.
-/
theorem deletion_pair_rescaling
    (m s e : ℚ)
    (h : 6 * e ≤ ((m + 2) * (m + 1) / 2) * (m + 1) ^ 2 * s) :
    12 * e ≤ (m + 2) * (m + 1) ^ 3 * s := by
  calc
    12 * e = 2 * (6 * e) := by ring
    _ ≤ 2 * (((m + 2) * (m + 1) / 2) * (m + 1) ^ 2 * s) :=
      mul_le_mul_of_nonneg_left h (by norm_num)
    _ = (m + 2) * (m + 1) ^ 3 * s := by ring

/--
Cross-multiplied rearrangement of the Caro--Wei lower bound combined with an
upper bound on the independence number.
-/
theorem close_pairs_from_independence_bounds
    (M V Q e : ℚ)
    (h : M ^ 2 * V ≤ Q * (M + 2 * e)) :
    M * (M * V - Q) ≤ 2 * Q * e := by
  nlinarith [h]

/--
The quadratic lower-bound expression is monotone once the perfect-code point
`K` lies beyond its nonnegative root.
-/
theorem quadratic_pair_expression_monotone
    (M K V Q : ℚ)
    (hK : 0 ≤ K)
    (hMK : K ≤ M)
    (hV : 0 ≤ V)
    (hroot : Q ≤ K * V) :
    K * (K * V - Q) ≤ M * (M * V - Q) := by
  have hM : 0 ≤ M := hK.trans hMK
  have hVM : 0 ≤ V * M := mul_nonneg hV hM
  have hsum : Q ≤ V * (M + K) := by
    nlinarith [hroot]
  have hprod : 0 ≤ (M - K) * (V * (M + K) - Q) :=
    mul_nonneg (sub_nonneg.mpr hMK) (sub_nonneg.mpr hsum)
  nlinarith [hprod]

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

/-- The rational `m=31` lower bound forces at least 1263 excess rows. -/
theorem hamming31_integral_gap {s : ℕ}
    (hs : (13888 : ℚ) / 11 ≤ (s : ℚ)) : 1263 ≤ s := by
  by_contra h
  have hs_le : s ≤ 1262 := by omega
  have hs_cast : (s : ℚ) ≤ 1262 := by exact_mod_cast hs_le
  have hstrict : (1262 : ℚ) < 13888 / 11 := by norm_num
  linarith

/-- At Hamming length `m=63`, the integer excess is at least 374,653,301,052. -/
theorem hamming63_gap_coefficient :
    (3 * (144115188075855872 : ℚ) * 63 * (63 - 3)) /
        (4 * (63 + 2) * (63 + 1) ^ 4) = 4870492913664 / 13 ∧
      (374653301051 : ℚ) < 4870492913664 / 13 ∧
      4870492913664 / 13 < 374653301052 := by
  norm_num

/-- The rational `m=63` lower bound forces the displayed integral excess. -/
theorem hamming63_integral_gap {s : ℕ}
    (hs : (4870492913664 : ℚ) / 13 ≤ (s : ℚ)) :
    374653301052 ≤ s := by
  by_contra h
  have hs_le : s ≤ 374653301051 := by omega
  have hs_cast : (s : ℚ) ≤ 374653301051 := by exact_mod_cast hs_le
  have hstrict : (374653301051 : ℚ) < 4870492913664 / 13 := by
    norm_num
  linarith

#print axioms multiplicity_pair_bound
#print axioms close_pairs_from_independence_bounds
#print axioms quadratic_pair_expression_monotone
#print axioms quantitative_gap_from_pair_counts
#print axioms hamming31_integral_gap
#print axioms hamming63_integral_gap

end HypercubeIsolation.QuantitativeGap
