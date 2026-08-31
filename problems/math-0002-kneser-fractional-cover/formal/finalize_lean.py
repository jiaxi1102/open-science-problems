#!/usr/bin/env python3
"""Expose generated circuits to `bv_decide` using supported Prop equality."""
from pathlib import Path

p = Path(__file__).with_name("KneserCover.lean")
s = p.read_text()

# `bv_decide` supports propositional BitVec equality, not Boolean `BEq` atoms.
start = s.index("def containedInDoubleStar")
end = s.index("\ndef blueOnChunk0", start)
core = s[start:end]
core = core.replace(": Bool :=", ": Prop :=", 1)
core = core.replace(" == chosen", " = chosen")
core = core.replace(" ||", " ∨")
s = s[:start] + core + s[end:]
s = s.replace("    containedInDoubleStar chosen = true := by",
              "    containedInDoubleStar chosen := by")
s = s.replace("    (hAStar : containedInDoubleStar A = true)",
              "    (hAStar : containedInDoubleStar A)")
s = s.replace("    (hBStar : containedInDoubleStar B = true)",
              "    (hBStar : containedInDoubleStar B)")

matching = ["popcount28", "bitAsFive", "matchingFree"] + [
    f"matchingFreeChunk{i}" for i in range(18)
] + ["containedInDoubleStar"]
obstruction = ["popcount28", "bitAsFive", "containedInDoubleStar", "blueOn"] + [
    f"blueOnChunk{i}" for i in range(9)
] + ["redOn"] + [
    f"redOnChunk{i}" for i in range(9)
] + ["triangleFree"] + [
    f"triangleFreeChunk{i}" for i in range(18)
]
old1 = "    containedInDoubleStar chosen := by\n  bv_decide"
new1 = ("    containedInDoubleStar chosen := by\n"
        f"  simp only [{', '.join(matching)}] at *\n"
        "  bv_decide (config := { timeout := 120 })")
old2 = "    (hTriangles : triangleFree colour = true) : False := by\n  bv_decide"
new2 = ("    (hTriangles : triangleFree colour = true) : False := by\n"
        f"  simp only [{', '.join(obstruction)}] at *\n"
        "  bv_decide (config := { timeout := 300 })")
assert s.count(old1) == 1
assert s.count(old2) == 1
s = s.replace(old1, new1).replace(old2, new2)
p.write_text(s)
