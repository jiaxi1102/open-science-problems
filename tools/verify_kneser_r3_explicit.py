#!/usr/bin/env python3
"""Deterministically verify the explicit 6+5 coloring of KG(11,3)."""
from __future__ import annotations

import hashlib
import itertools
import json

X = frozenset(range(6))
Y0 = 6
YMOD = 5


def weight(a: tuple[int, ...]) -> int:
    return sum(x in X for x in a)


def y_coords(a: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(x - Y0 for x in a if x >= Y0)


def colour(a: tuple[int, ...], b: tuple[int, ...]) -> bool:
    """Return True for red and False for blue."""
    wa, wb = weight(a), weight(b)

    if wa != 2 and wb != 2:
        return (wa <= 1 and wb <= 1) or (wa == 3 and wb == 3)

    if wa == 2 and wb == 2:
        ya, yb = y_coords(a)[0], y_coords(b)[0]
        return (yb - ya) % YMOD in {1, YMOD - 1}

    central, other = (a, b) if wa == 2 else (b, a)
    wo = weight(other)
    if wo == 3:
        return True
    y = y_coords(central)[0]
    predecessor = Y0 + ((y - 1) % YMOD)
    return predecessor in other


def main() -> None:
    vertices = list(itertools.combinations(range(11), 3))
    edges: list[tuple[int, int]] = []
    edge_colours: list[bool] = []
    edge_id: dict[tuple[int, int], int] = {}

    for i, a in enumerate(vertices):
        A = set(a)
        for j in range(i + 1, len(vertices)):
            b = vertices[j]
            if A.isdisjoint(b):
                edge_id[(i, j)] = len(edges)
                edges.append((i, j))
                edge_colours.append(colour(a, b))

    raw = bytearray((len(edges) + 7) // 8)
    for i, red in enumerate(edge_colours):
        if red:
            raw[i // 8] |= 1 << (i % 8)

    triangles = 0
    weight_patterns: dict[str, int] = {}
    colour_patterns: dict[str, int] = {}
    for i, a in enumerate(vertices):
        A = set(a)
        for j in range(i + 1, len(vertices)):
            b = vertices[j]
            if not A.isdisjoint(b):
                continue
            AB = A | set(b)
            for h in range(j + 1, len(vertices)):
                c = vertices[h]
                if not AB.isdisjoint(c):
                    continue
                triangles += 1
                e1 = edge_colours[edge_id[(i, j)]]
                e2 = edge_colours[edge_id[(i, h)]]
                e3 = edge_colours[edge_id[(j, h)]]
                assert not (e1 == e2 == e3), (a, b, c, e1)
                wp = str(tuple(sorted((weight(a), weight(b), weight(c)))))
                cp = str(tuple(sorted((int(e1), int(e2), int(e3)))))
                weight_patterns[wp] = weight_patterns.get(wp, 0) + 1
                key = f"{wp}:{cp}"
                colour_patterns[key] = colour_patterns.get(key, 0) + 1

    result = {
        "vertices": len(vertices),
        "edges": len(edges),
        "red_edges": sum(edge_colours),
        "blue_edges": len(edges) - sum(edge_colours),
        "triangles": triangles,
        "monochromatic_triangles": 0,
        "edge_colour_bitset_sha256": hashlib.sha256(raw).hexdigest(),
        "weight_patterns": dict(sorted(weight_patterns.items())),
        "colour_patterns": dict(sorted(colour_patterns.items())),
    }

    assert result["vertices"] == 165
    assert result["edges"] == 4620
    assert result["triangles"] == 15400
    assert result["edge_colour_bitset_sha256"] == (
        "e32129b5e64783311ab3443e3e3e492887bcb8025b9efaf4cd9182c7f113788b"
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
