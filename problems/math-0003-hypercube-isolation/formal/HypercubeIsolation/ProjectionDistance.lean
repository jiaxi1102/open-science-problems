import HypercubeIsolation.StructuralTheory
import Mathlib.Data.Fintype.Card
import Mathlib.Tactic

namespace HypercubeIsolation.StructuralTheory

/-- Coordinates on which two binary words disagree. -/
def disagreementCoords {n : ℕ} (x y : BitWord n) : Finset (Fin n) :=
  {i | x i ≠ y i}

@[simp] theorem card_disagreementCoords {n : ℕ} (x y : BitWord n) :
    (disagreementCoords x y).card = dist x y := by
  rfl

/--
After deleting exactly `ell` coordinates, one can retain precisely
`dist x y - ell` disagreements.  This is the puncturing lemma used to lift
minimum distance from every fixed-size projection to the full words.
-/
theorem exists_keptCoordinates_min_restrictedDist {n ell : ℕ}
    (hell : ell ≤ n) (x y : BitWord n) :
    ∃ S : Finset (Fin n),
      S.card = n - ell ∧ restrictedDist S x y = dist x y - ell := by
  classical
  let Δ : Finset (Fin n) := disagreementCoords x y
  have hΔcard : Δ.card = dist x y := by
    simp [Δ]
  by_cases hlarge : ell ≤ Δ.card
  · obtain ⟨T, hTΔ, hTcard⟩ := Finset.exists_subset_card_eq hlarge
    refine ⟨Finset.univ \ T, ?_, ?_⟩
    · calc
        (Finset.univ \ T).card = (Finset.univ : Finset (Fin n)).card - T.card :=
          Finset.card_sdiff_of_subset (Finset.subset_univ T)
        _ = n - ell := by simp [hTcard]
    · have hfilter :
          ((Finset.univ \ T).filter fun i => x i ≠ y i) = Δ \ T := by
        ext i
        simp [Δ, disagreementCoords, and_left_comm, and_comm, and_assoc]
      unfold restrictedDist
      rw [hfilter, Finset.card_sdiff_of_subset hTΔ, hTcard, hΔcard]
  · have hsmall : Δ.card < ell := Nat.lt_of_not_ge hlarge
    have hΔle : Δ.card ≤ ell := Nat.le_of_lt hsmall
    obtain ⟨T, hΔT, hTcard⟩ :=
      Finset.exists_superset_card_eq (α := Fin n) hΔle (by simpa using hell)
    refine ⟨Finset.univ \ T, ?_, ?_⟩
    · calc
        (Finset.univ \ T).card = (Finset.univ : Finset (Fin n)).card - T.card :=
          Finset.card_sdiff_of_subset (Finset.subset_univ T)
        _ = n - ell := by simp [hTcard]
    · have hfilter :
          ((Finset.univ \ T).filter fun i => x i ≠ y i) = Δ \ T := by
        ext i
        simp [Δ, disagreementCoords, and_left_comm, and_comm, and_assoc]
      have hempty : Δ \ T = ∅ := Finset.sdiff_eq_empty_iff_subset.mpr hΔT
      have hdist_le : dist x y ≤ ell := by
        rw [← hΔcard]
        exact hΔle
      unfold restrictedDist
      rw [hfilter, hempty]
      exact (Nat.sub_eq_zero_of_le hdist_le).symm

/--
If every projection obtained by retaining `n-ell` coordinates separates two
words by at least a positive distance `delta`, then the full words are separated
by at least `delta+ell`.
-/
theorem fullDist_ge_of_all_projectionDist_ge {n ell delta : ℕ}
    (hell : ell ≤ n) (hdelta : 0 < delta) (x y : BitWord n)
    (hproj : ∀ S : Finset (Fin n),
      S.card = n - ell → delta ≤ restrictedDist S x y) :
    delta + ell ≤ dist x y := by
  obtain ⟨S, hScard, hSdist⟩ :=
    exists_keptCoordinates_min_restrictedDist hell x y
  have h := hproj S hScard
  rw [hSdist] at h
  omega

/-- Code-level form of the projection-to-full-distance lift. -/
theorem code_fullDist_ge_of_all_projectionDist_ge {n ell delta : ℕ}
    (hell : ell ≤ n) (hdelta : 0 < delta) (C : Finset (BitWord n))
    (hproj : ∀ x ∈ C, ∀ y ∈ C, x ≠ y →
      ∀ S : Finset (Fin n),
        S.card = n - ell → delta ≤ restrictedDist S x y) :
    ∀ x ∈ C, ∀ y ∈ C, x ≠ y → delta + ell ≤ dist x y := by
  intro x hx y hy hxy
  exact fullDist_ge_of_all_projectionDist_ge hell hdelta x y
    (hproj x hx y hy hxy)

#print axioms exists_keptCoordinates_min_restrictedDist
#print axioms code_fullDist_ge_of_all_projectionDist_ge

end HypercubeIsolation.StructuralTheory
