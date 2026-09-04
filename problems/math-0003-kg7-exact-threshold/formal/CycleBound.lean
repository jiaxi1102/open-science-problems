import Lean.Elab.Tactic.Omega

/-! Counting bounds for arbitrary finite fractional colorings of C3 and C5. -/
namespace KG7.CycleBound

def bitValue (b : Bool) : Nat := if b then 1 else 0

def pentagonIndependent (a b c d e : Bool) : Bool :=
  !((a && b) || (b && c) || (c && d) || (d && e) || (e && a))

def triangleIndependent (a b c : Bool) : Bool :=
  !((a && b) || (b && c) || (c && a))

theorem pentagon_one_color_bound (a b c d e : Bool)
    (h : pentagonIndependent a b c d e = true) :
    bitValue a + bitValue b + bitValue c + bitValue d + bitValue e ≤ 2 := by
  cases a <;> cases b <;> cases c <;> cases d <;> cases e <;>
    simp_all [pentagonIndependent, bitValue]

def colorCount : Nat → (Nat → Bool) → Nat
  | 0, _ => 0
  | p + 1, f => colorCount p f + bitValue (f p)

theorem pentagon_count_bound (p : Nat) :
    ∀ (a b c d e : Nat → Bool),
    (∀ i, i < p → pentagonIndependent (a i) (b i) (c i) (d i) (e i) = true) →
    colorCount p a + colorCount p b + colorCount p c +
      colorCount p d + colorCount p e ≤ 2 * p := by
  induction p with
  | zero =>
    intro a b c d e h
    simp [colorCount]
  | succ p ih =>
    intro a b c d e h
    have hprev := ih a b c d e
      (fun i hi => h i (Nat.lt_trans hi (Nat.lt_succ_self p)))
    have hlast := pentagon_one_color_bound (a p) (b p) (c p) (d p) (e p)
      (h p (Nat.lt_succ_self p))
    simp only [colorCount]
    omega

/-- In any q-fold coloring of a pentagon with p colors, 5q ≤ 2p. -/
theorem pentagon_bfold_bound (p q : Nat) (a b c d e : Nat → Bool)
    (h : ∀ i, i < p → pentagonIndependent (a i) (b i) (c i) (d i) (e i) = true)
    (ha : q ≤ colorCount p a) (hb : q ≤ colorCount p b)
    (hc : q ≤ colorCount p c) (hd : q ≤ colorCount p d)
    (he : q ≤ colorCount p e) : 5 * q ≤ 2 * p := by
  have htotal := pentagon_count_bound p a b c d e h
  omega

theorem triangle_to_pentagon (a b c : Bool)
    (h : triangleIndependent a b c = true) :
    pentagonIndependent a b a b c = true := by
  cases a <;> cases b <;> cases c <;>
    simp_all [triangleIndependent, pentagonIndependent]

/-- The same 5/2 lower bound holds for a triangle, via a closed five-step walk. -/
theorem triangle_bfold_bound (p q : Nat) (a b c : Nat → Bool)
    (h : ∀ i, i < p → triangleIndependent (a i) (b i) (c i) = true)
    (ha : q ≤ colorCount p a) (hb : q ≤ colorCount p b)
    (hc : q ≤ colorCount p c) : 5 * q ≤ 2 * p := by
  exact pentagon_bfold_bound p q a b a b c
    (fun i hi => triangle_to_pentagon (a i) (b i) (c i) (h i hi))
    ha hb ha hb hc

#print axioms pentagon_one_color_bound
#print axioms pentagon_count_bound
#print axioms pentagon_bfold_bound
#print axioms triangle_bfold_bound

end KG7.CycleBound
