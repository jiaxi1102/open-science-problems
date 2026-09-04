#!/usr/bin/env python3
"""Expose circuits and use S8-transitivity to fix the first double-star core.

The strengthened certificate works with 11-vertex independent sets.  This is
the threshold needed to rule out every two-cover whose two fractional
chromatic numbers are strictly below 14/5.
"""
from pathlib import Path

p = Path(__file__).with_name("KneserCover.lean")
s = p.read_text()

# Strengthen the matching-family classification generated in the base file.
s = s.replace("matchingFree12_is_doubleStar", "matchingFree11_is_doubleStar")
s = s.replace("Every 12-edge family", "Every 11-edge family")
s = s.replace("popcount28 chosen = 12#5", "popcount28 chosen = 11#5")

# Expose the double-star predicate as a proposition so its disjunction can be
# simplified before the bit-vector decision procedure is invoked.
start = s.index("def containedInDoubleStar")
end = s.index("\ndef blueOnChunk0", start)
core = s[start:end].replace(": Bool :=", ": Prop :=", 1)
core = core.replace(" == chosen", " = chosen").replace(" ||", " ∨")
s = s[:start] + core + s[end:]

matching = ["popcount28", "bitAsFive", "matchingFree"] + [
    f"matchingFreeChunk{i}" for i in range(18)
] + ["containedInDoubleStar"]
s = s.replace(
    "    containedInDoubleStar chosen = true := by\n  bv_decide",
    """    containedInDoubleStar chosen := by
  simp only [%s] at *
  bv_decide (config := { timeout := 300 })""" % ", ".join(matching),
)

# Replace the unsymmetrized generated obstruction by the transitivity-reduced
# statement.  The first double-star core is fixed to {0,1}; its 28-bit mask is
# 8191.  The selected 11-set A, the second core/set B, and all 210 edge colors
# remain universally quantified.
cut = s.index("/-- No triangle-free red/blue colouring")
s = s[:cut]
defs = (
    ["popcount28", "bitAsFive", "containedInDoubleStar", "blueOn"]
    + [f"blueOnChunk{i}" for i in range(9)]
    + ["redOn"]
    + [f"redOnChunk{i}" for i in range(9)]
    + ["triangleFree"]
    + [f"triangleFreeChunk{i}" for i in range(18)]
)
s += """/-- After relabelling the first double-star core to `{0,1}`, no
triangle-free red/blue colouring has opposite 11-vertex independent sets.
The second core remains completely arbitrary. -/
theorem core01_obstruction_11
    (A B : BV28) (colour : BV210)
    (hACard : popcount28 A = 11#5)
    (hBCard : popcount28 B = 11#5)
    (hAStar : (A &&& 8191#28) = A)
    (hBStar : containedInDoubleStar B)
    (hABlue : blueOn A colour = true)
    (hBRed : redOn B colour = true)
    (hTriangles : triangleFree colour = true) : False := by
  simp only [%s] at *
  bv_decide (config := { timeout := 1800 })

#print axioms matchingFree11_is_doubleStar
#print axioms core01_obstruction_11

end KneserCover
""" % ", ".join(defs)
p.write_text(s)
