import HypercubeIsolation.ProjectionDistance
import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Data.Finset.Union
import Mathlib.Tactic

open scoped BigOperators

namespace HypercubeIsolation.StructuralTheory

/-- The closed Hamming ball of radius `r` about a binary word. -/
def hammingBall {n : ℕ} (x : BitWord n) (r : ℕ) : Finset (BitWord n) :=
  Finset.univ.filter fun y => dist x y ≤ r

@[simp] theorem mem_hammingBall {n r : ℕ} {x y : BitWord n} :
    y ∈ hammingBall x r ↔ dist x y ≤ r := by
  simp [hammingBall]

/-- Balls whose centers are more than twice the radius apart are disjoint. -/
theorem hammingBall_disjoint_of_two_mul_lt_dist {n r : ℕ} {x y : BitWord n}
    (hxy : 2 * r < dist x y) :
    Disjoint (hammingBall x r) (hammingBall y r) := by
  rw [Finset.disjoint_left]
  intro z hzx hzy
  have hxz : dist x z ≤ r := mem_hammingBall.mp hzx
  have hyz : dist y z ≤ r := mem_hammingBall.mp hzy
  have hzy' : dist z y ≤ r := by
    rw [show dist z y = dist y z by
      simpa [dist] using hammingDist_comm z y]
    exact hyz
  have htri : dist x y ≤ dist x z + dist z y := by
    simpa [dist] using hammingDist_triangle x z y
  omega

/-- Pairwise center separation induces pairwise disjoint Hamming balls. -/
theorem hammingBalls_pairwiseDisjoint {n r : ℕ} (C : Finset (BitWord n))
    (hsep : ∀ x ∈ C, ∀ y ∈ C, x ≠ y → 2 * r < dist x y) :
    Set.PairwiseDisjoint (↑C : Set (BitWord n)) (fun x => hammingBall x r) := by
  intro x hx y hy hxy
  exact hammingBall_disjoint_of_two_mul_lt_dist (hsep x hx y hy hxy)

/--
Abstract Hamming packing bound for a binary code.  The theorem deliberately
takes uniform ball cardinality as a hypothesis, isolating the metric/disjointness
argument from the separate combinatorial formula for Hamming-ball volume.
-/
theorem packing_bound_of_uniform_ball_card {n r V : ℕ}
    (C : Finset (BitWord n))
    (hsep : ∀ x ∈ C, ∀ y ∈ C, x ≠ y → 2 * r < dist x y)
    (hcard : ∀ x ∈ C, (hammingBall x r).card = V) :
    C.card * V ≤ 2 ^ n := by
  classical
  let hpair : Set.PairwiseDisjoint (↑C : Set (BitWord n))
      (fun x => hammingBall x r) := hammingBalls_pairwiseDisjoint C hsep
  calc
    C.card * V = ∑ x ∈ C, V := by simp
    _ = ∑ x ∈ C, (hammingBall x r).card := by
      apply Finset.sum_congr rfl
      intro x hx
      exact (hcard x hx).symm
    _ = (C.disjiUnion (fun x => hammingBall x r) hpair).card := by
      exact (Finset.card_disjiUnion C (fun x => hammingBall x r) hpair).symm
    _ ≤ (Finset.univ : Finset (BitWord n)).card := by
      exact Finset.card_le_card (Finset.subset_univ _)
    _ = 2 ^ n := by
      simp [BitWord]

/--
Projection separation plus puncturing implies the full Hamming packing bound.
This is the formal metric core of the perfect-code extension obstruction.
-/
theorem packing_bound_of_all_projectionDist_ge
    {n ell delta r V : ℕ}
    (hell : ell ≤ n) (hdelta : 0 < delta) (hr : 2 * r < delta + ell)
    (C : Finset (BitWord n))
    (hproj : ∀ x ∈ C, ∀ y ∈ C, x ≠ y →
      ∀ S : Finset (Fin n),
        S.card = n - ell → delta ≤ restrictedDist S x y)
    (hcard : ∀ x ∈ C, (hammingBall x r).card = V) :
    C.card * V ≤ 2 ^ n := by
  apply packing_bound_of_uniform_ball_card C
  · intro x hx y hy hxy
    exact lt_of_lt_of_le hr
      (code_fullDist_ge_of_all_projectionDist_ge hell hdelta C hproj x hx y hy hxy)
  · exact hcard

#print axioms packing_bound_of_uniform_ball_card
#print axioms packing_bound_of_all_projectionDist_ge

end HypercubeIsolation.StructuralTheory
