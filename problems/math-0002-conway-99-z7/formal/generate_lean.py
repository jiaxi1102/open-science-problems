#!/usr/bin/env python3
"""Generate the 16 Lean SAT certificates for the Conway Z7 quotient obstruction."""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path

N = 12
POS = set(range(3))
MID = set(range(3, 9))
NEG = set(range(9, 12))
WING = POS | NEG
PAIRS = [(i, j) for i in range(N) for j in range(i, N)]
TRIPLES = [
    (p, m, n)
    for p in range(4)
    for m in range(7)
    for n in range(4)
    if p + m + n == 7
]
FIRST = {
    None: 0,
    (0, 4, 3): 9,
    (0, 5, 2): 9,
    (0, 6, 1): 9,
    (1, 3, 3): 0,
    (1, 4, 2): 0,
    (1, 5, 1): 0,
    (1, 6, 0): 0,
    (2, 2, 3): 0,
    (2, 3, 2): 0,
    (2, 4, 1): 9,
    (2, 5, 0): 0,
    (3, 1, 3): 3,
    (3, 2, 2): 9,
    (3, 3, 1): 9,
    (3, 4, 0): 0,
}


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


def diagonal(case: tuple[int, int, int] | None) -> list[int]:
    if case is None:
        return [0] * N
    p, m, n = case
    return [2] * p + [0] * (3 - p) + [2] * m + [0] * (6 - m) + [2] * n + [0] * (3 - n)


def theorem_name(case: tuple[int, int, int] | None) -> str:
    if case is None:
        return "noCanonicalCase_allZero"
    return f"noCanonicalCase_{case[0]}_{case[1]}_{case[2]}"


def stabilizer_classes(diag: list[int], fixed: int) -> list[list[int]]:
    result: list[list[int]] = []
    for group in (range(3), range(3, 9), range(9, 12)):
        for value in (0, 2):
            cls = [j for j in group if diag[j] == value and j != fixed]
            if len(cls) >= 2:
                result.append(cls)
    return result


def constraints(diag: list[int], fixed: int) -> list[str]:
    result: list[str] = []

    # The trace reduction leaves only diagonal 0, or seven diagonal 2s.
    for i, value in enumerate(diag):
        result.append(f"{var(i, i)} = {value}#3")

    # X * 1 = 12 * 1.
    for i in range(N):
        result.append(f"({add([wide(i, k) for k in range(N)])}) = 12#10")

    # X * u = 0 for u=(1,1,1,0,...,0,-1,-1,-1).
    for i in range(N):
        left = add([wide(i, k) for k in range(3)])
        right = add([wide(i, k) for k in range(9, 12)])
        result.append(f"({left}) = ({right})")

    # X^2 + X = 12I + 12J - 2 u u^T.
    for i, j in PAIRS:
        products = [f"({wide(i, k)} * {wide(k, j)})" for k in range(N)]
        result.append(
            f"(({add(products)}) + {wide(i, j)}) = {target(i, j)}#10"
        )

    # Canonicalize one row under permutations preserving the three groups and diag.
    for cls in stabilizer_classes(diag, fixed):
        for left, right in zip(cls, cls[1:]):
            result.append(f"{var(fixed, left)} ≤ {var(fixed, right)}")

    return result


def generate() -> str:
    output: list[str] = [
        "import Std.Tactic.BVDecide",
        "",
        "/-!",
        "# Conway's 99-graph: certified obstruction to order-seven symmetry",
        "",
        "Sixteen UNSAT theorems cover canonical representatives of all possible",
        "diagonal patterns of the reduced 12 × 12 orbit matrix. Entries are",
        "3-bit unsigned integers. Products and sums are evaluated in 10 bits;",
        "12*7^2+7 = 595 < 2^10, so modular wraparound cannot occur.",
        "",
        "The cases are: all diagonal entries zero, or exactly seven entries equal",
        "two, classified by their counts in the three invariant index blocks",
        "of sizes 3, 6, and 3. Within each diagonal class, a stabilizer permutation",
        "sorts one distinguished row; the inequalities impose that representative.",
        "",
        "Generated deterministically by `generate_lean.py`.",
        "-/",
        "",
        "namespace ConwayZ7",
        "",
        "private abbrev w (x : BitVec 3) : BitVec 10 := BitVec.zeroExtend 10 x",
        "",
    ]

    names = [var(i, j) for i, j in PAIRS]
    for case in [None, *TRIPLES]:
        diag = diagonal(case)
        output.extend(
            [
                "set_option maxRecDepth 1000000 in",
                "set_option maxHeartbeats 0 in",
                "set_option sat.timeout 300 in",
                f"theorem {theorem_name(case)}",
            ]
        )
        for start in range(0, len(names), 6):
            output.append(f"    ({' '.join(names[start:start + 6])} : BitVec 3)")

        case_constraints = constraints(diag, FIRST[case])
        output.append("    : ¬ (")
        for index, constraint in enumerate(case_constraints):
            suffix = " ∧" if index + 1 < len(case_constraints) else ""
            output.append(f"      {constraint}{suffix}")
        output.extend(["    ) := by", "  bv_decide", ""])

    output.extend(["end ConwayZ7", ""])
    return "\n".join(output)


def main() -> None:
    destination = Path(__file__).with_name("ConwayZ7.lean")
    source = generate()
    destination.write_text(source, encoding="utf-8")
    digest = sha256(source.encode("utf-8")).hexdigest()
    print(
        f"generated {destination.name}: sha256={digest}, "
        f"bytes={len(source.encode('utf-8'))}"
    )


if __name__ == "__main__":
    main()
