import QFibonomial4PowerSeries
import QFibonomial4Unimodal

/-!
# The n = 4 q-Fibonomial rational series

For `x = F_(m+1)` and `y = F_(m+2)`, the four numerator lengths are
`x`, `y`, `x+y`, and `x+2y`.  This file expands that numerator, identifies
all coefficients of `(1-X)Q`, and combines the result with the verified
first-half inequality.
-/

namespace QFibonomial4

open PowerSeries

lemma X_linear_monomial (x y a b : ℕ) :
    ((X : PowerSeries ℤ) ^ x) ^ a * ((X : PowerSeries ℤ) ^ y) ^ b =
      X ^ (a * x + b * y) := by
  rw [← pow_mul, ← pow_mul, ← pow_add]
  congr 1
  omega

/-- Numerator of `(1-X)` times the `n=4` q-Fibonomial rational series. -/
def qFib4Numerator (x y : ℕ) : PowerSeries ℤ :=
  (1 - X ^ x) * (1 - X ^ y) *
    (1 - X ^ (x + y)) * (1 - X ^ (x + 2 * y))

lemma qFib4Numerator_expansion (x y : ℕ) :
    qFib4Numerator x y =
      1 - X ^ x - X ^ y + X ^ (2 * x + y) + X ^ (x + 3 * y) -
        X ^ (3 * x + 3 * y) - X ^ (2 * x + 4 * y) +
          X ^ (3 * x + 4 * y) := by
  let A : PowerSeries ℤ := X ^ x
  let B : PowerSeries ℤ := X ^ y
  have hxy : (X : PowerSeries ℤ) ^ (x + y) = A * B := by
    simp [A, B, pow_add]
  have hx2y : (X : PowerSeries ℤ) ^ (x + 2 * y) = A * B ^ 2 := by
    symm
    simpa [A, B] using X_linear_monomial x y 1 2
  have h21 : A ^ 2 * B = (X : PowerSeries ℤ) ^ (2 * x + y) := by
    simpa [A, B] using X_linear_monomial x y 2 1
  have h13 : A * B ^ 3 = (X : PowerSeries ℤ) ^ (x + 3 * y) := by
    simpa [A, B] using X_linear_monomial x y 1 3
  have h33 : A ^ 3 * B ^ 3 = (X : PowerSeries ℤ) ^ (3 * x + 3 * y) := by
    simpa [A, B] using X_linear_monomial x y 3 3
  have h24 : A ^ 2 * B ^ 4 = (X : PowerSeries ℤ) ^ (2 * x + 4 * y) := by
    simpa [A, B] using X_linear_monomial x y 2 4
  have h34 : A ^ 3 * B ^ 4 = (X : PowerSeries ℤ) ^ (3 * x + 4 * y) := by
    simpa [A, B] using X_linear_monomial x y 3 4
  calc
    qFib4Numerator x y =
        (1 - A) * (1 - B) * (1 - A * B) * (1 - A * B ^ 2) := by
          rw [qFib4Numerator, hxy, hx2y]
          rfl
    _ = 1 - A - B + A ^ 2 * B + A * B ^ 3 - A ^ 3 * B ^ 3 -
          A ^ 2 * B ^ 4 + A ^ 3 * B ^ 4 := by ring
    _ = 1 - X ^ x - X ^ y + X ^ (2 * x + y) + X ^ (x + 3 * y) -
          X ^ (3 * x + 3 * y) - X ^ (2 * x + 4 * y) +
            X ^ (3 * x + 4 * y) := by
          rw [h21, h13, h33, h24, h34]
          rfl

/-- Full coefficient formula for `(1-X)Q`. -/
def fullDelta (x y k : ℕ) : ℤ :=
  (g k : ℤ) - shiftedG k x - shiftedG k y + shiftedG k (2 * x + y) +
    shiftedG k (x + 3 * y) - shiftedG k (3 * x + 3 * y) -
      shiftedG k (2 * x + 4 * y) + shiftedG k (3 * x + 4 * y)

/-- The series `(1-X)Q`. -/
def qFib4DifferenceSeries (x y : ℕ) : PowerSeries ℤ :=
  partitionSeries * qFib4Numerator x y

lemma coeff_qFib4DifferenceSeries (x y k : ℕ) :
    PowerSeries.coeff k (qFib4DifferenceSeries x y) = fullDelta x y k := by
  unfold qFib4DifferenceSeries
  rw [qFib4Numerator_expansion]
  have hexpand :
      partitionSeries *
          (1 - X ^ x - X ^ y + X ^ (2 * x + y) + X ^ (x + 3 * y) -
            X ^ (3 * x + 3 * y) - X ^ (2 * x + 4 * y) +
              X ^ (3 * x + 4 * y)) =
        partitionSeries - partitionSeries * X ^ x - partitionSeries * X ^ y +
          partitionSeries * X ^ (2 * x + y) +
          partitionSeries * X ^ (x + 3 * y) -
          partitionSeries * X ^ (3 * x + 3 * y) -
          partitionSeries * X ^ (2 * x + 4 * y) +
          partitionSeries * X ^ (3 * x + 4 * y) := by ring
  rw [hexpand]
  simp only [map_add, map_sub, coeff_partitionSeries,
    coeff_partitionSeries_mul_X_pow]
  rfl

/-- Past the midpoint, the additional numerator shifts enter; before it they vanish. -/
theorem fullDelta_eq_delta_firstHalf
    (x y k : ℕ) (hxy : x ≤ y)
    (hk : 2 * k + 7 ≤ 3 * x + 4 * y) :
    fullDelta x y k = delta x y k := by
  have hk13 : k < x + 3 * y := by omega
  have hk33 : k < 3 * x + 3 * y := by omega
  have hk24 : k < 2 * x + 4 * y := by omega
  have hk34 : k < 3 * x + 4 * y := by omega
  simp [fullDelta, delta, shiftedG, Nat.not_le.mpr hk13,
    Nat.not_le.mpr hk33, Nat.not_le.mpr hk24, Nat.not_le.mpr hk34]

/-- Geometric series `1 + X + X^2 + ...`. -/
def geometricSeries : PowerSeries ℤ := PowerSeries.mk 1

/-- The formal series represented by the `n=4` q-Fibonomial rational function. -/
def qFib4Series (x y : ℕ) : PowerSeries ℤ :=
  geometricSeries * qFib4DifferenceSeries x y

lemma one_sub_X_mul_qFib4Series (x y : ℕ) :
    (1 - X) * qFib4Series x y = qFib4DifferenceSeries x y := by
  unfold qFib4Series geometricSeries
  have hgeom := PowerSeries.mk_one_mul_one_sub_eq_one (ℤ)
  calc
    (1 - X) * (PowerSeries.mk 1 * qFib4DifferenceSeries x y) =
        (PowerSeries.mk 1 * (1 - X)) * qFib4DifferenceSeries x y := by ring
    _ = qFib4DifferenceSeries x y := by rw [hgeom, one_mul]

/-- Full denominator in the rational form of the `n=4` q-Fibonomial. -/
def qFib4Denominator : PowerSeries ℤ :=
  (1 - X) * partitionDenominator

/-- Exact rational-function identity characterizing `qFib4Series`. -/
theorem qFib4Series_rational_identity (x y : ℕ) :
    qFib4Series x y * qFib4Denominator = qFib4Numerator x y := by
  unfold qFib4Series qFib4DifferenceSeries qFib4Denominator geometricSeries
  have hgeom := PowerSeries.mk_one_mul_one_sub_eq_one (ℤ)
  have hpart := partitionSeries_mul_denominator
  calc
    (PowerSeries.mk 1 * (partitionSeries * qFib4Numerator x y)) *
        ((1 - X) * partitionDenominator) =
      (PowerSeries.mk 1 * (1 - X)) *
        (partitionSeries * partitionDenominator) * qFib4Numerator x y := by ring
    _ = qFib4Numerator x y := by rw [hgeom, hpart]; ring

/-- Coefficients of the rational q-Fibonomial series. -/
def qFib4Coeff (x y k : ℕ) : ℤ :=
  PowerSeries.coeff k (qFib4Series x y)

/-- Exact first-difference formula, including every numerator shift. -/
theorem qFib4Coeff_difference_full (x y k : ℕ) (hk : 1 ≤ k) :
    qFib4Coeff x y k - qFib4Coeff x y (k - 1) = fullDelta x y k := by
  have h := congrArg (PowerSeries.coeff k) (one_sub_X_mul_qFib4Series x y)
  have hleft :
      (1 - X) * qFib4Series x y =
        qFib4Series x y - qFib4Series x y * X := by ring
  rw [hleft, map_sub, PowerSeries.coeff_mul_X_pow',
    coeff_qFib4DifferenceSeries] at h
  simpa [qFib4Coeff, hk] using h

/-- The four-term first-difference formula on the complete first-half range. -/
theorem qFib4Coeff_difference_firstHalf
    (x y k : ℕ) (hxy : x ≤ y) (hk1 : 1 ≤ k)
    (hk : 2 * k + 7 ≤ 3 * x + 4 * y) :
    qFib4Coeff x y k - qFib4Coeff x y (k - 1) = delta x y k := by
  rw [qFib4Coeff_difference_full x y k hk1,
    fullDelta_eq_delta_firstHalf x y k hxy hk]

/-- Fibonacci-specialized rational-series coefficients. -/
def fibQCoeff (m k : ℕ) : ℤ :=
  qFib4Coeff (Nat.fib (m + 1)) (Nat.fib (m + 2)) k

lemma fib_consecutive_mono (m : ℕ) :
    Nat.fib (m + 1) ≤ Nat.fib (m + 2) :=
  Nat.fib_mono (by omega)

/-- First-half difference law for the actual Fibonacci lengths. -/
theorem fibQCoeff_difference_firstHalf
    (m k : ℕ) (hk1 : 1 ≤ k) (hk : 2 * k ≤ qFib4Degree m) :
    fibQCoeff m k - fibQCoeff m (k - 1) =
      delta (Nat.fib (m + 1)) (Nat.fib (m + 2)) k := by
  have hk' :
      2 * k + 7 ≤ 3 * Nat.fib (m + 1) + 4 * Nat.fib (m + 2) := by
    unfold qFib4Degree at hk
    omega
  exact qFib4Coeff_difference_firstHalf _ _ _ (fib_consecutive_mono m) hk1 hk'

/--
Once the known symmetry of q-Fibonomials is supplied, the formally identified
`n=4` rational series is unimodal.
-/
theorem fibQCoeff_unimodal_of_symmetry
    (m : ℕ)
    (hsym : SymmetricAtDegree (fibQCoeff m) (qFib4Degree m)) :
    UnimodalAtDegree (fibQCoeff m) (qFib4Degree m) := by
  apply qFib4_unimodal_of_symmetry_and_difference m (fibQCoeff m) hsym
  intro k hk1 hk
  exact fibQCoeff_difference_firstHalf m k hk1 hk

#print axioms qFib4Series_rational_identity
#print axioms fibQCoeff_difference_firstHalf
#print axioms fibQCoeff_unimodal_of_symmetry

end QFibonomial4
