#!/usr/bin/env python3
"""Generate the explicit Lean 4 finite certificates for KG(8,2)."""
from itertools import combinations
from pathlib import Path
import hashlib

V = list(combinations(range(8), 2))
E = [(i, j) for i, j in combinations(range(28), 2)
     if set(V[i]).isdisjoint(V[j])]
edge_id = {e: i for i, e in enumerate(E)}
M3 = [(a, b, c) for a, b, c in combinations(range(28), 3)
      if set(V[a]).isdisjoint(V[b])
      and set(V[a]).isdisjoint(V[c])
      and set(V[b]).isdisjoint(V[c])]
T = [tuple(sorted((edge_id[(a, b)], edge_id[(a, c)], edge_id[(b, c)])))
     for a, b, c in M3]
CORE_MASKS = []
for x, y in V:
    mask = sum(1 << i for i, e in enumerate(V) if x in e or y in e)
    assert mask.bit_count() == 13
    CORE_MASKS.append(mask)
assert (len(V), len(E), len(M3), len(T), len(set(T)), len(set(CORE_MASKS))) == \
       (28, 210, 420, 420, 420, 28)


def bit(x, i):
    return f"{x}.getLsbD {i}"


def chunks(xs, n=24):
    return [xs[i:i+n] for i in range(0, len(xs), n)]


def emit_chunks(lines, name, binders, application, clauses):
    names = []
    for j, group in enumerate(chunks(clauses)):
        part = f"{name}Chunk{j}"
        names.append(part)
        lines.append(f"def {part} {binders} : Bool :=")
        for k, clause in enumerate(group):
            lines.append(f"  ({clause})" + (" &&" if k + 1 < len(group) else ""))
        lines.append("")
    lines.append(f"def {name} {binders} : Bool :=")
    for j, part in enumerate(names):
        lines.append(f"  {part} {application}" + (" &&" if j + 1 < len(names) else ""))
    lines.append("")


lines = [r'''import Std.Tactic.BVDecide

/-!
# Finite certificates for the fractional Kneser-cover obstruction

`KG(8,2)` has 28 vertices, represented by the edges of `K₈` in lexicographic
order. A 28-bit vector selects vertices. A 210-bit vector colours the edges
of `KG(8,2)`; `true` is blue and `false` is red.

The expensive finite claims are proved by `bv_decide`. It bit-blasts the
statements and reconstructs proof terms checked by Lean's kernel. No external
SAT or MILP output is imported as an axiom.
-/

set_option maxRecDepth 1000000
set_option maxHeartbeats 0

namespace KneserCover

abbrev BV28 := BitVec 28
abbrev BV210 := BitVec 210

@[inline] def bitAsFive (b : Bool) : BitVec 5 :=
  if b then 1#5 else 0#5

def popcount28 (x : BV28) : BitVec 5 :=
''']
terms = [f"bitAsFive ({bit('x', i)})" for i in range(28)]
for i in range(0, 28, 4):
    lines.append("  " + " + ".join(terms[i:i+4]) + (" +" if i + 4 < 28 else ""))
lines.append("")

emit_chunks(lines, "matchingFree", "(chosen : BV28)", "chosen", [
    f"!({bit('chosen', a)} && {bit('chosen', b)} && {bit('chosen', c)})"
    for a, b, c in M3])

core_terms = [f"((chosen &&& {mask}#28) == chosen)" for mask in CORE_MASKS]
lines.append("def containedInDoubleStar (chosen : BV28) : Bool :=")
for i in range(0, 28, 4):
    lines.append("  " + " || ".join(core_terms[i:i+4]) + (" ||" if i + 4 < 28 else ""))
lines.append("")

emit_chunks(lines, "blueOn", "(chosen : BV28) (colour : BV210)",
            "chosen colour", [
    f"!({bit('chosen', u)} && {bit('chosen', v)}) || {bit('colour', e)}"
    for e, (u, v) in enumerate(E)])
emit_chunks(lines, "redOn", "(chosen : BV28) (colour : BV210)",
            "chosen colour", [
    f"!({bit('chosen', u)} && {bit('chosen', v)}) || !{bit('colour', e)}"
    for e, (u, v) in enumerate(E)])
emit_chunks(lines, "triangleFree", "(colour : BV210)", "colour", [
    f"!(({bit('colour', a)} && {bit('colour', b)} && {bit('colour', c)}) || "
    f"(!{bit('colour', a)} && !{bit('colour', b)} && !{bit('colour', c)}))"
    for a, b, c in T])

lines.append(r'''/-- Every 12-edge family in `K₈` with no three-edge matching
is contained in the 13-edge double star of some two-vertex core. -/
theorem matchingFree12_is_doubleStar (chosen : BV28)
    (hCard : popcount28 chosen = 12#5)
    (hMatching : matchingFree chosen = true) :
    containedInDoubleStar chosen = true := by
  bv_decide

/-- Every 11-edge family in `K₈` with no three-edge matching
is contained in the 13-edge double star of some two-vertex core. -/
theorem matchingFree11_is_doubleStar (chosen : BV28)
    (hCard : popcount28 chosen = 11#5)
    (hMatching : matchingFree chosen = true) :
    containedInDoubleStar chosen = true := by
  bv_decide

/-- No triangle-free red/blue colouring of `KG(8,2)` has a red-independent
12-set and a blue-independent 12-set, both contained in double stars. -/
theorem no_opposite_independent_doubleStars
    (A B : BV28) (colour : BV210)
    (hACard : popcount28 A = 12#5)
    (hBCard : popcount28 B = 12#5)
    (hAStar : containedInDoubleStar A = true)
    (hBStar : containedInDoubleStar B = true)
    (hABlue : blueOn A colour = true)
    (hBRed : redOn B colour = true)
    (hTriangles : triangleFree colour = true) : False := by
  bv_decide

/-- Combined finite certificate used by the original `5/2` proof. -/
theorem finite_kneser_obstruction
    (A B : BV28) (colour : BV210)
    (hACard : popcount28 A = 12#5)
    (hBCard : popcount28 B = 12#5)
    (hAMatching : matchingFree A = true)
    (hBMatching : matchingFree B = true)
    (hABlue : blueOn A colour = true)
    (hBRed : redOn B colour = true)
    (hTriangles : triangleFree colour = true) : False := by
  have hAStar := matchingFree12_is_doubleStar A hACard hAMatching
  have hBStar := matchingFree12_is_doubleStar B hBCard hBMatching
  exact no_opposite_independent_doubleStars A B colour
    hACard hBCard hAStar hBStar hABlue hBRed hTriangles

#print axioms matchingFree12_is_doubleStar
#print axioms matchingFree11_is_doubleStar
#print axioms no_opposite_independent_doubleStars
#print axioms finite_kneser_obstruction

end KneserCover
''')
text = "\n".join(lines)
out = Path(__file__).with_name("KneserCover.lean")
out.write_text(text)
sha = hashlib.sha256(text.encode()).hexdigest()
print(f"generated {out.name}: {len(text)} bytes; sha256={sha}")
