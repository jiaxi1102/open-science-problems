import HedgehogStar

/-!
# Recursive star semantics

`HedgehogStar` formalizes the first pluck of a `{1,2}`-delayed star after
identifying the remaining trivial-delay star with its q-factorial coefficient
sequence.  This file removes that last identification as an assumption: it
proves that the q-factorial sequence satisfies the ordinary star-plucking
recursion, defines the recursion independently, and proves the two semantics
coincide.
-/

namespace Hedgehog

/-- A moving window is the finite sum of all monomial shifts in its range. -/
theorem window_eq_sum_range (r : ℕ) (a : ℤ → ℤ) (k : ℤ) :
    Window r a k = ∑ i in Finset.range r, a (k - (i : ℤ)) := by
  induction r with
  | zero => simp [Window]
  | succ r ih =>
      simp [Window, Finset.sum_range_succ, ih]

/-- If every leaf is eligible, `EligibleSum` is exactly a quantum-integer
window. -/
theorem eligibleSum_all (n : ℕ) (a : ℤ → ℤ) :
    EligibleSum n (fun _ => true) a = Window n a := by
  funext k
  rw [window_eq_sum_range]
  simp [EligibleSum]

/-- Quantum-integer windows commute. -/
theorem window_commute (r s : ℕ) (a : ℤ → ℤ) :
    Window r (Window s a) = Window s (Window r a) := by
  funext k
  calc
    Window r (Window s a) k =
        Window r (EligibleSum s (fun _ => true) a) k := by
          rw [eligibleSum_all]
    _ = EligibleSum s (fun _ => true) (Window r a) k :=
      window_eligibleSum r s (fun _ => true) a k
    _ = Window s (Window r a) k := by
      rw [eligibleSum_all]

/-- A quantum-integer window commutes through the complete descending
q-factorial product. -/
theorem descendWindows_window_commute (m r : ℕ) (a : ℤ → ℤ) :
    DescendWindows m (Window r a) =
      Window r (DescendWindows m a) := by
  induction m generalizing a with
  | zero => rfl
  | succ m ih =>
      simp only [DescendWindows]
      rw [window_commute (m + 1) r a]
      exact ih (Window (m + 1) a)

/-- The q-factorial coefficients satisfy the ordinary star first-pluck
recursion: pluck any one of the `n+1` leaves and shift by the number of leaves
to its right. -/
theorem plainStar_first_pluck (n : ℕ) :
    PlainStarCoeffs (n + 1) =
      EligibleSum (n + 1) (fun _ => true) (PlainStarCoeffs n) := by
  rw [eligibleSum_all]
  change
    DescendWindows n (Window (n + 1) Delta) =
      Window (n + 1) (DescendWindows n Delta)
  exact descendWindows_window_commute n (n + 1) Delta

/-- Independent recursive definition of the ordinary star plucking
coefficients. -/
def RecursivePlainStarCoeffs : ℕ → ℤ → ℤ
  | 0 => Delta
  | n + 1 =>
      EligibleSum (n + 1) (fun _ => true) (RecursivePlainStarCoeffs n)

/-- The recursively defined ordinary star polynomial has exactly the
q-factorial coefficient sequence. -/
theorem recursivePlainStar_eq_plain (n : ℕ) :
    RecursivePlainStarCoeffs n = PlainStarCoeffs n := by
  induction n with
  | zero => rfl
  | succ n ih =>
      simp only [RecursivePlainStarCoeffs]
      rw [ih]
      exact (plainStar_first_pluck n).symm

/-- Independent recursive semantics for a star whose initial delays lie in
`{1,2}`.  A true Boolean denotes an initially eligible delay-one leaf.  After
an eligible first pluck, the remaining ordinary star is evaluated by its own
recursive semantics above. -/
def RecursiveDelayedStarCoeffs : ℕ → (ℕ → Bool) → ℤ → ℤ
  | 0, _ => Delta
  | n + 1, ε =>
      EligibleSum (n + 1) ε (RecursivePlainStarCoeffs n)

/-- The independent recursive semantics agrees with the compact specialized
semantics from `HedgehogStar`. -/
theorem recursiveDelayedStar_eq_delayed (n : ℕ) (ε : ℕ → Bool) :
    RecursiveDelayedStarCoeffs n ε = DelayedStarCoeffs n ε := by
  cases n with
  | zero => rfl
  | succ n =>
      simp only [RecursiveDelayedStarCoeffs, DelayedStarCoeffs]
      rw [recursivePlainStar_eq_plain]

/-- Proposition 2.5, now derived from independently defined recursive star
semantics. -/
theorem recursiveDelayedStar_factorization (n : ℕ) (ε : ℕ → Bool) :
    RecursiveDelayedStarCoeffs (n + 1) ε =
      DescendWindows n (delayedIndicator (n + 1) ε) := by
  rw [recursiveDelayedStar_eq_delayed, delayedStar_factorization]

/-- End-to-end formally verified unimodality of the recursively defined
`{1,2}`-delayed hedgehog star coefficient sequence. -/
theorem recursiveDelayedStar_unimodal (n : ℕ) (ε : ℕ → Bool) :
    Unimodal (RecursiveDelayedStarCoeffs n ε) := by
  rw [recursiveDelayedStar_eq_delayed]
  exact delayedStar_unimodal n ε

#print axioms recursiveDelayedStar_unimodal

end Hedgehog
