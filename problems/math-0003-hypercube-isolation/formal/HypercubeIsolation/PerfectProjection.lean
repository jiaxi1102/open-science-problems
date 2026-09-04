import HypercubeIsolation.Packing
import Mathlib.Algebra.BigOperators.Group.Finset.Sigma
import Mathlib.Tactic

open scoped BigOperators

namespace HypercubeIsolation.StructuralTheory

/--
If a finite family of equal-size sets covers a finite universe and the total
incidence count is exactly the size of that universe, then the family is
pairwise disjoint.  This is the abstract double-counting step behind the fact
that a covering code meeting the sphere bound is perfect.
-/
theorem pairwiseDisjoint_of_cover_uniform_exact
    {α β : Type*} [DecidableEq α] [DecidableEq β] [Fintype β]
    (C : Finset α) (B : α → Finset β) (V : ℕ)
    (hcover : ∀ y : β, ∃ c ∈ C, y ∈ B c)
    (hcard : ∀ c ∈ C, (B c).card = V)
    (hexact : C.card * V = Fintype.card β) :
    Set.PairwiseDisjoint (↑C : Set α) B := by
  classical
  let I : Finset (Σ _ : α, β) := C.sigma B
  let p : (Σ _ : α, β) → β := fun z => z.2
  have hmaps : Set.MapsTo p (↑I : Set (Σ _ : α, β))
      (↑(Finset.univ : Finset β) : Set β) := by
    intro z hz
    simp
  have hsurj : Set.SurjOn p (↑I : Set (Σ _ : α, β))
      (↑(Finset.univ : Finset β) : Set β) := by
    intro y hy
    obtain ⟨c, hc, hyc⟩ := hcover y
    refine ⟨⟨c, y⟩, ?_, rfl⟩
    simp [I, hc, hyc]
  have hIcard : I.card = (Finset.univ : Finset β).card := by
    calc
      I.card = ∑ c ∈ C, (B c).card := by
        simpa [I] using (Finset.card_sigma C B)
      _ = ∑ c ∈ C, V := by
        apply Finset.sum_congr rfl
        intro c hc
        exact hcard c hc
      _ = C.card * V := by simp
      _ = Fintype.card β := hexact
      _ = (Finset.univ : Finset β).card := by simp
  have hinj : Set.InjOn p (↑I : Set (Σ _ : α, β)) :=
    Finset.injOn_of_surjOn_of_card_le p hmaps hsurj (by rw [hIcard])
  intro c hc d hd hcd
  change Disjoint (B c) (B d)
  rw [Finset.disjoint_left]
  intro y hyc hyd
  have hcy : (⟨c, y⟩ : Σ _ : α, β) ∈ I := by
    simp [I, hc, hyc]
  have hdy : (⟨d, y⟩ : Σ _ : α, β) ∈ I := by
    simp [I, hd, hyd]
  have heq : (⟨c, y⟩ : Σ _ : α, β) = ⟨d, y⟩ :=
    hinj hcy hdy rfl
  exact hcd (congrArg Sigma.fst heq)

/-- Interpolate from `x` to `y` on the selected coordinates. -/
def interpolateOn {n : ℕ} (T : Finset (Fin n)) (x y : BitWord n) : BitWord n :=
  fun i => if i ∈ T then y i else x i

/-- Restricted Hamming distance is symmetric. -/
theorem restrictedDist_comm {n : ℕ} (S : Finset (Fin n)) (x y : BitWord n) :
    restrictedDist S x y = restrictedDist S y x := by
  unfold restrictedDist
  congr 1
  ext i
  simp [ne_comm]

/-- Changing exactly `T` disagreement coordinates creates exactly `|T|` differences from `x`. -/
theorem restrictedDist_interpolateOn_left {n : ℕ}
    {S T : Finset (Fin n)} {x y : BitWord n}
    (hT : T ⊆ S.filter fun i => x i ≠ y i) :
    restrictedDist S x (interpolateOn T x y) = T.card := by
  unfold restrictedDist
  have hfilter :
      (S.filter fun i => x i ≠ interpolateOn T x y i) = T := by
    ext i
    by_cases hiT : i ∈ T
    · have hiΔ := hT hiT
      have hiS : i ∈ S := (Finset.mem_filter.mp hiΔ).1
      have hxy : x i ≠ y i := (Finset.mem_filter.mp hiΔ).2
      simp [interpolateOn, hiT, hiS, hxy]
    · simp [interpolateOn, hiT]
  rw [hfilter]

/-- The remaining distance to `y` is the original restricted distance minus `|T|`. -/
theorem restrictedDist_interpolateOn_right {n : ℕ}
    {S T : Finset (Fin n)} {x y : BitWord n}
    (hT : T ⊆ S.filter fun i => x i ≠ y i) :
    restrictedDist S (interpolateOn T x y) y = restrictedDist S x y - T.card := by
  unfold restrictedDist
  have hfilter :
      (S.filter fun i => interpolateOn T x y i ≠ y i) =
        (S.filter fun i => x i ≠ y i) \ T := by
    ext i
    by_cases hiT : i ∈ T <;> simp [interpolateOn, hiT]
  rw [hfilter, Finset.card_sdiff_of_subset hT]

/-- Two restricted Hamming balls overlap whenever their centers are at distance at most `2r`. -/
theorem exists_restricted_midpoint_of_dist_le_two_mul {n r : ℕ}
    (S : Finset (Fin n)) (x y : BitWord n)
    (hxy : restrictedDist S x y ≤ 2 * r) :
    ∃ z : BitWord n,
      restrictedDist S x z ≤ r ∧ restrictedDist S y z ≤ r := by
  classical
  let Δ := S.filter fun i => x i ≠ y i
  have hΔcard : Δ.card = restrictedDist S x y := by rfl
  have hchoose : restrictedDist S x y - r ≤ Δ.card := by
    rw [hΔcard]
    exact Nat.sub_le _ _
  obtain ⟨T, hTΔ, hTcard⟩ := Finset.exists_subset_card_eq hchoose
  have hT : T ⊆ S.filter fun i => x i ≠ y i := by
    simpa [Δ] using hTΔ
  let z := interpolateOn T x y
  refine ⟨z, ?_, ?_⟩
  · have hleft : restrictedDist S x z = T.card := by
      simpa [z] using restrictedDist_interpolateOn_left hT
    rw [hleft, hTcard]
    omega
  · have hright : restrictedDist S z y = restrictedDist S x y - T.card := by
      simpa [z] using restrictedDist_interpolateOn_right hT
    rw [restrictedDist_comm S y z, hright, hTcard]
    omega

/-- The restricted Hamming ball around `x` on coordinate set `S`. -/
def restrictedBall {n : ℕ} (S : Finset (Fin n)) (x : BitWord n) (r : ℕ) :
    Finset (BitWord n) :=
  Finset.univ.filter fun y => restrictedDist S x y ≤ r

@[simp] theorem mem_restrictedBall {n r : ℕ} {S : Finset (Fin n)} {x y : BitWord n} :
    y ∈ restrictedBall S x r ↔ restrictedDist S x y ≤ r := by
  simp [restrictedBall]

/-- Disjoint restricted balls force projected center distance greater than twice the radius. -/
theorem two_mul_lt_restrictedDist_of_ball_disjoint {n r : ℕ}
    {S : Finset (Fin n)} {x y : BitWord n}
    (hdisj : Disjoint (restrictedBall S x r) (restrictedBall S y r)) :
    2 * r < restrictedDist S x y := by
  by_contra hnot
  have hle : restrictedDist S x y ≤ 2 * r := Nat.le_of_not_gt hnot
  obtain ⟨z, hxz, hyz⟩ := exists_restricted_midpoint_of_dist_le_two_mul S x y hle
  exact (Finset.disjoint_left.mp hdisj)
    (mem_restrictedBall.mpr hxz) (mem_restrictedBall.mpr hyz)

/--
An exact restricted-ball cover is a perfect projected code and therefore has
projected minimum distance at least `2r+1`.
-/
theorem projection_separated_of_cover_uniform_exact {n r V : ℕ}
    (D : Finset (BitWord n)) (S : Finset (Fin n))
    (hcover : ∀ a : BitWord n, ∃ d ∈ D, restrictedDist S d a ≤ r)
    (hcard : ∀ d ∈ D, (restrictedBall S d r).card = V)
    (hexact : D.card * V = 2 ^ n) :
    ∀ x ∈ D, ∀ y ∈ D, x ≠ y → 2 * r + 1 ≤ restrictedDist S x y := by
  classical
  have hexact' : D.card * V = Fintype.card (BitWord n) := by
    simpa [BitWord] using hexact
  have hpair := pairwiseDisjoint_of_cover_uniform_exact
    D (fun d => restrictedBall S d r) V
    (by
      intro a
      obtain ⟨d, hd, hda⟩ := hcover a
      exact ⟨d, hd, mem_restrictedBall.mpr hda⟩)
    hcard hexact'
  intro x hx y hy hxy
  have hlt := two_mul_lt_restrictedDist_of_ball_disjoint (hpair hx hy hxy)
  omega

/--
Formal metric and double-counting core of the perfect-code extension
obstruction.  Exact projected covers force projected separation; puncturing
lifts that separation to the full rows; then ordinary Hamming packing applies.
The remaining external inputs for a concrete coding family are only the two
ball-cardinality formulas and the corresponding arithmetic identities.
-/
theorem packing_bound_of_exact_projection_covers
    {n ell r Vrestricted R Vpacking : ℕ}
    (hell : ell ≤ n) (D : Finset (BitWord n))
    (hcover : ∀ S : Finset (Fin n),
      S.card = n - ell →
        ∀ a : BitWord n, ∃ d ∈ D, restrictedDist S d a ≤ r)
    (hrestrictedCard : ∀ S : Finset (Fin n),
      S.card = n - ell →
        ∀ d ∈ D, (restrictedBall S d r).card = Vrestricted)
    (hexact : D.card * Vrestricted = 2 ^ n)
    (hR : 2 * R < (2 * r + 1) + ell)
    (hpackingCard : ∀ d ∈ D, (hammingBall d R).card = Vpacking) :
    D.card * Vpacking ≤ 2 ^ n := by
  have hproj : ∀ x ∈ D, ∀ y ∈ D, x ≠ y →
      ∀ S : Finset (Fin n),
        S.card = n - ell → 2 * r + 1 ≤ restrictedDist S x y := by
    intro x hx y hy hxy S hScard
    exact projection_separated_of_cover_uniform_exact D S
      (hcover S hScard) (hrestrictedCard S hScard) hexact x hx y hy hxy
  exact packing_bound_of_all_projectionDist_ge
    hell (by omega) hR D hproj hpackingCard

#print axioms pairwiseDisjoint_of_cover_uniform_exact
#print axioms projection_separated_of_cover_uniform_exact
#print axioms packing_bound_of_exact_projection_covers

end HypercubeIsolation.StructuralTheory
