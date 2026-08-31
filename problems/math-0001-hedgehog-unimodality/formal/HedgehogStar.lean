import Hedgehog

/-!
# Specialized recursive semantics for hedgehog stars

This file closes the algebraic bridge used in Proposition 2.5 of
Ibarra--Landry--Montoya-Vega--Przytycki for the only states reachable from a
star whose leaf delays lie in `{1,2}`.

Leaves are indexed from right to left.  A true Boolean means delay `1`, hence
that the leaf is eligible for the first pluck.  After any eligible first pluck,
all remaining delays become `1`; their coefficient sequence is the ordinary
q-factorial sequence.
-/

namespace Hedgehog

/-- Coefficients of the constant polynomial `1`, extended to all integer indices. -/
def Delta (k : ℤ) : ℤ := if k = 0 then 1 else 0

/-- Sum of the monomial shifts contributed by the eligible leaves of a star. -/
def EligibleSum (n : ℕ) (ε : ℕ → Bool) (a : ℤ → ℤ) (k : ℤ) : ℤ :=
  ∑ i ∈ Finset.range n, if ε i then a (k - (i : ℤ)) else 0

@[simp] theorem window_zero (r : ℕ) (k : ℤ) :
    Window r (fun _ => 0) k = 0 := by
  induction r with
  | zero => rfl
  | succ r ih => simp [Window, ih]

/-- `Window` distributes over a finite sum of coefficient sequences. -/
theorem window_finset_sum {α : Type} (s : Finset α) (f : α → ℤ → ℤ)
    (r : ℕ) (k : ℤ) :
    Window r (fun x => ∑ i ∈ s, f i x) k =
      ∑ i ∈ s, Window r (f i) k := by
  induction r with
  | zero => simp [Window]
  | succ r ih =>
      simp only [Window]
      rw [ih]
      simp [Finset.sum_add_distrib]

/-- A moving window commutes with a monomial shift. -/
theorem window_shift (r i : ℕ) (a : ℤ → ℤ) (k : ℤ) :
    Window r (fun x => a (x - (i : ℤ))) k =
      Window r a (k - (i : ℤ)) := by
  induction r with
  | zero => rfl
  | succ r ih =>
      simp only [Window]
      rw [ih]
      congr 1
      congr 1
      omega

/-- Applying a quantum-integer window before or after summing eligible leaves
produces the same coefficient sequence. -/
theorem window_eligibleSum (r n : ℕ) (ε : ℕ → Bool) (a : ℤ → ℤ) (k : ℤ) :
    Window r (EligibleSum n ε a) k =
      EligibleSum n ε (Window r a) k := by
  simp only [EligibleSum]
  rw [window_finset_sum]
  apply Finset.sum_congr rfl
  intro i hi
  cases h : ε i <;> simp [h, window_shift]

/-- Every q-factorial window commutes past the eligible-leaf sum. -/
theorem descendWindows_eligibleSum (m n : ℕ) (ε : ℕ → Bool) (a : ℤ → ℤ) :
    DescendWindows m (EligibleSum n ε a) =
      EligibleSum n ε (DescendWindows m a) := by
  induction m generalizing a with
  | zero => rfl
  | succ m ih =>
      simp only [DescendWindows]
      have hcomm :
          Window (m + 1) (EligibleSum n ε a) =
            EligibleSum n ε (Window (m + 1) a) := by
        funext k
        exact window_eligibleSum (m + 1) n ε a k
      rw [hcomm]
      exact ih (Window (m + 1) a)

/-- The eligible monomials applied to `1` are exactly the zero-one indicator
sequence used in the coefficient theorem. -/
theorem eligibleSum_delta (n : ℕ) (ε : ℕ → Bool) :
    EligibleSum n ε Delta = delayedIndicator n ε := by
  funext k
  simp only [EligibleSum, delayedIndicator]
  by_cases hk : 0 ≤ k ∧ k < (n : ℤ)
  · rw [if_pos hk]
    have hkCast : ((k.toNat : ℕ) : ℤ) = k := Int.toNat_of_nonneg hk.1
    have hkMem : k.toNat ∈ Finset.range n := by
      apply Finset.mem_range.mpr
      have hlt : ((k.toNat : ℕ) : ℤ) < (n : ℤ) := by simpa [hkCast] using hk.2
      exact_mod_cast hlt
    rw [Finset.sum_eq_single k.toNat]
    · simp [Delta, hkCast]
    · intro b hb hne
      have hkb : k ≠ (b : ℤ) := by
        intro heq
        have hnat : k.toNat = b := by
          exact_mod_cast hkCast.trans heq
        exact hne hnat.symm
      simp [Delta, sub_ne_zero.mpr hkb]
    · intro hnot
      exact (hnot hkMem).elim
  · rw [if_neg hk]
    apply Finset.sum_eq_zero
    intro i hi
    have hki : k ≠ (i : ℤ) := by
      intro heq
      apply hk
      constructor
      · rw [heq]
        exact_mod_cast Nat.zero_le i
      · rw [heq]
        exact_mod_cast Finset.mem_range.mp hi
    simp [Delta, sub_ne_zero.mpr hki]

/-- Coefficients of the ordinary plucking polynomial of a trivial-delay star. -/
def PlainStarCoeffs (n : ℕ) : ℤ → ℤ := DescendWindows n Delta

/--
Coefficient-level recursive semantics for a hedgehog star with delays in
`{1,2}`.  The successor clause is precisely the first-pluck recursion: every
eligible leaf contributes its monomial shift, and the remaining `n`-ray star
has trivial delay.
-/
def DelayedStarCoeffs : ℕ → (ℕ → Bool) → ℤ → ℤ
  | 0, _ => Delta
  | n + 1, ε => EligibleSum (n + 1) ε (PlainStarCoeffs n)

/-- The specialized first-pluck recursion, exposed as a named equation. -/
theorem delayedStar_first_pluck (n : ℕ) (ε : ℕ → Bool) :
    DelayedStarCoeffs (n + 1) ε =
      EligibleSum (n + 1) ε (PlainStarCoeffs n) := rfl

/-- Formal Proposition 2.5 at coefficient level. -/
theorem delayedStar_factorization (n : ℕ) (ε : ℕ → Bool) :
    DelayedStarCoeffs (n + 1) ε =
      DescendWindows n (delayedIndicator (n + 1) ε) := by
  simp only [DelayedStarCoeffs, PlainStarCoeffs]
  rw [← eligibleSum_delta (n + 1) ε]
  rw [descendWindows_eligibleSum]

/-- The one-vertex coefficient sequence is unimodal. -/
theorem delta_unimodal : Unimodal Delta := by
  refine ⟨0, ?_⟩
  constructor
  · intro k hk
    by_cases hkm : k = -1
    · subst k
      norm_num [Delta]
    · have hk0 : k ≠ 0 := by omega
      have hk10 : k + 1 ≠ 0 := by omega
      simp [Delta, hk0, hk10]
  · intro k hk
    by_cases hk0 : k = 0
    · subst k
      norm_num [Delta]
    · have hk10 : k + 1 ≠ 0 := by omega
      simp [Delta, hk0, hk10]

/-- End-to-end coefficient statement for the hedgehog `{1,2}` delay case. -/
theorem delayedStar_unimodal (n : ℕ) (ε : ℕ → Bool) :
    Unimodal (DelayedStarCoeffs n ε) := by
  cases n with
  | zero => exact delta_unimodal
  | succ n =>
      rw [delayedStar_factorization]
      simpa using hedgehog_plucking_coefficients_unimodal (n + 1) ε

#print axioms delayedStar_unimodal

end Hedgehog
