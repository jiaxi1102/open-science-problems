#!/usr/bin/env python3
"""Expose circuits and split the hard finite theorem by the 28 double-star cores."""
from pathlib import Path

p = Path(__file__).with_name("KneserCover.lean")
s = p.read_text()
start = s.index("def containedInDoubleStar")
end = s.index("\ndef blueOnChunk0", start)
core = s[start:end].replace(": Bool :=", ": Prop :=", 1)
core = core.replace(" == chosen", " = chosen").replace(" ||", " ∨")
s = s[:start] + core + s[end:]
s = s.replace(
    "    containedInDoubleStar chosen = true := by\n  bv_decide",
    """    containedInDoubleStar chosen := by
  simp only [popcount28, bitAsFive, matchingFree, matchingFreeChunk0,
    matchingFreeChunk1, matchingFreeChunk2, matchingFreeChunk3,
    matchingFreeChunk4, matchingFreeChunk5, matchingFreeChunk6,
    matchingFreeChunk7, matchingFreeChunk8, matchingFreeChunk9,
    matchingFreeChunk10, matchingFreeChunk11, matchingFreeChunk12,
    matchingFreeChunk13, matchingFreeChunk14, matchingFreeChunk15,
    matchingFreeChunk16, matchingFreeChunk17, containedInDoubleStar] at *
  bv_decide (config := { timeout := 120 })""",
)
s = s.replace(
    "    (hAStar : containedInDoubleStar A = true)",
    "    (hAStar : containedInDoubleStar A)",
)
s = s.replace(
    "    (hBStar : containedInDoubleStar B = true)",
    "    (hBStar : containedInDoubleStar B)",
)
old = """    (hTriangles : triangleFree colour = true) : False := by
  bv_decide"""
branches = " | ".join(f"hA{i}" for i in range(28))
defs = ["popcount28", "bitAsFive", "blueOn"] + [
    f"blueOnChunk{i}" for i in range(9)
] + ["redOn"] + [
    f"redOnChunk{i}" for i in range(9)
] + ["triangleFree"] + [
    f"triangleFreeChunk{i}" for i in range(18)
]
new = f"""    (hTriangles : triangleFree colour = true) : False := by
  simp only [containedInDoubleStar] at hAStar hBStar
  rcases hAStar with {branches}
  all_goals
    simp only [{', '.join(defs)}] at *
    bv_decide (config := {{ timeout := 120 }})"""
assert s.count(old) == 1
s = s.replace(old, new)
p.write_text(s)
