#!/usr/bin/env python3
"""Generate kernel-checked finite orbit certificates for the Kneser cover proof."""
from itertools import combinations
from pathlib import Path

V = list(combinations(range(8), 2))
E = [(i, j) for i, j in combinations(range(28), 2)
     if set(V[i]).isdisjoint(V[j])]
CASES = [
    ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], [0, 1, 2, 3, 4, 5, 6, 13, 14, 15, 16, 17]),
    ([0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], [0, 1, 2, 3, 4, 5, 6, 13, 14, 15, 16, 17]),
    ([0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], [0, 1, 2, 3, 4, 5, 6, 13, 18, 19, 20, 21]),
    ([0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], [1, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]),
    ([0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], [0, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]),
    ([0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], [0, 1, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]),
    ([0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], [0, 1, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17]),
    ([0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], [0, 1, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17]),
    ([0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], [0, 7, 8, 9, 10, 11, 12, 13, 18, 19, 20, 21]),
    ([0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], [1, 7, 8, 13, 14, 15, 16, 17, 18, 19, 20, 21]),
    ([0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], [1, 2, 8, 13, 14, 15, 16, 17, 18, 19, 20, 21]),
]

p = Path(__file__).with_name("KneserCover.lean")
s = p.read_text()
start = s.index("def containedInDoubleStar")
end = s.index("\ndef blueOnChunk0", start)
core = s[start:end].replace(": Bool :=", ": Prop :=", 1)
core = core.replace(" == chosen", " = chosen").replace(" ||", " ∨")
s = s[:start] + core + s[end:]
matching_defs = ["popcount28", "bitAsFive", "matchingFree"] + [
    f"matchingFreeChunk{i}" for i in range(18)
] + ["containedInDoubleStar"]
s = s.replace(
    "    containedInDoubleStar chosen = true := by\n  bv_decide",
    "    containedInDoubleStar chosen := by\n"
    f"  simp only [{', '.join(matching_defs)}] at *\n"
    "  bv_decide (config := { timeout := 120 })",
)
cut = s.index("/-- No triangle-free red/blue colouring")
s = s[:cut]
parts = [s]
for ci, (a_list, b_list) in enumerate(CASES):
    A, B = set(a_list), set(b_list)
    lits = []
    for ei, (u, v) in enumerate(E):
        if u in A and v in A:
            lits.append(f"colour.getLsbD {ei}")
        if u in B and v in B:
            lits.append(f"!colour.getLsbD {ei}")
    assert len(lits) in (50, 55)
    names = []
    for offset in range(0, len(lits), 20):
        name = f"case{ci}ForcedChunk{offset // 20}"
        names.append(name)
        parts.append(f"def {name} (colour : BV210) : Bool :=\n")
        group = lits[offset:offset + 20]
        for k, lit in enumerate(group):
            parts.append("  " + lit + (" &&\n" if k + 1 < len(group) else "\n"))
        parts.append("\n")
    parts.append(f"def case{ci}Forced (colour : BV210) : Bool :=\n")
    for k, name in enumerate(names):
        parts.append(f"  {name} colour" + (" &&\n" if k + 1 < len(names) else "\n\n"))
    defs = [f"case{ci}Forced"] + names + ["triangleFree"] + [
        f"triangleFreeChunk{i}" for i in range(18)
    ]
    parts.append(f"/-- Symmetry representative {ci}: no NAE colouring extends its forced crowns. -/\n")
    parts.append(f"theorem orbitCase{ci}_impossible (colour : BV210)\n")
    parts.append(f"    (hForced : case{ci}Forced colour = true)\n")
    parts.append("    (hTriangles : triangleFree colour = true) : False := by\n")
    parts.append(f"  simp only [{', '.join(defs)}] at *\n")
    parts.append("  bv_decide (config := { timeout := 120 })\n\n")
parts.append("#print axioms matchingFree12_is_doubleStar\n")
for ci in range(len(CASES)):
    parts.append(f"#print axioms orbitCase{ci}_impossible\n")
parts.append("\nend KneserCover\n")
p.write_text("".join(parts))
