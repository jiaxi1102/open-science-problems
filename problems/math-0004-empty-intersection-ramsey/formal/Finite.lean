import Resolution

namespace EmptyIntersection

/-- Every coloring on the twenty three-subsets of six points contains
an ordered monochromatic triple with empty three-way intersection. -/
theorem finiteIntersectionRamsey (color : Vertex → Vertex → Bool) :
    ∃ a b c : Vertex,
      a < b ∧ b < c ∧ EmptyTriple a b c ∧ Mono color a b c := by
  apply Classical.byContradiction
  intro hnone
  let p : Nat → Prop := fun e => color (edgeAt e).1 (edgeAt e).2 = true
  have hc : ∀ i, clause p i := by
    intro i
    unfold clause
    split
    · rename_i hi
      let j : Fin 480 := ⟨i / 2, by omega⟩
      have hv := rowValid j
      have hn : ¬ Mono color (row j).1 (row j).2.1 (row j).2.2 := by
        intro hm
        exact hnone ⟨(row j).1, (row j).2.1, (row j).2.2,
          hv.1, hv.2.1, hv.2.2, hm⟩
      have hb := booleanClauses
        (color (row j).1 (row j).2.1)
        (color (row j).1 (row j).2.2)
        (color (row j).2.1 (row j).2.2) hn
      have hab := edgeLookup (row j).1 (row j).2.1 hv.1
      have hac := edgeLookup (row j).1 (row j).2.2 (by
        have h1 := hv.1
        have h2 := hv.2.1
        omega)
      have hbc := edgeLookup (row j).2.1 (row j).2.2 hv.2.1
      have hh : positive p (row j) ∧ negative p (row j) := by
        simpa only [positive, negative, p, hab, hac, hbc] using hb
      change (if i % 2 = 0 then positive p (row j) else negative p (row j))
      split
      · exact hh.1
      · exact hh.2
    · trivial
  exact impossible p hc

#print axioms finiteIntersectionRamsey
end EmptyIntersection
