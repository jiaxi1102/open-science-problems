import Lean.Elab.Tactic.Decide

/-!
# Five-point trace gadget for Kneser Ramsey colorings

A `Trace` is a subset of five distinguished points, encoded as a five-bit
vector. `red a b` implements the four-rule coloring from the accompanying
human proof. The main theorem verifies the complete finite statement: three
pairwise-disjoint traces covering at least three points cannot induce a
monochromatic triangle.
-/

namespace KneserFivePoint

abbrev Trace := BitVec 5

/-- A five-bit trace contains exactly one distinguished point. -/
def isSingleton (a : Trace) : Bool :=
  a == 0b00001#5 || a == 0b00010#5 || a == 0b00100#5 ||
  a == 0b01000#5 || a == 0b10000#5

/-- A trace is empty. -/
def isEmpty (a : Trace) : Bool := a == 0#5

/-- Test whether a bit mask is contained in a trace. -/
def containsMask (a mask : Trace) : Bool := (a &&& mask) == mask

/-- A trace contains at least three of the five distinguished points. -/
def atLeastThree (a : Trace) : Bool :=
  containsMask a 0b00111#5 || containsMask a 0b01011#5 ||
  containsMask a 0b10011#5 || containsMask a 0b01101#5 ||
  containsMask a 0b10101#5 || containsMask a 0b11001#5 ||
  containsMask a 0b01110#5 || containsMask a 0b10110#5 ||
  containsMask a 0b11010#5 || containsMask a 0b11100#5

/-- Two traces are disjoint. -/
def disjoint (a b : Trace) : Bool := (a &&& b) == 0#5

/--
The universal trace coloring. `true` is red and `false` is blue.

* If neither trace is a singleton, equal empty/large types are red.
* Two singleton traces are red when adjacent on the five-cycle.
* A singleton--empty edge is red.
* A singleton--large edge is red when the large trace contains the chosen
  cyclic predecessor of the singleton.
-/
def red (a b : Trace) : Bool :=
  let sa := isSingleton a
  let sb := isSingleton b
  if !sa && !sb then
    isEmpty a == isEmpty b
  else if sa && sb then
    let neighbors := BitVec.rotateLeft a 1 ||| BitVec.rotateRight a 1
    !((b &&& neighbors) == 0#5)
  else
    let singleton := if sa then a else b
    let other := if sa then b else a
    if isEmpty other then
      true
    else
      !((other &&& BitVec.rotateRight singleton 1) == 0#5)

/-- The four-rule coloring is symmetric in its two trace arguments. -/
theorem red_symm : ∀ a b : Trace, red a b = red b a := by
  native_decide

/--
The finite five-point gadget: pairwise-disjoint traces whose union contains at
least three points induce both edge colors.
-/
theorem fivePointGadget :
    ∀ a b c : Trace,
      disjoint a b = true →
      disjoint a c = true →
      disjoint b c = true →
      atLeastThree (a ||| b ||| c) = true →
      ¬ (red a b = red a c ∧ red a c = red b c) := by
  native_decide

#print axioms KneserFivePoint.red_symm
#print axioms KneserFivePoint.fivePointGadget

end KneserFivePoint
