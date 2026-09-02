#!/usr/bin/env python3
"""Verify the universal five-point coloring for Kneser triangles.

The theorem reduces every triangle in KG(3r+2,r) to three pairwise-disjoint
traces in a fixed five-point set whose union misses at most two points.  This
script exhausts all 4^5 assignments of those points to the three traces or to
the unused set.  It also reconstructs KG(3r+2,r) directly for r=1,...,4 as a
regression test.

No SAT solver or third-party package is used.
"""
from __future__ import annotations

import hashlib
import itertools
import json


def trace_color(a: int, b: int) -> bool:
    """Return True for red, False for blue, for disjoint 5-bit traces."""
    assert a & b == 0
    pa, pb = a.bit_count(), b.bit_count()
    a_single, b_single = pa == 1, pb == 1

    # Empty/large rule when neither endpoint is a singleton.
    if not a_single and not b_single:
        return (pa == 0) == (pb == 0)

    # The unique triangle-free two-coloring of K5 on singleton traces:
    # cycle edges red, diagonals blue.
    if a_single and b_single:
        y = a.bit_length() - 1
        z = b.bit_length() - 1
        return (z - y) % 5 in (1, 4)

    singleton = a if a_single else b
    other = b if a_single else a
    y = singleton.bit_length() - 1

    # Singleton/empty edges are red.
    if other == 0:
        return True

    # Singleton/large: red iff the large trace contains the predecessor.
    return bool(other & (1 << ((y - 1) % 5)))


def mask(points) -> int:
    value = 0
    for p in points:
        value |= 1 << p
    return value


def verify_trace_gadget() -> dict:
    checked = 0
    color_counts = {1: 0, 2: 0}
    trace_size_patterns: dict[str, int] = {}

    # Labels 0,1,2 are the three traces; label 3 is unused.
    for labels in itertools.product(range(4), repeat=5):
        bins = [[], [], [], []]
        for point, label in enumerate(labels):
            bins[label].append(point)
        a, b, c, unused = map(mask, bins)
        if unused.bit_count() > 2:
            continue

        checked += 1
        colors = (trace_color(a, b), trace_color(a, c), trace_color(b, c))
        assert not (colors[0] == colors[1] == colors[2]), (
            labels, a, b, c, unused, colors
        )
        red_count = sum(colors)
        assert red_count in (1, 2)
        color_counts[red_count] += 1

        pattern = str(tuple(sorted((a.bit_count(), b.bit_count(), c.bit_count()))))
        trace_size_patterns[pattern] = trace_size_patterns.get(pattern, 0) + 1

    assert checked == 918

    ordered_table = [
        (a, b, int(trace_color(a, b)))
        for a in range(32)
        for b in range(32)
        if a & b == 0
    ]
    table_hash = hashlib.sha256(
        json.dumps(ordered_table, separators=(",", ":")).encode()
    ).hexdigest()
    assert len(ordered_table) == 243
    assert table_hash == "8426231092c6081026c57f6ed1b48eaf1f766233fc4fe1191cea39d1e0a44faa"

    return {
        "ordered_disjoint_trace_pairs": len(ordered_table),
        "ordered_trace_color_table_sha256": table_hash,
        "trace_partitions_checked": checked,
        "trace_partitions_with_one_red_edge": color_counts[1],
        "trace_partitions_with_two_red_edges": color_counts[2],
        "monochromatic_trace_triangles": 0,
        "trace_size_patterns": dict(sorted(trace_size_patterns.items())),
    }


def complement_tuple(n: int, used) -> tuple[int, ...]:
    taken = set(used)
    return tuple(x for x in range(n) if x not in taken)


def trace_of(vertex: tuple[int, ...]) -> int:
    return mask(x for x in vertex if x < 5)


def verify_actual_kneser(r: int) -> dict:
    n = 3 * r + 2
    vertices = list(itertools.combinations(range(n), r))
    vertex_id = {a: i for i, a in enumerate(vertices)}
    traces = [trace_of(a) for a in vertices]

    edges: list[tuple[int, int]] = []
    edge_id: dict[tuple[int, int], int] = {}
    edge_colors: list[bool] = []
    for i, a in enumerate(vertices):
        for b in itertools.combinations(complement_tuple(n, a), r):
            j = vertex_id[b]
            if j <= i:
                continue
            edge_id[(i, j)] = len(edges)
            edges.append((i, j))
            edge_colors.append(trace_color(traces[i], traces[j]))

    triangles = 0
    one_red = 0
    two_red = 0
    for i, a in enumerate(vertices):
        rem_a = complement_tuple(n, a)
        for b in itertools.combinations(rem_a, r):
            j = vertex_id[b]
            if j <= i:
                continue
            rem_ab = complement_tuple(n, a + b)
            for c in itertools.combinations(rem_ab, r):
                h = vertex_id[c]
                if h <= j:
                    continue
                colors = (
                    edge_colors[edge_id[(i, j)]],
                    edge_colors[edge_id[(i, h)]],
                    edge_colors[edge_id[(j, h)]],
                )
                assert not (colors[0] == colors[1] == colors[2]), (
                    r, a, b, c, colors
                )
                triangles += 1
                if sum(colors) == 1:
                    one_red += 1
                else:
                    two_red += 1

    return {
        "r": r,
        "n": n,
        "vertices": len(vertices),
        "edges": len(edges),
        "triangles": triangles,
        "triangles_with_one_red_edge": one_red,
        "triangles_with_two_red_edges": two_red,
        "monochromatic_triangles": 0,
    }


def main() -> None:
    result = {
        "theorem": "R_r^KG(3,3) >= 3r+3 for every r >= 1",
        "finite_trace_gadget": verify_trace_gadget(),
        "actual_kneser_regressions": [verify_actual_kneser(r) for r in range(1, 5)],
    }

    expected = [
        (1, 5, 10, 10),
        (2, 28, 210, 420),
        (3, 165, 4620, 15400),
        (4, 1001, 105105, 525525),
    ]
    observed = [
        (row["r"], row["vertices"], row["edges"], row["triangles"])
        for row in result["actual_kneser_regressions"]
    ]
    assert observed == expected
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
