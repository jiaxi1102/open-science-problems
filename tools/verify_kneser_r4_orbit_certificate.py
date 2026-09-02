#!/usr/bin/env python3
"""Verify the compact (8)(6)-symmetric coloring certificate for KG(14,4)."""
from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

CERTIFICATE = Path(__file__).parents[1] / (
    "experiments/kneser_ramsey/certificates/kg14_r4_8x6.json"
)


def complement_tuple(n: int, used) -> tuple[int, ...]:
    taken = set(used)
    return tuple(x for x in range(n) if x not in taken)


def permute_set(a: tuple[int, ...], p: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(sorted(p[x] for x in a))


def main() -> None:
    cert = json.loads(CERTIFICATE.read_text())
    n, k = cert["n"], cert["k"]
    assert (n, k, cert["cycle_type"]) == (14, 4, [8, 6])

    vertices = list(itertools.combinations(range(n), k))
    vertex_id = {a: i for i, a in enumerate(vertices)}
    edges: list[tuple[int, int]] = []
    edge_id: dict[tuple[int, int], int] = {}
    for i, a in enumerate(vertices):
        for b in itertools.combinations(complement_tuple(n, a), k):
            j = vertex_id[b]
            if j <= i:
                continue
            edge_id[(i, j)] = len(edges)
            edges.append((i, j))

    # Generator (0 1 ... 7)(8 9 ... 13), of order lcm(8,6)=24.
    permutation = tuple([1, 2, 3, 4, 5, 6, 7, 0, 9, 10, 11, 12, 13, 8])
    edge_image: list[int] = []
    for i, j in edges:
        pi = vertex_id[permute_set(vertices[i], permutation)]
        pj = vertex_id[permute_set(vertices[j], permutation)]
        if pi > pj:
            pi, pj = pj, pi
        edge_image.append(edge_id[(pi, pj)])

    orbit = [-1] * len(edges)
    representatives: list[int] = []
    for start in range(len(edges)):
        if orbit[start] >= 0:
            continue
        oid = len(representatives)
        representatives.append(start)
        current = start
        while orbit[current] < 0:
            orbit[current] = oid
            current = edge_image[current]

    assert len(representatives) == cert["edge_orbits"] == 4475

    raw = bytes.fromhex(cert["orbit_assignment_hex"])
    assert hashlib.sha256(raw).hexdigest() == cert["orbit_assignment_sha256"]

    def red_orbit(oid: int) -> bool:
        return bool(raw[oid // 8] & (1 << (oid % 8)))

    assert sum(red_orbit(i) for i in range(len(representatives))) == cert["red_edge_orbits"]
    edge_colours = [red_orbit(orbit[e]) for e in range(len(edges))]

    triangles = 0
    one_red = 0
    two_red = 0
    for i, a in enumerate(vertices):
        rem_a = complement_tuple(n, a)
        for b in itertools.combinations(rem_a, k):
            j = vertex_id[b]
            if j <= i:
                continue
            rem_ab = complement_tuple(n, a + b)
            for c in itertools.combinations(rem_ab, k):
                h = vertex_id[c]
                if h <= j:
                    continue
                colours = (
                    edge_colours[edge_id[(i, j)]],
                    edge_colours[edge_id[(i, h)]],
                    edge_colours[edge_id[(j, h)]],
                )
                assert not (colours[0] == colours[1] == colours[2]), (
                    a, b, c, colours
                )
                triangles += 1
                red_count = sum(colours)
                if red_count == 1:
                    one_red += 1
                elif red_count == 2:
                    two_red += 1
                else:
                    raise AssertionError((a, b, c, colours))

    result = {
        "vertices": len(vertices),
        "edges": len(edges),
        "edge_orbits": len(representatives),
        "red_edge_orbits": cert["red_edge_orbits"],
        "red_edges": sum(edge_colours),
        "blue_edges": len(edges) - sum(edge_colours),
        "triangles": triangles,
        "triangles_with_one_red_edge": one_red,
        "triangles_with_two_red_edges": two_red,
        "monochromatic_triangles": 0,
        "orbit_assignment_sha256": cert["orbit_assignment_sha256"],
    }

    assert result == {
        "vertices": 1001,
        "edges": 105105,
        "edge_orbits": 4475,
        "red_edge_orbits": 2237,
        "red_edges": 52062,
        "blue_edges": 53043,
        "triangles": 525525,
        "triangles_with_one_red_edge": 270120,
        "triangles_with_two_red_edges": 255405,
        "monochromatic_triangles": 0,
        "orbit_assignment_sha256": (
            "057d4833da5e4aef547ff836ff8591428c3e00fd52f0041caa046cf986a9bf79"
        ),
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
