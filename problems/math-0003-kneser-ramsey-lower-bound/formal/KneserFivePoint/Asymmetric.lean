import KneserFivePoint.LowerBound

/-!
# Padded five-point asymmetric Kneser Ramsey bound

Constructs a red-K_s/blue-K_3 avoiding coloring on s*(r+1)-1 points.
-/
namespace KneserFivePoint
set_option maxRecDepth 10000
set_option maxHeartbeats 0

abbrev PaddingTrace := Option (Finset (Fin 5))

/-- `none` is tagged, `some a` is an untagged five-point trace. -/
def paddingRed : PaddingTrace → PaddingTrace → Bool
  | none, none => true
  | none, some b => decide b.Nonempty
  | some a, none => decide a.Nonempty
  | some a, some b => red (maskOfTrace a) (maskOfTrace b)

def compatibleTrace : PaddingTrace → PaddingTrace → Prop
  | some a, some b => Disjoint a b
  | _, _ => True

instance (a b : PaddingTrace) : Decidable (compatibleTrace a b) := by
  cases a <;> cases b <;> dsimp [compatibleTrace] <;> infer_instance

theorem paddingRed_symm : ∀ a b, paddingRed a b = paddingRed b a := by
  intro a b
  cases a <;> cases b <;> simp [paddingRed, red_symm]

/-- No blue template triangle, without any coverage assumption. -/
theorem padding_blue_triangle_free :
    ∀ a b c : PaddingTrace,
      compatibleTrace a b → compatibleTrace a c → compatibleTrace b c →
      ¬ (paddingRed a b = false ∧ paddingRed a c = false ∧
         paddingRed b c = false) := by
  decide +kernel

/-- Red neighbors of the empty trace are untagged and have size at most one. -/
theorem padding_empty_interface :
    ∀ x : PaddingTrace, paddingRed (some ∅) x = true →
      ∃ a : Finset (Fin 5), x = some a ∧ a.card ≤ 1 := by
  decide +kernel

theorem nonempty_red_triangle_free :
    ∀ a b c : Finset (Fin 5),
      a.Nonempty → b.Nonempty → c.Nonempty →
      Disjoint a b → Disjoint a c → Disjoint b c →
      ¬ (paddingRed (some a) (some b) = true ∧
         paddingRed (some a) (some c) = true ∧
         paddingRed (some b) (some c) = true) := by
  decide +kernel

def traceOn {n : Nat} (e : Fin 5 ↪ Fin n) (A : Finset (Fin n)) :
    Finset (Fin 5) := Finset.univ.filter fun i => e i ∈ A

def paddingCode {n : Nat} (e : Fin 5 ↪ Fin n) (D A : Finset (Fin n)) :
    PaddingTrace :=
  if (A ∩ D).Nonempty then none else some (traceOn e A)

theorem traceOn_disjoint {n : Nat} (e : Fin 5 ↪ Fin n)
    {A B : Finset (Fin n)} (h : Disjoint A B) :
    Disjoint (traceOn e A) (traceOn e B) := by
  apply Finset.disjoint_left.mpr
  intro i hi hj
  exact Finset.disjoint_left.mp h
    (Finset.mem_filter.mp hi).2 (Finset.mem_filter.mp hj).2

theorem paddingCode_compatible {n : Nat} (e : Fin 5 ↪ Fin n)
    (D : Finset (Fin n)) {A B : Finset (Fin n)} (h : Disjoint A B) :
    compatibleTrace (paddingCode e D A) (paddingCode e D B) := by
  by_cases ha : (A ∩ D).Nonempty <;> by_cases hb : (B ∩ D).Nonempty
  all_goals simp [paddingCode, ha, hb, compatibleTrace]
  exact traceOn_disjoint e h

/-- Select a different padding point from each tagged disjoint set. -/
theorem count_tagged_le {n s : Nat} (D : Finset (Fin n))
    (A : Fin s → Finset (Fin n))
    (hdis : Pairwise fun i j => Disjoint (A i) (A j)) :
    (Finset.univ.filter fun i => (A i ∩ D).Nonempty).card ≤ D.card := by
  classical
  let T := Finset.univ.filter fun i => (A i ∩ D).Nonempty
  have hex (i : T) : ∃ x, x ∈ A i.1 ∧ x ∈ D := by
    obtain ⟨x, hx⟩ := (Finset.mem_filter.mp i.2).2
    exact ⟨x, (Finset.mem_inter.mp hx).1, (Finset.mem_inter.mp hx).2⟩
  let f : T → D := fun i => ⟨Classical.choose (hex i), (Classical.choose_spec (hex i)).2⟩
  have hf : Function.Injective f := by
    intro i j hij
    apply Subtype.ext
    by_contra hne
    have hi : (f i).1 ∈ A i.1 := (Classical.choose_spec (hex i)).1
    have hj : (f j).1 ∈ A j.1 := (Classical.choose_spec (hex j)).1
    have heq : (f i).1 = (f j).1 := congrArg Subtype.val hij
    exact Finset.disjoint_left.mp (hdis hne) hi (by simpa only [heq] using hj)
  exact Finset.card_le_card_of_injective hf

/-- At most two untagged nonempty traces can occur in a red family. -/
theorem count_nonempty_untagged_le_two {n s : Nat} (e : Fin 5 ↪ Fin n)
    (D : Finset (Fin n)) (A : Fin s → Finset (Fin n))
    (hdis : Pairwise fun i j => Disjoint (A i) (A j))
    (hred : ∀ i j, i ≠ j →
      paddingRed (paddingCode e D (A i)) (paddingCode e D (A j)) = true) :
    (Finset.univ.filter fun i =>
      ¬ (A i ∩ D).Nonempty ∧ (traceOn e (A i)).Nonempty).card ≤ 2 := by
  classical
  by_contra h
  obtain ⟨i,j,k,hi,hj,hk,hij,hik,hjk⟩ :=
    Finset.two_lt_card_iff.mp (by omega : 2 <
      (Finset.univ.filter fun i =>
        ¬ (A i ∩ D).Nonempty ∧ (traceOn e (A i)).Nonempty).card)
  obtain ⟨hiD,hiP⟩ := (Finset.mem_filter.mp hi).2
  obtain ⟨hjD,hjP⟩ := (Finset.mem_filter.mp hj).2
  obtain ⟨hkD,hkP⟩ := (Finset.mem_filter.mp hk).2
  apply nonempty_red_triangle_free (traceOn e (A i)) (traceOn e (A j))
    (traceOn e (A k)) hiP hjP hkP
    (traceOn_disjoint e (hdis hij)) (traceOn_disjoint e (hdis hik))
    (traceOn_disjoint e (hdis hjk))
  refine ⟨?_,?_,?_⟩
  · simpa [paddingCode,hiD,hjD] using hred i j hij
  · simpa [paddingCode,hiD,hkD] using hred i k hik
  · simpa [paddingCode,hjD,hkD] using hred j k hjk

theorem red_family_has_empty {n s : Nat} (hs : 3 ≤ s)
    (e : Fin 5 ↪ Fin n) (D : Finset (Fin n)) (hD : D.card = s-3)
    (A : Fin s → Finset (Fin n))
    (hdis : Pairwise fun i j => Disjoint (A i) (A j))
    (hred : ∀ i j, i ≠ j →
      paddingRed (paddingCode e D (A i)) (paddingCode e D (A j)) = true) :
    ∃ i, ¬ (A i ∩ D).Nonempty ∧ traceOn e (A i) = ∅ := by
  classical
  let T := Finset.univ.filter fun i => (A i ∩ D).Nonempty
  let N := Finset.univ.filter fun i =>
    ¬ (A i ∩ D).Nonempty ∧ (traceOn e (A i)).Nonempty
  have ht : T.card ≤ s-3 := by
    simpa [T,hD] using count_tagged_le D A hdis
  have hn : N.card ≤ 2 := count_nonempty_untagged_le_two e D A hdis hred
  by_contra he
  have hcover : (Finset.univ : Finset (Fin s)) ⊆ T ∪ N := by
    intro i _
    by_cases hi : (A i ∩ D).Nonempty
    · exact Finset.mem_union.mpr (Or.inl (Finset.mem_filter.mpr ⟨Finset.mem_univ _,hi⟩))
    · have hp : (traceOn e (A i)).Nonempty := by
        apply Finset.nonempty_iff_ne_empty.mpr
        intro hempty
        exact he ⟨i,hi,hempty⟩
      exact Finset.mem_union.mpr (Or.inr (Finset.mem_filter.mpr ⟨Finset.mem_univ _,hi,hp⟩))
  have hc : s ≤ T.card + N.card := by
    calc
      s = (Finset.univ : Finset (Fin s)).card := by simp
      _ ≤ (T ∪ N).card := Finset.card_le_card hcover
      _ ≤ T.card + N.card := Finset.card_union_le T N
  omega

theorem red_family_small_traces {n s : Nat} (hs : 3 ≤ s)
    (e : Fin 5 ↪ Fin n) (D : Finset (Fin n)) (hD : D.card = s-3)
    (A : Fin s → Finset (Fin n))
    (hdis : Pairwise fun i j => Disjoint (A i) (A j))
    (hred : ∀ i j, i ≠ j →
      paddingRed (paddingCode e D (A i)) (paddingCode e D (A j)) = true) :
    ∀ i, ¬ (A i ∩ D).Nonempty ∧ (traceOn e (A i)).card ≤ 1 := by
  classical
  obtain ⟨i0,ht,hp⟩ := red_family_has_empty hs e D hD A hdis hred
  intro i
  by_cases hi : i0 = i
  · subst i
    exact ⟨ht, by simp [hp]⟩
  have hc : paddingRed (some ∅) (paddingCode e D (A i)) = true := by
    simpa [paddingCode,ht,hp] using hred i0 i hi
  obtain ⟨a,ha,hcard⟩ := padding_empty_interface _ hc
  by_cases hd : (A i ∩ D).Nonempty
  · simp [paddingCode,hd] at ha
  · have heq : traceOn e (A i) = a := by
      simpa [paddingCode,hd] using ha
    exact ⟨hd, by simpa [heq] using hcard⟩

theorem red_family_trace_union_le_two {n s : Nat} (hs : 3 ≤ s)
    (e : Fin 5 ↪ Fin n) (D : Finset (Fin n)) (hD : D.card = s-3)
    (A : Fin s → Finset (Fin n))
    (hdis : Pairwise fun i j => Disjoint (A i) (A j))
    (hred : ∀ i j, i ≠ j →
      paddingRed (paddingCode e D (A i)) (paddingCode e D (A j)) = true) :
    (Finset.univ.biUnion fun i => traceOn e (A i)).card ≤ 2 := by
  classical
  let N := Finset.univ.filter fun i =>
    ¬ (A i ∩ D).Nonempty ∧ (traceOn e (A i)).Nonempty
  have hn : N.card ≤ 2 := count_nonempty_untagged_le_two e D A hdis hred
  have hsmall := red_family_small_traces hs e D hD A hdis hred
  calc
    (Finset.univ.biUnion fun i => traceOn e (A i)).card
        ≤ ∑ i : Fin s, (traceOn e (A i)).card := Finset.card_biUnion_le
    _ ≤ ∑ i : Fin s, if i ∈ N then 1 else 0 := by
      apply Finset.sum_le_sum
      intro i _
      by_cases hi : i ∈ N
      · simpa [hi] using (hsmall i).2
      · have hp : ¬ (traceOn e (A i)).Nonempty := by
          intro hne
          exact hi (Finset.mem_filter.mpr ⟨Finset.mem_univ _,(hsmall i).1,hne⟩)
        simp [hi, Finset.not_nonempty_iff_eq_empty.mp hp]
    _ = N.card := by simp
    _ ≤ 2 := hn

/-- Missing-ground-point count rules out the red s-clique. -/
theorem padding_no_red_clique {n r s : Nat} (hs : 3 ≤ s)
    (hn : n = s*r+s-1) (e : Fin 5 ↪ Fin n)
    (D : Finset (Fin n)) (hD : D.card = s-3)
    (hDP : Disjoint D (Finset.univ.map e))
    (A : Fin s → KneserVertex n r)
    (hdis : Pairwise fun i j => Disjoint (A i).1 (A j).1) :
    ¬ (∀ i j, i ≠ j →
      paddingRed (paddingCode e D (A i).1) (paddingCode e D (A j).1) = true) := by
  classical
  intro hred
  let U : Finset (Fin n) := Finset.univ.biUnion fun i => (A i).1
  let P : Finset (Fin 5) := Finset.univ.biUnion fun i => traceOn e (A i).1
  let M : Finset (Fin n) := Finset.univ \ U
  let Q : Finset (Fin 5) := Finset.univ \ P
  have hsmall := red_family_small_traces hs e D hD (fun i => (A i).1) hdis hred
  have hP : P.card ≤ 2 :=
    red_family_trace_union_le_two hs e D hD (fun i => (A i).1) hdis hred
  have hU : U.card = s*r := by
    dsimp [U]
    rw [Finset.card_biUnion]
    · simp only [show ∀ i, (A i).1.card = r from fun i => (A i).2]
      simp
    · intro i _ j _ hij
      exact hdis hij
  have hM : M.card = s-1 := by
    dsimp [M]
    rw [Finset.card_sdiff_of_subset (Finset.subset_univ U)]
    simp only [Finset.card_univ,Fintype.card_fin,hU]
    omega
  have hQM : Q.map e ⊆ M := by
    intro x hx
    obtain ⟨i,hi,rfl⟩ := Finset.mem_map.mp hx
    apply Finset.mem_sdiff.mpr
    refine ⟨Finset.mem_univ _,?_⟩
    intro hu
    obtain ⟨j,_,hj⟩ := Finset.mem_biUnion.mp hu
    have hip : i ∈ P := Finset.mem_biUnion.mpr
      ⟨j,Finset.mem_univ _,Finset.mem_filter.mpr ⟨Finset.mem_univ _,hj⟩⟩
    exact (Finset.mem_sdiff.mp hi).2 hip
  have hDM : D ⊆ M := by
    intro x hx
    apply Finset.mem_sdiff.mpr
    refine ⟨Finset.mem_univ _,?_⟩
    intro hu
    obtain ⟨j,_,hj⟩ := Finset.mem_biUnion.mp hu
    exact (hsmall j).1 ⟨x, Finset.mem_inter.mpr ⟨hj,hx⟩⟩
  have hDQ : Disjoint D (Q.map e) := by
    apply hDP.mono_right
    exact Finset.map_subset_map.mpr (Finset.subset_univ Q)
  have hsum : D.card + Q.card ≤ M.card := by
    calc
      D.card + Q.card = (D ∪ Q.map e).card := by
        rw [Finset.card_union_of_disjoint hDQ,Finset.card_map]
      _ ≤ M.card := Finset.card_le_card (Finset.union_subset hDM hQM)
  have hPQ : Q.card + P.card = 5 := by
    simpa [Q] using Finset.card_sdiff_add_card_inter (Finset.univ : Finset (Fin 5)) P
  omega

/-- Explicit symmetric coloring with neither a red s-clique nor a blue triangle. -/
def KneserAsymmetricAvoiding (n r s : Nat) : Prop :=
  ∃ color : KneserVertex n r → KneserVertex n r → Bool,
    (∀ A B, color A B = color B A) ∧
    (∀ A : Fin s → KneserVertex n r,
      (Pairwise fun i j => Disjoint (A i).1 (A j).1) →
      ¬ (∀ i j, i ≠ j → color (A i) (A j) = true)) ∧
    (∀ A B C, Disjoint A.1 B.1 → Disjoint A.1 C.1 → Disjoint B.1 C.1 →
      ¬ (color A B = false ∧ color A C = false ∧ color B C = false))

/-- Witness for `R_r^KG(s,3) >= s*(r+1)`. -/
theorem kneserRamsey_asymmetric_lower_bound (r s : Nat) (hr : 1 ≤ r) (hs : 3 ≤ s) :
    KneserAsymmetricAvoiding (s*(r+1)-1) r s := by
  classical
  let n := s*(r+1)-1
  have hsr : s ≤ s*r := by simpa using Nat.mul_le_mul_left s hr
  have hn : n = s*r+s-1 := by simp [n,Nat.mul_add]
  have hnP : 5 ≤ n := by omega
  have hnD : s+2 ≤ n := by omega
  let e : Fin 5 ↪ Fin n :=
    { toFun := fun i => ⟨i.val, by omega⟩
      inj' := by
        intro i j h
        exact Fin.ext (congrArg (fun x : Fin n => x.val) h) }
  let d : Fin (s-3) ↪ Fin n :=
    { toFun := fun i => ⟨5+i.val, by omega⟩
      inj' := by
        intro i j h
        apply Fin.ext
        have he := congrArg (fun x : Fin n => x.val) h
        dsimp at he
        omega }
  let D := Finset.univ.map d
  have hD : D.card = s-3 := by simp [D]
  have hDP : Disjoint D (Finset.univ.map e) := by
    apply Finset.disjoint_left.mpr
    intro x hx hy
    obtain ⟨i,_,hi⟩ := Finset.mem_map.mp hx
    obtain ⟨j,_,hj⟩ := Finset.mem_map.mp hy
    have he : d i = e j := hi.trans hj.symm
    have hv := congrArg (fun x : Fin n => x.val) he
    change 5 + i.val = j.val at hv
    have hjlt := j.isLt
    omega
  refine ⟨fun A B => paddingRed (paddingCode e D A.1) (paddingCode e D B.1),?_,?_,?_⟩
  · intro A B
    exact paddingRed_symm _ _
  · intro A hdis
    exact padding_no_red_clique hs hn e D hD hDP A hdis
  · intro A B C hAB hAC hBC
    exact padding_blue_triangle_free _ _ _
      (paddingCode_compatible e D hAB) (paddingCode_compatible e D hAC)
      (paddingCode_compatible e D hBC)

#print axioms KneserFivePoint.padding_blue_triangle_free
#print axioms KneserFivePoint.kneserRamsey_asymmetric_lower_bound
end KneserFivePoint
