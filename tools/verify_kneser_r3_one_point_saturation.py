#!/usr/bin/env python3
"""Verify one-point saturation of the explicit five-point coloring of KG(11,3).

Adding a twelfth ground point x creates 55 new Kneser vertices x union P,
where P is a pair of old points. New vertices have no edges among themselves,
so extension decouples into 55 independent monotone 2-SAT instances. This
script solves every instance, validates every satisfiable assignment, and
checks explicit signed odd-bicycle certificates for the two unsatisfiable
symmetry classes.

No third-party package is used.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path
from typing import Iterable, Sequence

from verify_kneser_five_point import trace_color, trace_of


Triple = tuple[int, int, int]
Pair = tuple[int, int]
Literal = tuple[int, bool]


def old_edge_color(a: Triple, b: Triple) -> bool:
    """Color an old KG(11,3) edge; True is red and False is blue."""
    assert set(a).isdisjoint(b)
    return trace_color(trace_of(a), trace_of(b))


def pair_class(pair: Pair) -> str:
    if pair[1] < 5:
        return "distinguished-distinguished"
    if pair[0] < 5:
        return "distinguished-anonymous"
    return "anonymous-anonymous"


def literal_node(variable: int, value: bool) -> int:
    return 2 * variable + int(value)


def decode_node(node: int) -> Literal:
    return node // 2, bool(node % 2)


def local_instance(pair: Pair) -> tuple[tuple[Triple, ...], tuple[tuple[Literal, Literal], ...]]:
    complement = tuple(point for point in range(11) if point not in pair)
    triples = tuple(itertools.combinations(complement, 3))
    clauses: list[tuple[Literal, Literal]] = []
    for i, a in enumerate(triples):
        a_set = set(a)
        for j in range(i + 1, len(triples)):
            b = triples[j]
            if not a_set.isdisjoint(b):
                continue
            color = old_edge_color(a, b)
            # If the old edge AB has color gamma, triangle (x union P),A,B
            # forbids both new edges from also having color gamma.
            clauses.append(((i, not color), (j, not color)))
    assert len(triples) == 84
    assert len(clauses) == 840
    return triples, tuple(clauses)


def implication_graph(
    variable_count: int,
    clauses: Sequence[tuple[Literal, Literal]],
) -> tuple[list[list[int]], list[list[int]]]:
    graph = [[] for _ in range(2 * variable_count)]
    reverse = [[] for _ in range(2 * variable_count)]
    for left, right in clauses:
        implications = (
            ((left[0], not left[1]), right),
            ((right[0], not right[1]), left),
        )
        for source, target in implications:
            u = literal_node(*source)
            v = literal_node(*target)
            graph[u].append(v)
            reverse[v].append(u)
    return graph, reverse


def strongly_connected_components(
    graph: Sequence[Sequence[int]],
    reverse: Sequence[Sequence[int]],
) -> list[int]:
    seen = [False] * len(graph)
    order: list[int] = []

    def visit(node: int) -> None:
        seen[node] = True
        for neighbor in graph[node]:
            if not seen[neighbor]:
                visit(neighbor)
        order.append(node)

    for node in range(len(graph)):
        if not seen[node]:
            visit(node)

    component = [-1] * len(graph)

    def assign(node: int, label: int) -> None:
        component[node] = label
        for neighbor in reverse[node]:
            if component[neighbor] < 0:
                assign(neighbor, label)

    label = 0
    for node in reversed(order):
        if component[node] < 0:
            assign(node, label)
            label += 1
    return component


def solve_local_extension(pair: Pair) -> dict[str, object]:
    triples, clauses = local_instance(pair)
    graph, reverse = implication_graph(len(triples), clauses)
    component = strongly_connected_components(graph, reverse)

    contradictory = [
        index
        for index in range(len(triples))
        if component[literal_node(index, False)] == component[literal_node(index, True)]
    ]
    if contradictory:
        return {
            "pair": list(pair),
            "pair_class": pair_class(pair),
            "satisfiable": False,
            "contradictory_variables": len(contradictory),
        }

    assignment = tuple(
        component[literal_node(index, True)] > component[literal_node(index, False)]
        for index in range(len(triples))
    )
    for left, right in clauses:
        assert assignment[left[0]] == left[1] or assignment[right[0]] == right[1]

    # Directly recheck the original triangle condition, independently of the
    # implication graph construction.
    variable_id = {triple: index for index, triple in enumerate(triples)}
    triangles_checked = 0
    for i, a in enumerate(triples):
        a_set = set(a)
        for j in range(i + 1, len(triples)):
            b = triples[j]
            if not a_set.isdisjoint(b):
                continue
            colors = (assignment[i], assignment[j], old_edge_color(a, b))
            assert not (colors[0] == colors[1] == colors[2])
            assert variable_id[b] == j
            triangles_checked += 1
    assert triangles_checked == 840

    bits = "".join("1" if value else "0" for value in assignment)
    return {
        "pair": list(pair),
        "pair_class": pair_class(pair),
        "satisfiable": True,
        "red_new_edges": sum(assignment),
        "blue_new_edges": len(assignment) - sum(assignment),
        "assignment_sha256": hashlib.sha256(bits.encode()).hexdigest(),
        "validated_original_triangles": triangles_checked,
    }


def verify_old_coloring() -> dict[str, object]:
    vertices = tuple(itertools.combinations(range(11), 3))
    edge_counts = Counter()
    triangles = 0
    one_red = 0
    two_red = 0
    for i, a in enumerate(vertices):
        a_set = set(a)
        for j in range(i + 1, len(vertices)):
            b = vertices[j]
            if not a_set.isdisjoint(b):
                continue
            edge_counts[old_edge_color(a, b)] += 1
            used = a_set | set(b)
            for c in itertools.combinations(tuple(x for x in range(11) if x not in used), 3):
                h = vertices.index(c)
                if h <= j:
                    continue
                colors = (
                    old_edge_color(a, b),
                    old_edge_color(a, c),
                    old_edge_color(b, c),
                )
                assert not (colors[0] == colors[1] == colors[2])
                triangles += 1
                if sum(colors) == 1:
                    one_red += 1
                else:
                    two_red += 1
    assert len(vertices) == 165
    assert edge_counts[True] + edge_counts[False] == 4620
    assert (triangles, one_red, two_red) == (15400, 6850, 8550)
    return {
        "vertices": len(vertices),
        "red_edges": edge_counts[True],
        "blue_edges": edge_counts[False],
        "triangles": triangles,
        "triangles_with_one_red_edge": one_red,
        "triangles_with_two_red_edges": two_red,
        "monochromatic_triangles": 0,
    }


def verify_forcing_path(
    pair: Pair,
    path: Sequence[Triple],
    initial_color: bool,
) -> dict[str, object]:
    assert len(path) >= 2
    assert path[0] == path[-1]
    current = initial_color
    steps = []
    for source, target in zip(path, path[1:]):
        assert set(source).isdisjoint(target)
        assert set(source).isdisjoint(pair)
        assert set(target).isdisjoint(pair)
        edge_color = old_edge_color(source, target)
        # Assuming the new edge to source has the same color as the old
        # source-target edge, the triangle forces the new edge to target to
        # have the opposite color.
        assert edge_color == current
        next_color = not current
        steps.append(
            {
                "source": list(source),
                "target": list(target),
                "old_edge_color": "red" if edge_color else "blue",
                "assumed_source_new_edge": "red" if current else "blue",
                "forced_target_new_edge": "red" if next_color else "blue",
            }
        )
        current = next_color
    assert current == (not initial_color)
    return {
        "initial_new_edge_color": "red" if initial_color else "blue",
        "final_forced_color_on_same_edge": "red" if current else "blue",
        "path_length": len(path) - 1,
        "steps": steps,
    }


def explicit_bicycle_certificates() -> dict[str, object]:
    # Representative of the anonymous-anonymous pair orbit.
    anonymous_pair = (5, 6)
    anonymous_base = (0, 1, 7)
    anonymous_red_path = (
        anonymous_base,
        (2, 8, 9),
        (3, 4, 10),
        anonymous_base,
    )
    anonymous_blue_path = (
        anonymous_base,
        (3, 8, 9),
        (0, 1, 2),
        (4, 7, 8),
        (3, 9, 10),
        anonymous_base,
    )

    # Representative of the distinguished-anonymous pair orbit.
    mixed_pair = (0, 5)
    mixed_base = (1, 6, 7)
    mixed_red_path = (
        mixed_base,
        (2, 8, 9),
        (3, 4, 6),
        (1, 2, 7),
        (8, 9, 10),
        mixed_base,
    )
    mixed_blue_path = (
        mixed_base,
        (2, 3, 8),
        (4, 9, 10),
        mixed_base,
    )

    certificates = {
        "anonymous-anonymous": {
            "representative_pair": list(anonymous_pair),
            "base_triple": list(anonymous_base),
            "if_red": verify_forcing_path(anonymous_pair, anonymous_red_path, True),
            "if_blue": verify_forcing_path(anonymous_pair, anonymous_blue_path, False),
        },
        "distinguished-anonymous": {
            "representative_pair": list(mixed_pair),
            "base_triple": list(mixed_base),
            "if_red": verify_forcing_path(mixed_pair, mixed_red_path, True),
            "if_blue": verify_forcing_path(mixed_pair, mixed_blue_path, False),
        },
    }
    for certificate in certificates.values():
        assert certificate["if_red"]["final_forced_color_on_same_edge"] == "blue"
        assert certificate["if_blue"]["final_forced_color_on_same_edge"] == "red"
    return certificates


def apply_permutation(triple: Triple, permutation: Sequence[int]) -> Triple:
    return tuple(sorted(permutation[x] for x in triple))  # type: ignore[return-value]


def verify_symmetry_generators() -> dict[str, object]:
    generators = {
        "five_cycle_rotation": tuple((x + 1) % 5 if x < 5 else x for x in range(11)),
        "five_cycle_reflection": tuple((-x) % 5 if x < 5 else x for x in range(11)),
        "anonymous_transposition": (0, 1, 2, 3, 4, 6, 5, 7, 8, 9, 10),
        "anonymous_six_cycle": (0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 5),
    }
    vertices = tuple(itertools.combinations(range(11), 3))
    edges_checked = 0
    for permutation in generators.values():
        assert sorted(permutation) == list(range(11))
        for i, a in enumerate(vertices):
            a_set = set(a)
            for b in vertices[i + 1 :]:
                if not a_set.isdisjoint(b):
                    continue
                image_a = apply_permutation(a, permutation)
                image_b = apply_permutation(b, permutation)
                assert old_edge_color(a, b) == old_edge_color(image_a, image_b)
                edges_checked += 1
    assert edges_checked == 4 * 4620
    return {
        "generators": list(generators),
        "edge_images_checked": edges_checked,
        "generated_group": "D5 x S6",
        "color_invariant": True,
    }


def main() -> None:
    old = verify_old_coloring()
    rows = [solve_local_extension(pair) for pair in itertools.combinations(range(11), 2)]
    counts = Counter((row["pair_class"], row["satisfiable"]) for row in rows)

    expected_counts = {
        ("distinguished-distinguished", True): 10,
        ("distinguished-anonymous", False): 30,
        ("anonymous-anonymous", False): 15,
    }
    assert dict(counts) == expected_counts
    assert sum(bool(row["satisfiable"]) for row in rows) == 10
    assert sum(not bool(row["satisfiable"]) for row in rows) == 45

    status_digest = hashlib.sha256(
        json.dumps(rows, separators=(",", ":"), sort_keys=True).encode()
    ).hexdigest()

    result = {
        "theorem": (
            "The explicit five-point coloring of KG(11,3) is one-point saturated: "
            "it does not extend to a good coloring of KG(12,3) while preserving old edge colors."
        ),
        "old_coloring": old,
        "decoupling": {
            "new_ground_point": 11,
            "new_vertices": 55,
            "edges_between_new_vertices": 0,
            "local_variables_per_new_vertex": 84,
            "local_monotone_2sat_clauses_per_new_vertex": 840,
        },
        "local_extension_counts": {
            "satisfiable": 10,
            "unsatisfiable": 45,
            "distinguished-distinguished_satisfiable": 10,
            "distinguished-anonymous_unsatisfiable": 30,
            "anonymous-anonymous_unsatisfiable": 15,
        },
        "all_55_local_instances": rows,
        "status_table_sha256": status_digest,
        "explicit_signed_odd_bicycles": explicit_bicycle_certificates(),
        "symmetry": verify_symmetry_generators(),
        "global_one_point_extension_exists": False,
    }

    assert status_digest == "3fc5044c31c3338461a3d4118a1b2b564f872004636ca9f41ef66c777b3562c3"
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
