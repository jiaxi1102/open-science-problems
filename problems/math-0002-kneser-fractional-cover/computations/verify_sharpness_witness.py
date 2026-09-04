#!/usr/bin/env python3
"""Independently verify the concrete sharpness coloring for math-0002."""
from itertools import combinations

VERTICES = list(combinations(range(8), 2))
EDGES = [
    (u, v)
    for u, v in combinations(range(28), 2)
    if set(VERTICES[u]).isdisjoint(VERTICES[v])
]
EDGE_ID = {edge: i for i, edge in enumerate(EDGES)}
TRIANGLES = []
for a, b, c in combinations(range(28), 3):
    if (
        set(VERTICES[a]).isdisjoint(VERTICES[b])
        and set(VERTICES[a]).isdisjoint(VERTICES[c])
        and set(VERTICES[b]).isdisjoint(VERTICES[c])
    ):
        TRIANGLES.append(
            (
                EDGE_ID[(a, b)],
                EDGE_ID[(a, c)],
                EDGE_ID[(b, c)],
            )
        )

BITS = (
    "111011101100010000110011010111000110011010111000001111111110000110011011101"
    "000001111110100110101010011001100111101110011110111111111110010110111111101"
    "101001010010000011001010100000111100110000000100111110000001"
)
COLOR = tuple(int(bit) for bit in BITS)

# These names describe independence in the color graph. A red-independent set
# has all of its induced Kneser edges blue, and conversely.
RED_INDEPENDENT_TEN = (4, 1, 2, 27, 5, 16, 11, 25, 20, 23)
BLUE_INDEPENDENT_TEN = (12, 18, 23, 27, 6, 14, 22, 24, 17, 26)

assert len(VERTICES) == 28
assert len(EDGES) == 210
assert len(TRIANGLES) == 420
assert len(COLOR) == 210
assert len(set(RED_INDEPENDENT_TEN)) == 10
assert len(set(BLUE_INDEPENDENT_TEN)) == 10


def induced_edge_ids(chosen: tuple[int, ...]) -> list[int]:
    result = []
    for u, v in combinations(sorted(chosen), 2):
        edge_id = EDGE_ID.get((u, v))
        if edge_id is not None:
            result.append(edge_id)
    return result


red_induced = induced_edge_ids(RED_INDEPENDENT_TEN)
blue_induced = induced_edge_ids(BLUE_INDEPENDENT_TEN)
assert red_induced and blue_induced
assert all(COLOR[e] == 1 for e in red_induced)
assert all(COLOR[e] == 0 for e in blue_induced)
assert all(0 < sum(COLOR[e] for e in triangle) < 3 for triangle in TRIANGLES)

print(
    "PASS sharpness_witness=PASS"
    f" vertices={len(VERTICES)}"
    f" kneser_edges={len(EDGES)}"
    f" triangles={len(TRIANGLES)}"
    f" red_independent_size={len(RED_INDEPENDENT_TEN)}"
    f" blue_independent_size={len(BLUE_INDEPENDENT_TEN)}"
    f" red_induced_edges={len(red_induced)}"
    f" blue_induced_edges={len(blue_induced)}"
)
