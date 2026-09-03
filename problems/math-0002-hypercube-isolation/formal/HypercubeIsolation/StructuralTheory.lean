import Mathlib.InformationTheory.Hamming
import Mathlib.Tactic

namespace HypercubeIsolation.StructuralTheory

/-!
This file formalizes the structural bridge behind the hypercube-isolation result.

A binary word is a vertex of a hypercube.  A codimension-`m` coordinate face is
specified by a set `S` of `m` fixed coordinates and a target word `a`; only the
coordinates of `a` in `S` matter.  The distance from `x` to that face is exactly
the number of disagreements between `x` and `a` on `S`.  Consequently, a set
hits the radius-`r` neighborhood of every such face exactly when its rows form
a binary radius-covering array.

This module also verifies the polynomial identity and positivity inequality
used by the two-extra-column Hamming-family obstruction.  The general theorem
that turns perfect projected codes into a packing contradiction is currently
proved in the accompanying human proof and is not claimed as formalized here.
-/

/-- Vertices of the binary `n`-cube. -/
abbrev BitWord (n : ℕ) := Fin n → Bool

/-- Hamming distance on binary words. -/
def dist {n : ℕ} (x y : BitWord n) : ℕ := hammingDist x y

/-- Hamming distance restricted to a chosen coordinate set. -/
def restrictedDist {n : ℕ} (S : Finset (Fin n)) (x a : BitWord n) : ℕ :=
  (S.filter fun i => x i ≠ a i).card

/-- The coordinate face whose coordinates in `S` agree with `a`. -/
def InFace {n : ℕ} (S : Finset (Fin n)) (a y : BitWord n) : Prop :=
  ∀ i ∈ S, y i = a i

/-- The closest point of the face `(S,a)` obtained by changing only fixed coordinates. -/
def faceCompletion {n : ℕ} (S : Finset (Fin n)) (a x : BitWord n) : BitWord n :=
  fun i => if i ∈ S then a i else x i

/-- The canonical completion belongs to the required face. -/
theorem faceCompletion_mem {n : ℕ} (S : Finset (Fin n)) (a x : BitWord n) :
    InFace S a (faceCompletion S a x) := by
  intro i hi
  simp [faceCompletion, hi]

/-- Completing `x` into a face changes exactly the disagreeing fixed coordinates. -/
theorem dist_faceCompletion {n : ℕ} (S : Finset (Fin n)) (a x : BitWord n) :
    dist x (faceCompletion S a x) = restrictedDist S x a := by
  classical
  unfold dist hammingDist restrictedDist
  congr 1
  ext i
  by_cases hi : i ∈ S <;> simp [faceCompletion, hi]

/-- Every point in the face is at least the restricted distance away. -/
theorem restrictedDist_le_dist_of_mem {n : ℕ} {S : Finset (Fin n)}
    {a x y : BitWord n} (hy : InFace S a y) :
    restrictedDist S x a ≤ dist x y := by
  classical
  unfold restrictedDist dist hammingDist
  apply Finset.card_le_card
  intro i hi
  have hiS : i ∈ S := (Finset.mem_filter.mp hi).1
  have hxa : x i ≠ a i := (Finset.mem_filter.mp hi).2
  simp only [Finset.mem_filter, Finset.mem_univ, true_and]
  intro hxy
  apply hxa
  calc
    x i = y i := hxy
    _ = a i := hy i hiS

/-- Exact distance-to-face formula, expressed without taking a minimum. -/
theorem exists_near_face_iff {n r : ℕ} (S : Finset (Fin n)) (a x : BitWord n) :
    (∃ y : BitWord n, InFace S a y ∧ dist x y ≤ r) ↔
      restrictedDist S x a ≤ r := by
  constructor
  · rintro ⟨y, hy, hxy⟩
    exact (restrictedDist_le_dist_of_mem hy).trans hxy
  · intro h
    refine ⟨faceCompletion S a x, faceCompletion_mem S a x, ?_⟩
    rw [dist_faceCompletion]
    exact h

/-- A row set whose radius-`r` neighborhood meets every codimension-`m` face. -/
def HitsAllCodimFaces {n : ℕ} (D : Finset (BitWord n)) (m r : ℕ) : Prop :=
  ∀ S : Finset (Fin n), S.card = m → ∀ a : BitWord n,
    ∃ d ∈ D, ∃ y : BitWord n, InFace S a y ∧ dist d y ≤ r

/-- Binary radius-covering-array property, encoded on ambient target words. -/
def IsRadiusCoveringArray {n : ℕ} (D : Finset (BitWord n)) (m r : ℕ) : Prop :=
  ∀ S : Finset (Fin n), S.card = m → ∀ a : BitWord n,
    ∃ d ∈ D, restrictedDist S d a ≤ r

/--
The exact graph-to-coding dictionary for coordinate subcubes: radius-`r`
subcube isolation is precisely the binary radius-covering-array property.
-/
theorem hitsAllCodimFaces_iff_radiusCoveringArray {n m r : ℕ}
    (D : Finset (BitWord n)) :
    HitsAllCodimFaces D m r ↔ IsRadiusCoveringArray D m r := by
  constructor
  · intro h S hS a
    obtain ⟨d, hd, y, hy, hdy⟩ := h S hS a
    exact ⟨d, hd, (exists_near_face_iff S a d).mp ⟨y, hy, hdy⟩⟩
  · intro h S hS a
    obtain ⟨d, hd, hda⟩ := h S hS a
    obtain ⟨y, hy, hdy⟩ := (exists_near_face_iff S a d).mpr hda
    exact ⟨d, hd, y, hy, hdy⟩

/--
After clearing the factor `1/2`, the two-extra-column Hamming volume gap is
exactly `m(m-3)`.  This is the arithmetic heart of the infinite binary
Hamming-family obstruction.
-/
theorem binary_two_column_volume_gap (m : ℤ) :
    (2 * (1 + (m + 2)) + (m + 2) * (m + 1)) - 8 * (m + 1) = m * (m - 3) := by
  ring

/-- The relevant volume inequality is strict for every Hamming length `m ≥ 4`. -/
theorem binary_two_column_volume_obstruction (m : ℤ) (hm : 4 ≤ m) :
    8 * (m + 1) < 2 * (1 + (m + 2)) + (m + 2) * (m + 1) := by
  rw [← sub_pos]
  rw [binary_two_column_volume_gap]
  nlinarith

/-- At the first binary Hamming length, sixteen radius-two balls already exceed `Q₉`. -/
theorem hamming7_first_obstruction : 512 < 16 * 46 := by
  norm_num

#print axioms hitsAllCodimFaces_iff_radiusCoveringArray
#print axioms binary_two_column_volume_obstruction

end HypercubeIsolation.StructuralTheory
