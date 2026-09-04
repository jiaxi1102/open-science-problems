#!/usr/bin/env python3
"""Independent exhaustive search for iota(Q_6,Q_2)."""
from itertools import combinations


def hamming(a: int, b: int) -> int:
    return (a ^ b).bit_count()


def project(x: int, coords: tuple[int, ...]) -> int:
    return sum(((x >> c) & 1) << j for j, c in enumerate(coords))


COORDS4 = tuple(combinations(range(6), 4))
FULL16 = (1 << 16) - 1


def ball4(c: int) -> int:
    return sum(1 << x for x in range(16) if hamming(c, x) <= 1)


BALLS = tuple(ball4(c) for c in range(16))
MASKS = tuple(
    sum(BALLS[project(v, coords)] << (16 * j) for j, coords in enumerate(COORDS4))
    for v in range(64)
)
FULL240 = (1 << 240) - 1


def isolates(vertices: tuple[int, ...]) -> bool:
    mask = 0
    for v in vertices:
        mask |= MASKS[v]
    return mask == FULL240


def main() -> None:
    four = next((d for d in combinations(range(64), 4) if isolates(d)), None)
    five = next(d for d in combinations(range(64), 5) if isolates(d))
    assert four is None
    assert five == (0, 3, 5, 57, 62)
    print("No 4-vertex Q2-isolating set in Q6.")
    print("5-vertex witness:", tuple(f"{v:06b}" for v in five))


if __name__ == "__main__":
    main()
