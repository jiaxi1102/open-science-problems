import Mathlib

open Polynomial
open scoped BigOperators

namespace QRiousCounterexample

noncomputable section

/-- The q-integer `[n]_q = 1 + q + ... + q^(n-1)`. -/
def qNat (n : ℕ) : Polynomial ℤ :=
  (Finset.range n).sum fun i => X ^ i

/-- The q-factorial `[n]_q!`. -/
def qFactorial : ℕ → Polynomial ℤ
  | 0 => 1
  | n + 1 => qFactorial n * qNat (n + 1)

/--
The exact polynomial quotient for

  [12]![5]![3]![2]! / ([9]![6]![4]![1]!^3).
-/
def candidateD : Polynomial ℤ :=
  1 +
    2 * X ^ 1 +
    2 * X ^ 2 +
    2 * X ^ 3 +
    3 * X ^ 4 +
    4 * X ^ 5 +
    5 * X ^ 6 +
    6 * X ^ 7 +
    7 * X ^ 8 +
    8 * X ^ 9 +
    8 * X ^ 10 +
    7 * X ^ 11 +
    7 * X ^ 12 +
    8 * X ^ 13 +
    8 * X ^ 14 +
    7 * X ^ 15 +
    6 * X ^ 16 +
    5 * X ^ 17 +
    4 * X ^ 18 +
    3 * X ^ 19 +
    2 * X ^ 20 +
    2 * X ^ 21 +
    2 * X ^ 22 +
    X ^ 23

/-- The proposed conjecture concerns this polynomial. -/
def candidateQ : Polynomial ℤ := (1 + X) * candidateD

/-- A global weak-unimodality definition for polynomial coefficients. -/
def CoeffUnimodal (p : Polynomial ℤ) : Prop :=
  ∃ m : ℕ,
    (∀ i j : ℕ, i ≤ j → j ≤ m → p.coeff i ≤ p.coeff j) ∧
    (∀ i j : ℕ, m ≤ i → i ≤ j → p.coeff j ≤ p.coeff i)

/-- Exact quotient certificate, avoiding polynomial division inside the theorem statement. -/
theorem qFactorial_quotient_certificate :
    qFactorial 9 * qFactorial 6 * qFactorial 4 * (qFactorial 1) ^ 3 * candidateD =
      qFactorial 12 * qFactorial 5 * qFactorial 3 * qFactorial 2 := by
  norm_num [qFactorial, qNat, candidateD, Finset.sum_range_succ]
  ring

/-- Multiplication by `1+q` adds two adjacent coefficients. -/
lemma candidateQ_coeff_succ (n : ℕ) :
    candidateQ.coeff (n + 1) = candidateD.coeff (n + 1) + candidateD.coeff n := by
  simp [candidateQ, add_mul]

/-- The three coefficients witnessing the central valley. -/
theorem central_coefficients :
    candidateQ.coeff 10 = 16 ∧
    candidateQ.coeff 12 = 14 ∧
    candidateQ.coeff 14 = 16 := by
  constructor
  · have h := candidateQ_coeff_succ 9
    norm_num [candidateD] at h ⊢
    exact h
  · constructor
    · have h := candidateQ_coeff_succ 11
      norm_num [candidateD] at h ⊢
      exact h
    · have h := candidateQ_coeff_succ 13
      norm_num [candidateD] at h ⊢
      exact h

/-- The polynomial `(1+q)D(q)` is not unimodal. -/
theorem candidateQ_not_unimodal : ¬ CoeffUnimodal candidateQ := by
  rintro ⟨m, hinc, hdec⟩
  obtain ⟨h10, h12, h14⟩ := central_coefficients
  by_cases hm : m ≤ 12
  · have h := hdec 12 14 hm (by omega)
    rw [h12, h14] at h
    omega
  · have hm' : 12 ≤ m := by omega
    have h := hinc 10 12 (by omega) hm'
    rw [h10, h12] at h
    omega

/-- The Landau floor-step function for the candidate pair. -/
def landauStep (x : ℝ) : ℤ :=
  ⌊12 * x⌋ + ⌊5 * x⌋ + ⌊3 * x⌋ + ⌊2 * x⌋ -
    ⌊9 * x⌋ - ⌊6 * x⌋ - ⌊4 * x⌋ - 3 * ⌊x⌋

/-- The same step function after replacing all floors by divisions of `⌊180x⌋`. -/
def reducedLandau (k : ℤ) : ℤ :=
  k / 15 + k / 36 + k / 60 + k / 90 -
    k / 20 - k / 30 - k / 45 - 3 * (k / 180)

lemma floor_mul_twelve (x : ℝ) : ⌊12 * x⌋ = ⌊180 * x⌋ / 15 := by
  calc
    ⌊12 * x⌋ = ⌊(180 * x) / 15⌋ := by congr 1 <;> ring
    _ = ⌊180 * x⌋ / 15 := by simpa using (Int.floor_div_natCast (180 * x) 15)

lemma floor_mul_five (x : ℝ) : ⌊5 * x⌋ = ⌊180 * x⌋ / 36 := by
  calc
    ⌊5 * x⌋ = ⌊(180 * x) / 36⌋ := by congr 1 <;> ring
    _ = ⌊180 * x⌋ / 36 := by simpa using (Int.floor_div_natCast (180 * x) 36)

lemma floor_mul_three (x : ℝ) : ⌊3 * x⌋ = ⌊180 * x⌋ / 60 := by
  calc
    ⌊3 * x⌋ = ⌊(180 * x) / 60⌋ := by congr 1 <;> ring
    _ = ⌊180 * x⌋ / 60 := by simpa using (Int.floor_div_natCast (180 * x) 60)

lemma floor_mul_two (x : ℝ) : ⌊2 * x⌋ = ⌊180 * x⌋ / 90 := by
  calc
    ⌊2 * x⌋ = ⌊(180 * x) / 90⌋ := by congr 1 <;> ring
    _ = ⌊180 * x⌋ / 90 := by simpa using (Int.floor_div_natCast (180 * x) 90)

lemma floor_mul_nine (x : ℝ) : ⌊9 * x⌋ = ⌊180 * x⌋ / 20 := by
  calc
    ⌊9 * x⌋ = ⌊(180 * x) / 20⌋ := by congr 1 <;> ring
    _ = ⌊180 * x⌋ / 20 := by simpa using (Int.floor_div_natCast (180 * x) 20)

lemma floor_mul_six (x : ℝ) : ⌊6 * x⌋ = ⌊180 * x⌋ / 30 := by
  calc
    ⌊6 * x⌋ = ⌊(180 * x) / 30⌋ := by congr 1 <;> ring
    _ = ⌊180 * x⌋ / 30 := by simpa using (Int.floor_div_natCast (180 * x) 30)

lemma floor_mul_four (x : ℝ) : ⌊4 * x⌋ = ⌊180 * x⌋ / 45 := by
  calc
    ⌊4 * x⌋ = ⌊(180 * x) / 45⌋ := by congr 1 <;> ring
    _ = ⌊180 * x⌋ / 45 := by simpa using (Int.floor_div_natCast (180 * x) 45)

lemma floor_mul_one (x : ℝ) : ⌊x⌋ = ⌊180 * x⌋ / 180 := by
  calc
    ⌊x⌋ = ⌊(180 * x) / 180⌋ := by congr 1 <;> ring
    _ = ⌊180 * x⌋ / 180 := by simpa using (Int.floor_div_natCast (180 * x) 180)

lemma landauStep_eq_reduced (x : ℝ) : landauStep x = reducedLandau ⌊180 * x⌋ := by
  unfold landauStep reducedLandau
  rw [floor_mul_twelve x, floor_mul_five x, floor_mul_three x, floor_mul_two x,
    floor_mul_nine x, floor_mul_six x, floor_mul_four x, floor_mul_one x]

lemma reducedLandau_periodic (k : ℤ) :
    reducedLandau k = reducedLandau (k % 180) := by
  unfold reducedLandau
  omega

lemma reducedLandau_on_residues :
    ∀ r : Fin 180, 0 ≤ reducedLandau (r : ℕ) := by
  set_option maxRecDepth 100000 in
    decide

/-- The candidate satisfies Landau's criterion for every real input. -/
theorem landauCriterion : ∀ x : ℝ, 0 ≤ landauStep x := by
  intro x
  rw [landauStep_eq_reduced, reducedLandau_periodic]
  have hr0 : 0 ≤ ⌊180 * x⌋ % 180 := Int.emod_nonneg _ (by norm_num)
  have hrlt : ⌊180 * x⌋ % 180 < 180 := Int.emod_lt_of_pos _ (by norm_num)
  let r : Fin 180 := ⟨(⌊180 * x⌋ % 180).toNat, by omega⟩
  have h := reducedLandau_on_residues r
  have hcast : ((r : ℕ) : ℤ) = ⌊180 * x⌋ % 180 := by
    simp [r, Int.toNat_of_nonneg hr0]
  rw [← hcast]
  exact h

/-- The exact counterexample package: valid Landau pair, exact quotient, non-unimodality. -/
theorem q_rious_unimodality_counterexample :
    (∀ x : ℝ, 0 ≤ landauStep x) ∧
    (qFactorial 9 * qFactorial 6 * qFactorial 4 * (qFactorial 1) ^ 3 * candidateD =
      qFactorial 12 * qFactorial 5 * qFactorial 3 * qFactorial 2) ∧
    ¬ CoeffUnimodal ((1 + X) * candidateD) := by
  exact ⟨landauCriterion, qFactorial_quotient_certificate, candidateQ_not_unimodal⟩

#print axioms q_rious_unimodality_counterexample

end

end QRiousCounterexample
