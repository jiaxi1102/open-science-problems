#!/usr/bin/env python3
"""Expose circuits and apply the S8/stabilizer symmetry reductions."""
from pathlib import Path

p = Path(__file__).with_name("KneserCover.lean")
s = p.read_text()

# Turn containment into a proposition so `simp only` can expose its disjunction.
start = s.index("def containedInDoubleStar")
end = s.index("\ndef blueOnChunk0", start)
core = s[start:end].replace(": Bool :=", ": Prop :=", 1)
core = core.replace(" == chosen", " = chosen").replace(" ||", " ∨")
s = s[:start] + core + s[end:]

matching_defs = (
    ["popcount28", "bitAsFive", "matchingFree"]
    + [f"matchingFreeChunk{i}" for i in range(18)]
    + ["containedInDoubleStar"]
)
for size, timeout in ((12, 180), (11, 300)):
    old = (
        f"    containedInDoubleStar chosen = true := by\n"
        f"  bv_decide"
    )
    new = (
        f"    containedInDoubleStar chosen := by\n"
        f"  simp only [{', '.join(matching_defs)}] at *\n"
        f"  bv_decide (config := {{ timeout := {timeout} }})"
    )
    if old not in s:
        raise RuntimeError(f"could not find generated size-{size} structure theorem")
    s = s.replace(old, new, 1)

# The original generated broad theorem is replaced by symmetry-reduced theorems.
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
unfold = ", ".join(defs)

# In lexicographic K8-edge order, the double star D_{01} is bits 0,...,12.
# Its 11-subsets have four orbits under the stabilizer of the unordered core:
#   8188: delete 01 and 02;
#   8185: delete 02 and 03;
#   8061: delete 02 and 12;
#   7933: delete 02 and 13.
assert 8191 - (1 << 0) - (1 << 1) == 8188
assert 8191 - (1 << 1) - (1 << 2) == 8185
assert 8191 - (1 << 1) - (1 << 7) == 8061
assert 8191 - (1 << 1) - (1 << 8) == 7933

s += f'''/-- After relabelling the first double-star core to `{{0,1}}`, no
triangle-free red/blue colouring has opposite 12-vertex independent sets.
The second core remains completely arbitrary. -/
theorem core01_obstruction
    (A B : BV28) (colour : BV210)
    (hACard : popcount28 A = 12#5)
    (hBCard : popcount28 B = 12#5)
    (hAStar : (A &&& 8191#28) = A)
    (hBStar : containedInDoubleStar B)
    (hABlue : blueOn A colour = true)
    (hBRed : redOn B colour = true)
    (hTriangles : triangleFree colour = true) : False := by
  simp only [{unfold}] at *
  bv_decide (config := {{ timeout := 600 }})

/-- Fixed first 11-set obtained from `D_{{01}}` by deleting its centre `01`
and the spoke `02`. -/
theorem alpha10_center_spoke_obstruction
    (B : BV28) (colour : BV210)
    (hBCard : popcount28 B = 11#5)
    (hBStar : containedInDoubleStar B)
    (hABlue : blueOn 8188#28 colour = true)
    (hBRed : redOn B colour = true)
    (hTriangles : triangleFree colour = true) : False := by
  simp only [{unfold}] at *
  bv_decide (config := {{ timeout := 900 }})

/-- Fixed first 11-set obtained from `D_{{01}}` by deleting two spokes at the
same centre, `02` and `03`. -/
theorem alpha10_same_center_obstruction
    (B : BV28) (colour : BV210)
    (hBCard : popcount28 B = 11#5)
    (hBStar : containedInDoubleStar B)
    (hABlue : blueOn 8185#28 colour = true)
    (hBRed : redOn B colour = true)
    (hTriangles : triangleFree colour = true) : False := by
  simp only [{unfold}] at *
  bv_decide (config := {{ timeout := 900 }})

/-- Fixed first 11-set obtained from `D_{{01}}` by deleting opposite spokes
with the same leaf, `02` and `12`. -/
theorem alpha10_same_leaf_obstruction
    (B : BV28) (colour : BV210)
    (hBCard : popcount28 B = 11#5)
    (hBStar : containedInDoubleStar B)
    (hABlue : blueOn 8061#28 colour = true)
    (hBRed : redOn B colour = true)
    (hTriangles : triangleFree colour = true) : False := by
  simp only [{unfold}] at *
  bv_decide (config := {{ timeout := 900 }})

/-- Fixed first 11-set obtained from `D_{{01}}` by deleting opposite spokes
with distinct leaves, `02` and `13`. -/
theorem alpha10_distinct_leaves_obstruction
    (B : BV28) (colour : BV210)
    (hBCard : popcount28 B = 11#5)
    (hBStar : containedInDoubleStar B)
    (hABlue : blueOn 7933#28 colour = true)
    (hBRed : redOn B colour = true)
    (hTriangles : triangleFree colour = true) : False := by
  simp only [{unfold}] at *
  bv_decide (config := {{ timeout := 900 }})

#print axioms matchingFree12_is_doubleStar
#print axioms matchingFree11_is_doubleStar
#print axioms core01_obstruction
#print axioms alpha10_center_spoke_obstruction
#print axioms alpha10_same_center_obstruction
#print axioms alpha10_same_leaf_obstruction
#print axioms alpha10_distinct_leaves_obstruction

end KneserCover
'''
p.write_text(s)
