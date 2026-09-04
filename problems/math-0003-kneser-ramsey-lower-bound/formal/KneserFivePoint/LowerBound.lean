import KneserFivePoint
import Mathlib

/-!
# End-to-end Kneser--Ramsey lower bound

This module lifts the kernel-checked five-point trace gadget to an explicit
red/blue coloring of every Kneser graph `KG(3r+2,r)`, for `r ≥ 1`.  The final
theorem is a direct formal witness for

`R_r^KG(3,3) ≥ 3r+3`.
-/

namespace KneserFivePoint

/-- The vertices of `KG(n,r)`, represented as `r`-element finsets of `Fin n`. -/
abbrev KneserVertex (n r : Nat) := {s : Finset (Fin n) // s.card = r}

/--
A symmetric two-coloring of `KG(n,r)` with no monochromatic Kneser triangle.
The coloring is total on vertex pairs, but the triangle condition is imposed
only on three pairwise-disjoint vertices, exactly the triangles of the Kneser
graph.
-/
def KneserTriangleAvoidingColoring (n r : Nat) : Prop :=
  ∃ color : KneserVertex n r → KneserVertex n r → Bool,
    (∀ A B, color A B = color B A) ∧
      ∀ A B C,
        Disjoint A.1 B.1 →
        Disjoint A.1 C.1 →
        Disjoint B.1 C.1 →
        ¬ (color A B = color A C ∧ color A C = color B C)

/--
`KneserRamseyLowerBound r N` means that a triangle-avoiding two-coloring
exists one ground-set size below `N`.  Thus it is the witness form of
`R_r^KG(3,3) ≥ N`.
-/
def KneserRamseyLowerBound (r N : Nat) : Prop :=
  KneserTriangleAvoidingColoring (N - 1) r

/-- Embed the five distinguished points into the ground set of `KG(3r+2,r)`. -/
def distinguishedEmbedding (r : Nat) (hr : 1 ≤ r) : Fin 5 ↪ Fin (3 * r + 2) where
  toFun i := ⟨i.1, by omega⟩
  inj' := by
    intro i j h
    apply Fin.ext
    simpa using congrArg (fun x : Fin (3 * r + 2) => x.val) h

/-- The trace of a Kneser vertex on the five distinguished points. -/
def traceSet {r : Nat} (hr : 1 ≤ r) (A : KneserVertex (3 * r + 2) r) :
    Finset (Fin 5) :=
  Finset.univ.filter fun i => distinguishedEmbedding r hr i ∈ A.1

/-- Encode a finset of the five distinguished points as the existing bitvector trace. -/
def maskOfTrace (s : Finset (Fin 5)) : Trace :=
  (if (0 : Fin 5) ∈ s then 0b00001#5 else 0#5) |||
  (if (1 : Fin 5) ∈ s then 0b00010#5 else 0#5) |||
  (if (2 : Fin 5) ∈ s then 0b00100#5 else 0#5) |||
  (if (3 : Fin 5) ∈ s then 0b01000#5 else 0#5) |||
  (if (4 : Fin 5) ∈ s then 0b10000#5 else 0#5)

/--
The finset form of the five-point gadget.  This is a closed finite theorem:
all `32^3` trace triples are reduced by the Lean kernel.
-/
theorem finsetTraceGadget :
    ∀ a b c : Finset (Fin 5),
      Disjoint a b →
      Disjoint a c →
      Disjoint b c →
      3 ≤ (a ∪ b ∪ c).card →
      ¬ (red (maskOfTrace a) (maskOfTrace b) =
          red (maskOfTrace a) (maskOfTrace c) ∧
         red (maskOfTrace a) (maskOfTrace c) =
          red (maskOfTrace b) (maskOfTrace c)) := by
  decide +kernel

/-- Disjoint Kneser vertices have disjoint five-point traces. -/
theorem traceSet_disjoint {r : Nat} (hr : 1 ≤ r)
    {A B : KneserVertex (3 * r + 2) r}
    (hAB : Disjoint A.1 B.1) :
    Disjoint (traceSet hr A) (traceSet hr B) := by
  refine Finset.disjoint_left.mpr ?_
  intro i hiA hiB
  have hiA' : distinguishedEmbedding r hr i ∈ A.1 := by
    simpa [traceSet] using hiA
  have hiB' : distinguishedEmbedding r hr i ∈ B.1 := by
    simpa [traceSet] using hiB
  exact (Finset.disjoint_left.mp hAB) hiA' hiB'

/--
Three pairwise-disjoint `r`-sets in a `(3r+2)`-point ground set cover at least
three of the five distinguished points.
-/
theorem trace_union_card_ge_three {r : Nat} (hr : 1 ≤ r)
    (A B C : KneserVertex (3 * r + 2) r)
    (hAB : Disjoint A.1 B.1)
    (hAC : Disjoint A.1 C.1)
    (hBC : Disjoint B.1 C.1) :
    3 ≤ (traceSet hr A ∪ traceSet hr B ∪ traceSet hr C).card := by
  classical
  let U : Finset (Fin (3 * r + 2)) := A.1 ∪ B.1 ∪ C.1
  let T : Finset (Fin 5) := traceSet hr A ∪ traceSet hr B ∪ traceSet hr C
  let M : Finset (Fin 5) := Finset.univ \ T

  have hAB_C : Disjoint (A.1 ∪ B.1) C.1 :=
    Finset.disjoint_union_left.mpr ⟨hAC, hBC⟩

  have hUcard : U.card = 3 * r := by
    dsimp [U]
    rw [Finset.card_union_of_disjoint hAB_C,
      Finset.card_union_of_disjoint hAB, A.2, B.2, C.2]
    omega

  have hComplementCard : (Finset.univ \ U).card = 2 := by
    rw [Finset.card_sdiff_of_subset (Finset.subset_univ U)]
    simp only [Finset.card_univ, Fintype.card_fin, hUcard]
    omega

  have hMapSubset :
      M.map (distinguishedEmbedding r hr) ⊆ Finset.univ \ U := by
    intro x hx
    rcases Finset.mem_map.mp hx with ⟨i, hiM, rfl⟩
    refine Finset.mem_sdiff.mpr ⟨Finset.mem_univ _, ?_⟩
    intro hiU
    have hiNotT : i ∉ T := (Finset.mem_sdiff.mp hiM).2
    apply hiNotT
    have hiU' : distinguishedEmbedding r hr i ∈ A.1 ∪ B.1 ∪ C.1 := by
      simpa [U] using hiU
    rcases Finset.mem_union.mp hiU' with hiAB | hiC
    · rcases Finset.mem_union.mp hiAB with hiA | hiB
      · have hti : i ∈ traceSet hr A := by
          simp [traceSet, hiA]
        exact Finset.mem_union.mpr (Or.inl (Finset.mem_union.mpr (Or.inl hti)))
      · have hti : i ∈ traceSet hr B := by
          simp [traceSet, hiB]
        exact Finset.mem_union.mpr (Or.inl (Finset.mem_union.mpr (Or.inr hti)))
    · have hti : i ∈ traceSet hr C := by
        simp [traceSet, hiC]
      exact Finset.mem_union.mpr (Or.inr hti)

  have hMcard : M.card ≤ 2 := by
    calc
      M.card = (M.map (distinguishedEmbedding r hr)).card := by simp
      _ ≤ (Finset.univ \ U).card := Finset.card_le_card hMapSubset
      _ = 2 := hComplementCard

  have hMTcard : M.card + T.card = 5 := by
    simpa [M] using
      (Finset.card_sdiff_add_card_inter (Finset.univ : Finset (Fin 5)) T)

  have hTcard : 3 ≤ T.card := by omega
  simpa [T] using hTcard

/-- The explicit five-point coloring of `KG(3r+2,r)`. -/
def traceColor {r : Nat} (hr : 1 ≤ r)
    (A B : KneserVertex (3 * r + 2) r) : Bool :=
  red (maskOfTrace (traceSet hr A)) (maskOfTrace (traceSet hr B))

/-- The explicit coloring is symmetric. -/
theorem traceColor_symm {r : Nat} (hr : 1 ≤ r)
    (A B : KneserVertex (3 * r + 2) r) :
    traceColor hr A B = traceColor hr B A := by
  exact red_symm _ _

/-- Every Kneser triangle receives both colors under the explicit coloring. -/
theorem traceColor_noMonochromaticTriangle {r : Nat} (hr : 1 ≤ r)
    (A B C : KneserVertex (3 * r + 2) r)
    (hAB : Disjoint A.1 B.1)
    (hAC : Disjoint A.1 C.1)
    (hBC : Disjoint B.1 C.1) :
    ¬ (traceColor hr A B = traceColor hr A C ∧
       traceColor hr A C = traceColor hr B C) := by
  exact finsetTraceGadget
    (traceSet hr A) (traceSet hr B) (traceSet hr C)
    (traceSet_disjoint hr hAB)
    (traceSet_disjoint hr hAC)
    (traceSet_disjoint hr hBC)
    (trace_union_card_ge_three hr A B C hAB hAC hBC)

/-- A complete formal coloring witness on `KG(3r+2,r)`. -/
theorem exists_triangle_avoiding_coloring (r : Nat) (hr : 1 ≤ r) :
    KneserTriangleAvoidingColoring (3 * r + 2) r := by
  refine ⟨traceColor hr, ?_⟩
  constructor
  · intro A B
    exact traceColor_symm hr A B
  · intro A B C hAB hAC hBC
    exact traceColor_noMonochromaticTriangle hr A B C hAB hAC hBC

/--
End-to-end lower-bound half:

`R_r^KG(3,3) ≥ 3r+3` for every `r ≥ 1`.
-/
theorem kneserRamsey_three_three_lower_bound (r : Nat) (hr : 1 ≤ r) :
    KneserRamseyLowerBound r (3 * r + 3) := by
  have hN : 3 * r + 3 - 1 = 3 * r + 2 := by omega
  simpa [KneserRamseyLowerBound, hN] using
    (exists_triangle_avoiding_coloring r hr)

#print axioms KneserFivePoint.finsetTraceGadget
#print axioms KneserFivePoint.kneserRamsey_three_three_lower_bound

end KneserFivePoint
