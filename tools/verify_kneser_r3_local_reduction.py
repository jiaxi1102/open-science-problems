#!/usr/bin/env python3
"""Verify the finite identities behind the KG(12,3) local-star reduction."""

from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter


def partitions(items: tuple[int, ...], block_size: int) -> set[tuple[tuple[int, ...], ...]]:
    result: set[tuple[tuple[int, ...], ...]] = set()
    first = items[0]
    for rest in itertools.combinations(items[1:], block_size - 1):
        block = tuple(sorted((first,) + rest))
        remaining = tuple(x for x in items if x not in block)
        if not remaining:
            result.add((block,))
            continue
        for suffix in partitions(remaining, block_size):
            result.add(tuple(sorted((block,) + suffix)))
    return result


def k4_good_colorings() -> dict[str, object]:
    edges = ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))
    edge_id = {edge: index for index, edge in enumerate(edges)}
    triangles = tuple(itertools.combinations(range(4), 3))

    def triangle_colors(bits: tuple[int, ...], tri: tuple[int, int, int]) -> tuple[int, ...]:
        return tuple(bits[edge_id[tuple(sorted(pair))]] for pair in itertools.combinations(tri, 2))

    def star_colors(bits: tuple[int, ...], vertex: int) -> tuple[int, ...]:
        return tuple(bits[edge_id[tuple(sorted((vertex, other)))]] for other in range(4) if other != vertex)

    good = []
    star_good = []
    type_counts: Counter[str] = Counter()
    for bits in itertools.product((0, 1), repeat=6):
        triangle_condition = all(len(set(triangle_colors(bits, tri))) == 2 for tri in triangles)
        star_condition = all(len(set(star_colors(bits, vertex))) == 2 for vertex in range(4))
        if triangle_condition:
            good.append(bits)
            red_edges = sum(bits)
            if red_edges in (2, 4):
                type_counts["matching"] += 1
            elif red_edges == 3:
                red_degree_sequence = sorted(
                    sum(bits[edge_id[tuple(sorted((v, w)))]] for w in range(4) if w != v)
                    for v in range(4)
                )
                assert red_degree_sequence == [1, 1, 2, 2]
                type_counts["path"] += 1
            else:
                raise AssertionError(bits)
        if star_condition:
            star_good.append(bits)
        assert triangle_condition == star_condition

    encoded = "\n".join("".join(map(str, bits)) for bits in sorted(good)) + "\n"
    return {
        "all_edge_colorings": 64,
        "good_colorings": len(good),
        "star_condition_colorings": len(star_good),
        "triangle_iff_star_condition": good == star_good,
        "labeled_type_counts": dict(sorted(type_counts.items())),
        "good_table_sha256": hashlib.sha256(encoded.encode()).hexdigest(),
    }


def kg9_triangle_decomposition() -> dict[str, object]:
    points = tuple(range(9))
    triples = tuple(itertools.combinations(points, 3))
    triple_id = {triple: index for index, triple in enumerate(triples)}
    edges = []
    edge_id = {}
    for i, a in enumerate(triples):
        a_set = set(a)
        for j in range(i + 1, len(triples)):
            if a_set.isdisjoint(triples[j]):
                edge_id[(i, j)] = len(edges)
                edges.append((i, j))

    partition_set = partitions(points, 3)
    assert len(partition_set) == 280
    edge_multiplicity: Counter[int] = Counter()
    triangle_rows = []
    for partition in sorted(partition_set):
        ids = sorted(triple_id[block] for block in partition)
        triangle_edges = []
        for a, b in itertools.combinations(ids, 2):
            eid = edge_id[tuple(sorted((a, b)))]
            edge_multiplicity[eid] += 1
            triangle_edges.append(eid)
        triangle_rows.append(tuple(sorted(triangle_edges)))

    assert len(edges) == 840
    assert len(edge_multiplicity) == len(edges)
    assert set(edge_multiplicity.values()) == {1}

    encoded = "\n".join(
        ",".join(map(str, row)) for row in sorted(triangle_rows)
    ) + "\n"
    return {
        "vertices": len(triples),
        "edges": len(edges),
        "partition_triangles": len(partition_set),
        "each_edge_in_exactly_one_triangle": True,
        "universal_cut_upper_bound": 2 * len(partition_set),
        "triangle_decomposition_sha256": hashlib.sha256(encoded.encode()).hexdigest(),
    }


def kg12_counts() -> dict[str, object]:
    points = tuple(range(12))
    triples = tuple(itertools.combinations(points, 3))
    edges = []
    for i, a in enumerate(triples):
        a_set = set(a)
        for j in range(i + 1, len(triples)):
            if a_set.isdisjoint(triples[j]):
                edges.append((i, j))

    four_partitions = partitions(points, 3)
    assert len(four_partitions) == 15400
    triangles = 4 * len(four_partitions)
    assert triangles == 61600

    return {
        "vertices": len(triples),
        "edges": len(edges),
        "four_triple_partitions": len(four_partitions),
        "triangles": triangles,
        "nae_clauses": 2 * triangles,
        "local_stars": len(triples),
        "local_vertices_per_star": 84,
        "local_partition_constraints_per_star": 280,
    }


def main() -> None:
    result = {
        "k4_equivalence": k4_good_colorings(),
        "kg9_neighborhood": kg9_triangle_decomposition(),
        "kg12_global": kg12_counts(),
        "structural_statement": (
            "A coloring of KG(12,3) is triangle-Ramsey-good iff every vertex star "
            "properly 2-colors the perfect-matching hypergraph on its 9-point complement."
        ),
    }
    assert result["k4_equivalence"]["triangle_iff_star_condition"]
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
