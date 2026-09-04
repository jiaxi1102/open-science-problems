import Mathlib

/-!
# Formal `K₄` structure behind the exact `R₃^KG(3,3)` search

The six Boolean coordinates have edge order

`AB, AC, AD, BC, BD, CD`.

`Admissible x` says that none of the four triangles of `K₄` is
monochromatic.  The finite theorem below verifies:

* exactly 18 labeled edge colorings are admissible;
* every admissible coloring is, up to a vertex permutation and global color
  complement, either a perfect matching or a path `P₄`;
* the four nonmonochromatic-star constraints are equivalent to the four
  nonmonochromatic-triangle constraints.

These are the finite facts used by the two-branch and 36-cube exact SAT
reductions.  The SAT/DRAT certificates remain separate from this file.
-/

namespace K4Classification

abbrev Bits := Fin 6 → Bool

/-- A Boolean triple is not monochromatic. -/
def NAE (a b c : Bool) : Prop := ¬ (a = b ∧ b = c)

/-- The four triangular faces of `K₄` are all nonmonochromatic. -/
def Admissible (x : Bits) : Prop :=
  NAE (x 0) (x 1) (x 3) ∧
  NAE (x 0) (x 2) (x 4) ∧
  NAE (x 1) (x 2) (x 5) ∧
  NAE (x 3) (x 4) (x 5)

/-- The four three-edge stars of `K₄` are all nonmonochromatic. -/
def StarAdmissible (x : Bits) : Prop :=
  NAE (x 0) (x 1) (x 2) ∧
  NAE (x 0) (x 3) (x 4) ∧
  NAE (x 1) (x 3) (x 5) ∧
  NAE (x 2) (x 4) (x 5)

/-- Edge number of the unordered pair `{i,j}` in the fixed six-edge order.
The diagonal value is irrelevant because every use below assumes `i ≠ j`. -/
def edgeIndex (i j : Fin 4) : Fin 6 :=
  let a := min i.val j.val
  let b := max i.val j.val
  if a = 0 then
    if b = 1 then 0 else if b = 2 then 1 else 2
  else if a = 1 then
    if b = 2 then 3 else 4
  else
    5

/-- Read a six-bit edge coloring on an unordered pair of vertices. -/
def colorAt (x : Bits) (i j : Fin 4) : Bool := x (edgeIndex i j)

/-- Complement a color exactly when `flip` is true. -/
def flipIf (flip color : Bool) : Bool := if flip then !color else color

/-- The red perfect matching `AB,CD`. -/
def matching : Bits := fun edge => decide (edge = 0 ∨ edge = 5)

/-- The red path `A-B-D-C`, with edges `AB,BD,CD`. -/
def path : Bits := fun edge => decide (edge = 0 ∨ edge = 4 ∨ edge = 5)

/-- Equivalence under a permutation of the four vertices and an optional
exchange of the two colors. -/
def Equivalent (x y : Bits) : Prop :=
  ∃ permutation : Equiv.Perm (Fin 4), ∃ flip : Bool,
    ∀ i j : Fin 4, i ≠ j →
      colorAt x i j = flipIf flip (colorAt y (permutation i) (permutation j))

/-- There are exactly 18 labeled red–blue edge colorings of `K₄` with no
monochromatic triangle. -/
theorem admissible_cardinality :
    ((Finset.univ : Finset Bits).filter Admissible).card = 18 := by
  native_decide

/-- The star clauses used to strengthen the SAT instance are logically
redundant: on six edge bits, the four triangle NAE constraints are equivalent
to the four star NAE constraints. -/
theorem triangle_star_equivalence :
    ∀ x : Bits, Admissible x ↔ StarAdmissible x := by
  native_decide

/-- Up to `S₄` and a global exchange of red and blue, every admissible `K₄`
coloring is either matching/C4 type or P4/P4 type. -/
theorem two_orbit_classification :
    ∀ x : Bits, Admissible x →
      Equivalent x matching ∨ Equivalent x path := by
  native_decide

/-- Both representatives are themselves admissible. -/
theorem canonical_representatives_admissible :
    Admissible matching ∧ Admissible path := by
  native_decide

#print axioms admissible_cardinality
#print axioms triangle_star_equivalence
#print axioms two_orbit_classification
#print axioms canonical_representatives_admissible

end K4Classification
