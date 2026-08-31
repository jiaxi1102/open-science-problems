import Mathlib

/-!
# Conway 99-graph: finite obstruction for one fixed point and an order-seven automorphism

The human proof reduces the graph question to sixteen canonical integer-vector
cases.  For each vector `p`, an admissible `12 × 12` quotient block must have
rows in the finite domains generated below, and every pair of rows must satisfy
the symmetry and quadratic identities checked by `compatible`.

`quotientCasesUnsat` is a kernel-checked evaluation of an exact, integer-only,
minimum-remaining-values backtracking search.  The graph-to-quotient reduction
is documented separately and is not claimed to be formalized in this file.
-/

namespace ConwayZ7

abbrev Row := List Nat

private def N : Nat := 12
private def A : List Nat := [0, 1, 2]
private def C : List Nat := [9, 10, 11]

private def at (xs : List Nat) (i : Nat) : Nat := xs.getD i 0

private def dot (xs ys : Row) : Nat :=
  (List.zipWith (· * ·) xs ys).sum

/-- Bounded weak compositions. Structural recursion is on the length. -/
private def compositions : Nat → Nat → Nat → List Row
  | 0, total, _ => if total = 0 then [[]] else []
  | length + 1, total, maximum =>
      (List.range (Nat.min maximum total + 1)).flatMap fun first =>
        (compositions length (total - first) maximum).map (first :: ·)

private def inWing (i : Nat) : Bool := i < 3 || 9 ≤ i

/-- Entry of `12 J + 12 I - 2 y yᵀ`, where
`y = (1,1,1,0,0,0,0,0,0,-1,-1,-1)`. -/
private def target (i j : Nat) : Nat :=
  if i = j then
    if inWing i then 22 else 24
  else if (i < 3 && j < 3) || (9 ≤ i && 9 ≤ j) then
    10
  else if (i < 3 && 9 ≤ j) || (9 ≤ i && j < 3) then
    14
  else
    12

private def rowOptions (p : Row) (i : Nat) : List Row :=
  let pi := at p i
  let sumA := pi
  let sumC := pi
  let sumM := 12 - 2 * pi
  let norm2 := if inWing i then 22 else 24
  let pDot := (if inWing i then 42 else 36) - pi
  (compositions 3 sumA 4).flatMap fun rA =>
    (compositions 6 sumM 4).flatMap fun rM =>
      (compositions 3 sumC 4).filterMap fun rC =>
        let r := rA ++ rM ++ rC
        if at r i = 0 ∧
            dot r r = norm2 ∧
            dot r p = pDot then
          some r
        else
          none

private def compatible (i : Nat) (ri : Row) (j : Nat) (rj : Row) : Bool :=
  at ri j = at rj i && dot ri rj + at ri j = target i j

private def compatibleAssigned
    (assigned : List (Option Row)) (i : Nat) (ri : Row) : Bool :=
  (List.range N).all fun j =>
    match assigned.getD j none with
    | none => true
    | some rj => compatible i ri j rj

private def chooseMRV
    (assigned : List (Option Row)) (domains : List (List Row)) : Option Nat :=
  match (List.range N).filter (fun i => (assigned.getD i none).isNone) with
  | [] => none
  | i :: rest =>
      some <| rest.foldl (fun best j =>
        if (domains.getD j []).length < (domains.getD best []).length then j else best) i

private def refineDomains
    (assigned : List (Option Row)) (domains : List (List Row))
    (picked : Nat) (row : Row) : Option (List (List Row)) :=
  let start := domains.set picked [row]
  (List.range N).foldl (fun state j =>
    match state with
    | none => none
    | some ds =>
        if j = picked then
          some ds
        else
          match assigned.getD j none with
          | some _ => some ds
          | none =>
              let next := (ds.getD j []).filter fun rj =>
                compatible picked row j rj && compatibleAssigned assigned j rj
              if next.isEmpty then none else some (ds.set j next)) (some start)

/-- Exact backtracking. `fuel = 12` is sufficient because every recursive call
assigns one previously unassigned row. -/
private def search : Nat → List (Option Row) → List (List Row) → Bool
  | 0, assigned, domains => (chooseMRV assigned domains).isNone
  | fuel + 1, assigned, domains =>
      match chooseMRV assigned domains with
      | none => true
      | some i =>
          (domains.getD i []).any fun ri =>
            if compatibleAssigned assigned i ri then
              let assigned' := assigned.set i (some ri)
              match refineDomains assigned' domains i ri with
              | none => false
              | some domains' => search fuel assigned' domains'
            else
              false

private def patterns : List Row := [
  [2, 2, 2, 4, 4, 4, 4, 4, 4, 2, 2, 2],
  [4, 3, 1, 4, 4, 3, 3, 3, 3, 4, 2, 2],
  [4, 3, 1, 5, 3, 3, 3, 3, 3, 3, 3, 2],
  [4, 3, 1, 4, 4, 4, 3, 3, 2, 3, 3, 2],
  [4, 2, 2, 5, 3, 3, 3, 3, 3, 4, 2, 2],
  [4, 2, 2, 4, 4, 4, 3, 3, 2, 4, 2, 2],
  [4, 2, 2, 5, 4, 3, 3, 3, 2, 3, 3, 2],
  [4, 2, 2, 4, 4, 4, 4, 2, 2, 3, 3, 2],
  [3, 3, 2, 5, 4, 4, 3, 2, 2, 3, 3, 2],
  [3, 3, 2, 4, 4, 4, 4, 3, 1, 3, 3, 2],
  [5, 3, 2, 3, 3, 3, 3, 2, 2, 4, 3, 3],
  [4, 4, 2, 3, 3, 3, 3, 2, 2, 4, 4, 2],
  [4, 4, 2, 4, 3, 3, 2, 2, 2, 4, 3, 3],
  [4, 4, 2, 3, 3, 3, 3, 3, 1, 4, 3, 3],
  [4, 3, 3, 4, 4, 2, 2, 2, 2, 4, 3, 3],
  [4, 3, 3, 4, 3, 3, 3, 2, 1, 4, 3, 3]
]

private def initialAssigned : List (Option Row) := List.replicate N none

private def caseHasSolution (p : Row) : Bool :=
  search N initialAssigned ((List.range N).map (rowOptions p))

/-- The exact finite quotient search finds no solution in any of the sixteen
canonical moment types. -/
def quotientSearchPassed : Bool := patterns.all fun p => !(caseHasSolution p)

set_option maxRecDepth 1000000 in
set_option maxHeartbeats 0 in
/-- Kernel-checked finite certificate. -/
theorem quotientCasesUnsat : quotientSearchPassed = true := by
  native_decide

end ConwayZ7
