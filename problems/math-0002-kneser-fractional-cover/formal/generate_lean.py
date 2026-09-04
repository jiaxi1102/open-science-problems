#!/usr/bin/env python3
"""Generate the explicit Lean 4 certificate for the KG(8,2) obstruction.

The target finite statement uses independent sets of size 11. Together with
chi_f(H) >= |V(H)| / alpha(H), this yields the lower bound 14/5 for every
two-graph fractional-chromatic cover of KG(8,2).
"""
from itertools import combinations
from pathlib import Path
import hashlib

TARGET_SIZE = 11
V = list(combinations(range(8), 2))
E = [
    (i, j)
    for i, j in combinations(range(28), 2)
    if set(V[i]).isdisjoint(V[j])
]
edge_id = {e: i for i, e in enumerate(E)}
MATCHINGS3 = [
    (a, b, c)
    for a, b, c in combinations(range(28), 3)
    if set(V[a]).isdisjoint(V[b])
    and set(V[a]).isdisjoint(V[c])
    and set(V[b]).isdisjoint(V[c])
]
TRIANGLES = [
    tuple(sorted((edge_id[(a, b)], edge_id[(a, c)], edge_id[(b, c)])))
    for a, b, c in MATCHINGS3
]
CORE_MASKS = []
for x, y in V:
    mask = sum(1 << i for i, e in enumerate(V) if x in e or y in e)
    assert mask.bit_count() == 13
    CORE_MASKS.append(mask)

assert (
    len(V),
    len(E),
    len(MATCHINGS3),
    len(TRIANGLES),
    len(set(TRIANGLES)),
    len(set(CORE_MASKS)),
    CORE_MASKS[0],
) == (28, 210, 420, 420, 420, 28, 8191)


def bit(x: str, i: int) -> str:
    return f"{x}.getLsbD {i}"


def chunks(xs: list[str], n: int = 24) -> list[list[str]]:
    return [xs[i : i + n] for i in range(0, len(xs), n)]


def emit_bool_chunks(
    lines: list[str], name: str, binders: str, application: str, clauses: list[str]
) -> list[str]:
    names = []
    for j, group in enumerate(chunks(clauses)):
        part = f"{name}Chunk{j}"
        names.append(part)
        lines.append(f"def {part} {binders} : Bool :=")
        for k, clause in enumerate(group):
            suffix = " &&" if k + 1 < len(group) else ""
            lines.append(f"  ({clause}){suffix}")
        lines.append("")
    lines.append(f"def {name} {binders} : Bool :=")
    for j, part in enumerate(names):
        suffix = " &&" if j + 1 < len(names) else ""
        lines.append(f"  {part} {application}{suffix}")
    lines.append("")
    return names


lines = [
    r'''import Std.Tactic.BVDecide

/-!
# Finite certificate for the fractional Kneser-cover obstruction

`KG(8,2)` has 28 vertices, represented by the edges of `K₈` in lexicographic
order. A 28-bit vector selects vertices. A 210-bit vector colors the edges of
`KG(8,2)`; `true` is blue and `false` is red.

The expensive finite claims are proved by `bv_decide`. It bit-blasts the
statements and reconstructs a checked proof. No external SAT or MILP output is
imported as an axiom.
-/

set_option maxRecDepth 1000000
set_option maxHeartbeats 0

namespace KneserCover

abbrev BV28 := BitVec 28
abbrev BV210 := BitVec 210

@[inline] def bitAsFive (b : Bool) : BitVec 5 :=
  if b then 1#5 else 0#5

def popcount28 (x : BV28) : BitVec 5 :=
'''
]
terms = [f"bitAsFive ({bit('x', i)})" for i in range(28)]
for i in range(0, 28, 4):
    suffix = " +" if i + 4 < 28 else ""
    lines.append("  " + " + ".join(terms[i : i + 4]) + suffix)
lines.append("")

matching_chunks = emit_bool_chunks(
    lines,
    "matchingFree",
    "(chosen : BV28)",
    "chosen",
    [
        f"!({bit('chosen', a)} && {bit('chosen', b)} && {bit('chosen', c)})"
        for a, b, c in MATCHINGS3
    ],
)

core_terms = [f"((chosen &&& {mask}#28) = chosen)" for mask in CORE_MASKS]
lines.append("def containedInDoubleStar (chosen : BV28) : Prop :=")
for i in range(0, 28, 4):
    suffix = " ∨" if i + 4 < 28 else ""
    lines.append("  " + " ∨ ".join(core_terms[i : i + 4]) + suffix)
lines.append("")

blue_chunks = emit_bool_chunks(
    lines,
    "blueOn",
    "(chosen : BV28) (colour : BV210)",
    "chosen colour",
    [
        f"!({bit('chosen', u)} && {bit('chosen', v)}) || {bit('colour', e)}"
        for e, (u, v) in enumerate(E)
    ],
)
red_chunks = emit_bool_chunks(
    lines,
    "redOn",
    "(chosen : BV28) (colour : BV210)",
    "chosen colour",
    [
        f"!({bit('chosen', u)} && {bit('chosen', v)}) || !{bit('colour', e)}"
        for e, (u, v) in enumerate(E)
    ],
)
triangle_chunks = emit_bool_chunks(
    lines,
    "triangleFree",
    "(colour : BV210)",
    "colour",
    [
        f"!(({bit('colour', a)} && {bit('colour', b)} && {bit('colour', c)}) || "
        f"(!{bit('colour', a)} && !{bit('colour', b)} && !{bit('colour', c)}))"
        for a, b, c in TRIANGLES
    ],
)

matching_defs = [
    "popcount28",
    "bitAsFive",
    "matchingFree",
    *matching_chunks,
    "containedInDoubleStar",
]
obstruction_defs = [
    "popcount28",
    "bitAsFive",
    "containedInDoubleStar",
    "blueOn",
    *blue_chunks,
    "redOn",
    *red_chunks,
    "triangleFree",
    *triangle_chunks,
]

lines.append(
    f'''/-- Every {TARGET_SIZE}-edge family in `K₈` with no three-edge matching
is contained in the 13-edge double star of some two-vertex core. -/
theorem matchingFree{TARGET_SIZE}_is_doubleStar (chosen : BV28)
    (hCard : popcount28 chosen = {TARGET_SIZE}#5)
    (hMatching : matchingFree chosen = true) :
    containedInDoubleStar chosen := by
  simp only [{", ".join(matching_defs)}] at *
  bv_decide (config := {{ timeout := 300 }})

/-- After relabelling the first double-star core to `{{0,1}}`, no
triangle-free red/blue colouring has opposite {TARGET_SIZE}-vertex independent
sets. The second core remains completely arbitrary. -/
theorem core01_obstruction_{TARGET_SIZE}
    (A B : BV28) (colour : BV210)
    (hACard : popcount28 A = {TARGET_SIZE}#5)
    (hBCard : popcount28 B = {TARGET_SIZE}#5)
    (hAStar : (A &&& {CORE_MASKS[0]}#28) = A)
    (hBStar : containedInDoubleStar B)
    (hABlue : blueOn A colour = true)
    (hBRed : redOn B colour = true)
    (hTriangles : triangleFree colour = true) : False := by
  simp only [{", ".join(obstruction_defs)}] at *
  bv_decide (config := {{ timeout := 1800 }})

#print axioms matchingFree{TARGET_SIZE}_is_doubleStar
#print axioms core01_obstruction_{TARGET_SIZE}

end KneserCover
'''
)

text = "\n".join(lines)
out = Path(__file__).with_name("KneserCover.lean")
out.write_text(text)
sha = hashlib.sha256(text.encode()).hexdigest()
print(f"generated {out.name}: {len(text)} bytes; sha256={sha}")
