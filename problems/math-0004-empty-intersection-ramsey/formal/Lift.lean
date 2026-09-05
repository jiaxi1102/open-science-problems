import Finite
import Mathlib

set_option maxHeartbeats 0
set_option maxRecDepth 16000

namespace EmptyIntersection

/-- Interpret a six-bit mask as a genuine finite set of ground points. -/
def baseSet (i : Vertex) : Finset (Fin 6) :=
  Finset.univ.filter fun x => (mask i).getLsbD x.val = true

theorem baseSet_card : ∀ i : Vertex, (baseSet i).card = 3 := by
  decide +kernel

theorem baseSet_ne : ∀ i j : Vertex, i ≠ j → baseSet i ≠ baseSet j := by
  decide +kernel

theorem baseSet_empty : ∀ a b c : Vertex, EmptyTriple a b c →
    baseSet a ∩ baseSet b ∩ baseSet c = ∅ := by
  decide +kernel

/-- All sets occupying half of the six-block ground set. -/
abbrev HalfVertex (q : Nat) :=
  {A : Finset (Fin 6 × Fin q) // A.card = 3 * q}

/-- Replace each base point by a block of q points. -/
def liftVertex (q : Nat) (i : Vertex) : HalfVertex q :=
  ⟨(baseSet i).product (Finset.univ : Finset (Fin q)), by
    simp [Finset.card_product, baseSet_card]⟩

theorem liftVertex_injective (q : Nat) (hq : 0 < q) :
    Function.Injective (liftVertex q) := by
  intro a b h
  have hab : (baseSet a).product (Finset.univ : Finset (Fin q)) =
      (baseSet b).product (Finset.univ : Finset (Fin q)) :=
    congrArg (fun v : HalfVertex q => v.1) h
  have heq : baseSet a = baseSet b := by
    apply Finset.ext
    intro x
    constructor
    · intro hx
      have hp : (x, (⟨0, hq⟩ : Fin q)) ∈
          (baseSet a).product (Finset.univ : Finset (Fin q)) :=
        Finset.mem_product.mpr ⟨hx, Finset.mem_univ _⟩
      rw [hab] at hp
      exact (Finset.mem_product.mp hp).1
    · intro hx
      have hp : (x, (⟨0, hq⟩ : Fin q)) ∈
          (baseSet b).product (Finset.univ : Finset (Fin q)) :=
        Finset.mem_product.mpr ⟨hx, Finset.mem_univ _⟩
      rw [← hab] at hp
      exact (Finset.mem_product.mp hp).1
  by_contra hne
  exact baseSet_ne a b hne heq

theorem liftVertex_empty (q : Nat) (a b c : Vertex) (he : EmptyTriple a b c) :
    (liftVertex q a).1 ∩ (liftVertex q b).1 ∩ (liftVertex q c).1 = ∅ := by
  apply Finset.ext
  intro x
  constructor
  · intro hx
    change x ∈ (baseSet a).product Finset.univ ∩
      (baseSet b).product Finset.univ ∩ (baseSet c).product Finset.univ at hx
    have hxa := (Finset.mem_product.mp
      (Finset.mem_inter.mp (Finset.mem_inter.mp hx).1).1).1
    have hxb := (Finset.mem_product.mp
      (Finset.mem_inter.mp (Finset.mem_inter.mp hx).1).2).1
    have hxc := (Finset.mem_product.mp (Finset.mem_inter.mp hx).2).1
    have hm : x.1 ∈ baseSet a ∩ baseSet b ∩ baseSet c :=
      Finset.mem_inter.mpr ⟨Finset.mem_inter.mpr ⟨hxa, hxb⟩, hxc⟩
    rw [baseSet_empty a b c he] at hm
    simp at hm
  · intro hx
    simp at hx

/-- The ground set has exactly 6q points. -/
theorem ground_card (q : Nat) : Fintype.card (Fin 6 × Fin q) = 6 * q := by
  simp

/-- Every coloring of all 3q-subsets of a 6q-point ground set has
three distinct monochromatic vertices with empty three-way intersection. -/
theorem uniformHalfIntersectionRamsey (q : Nat) (hq : 0 < q)
    (color : HalfVertex q → HalfVertex q → Bool) :
    ∃ A B C : HalfVertex q,
      A ≠ B ∧ A ≠ C ∧ B ≠ C ∧ A.1 ∩ B.1 ∩ C.1 = ∅ ∧
      color A B = color A C ∧ color A C = color B C := by
  obtain ⟨a, b, c, hab, hbc, he, hm⟩ :=
    finiteIntersectionRamsey (fun i j => color (liftVertex q i) (liftVertex q j))
  have hinj := liftVertex_injective q hq
  refine ⟨liftVertex q a, liftVertex q b, liftVertex q c, ?_, ?_, ?_,
    liftVertex_empty q a b c he, hm⟩
  · intro h
    exact (ne_of_lt hab) (hinj h)
  · intro h
    exact (ne_of_lt (lt_trans hab hbc)) (hinj h)
  · intro h
    exact (ne_of_lt hbc) (hinj h)

#print axioms finiteIntersectionRamsey
#print axioms uniformHalfIntersectionRamsey
end EmptyIntersection
