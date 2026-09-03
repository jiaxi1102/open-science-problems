import HypercubeIsolation.StructuralTheory
import Mathlib.Data.Finset.Card
import Mathlib.Tactic

namespace HypercubeIsolation.Puncturing

open StructuralTheory

/-- Coordinates on which two binary words disagree. -/
def disagreement {n : ℕ} (x y : BitWord n) : Finset (Fin n) :=
  Finset.univ.filter fun i => x i ≠ y i

/-- The disagreement set has cardinality equal to Hamming distance. -/
theorem disagreement_card {n : ℕ} (x y : BitWord n) :
    (disagreement x y).card = dist x y := by
  rfl

/--
If all deleted coordinates are disagreements, the remaining restricted
Hamming distance is the original distance minus the number deleted.
-/
theorem restrictedDist_compl_of_subset_disagreement {n : ℕ}
    (x y : BitWord n) {T : Finset (Fin n)}
    (hT : T ⊆ disagreement x y) :
    restrictedDist (Finset.univ \ T) x y =
      (disagreement x y).card - T.card := by
  classical
  unfold restrictedDist disagreement
  have hset :
      (Finset.univ \ T).filter (fun i => x i ≠ y i) =
        (Finset.univ.filter fun i => x i ≠ y i) \ T := by
    ext i
    simp [and_assoc, and_left_comm, and_comm]
  rw [hset, Finset.card_sdiff hT]

/--
If every disagreement is deleted, the remaining restricted Hamming distance
is zero.
-/
theorem restrictedDist_compl_eq_zero_of_disagreement_subset {n : ℕ}
    (x y : BitWord n) {T : Finset (Fin n)}
    (hT : disagreement x y ⊆ T) :
    restrictedDist (Finset.univ \ T) x y = 0 := by
  classical
  unfold restrictedDist
  have hempty :
      (Finset.univ \ T).filter (fun i => x i ≠ y i) = ∅ := by
    apply Finset.eq_empty_iff_forall_not_mem.mpr
    intro i hi
    have hiComp : i ∈ Finset.univ \ T := (Finset.mem_filter.mp hi).1
    have hiDiff : x i ≠ y i := (Finset.mem_filter.mp hi).2
    have hiNotT : i ∉ T := (Finset.mem_sdiff.mp hiComp).2
    have hiDisagreement : i ∈ disagreement x y := by
      exact Finset.mem_filter.mpr ⟨Finset.mem_univ i, hiDiff⟩
    exact hiNotT (hT hiDisagreement)
  rw [hempty]
  rfl

/--
Distance amplification under universal puncturing.

Suppose deleting any `ell` coordinates leaves `x` and `y` at Hamming
 distance at least `d`, with `d > 0`. Then the full words have distance at
least `d + ell`.

This is the rigidity step used in the perfect-code obstruction: if every
`m`-column projection of an `(m+ell)`-column array is a perfect radius-`r`
code, then any two full rows are separated by at least `2*r+1+ell`.
-/
theorem distance_amplification_of_all_punctures
    {n ell d : ℕ} (x y : BitWord n)
    (hd : 0 < d) (hell : ell ≤ n)
    (hpuncture : ∀ T : Finset (Fin n), T.card = ell →
      d ≤ restrictedDist (Finset.univ \ T) x y) :
    d + ell ≤ dist x y := by
  classical
  let Δ : Finset (Fin n) := disagreement x y
  have hΔcard : Δ.card = dist x y := by
    simpa [Δ] using disagreement_card x y
  by_cases hsmall : ell ≤ Δ.card
  · obtain ⟨T, hTsub, hTcard⟩ := Finset.exists_subset_card_eq hsmall
    have hrest : restrictedDist (Finset.univ \ T) x y = Δ.card - ell := by
      calc
        restrictedDist (Finset.univ \ T) x y =
            (disagreement x y).card - T.card :=
          restrictedDist_compl_of_subset_disagreement x y (by simpa [Δ] using hTsub)
        _ = Δ.card - ell := by simp [Δ, hTcard]
    have hbound := hpuncture T hTcard
    rw [hrest] at hbound
    rw [← hΔcard]
    omega
  · have hlt : Δ.card < ell := Nat.lt_of_not_ge hsmall
    have hellUniv : ell ≤ (Finset.univ : Finset (Fin n)).card := by
      simpa using hell
    obtain ⟨T, hΔT, _hTuniv, hTcard⟩ :=
      Finset.exists_subsuperset_card_eq
        (s := Δ) (t := (Finset.univ : Finset (Fin n))) (n := ell)
        (Finset.subset_univ Δ) (Nat.le_of_lt hlt) hellUniv
    have hzero : restrictedDist (Finset.univ \ T) x y = 0 :=
      restrictedDist_compl_eq_zero_of_disagreement_subset x y (by simpa [Δ] using hΔT)
    have hbound := hpuncture T hTcard
    rw [hzero] at hbound
    omega

/-- The radius-`r` form used by punctured perfect codes. -/
theorem radius_distance_amplification
    {n ell r : ℕ} (x y : BitWord n)
    (hell : ell ≤ n)
    (hpuncture : ∀ T : Finset (Fin n), T.card = ell →
      2 * r + 1 ≤ restrictedDist (Finset.univ \ T) x y) :
    2 * r + 1 + ell ≤ dist x y := by
  exact distance_amplification_of_all_punctures x y (by omega) hell hpuncture

#print axioms distance_amplification_of_all_punctures
#print axioms radius_distance_amplification

end HypercubeIsolation.Puncturing
