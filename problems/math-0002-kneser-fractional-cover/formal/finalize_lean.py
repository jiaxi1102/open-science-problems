#!/usr/bin/env python3
"""Expose generated Boolean circuits to `bv_decide`."""
from pathlib import Path

p = Path(__file__).with_name("KneserCover.lean")
s = p.read_text()
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
old1 = "    containedInDoubleStar chosen = true := by\n  bv_decide"
new1 = ("    containedInDoubleStar chosen = true := by\n"
        f"  simp only [{', '.join(matching)}] at *\n"
        "  bv_decide")
old2 = "    (hTriangles : triangleFree colour = true) : False := by\n  bv_decide"
new2 = ("    (hTriangles : triangleFree colour = true) : False := by\n"
        f"  simp only [{', '.join(obstruction)}] at *\n"
        "  bv_decide")
assert s.count(old1) == 1
assert s.count(old2) == 1
s = s.replace(old1, new1).replace(old2, new2)
p.write_text(s)
