import Lean
import HypercubeIsolation.StructuralTheory

set_option maxHeartbeats 0
set_option maxRecDepth 100000

namespace HypercubeIsolation

/-!
A finite, self-contained certificate for the counterexample

  iota(Q_6, Q_2) = 5 > 4 = gamma(Q_4).

Vertices of Q_n are natural numbers in [0, 2^n), interpreted as n-bit strings.
For each choice of four coordinates of Q_6, projection to those coordinates gives Q_4.
A set D is Q_2-isolating in Q_6 exactly when every such projection of D dominates Q_4:
a Q_2 in Q_6 is a coordinate 2-face, and its four fixed coordinates specify one vertex
of the projected Q_4.

The executable lower-bound check enumerates every strictly increasing four-element subset
of the 64 vertices. Coverage is represented by a 240-bit natural-number mask:
15 four-coordinate projections, each with 16 target vertices.
-/

/-- The `i`th bit of `x`, returned as `0` or `1`. -/
def bit (x i : Nat) : Nat := (x / (2 ^ i)) % 2

/-- Project a bit string onto the listed coordinates, preserving list order. -/
def projectAux : List Nat → Nat → Nat → Nat
  | [], _, _ => 0
  | i :: is, x, weight => bit x i * weight + projectAux is x (2 * weight)

/-- Project `x` onto `coords`, encoding the result as a natural number. -/
def project (coords : List Nat) (x : Nat) : Nat := projectAux coords x 1

/-- Hamming distance on the lowest `n` bits. -/
def hamming : Nat → Nat → Nat → Nat
  | 0, _, _ => 0
  | n + 1, x, y =>
      (if x % 2 = y % 2 then 0 else 1) + hamming n (x / 2) (y / 2)

/-- All 4-subsets of the six coordinate positions. -/
def coordinateFourSets : List (List Nat) :=
  [ [0, 1, 2, 3], [0, 1, 2, 4], [0, 1, 2, 5],
    [0, 1, 3, 4], [0, 1, 3, 5], [0, 1, 4, 5],
    [0, 2, 3, 4], [0, 2, 3, 5], [0, 2, 4, 5],
    [0, 3, 4, 5], [1, 2, 3, 4], [1, 2, 3, 5],
    [1, 2, 4, 5], [1, 3, 4, 5], [2, 3, 4, 5] ]

/-- The 16-bit closed-neighborhood mask of `center` in Q_4. -/
def ballMaskQ4 (center : Nat) : Nat :=
  (List.range 16).foldl
    (fun mask x =>
      if hamming 4 center x ≤ 1 then
        Nat.lor mask (Nat.shiftLeft 1 x)
      else
        mask)
    0

/-- Full coverage mask for Q_4. -/
def fullQ4Mask : Nat := Nat.shiftLeft 1 16 - 1

/-- Does a list of centers dominate Q_4? -/
def dominatesQ4 (centers : List Nat) : Bool :=
  centers.foldl (fun mask x => Nat.lor mask (ballMaskQ4 x)) 0 == fullQ4Mask

/-- Build the indexed projection mask by structural recursion over coordinate sets. -/
def q2FaceMaskQ6Aux (vertex : Nat) : List (List Nat) → Nat → Nat
  | [], _ => 0
  | coords :: rest, projectionIndex =>
      let block := Nat.shiftLeft (ballMaskQ4 (project coords vertex)) (16 * projectionIndex)
      Nat.lor block (q2FaceMaskQ6Aux vertex rest (projectionIndex + 1))

/--
The 240-bit mask of all coordinate 2-faces of Q_6 hit by the closed neighborhood
of a single vertex. Block `j` (16 bits) records domination in the `j`th Q_4 projection.
-/
def q2FaceMaskQ6 (vertex : Nat) : Nat :=
  q2FaceMaskQ6Aux vertex coordinateFourSets 0

/-- Full coverage mask for all 15 * 16 coordinate 2-faces. -/
def fullQ2FaceMaskQ6 : Nat := Nat.shiftLeft 1 240 - 1

/-- Closed-neighborhood coverage masks for all 64 vertices of Q_6. -/
def q2FaceMasksQ6 : Array Nat :=
  ((List.range 64).map q2FaceMaskQ6).toArray

/-- Read a precomputed Q_6 mask. -/
def q2FaceMaskAt (vertex : Nat) : Nat := q2FaceMasksQ6.getD vertex 0

/-- Does a list of vertices form a Q_2-isolating set in Q_6? -/
def q2IsolatingQ6 (vertices : List Nat) : Bool :=
  vertices.foldl (fun mask x => Nat.lor mask (q2FaceMaskAt x)) 0 == fullQ2FaceMaskQ6

/-- A four-vertex dominating set of Q_4. -/
def dominatingWitnessQ4 : List Nat := [0, 1, 14, 15]

/-- A five-vertex Q_2-isolating set of Q_6: 000000, 000011, 000101, 111001, 111110. -/
def isolatingWitnessQ6 : List Nat := [0, 3, 5, 57, 62]

/-- Exhaustively search all 3-element subsets of V(Q_4). -/
def existsDominatingTripleQ4 : Bool :=
  (List.range 16).any fun a =>
    (List.range 16).any fun b =>
      if a < b then
        (List.range 16).any fun c =>
          if b < c then dominatesQ4 [a, b, c] else false
      else
        false

/-- Exhaustively search all 4-element subsets of V(Q_6). -/
def existsFourVertexQ2IsolatingQ6 : Bool :=
  (List.range 64).any fun a =>
    (List.range 64).any fun b =>
      if a < b then
        (List.range 64).any fun c =>
          if b < c then
            (List.range 64).any fun d =>
              if c < d then q2IsolatingQ6 [a, b, c, d] else false
          else
            false
      else
        false

/-- The advertised Q_4 witness really dominates. -/
theorem dominatingWitnessQ4_valid : dominatesQ4 dominatingWitnessQ4 = true := by
  decide +kernel

/-- No three vertices dominate Q_4. -/
theorem noDominatingTripleQ4 : existsDominatingTripleQ4 = false := by
  decide +kernel

/-- The advertised five vertices hit every Q_2 after closed-neighborhood expansion. -/
theorem isolatingWitnessQ6_valid : q2IsolatingQ6 isolatingWitnessQ6 = true := by
  decide +kernel

/-- No four vertices form a Q_2-isolating set in Q_6. -/
theorem noFourVertexQ2IsolatingQ6 : existsFourVertexQ2IsolatingQ6 = false := by
  native_decide

/-- The complete finite certificate. -/
theorem counterexample_certificate :
    dominatesQ4 dominatingWitnessQ4 = true ∧
    existsDominatingTripleQ4 = false ∧
    q2IsolatingQ6 isolatingWitnessQ6 = true ∧
    existsFourVertexQ2IsolatingQ6 = false := by
  exact ⟨dominatingWitnessQ4_valid,
    noDominatingTripleQ4,
    isolatingWitnessQ6_valid,
    noFourVertexQ2IsolatingQ6⟩

#print axioms counterexample_certificate

end HypercubeIsolation
