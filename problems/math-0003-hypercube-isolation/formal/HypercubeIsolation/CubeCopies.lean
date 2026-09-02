import Mathlib.Data.Finset.SymmDiff
import Mathlib.Tactic

open scoped symmDiff

namespace HypercubeIsolation.CubeCopies

/-- A vertex of `Q_n`, represented by the set of coordinates equal to one. -/
abbrev CubeVertex (n : ℕ) := Finset (Fin n)

/-- Toggle one coordinate of a cube vertex. -/
def flip {n : ℕ} (x : CubeVertex n) (i : Fin n) : CubeVertex n := x ∆ {i}

@[simp] theorem flip_flip {n : ℕ} (x : CubeVertex n) (i : Fin n) :
    flip (flip x i) i = x := by
  simp [flip, symmDiff_assoc]

theorem flip_comm {n : ℕ} (x : CubeVertex n) (i j : Fin n) :
    flip (flip x i) j = flip (flip x j) i := by
  simp [flip, symmDiff_assoc, symmDiff_comm, symmDiff_left_comm]

@[simp] theorem flip_ne {n : ℕ} (x : CubeVertex n) (i : Fin n) :
    flip x i ≠ x := by
  intro h
  have hi := congrArg (fun s : CubeVertex n => i ∈ s) h
  simp [flip, Finset.mem_symmDiff] at hi

@[simp] theorem flip_eq_flip_iff {n : ℕ} (x : CubeVertex n) (i j : Fin n) :
    flip x i = flip x j ↔ i = j := by
  constructor
  · intro h
    have hs : ({i} : Finset (Fin n)) = {j} := by
      simpa [flip, symmDiff_assoc] using
        (show x ∆ ({i} : Finset (Fin n)) = x ∆ {j} from h)
    simpa using hs
  · rintro rfl
    rfl

/-- Toggling a coordinate absent from a vertex is insertion. -/
theorem flip_eq_insert_of_notMem {n : ℕ} {x : CubeVertex n} {i : Fin n}
    (hi : i ∉ x) : flip x i = insert i x := by
  ext j
  by_cases hji : j = i
  · subst j
    simp [flip, Finset.mem_symmDiff, hi]
  · simp [flip, Finset.mem_symmDiff, hji]

/-- Cube adjacency in toggle form. -/
def Adjacent {n : ℕ} (x y : CubeVertex n) : Prop := ∃ i, y = flip x i

/--
An injective edge-preserving map from `Q_k` into `Q_n`.  This is exactly the
data supplied by a graph copy of `Q_k` in `Q_n`: every domain edge obtained by
toggling one coordinate maps to an ambient edge obtained by toggling one
coordinate.
-/
structure CubeEmbedding (k n : ℕ) where
  toFun : CubeVertex k → CubeVertex n
  injective : Function.Injective toFun
  map_flip : ∀ x i, ∃ j, toFun (flip x i) = flip (toFun x) j

namespace CubeEmbedding

variable {k n : ℕ} (F : CubeEmbedding k n)

/-- The ambient coordinate used by a particular domain edge. -/
noncomputable def label (x : CubeVertex k) (i : Fin k) : Fin n :=
  Classical.choose (F.map_flip x i)

/-- The defining property of the edge label. -/
theorem map_flip_label (x : CubeVertex k) (i : Fin k) :
    F.toFun (flip x i) = flip (F.toFun x) (F.label x i) :=
  Classical.choose_spec (F.map_flip x i)

/-- Edge labels are unique. -/
theorem label_unique {x : CubeVertex k} {i : Fin k} {j : Fin n}
    (h : F.toFun (flip x i) = flip (F.toFun x) j) : F.label x i = j := by
  have h' := (F.map_flip_label x i).symm.trans h
  exact (flip_eq_flip_iff (F.toFun x) (F.label x i) j).mp h'

/-- Distinct coordinate directions at one vertex receive distinct labels. -/
theorem label_injective_at (x : CubeVertex k) : Function.Injective (F.label x) := by
  intro i j hij
  apply (flip_eq_flip_iff x i j).mp
  apply F.injective
  calc
    F.toFun (flip x i) = flip (F.toFun x) (F.label x i) := F.map_flip_label x i
    _ = flip (F.toFun x) (F.label x j) := by rw [hij]
    _ = F.toFun (flip x j) := (F.map_flip_label x j).symm

/-- Reversing an edge does not change its ambient coordinate label. -/
theorem label_flip_same (x : CubeVertex k) (i : Fin k) :
    F.label (flip x i) i = F.label x i := by
  apply F.label_unique
  have h := F.map_flip_label x i
  rw [flip_flip]
  rw [h]
  simp

/-- Opposite sides of a nondegenerate ambient cube square have the same label. -/
theorem opposite_labels_of_square {a : CubeVertex n} {p q r s : Fin n}
    (hpq : p ≠ q) (hps : p ≠ s)
    (h : flip (flip a p) q = flip (flip a s) r) : p = r ∧ q = s := by
  have hpair : ({p} : Finset (Fin n)) ∆ {q} = {s} ∆ {r} := by
    simpa [flip, symmDiff_assoc] using h
  have hp_left : p ∈ ({p} : Finset (Fin n)) ∆ {q} := by
    simp [Finset.mem_symmDiff, hpq]
  have hp_right : p ∈ ({s} : Finset (Fin n)) ∆ {r} := hpair ▸ hp_left
  have hpr : p = r := by
    simp only [Finset.mem_symmDiff, Finset.mem_singleton] at hp_right
    rcases hp_right with ⟨hps', _⟩ | ⟨hpr, _⟩
    · exact False.elim (hps hps')
    · exact hpr
  subst r
  have hsingle : ({q} : Finset (Fin n)) = {s} := by
    apply (symmDiff_right_inj (a := ({p} : Finset (Fin n)))).mp
    calc
      ({p} : Finset (Fin n)) ∆ {q} = {s} ∆ {p} := hpair
      _ = {p} ∆ {s} := symmDiff_comm _ _
  exact ⟨rfl, by simpa using hsingle⟩

/-- Flipping any domain coordinate preserves the label of every direction. -/
theorem label_flip (x : CubeVertex k) (i j : Fin k) :
    F.label (flip x j) i = F.label x i := by
  by_cases hij : i = j
  · subst j
    exact F.label_flip_same x i
  · let p := F.label x i
    let s := F.label x j
    let q := F.label (flip x i) j
    let r := F.label (flip x j) i
    have hps : p ≠ s := by
      exact (F.label_injective_at x) hij
    have hpq : p ≠ q := by
      intro hpqeq
      have hrev : F.label (flip x i) i = p := by
        simpa [p] using F.label_flip_same x i
      have hinj := F.label_injective_at (flip x i)
      apply hij
      apply hinj
      calc
        F.label (flip x i) i = p := hrev
        _ = q := hpqeq
    have hsquare : flip (flip (F.toFun x) p) q = flip (flip (F.toFun x) s) r := by
      calc
        flip (flip (F.toFun x) p) q = F.toFun (flip (flip x i) j) := by
          rw [F.map_flip_label x i]
          exact (F.map_flip_label (flip x i) j).symm
        _ = F.toFun (flip (flip x j) i) := by rw [flip_comm]
        _ = flip (flip (F.toFun x) s) r := by
          rw [F.map_flip_label x j]
          exact F.map_flip_label (flip x j) i
    have hop := opposite_labels_of_square hpq hps hsquare
    exact hop.1.symm

/-- Every edge in a fixed domain direction has the same ambient label. -/
theorem label_eq_empty (x : CubeVertex k) (i : Fin k) :
    F.label x i = F.label ∅ i := by
  induction x using Finset.induction_on with
  | empty => rfl
  | @insert a x ha ih =>
      calc
        F.label (insert a x) i = F.label (flip x a) i := by
          rw [flip_eq_insert_of_notMem ha]
        _ = F.label x i := F.label_flip x i a
        _ = F.label ∅ i := ih

/-- The fixed injection from intrinsic cube directions to ambient directions. -/
noncomputable def axis : Fin k ↪ Fin n where
  toFun i := F.label ∅ i
  inj' := F.label_injective_at ∅

/-- Every intrinsic edge in direction `i` toggles the single coordinate `axis i`. -/
theorem map_flip_axis (x : CubeVertex k) (i : Fin k) :
    F.toFun (flip x i) = flip (F.toFun x) (F.axis i) := by
  rw [F.map_flip_label]
  congr 1
  exact F.label_eq_empty x i

/-- The canonical coordinate embedding determined by a base vertex and the axis injection. -/
noncomputable def coordinateMap (x : CubeVertex k) : CubeVertex n :=
  F.toFun ∅ ∆ x.map F.axis

/-- Every injective edge-preserving cube map is a coordinate embedding. -/
theorem toFun_eq_coordinateMap (x : CubeVertex k) :
    F.toFun x = F.coordinateMap x := by
  induction x using Finset.induction_on with
  | empty => simp [coordinateMap]
  | @insert a x ha ih =>
      have ha_image : F.axis a ∉ x.map F.axis := by
        simp [ha]
      calc
        F.toFun (insert a x) = F.toFun (flip x a) := by
          rw [flip_eq_insert_of_notMem ha]
        _ = flip (F.toFun x) (F.axis a) := F.map_flip_axis x a
        _ = flip (F.coordinateMap x) (F.axis a) := by rw [ih]
        _ = F.coordinateMap (insert a x) := by
          simp [coordinateMap, flip, Finset.map_insert, symmDiff_assoc,
            Finset.symmDiff_eq_union, ha_image]

/--
Coordinate-copy theorem: the image of every abstract graph copy of `Q_k` in
`Q_n` is obtained from one base vertex by independently toggling `k` distinct
ambient coordinates.
-/
theorem is_coordinate_copy :
    ∃ (base : CubeVertex n) (σ : Fin k ↪ Fin n),
      ∀ x : CubeVertex k, F.toFun x = base ∆ x.map σ := by
  exact ⟨F.toFun ∅, F.axis, F.toFun_eq_coordinateMap⟩

#print axioms CubeEmbedding.is_coordinate_copy

end CubeEmbedding

end HypercubeIsolation.CubeCopies
