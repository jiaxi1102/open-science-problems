#!/usr/bin/env python3
"""Generate the Lean `bv_decide` certificate for the Conway Z7 quotient obstruction."""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path

N = 12
WING = {0, 1, 2, 9, 10, 11}
POS = {0, 1, 2}
NEG = {9, 10, 11}
PAIRS = [(i, j) for i in range(N) for j in range(i, N)]


def var(i: int, j: int) -> str:
    if i > j:
        i, j = j, i
    return f"x_{i}_{j}"


def wide(i: int, j: int) -> str:
    return f"w {var(i, j)}"


def add(terms: list[str]) -> str:
    return " + ".join(terms)


def target(i: int, j: int) -> int:
    if i == j:
        return 22 if i in WING else 24
    if (i in POS and j in POS) or (i in NEG and j in NEG):
        return 10
    if (i in POS and j in NEG) or (i in NEG and j in POS):
        return 14
    return 12


def generate() -> str:
    out: list[str] = [
        "import Std.Tactic.BVDecide",
        "",
        "/-!",
        "# Conway's 99-graph: direct bit-vector obstruction to an order-seven quotient",
        "",
        "This file checks the exact 12 × 12 integral system forced by an",
        "order-seven automorphism with one fixed vertex. The matrix is represented",
        "by its 78 upper-triangular entries, each a 3-bit unsigned integer (0..7).",
        "All arithmetic identities are evaluated in 10 bits; overflow is impossible:",
        "the largest quadratic sum is at most 12*7^2+7 = 595 < 2^10.",
        "",
        "Generated deterministically by `generate_lean.py`.",
        "-/",
        "",
        "namespace ConwayZ7",
        "",
        "private abbrev w (x : BitVec 3) : BitVec 10 := BitVec.zeroExtend 10 x",
        "",
        "set_option maxRecDepth 1000000 in",
        "set_option maxHeartbeats 0 in",
        "theorem noReducedOrbitMatrix",
    ]

    names = [var(i, j) for i, j in PAIRS]
    for k in range(0, len(names), 6):
        out.append(f"    ({' '.join(names[k:k+6])} : BitVec 3)")

    constraints: list[str] = []

    # An invariant simple graph on a 7-cycle has even internal valency.
    constraints.extend(f"({var(i, i)} &&& 1#3) = 0#3" for i in range(N))

    # X * 1 = 12 * 1.
    for i in range(N):
        constraints.append(f"({add([wide(i, k) for k in range(N)])}) = 12#10")

    # X * u = 0 for u=(1,1,1,0,...,0,-1,-1,-1).
    for i in range(N):
        left = add([wide(i, k) for k in range(3)])
        right = add([wide(i, k) for k in range(9, 12)])
        constraints.append(f"({left}) = ({right})")

    # X^2 + X = 12I + 12J - 2 u u^T.
    for i, j in PAIRS:
        products = [f"({wide(i, k)} * {wide(k, j)})" for k in range(N)]
        lhs = f"(({add(products)}) + {wide(i, j)})"
        constraints.append(f"{lhs} = {target(i, j)}#10")

    out.append("    : ¬ (")
    for index, constraint in enumerate(constraints):
        suffix = " ∧" if index + 1 < len(constraints) else ""
        out.append(f"      {constraint}{suffix}")
    out.extend([
        "    ) := by",
        "  bv_decide",
        "",
        "end ConwayZ7",
        "",
    ])
    return "\n".join(out)


def main() -> None:
    destination = Path(__file__).with_name("ConwayZ7.lean")
    source = generate()
    destination.write_text(source, encoding="utf-8")
    digest = sha256(source.encode("utf-8")).hexdigest()
    print(f"generated {destination.name}: sha256={digest}, bytes={len(source.encode('utf-8'))}")


if __name__ == "__main__":
    main()
