#!/usr/bin/env python3
"""Verify one-point saturation of the five-point coloring of KG(11,3).

Adding a twelfth ground point x creates 55 new vertices x union P, one for
each pair P of old points. All new vertices intersect at x, so there are no
edges among them. Extending the coloring therefore decouples into 55 monotone
2-SAT instances. This script solves all of them, validates every positive
instance directly, and checks short signed odd-bicycle certificates for the
two negative symmetry classes.

No third-party package is used.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter
from typing import Sequence

from verify_kneser_five_point import trace_color, trace_of

Triple = tuple[int, int, int]
Pair = tuple[int, int]
Literal = tuple[int, bool]


def old_color(a: Triple, b: Triple) -> bool:
    """Color an old edge; True is red and False is blue."""
    assert set(a).isdisjoint(b)
    return trace_color(trace_of(a), trace_of(b))


def pair_class(pair: Pair) -> str:
    if pair[1] < 5:
        return "distinguished-distinguished"
    if pair[0] < 5:
        return "distinguished-anonymous"
    return "anonymous-anonymous"


def local_formula(pair: Pair) -> tuple[tuple[Triple, ...], tuple[tuple[Literal, Literal], ...]]:
    complement = tuple(point for point in range(11) if point not in pair)
    triples = tuple(itertools.combinations(complement, 3))
    clauses: list[tuple[Literal, Literal]] = []
    for i, a in enumerate(triples):
        a_set = set(a)
        for j in range(i + 1, len(triples)):
            b = triples[j]
            if a_set.isdisjoint(b):
                gamma = old_color(a, b)
                # Triangle (x union P), a, b cannot have all three edges gamma.
                clauses.append(((i, not gamma), (j, not gamma)))
    assert len(triples) == 84
    assert len(clauses) == 840
    return triples, tuple(clauses)


def node(variable: int, value: bool) -> int:
    return 2 * variable + int(value)


def scc_labels(variable_count: int, clauses: Sequence[tuple[Literal, Literal]]) -> list[int]:
    graph = [[] for _ in range(2 * variable_count)]
    reverse = [[] for _ in range(2 * variable_count)]
    for left, right in clauses:
        implications = (
            ((left[0], not left[1]), right),
            ((right[0], not right[1]), left),
        )
        for source, target in implications:
            u, v = node(*source), node(*target)
            graph[u].append(v)
            reverse[v].append(u)

    seen = [False] * len(graph)
    order: list[int] = []

    def first_pass(vertex: int) -> None:
        seen[vertex] = True
        for neighbor in graph[vertex]:
            if not seen[neighbor]:
                first_pass(neighbor)
        order.append(vertex)

    for vertex in range(len(graph)):
        if not seen[vertex]:
            first_pass(vertex)

    labels = [-1] * len(graph)

    def second_pass(vertex: int, label: int) -> None:
        labels[vertex] = label
        for neighbor in reverse[vertex]:
            if labels[neighbor] < 0:
                second_pass(neighbor, label)

    label = 0
    for vertex in reversed(order):
        if labels[vertex] < 0:
            second_pass(vertex, label)
            label += 1
    return labels


def solve_pair(pair: Pair) -> dict[str, object]:
    triples, clauses = local_formula(pair)
    labels = scc_labels(len(triples), clauses)
    contradictory = [
        i for i in range(len(triples))
        if labels[node(i, False)] == labels[node(i, True)]
    ]
    if contradictory:
        return {
            "pair": list(pair),
            "pair_class": pair_class(pair),
            "satisfiable": False,
            "contradictory_variables": len(contradictory),
        }

    assignment = tuple(
        labels[node(i, True)] > labels[node(i, False)]
        for i in range(len(triples))
    )
    for left, right in clauses:
        assert assignment[left[0]] == left[1] or assignment[right[0]] == right[1]

    # Recheck the original mathematical triangle condition rather than merely
    # rechecking the implication graph.
    checked = 0
    for i, a in enumerate(triples):
        a_set = set(a)
        for j in range(i + 1, len(triples)):
            b = triples[j]
            if not a_set.isdisjoint(b):
                continue
            colors = assignment[i], assignment[j], old_color(a, b)
            assert not (colors[0] == colors[1] == colors[2])
            checked += 1
    assert checked == 840

    bits = "".join("1" if value else "0" for value in assignment)
    return {
        "pair": list(pair),
        "pair_class": pair_class(pair),
        "satisfiable": True,
        "red_new_edges": sum(assignment),
        "blue_new_edges": len(assignment) - sum(assignment),
        "assignment_sha256": hashlib.sha256(bits.encode()).hexdigest(),
        "validated_original_triangles": checked,
    }


def verify_old_coloring() -> dict[str, object]:
    vertices = tuple(itertools.combinations(range(11), 3))
    vertex_id = {vertex: i for i, vertex in enumerate(vertices)}
    edge_counts = Counter()
    triangles = one_red = two_red = 0
    for i, a in enumerate(vertices):
        a_set = set(a)
        for j in range(i + 1, len(vertices)):
            b = vertices[j]
            if not a_set.isdisjoint(b):
                continue
            edge_counts[old_color(a, b)] += 1
            remaining = tuple(point for point in range(11) if point not in a_set | set(b))
            for c in itertools.combinations(remaining, 3):
                if vertex_id[c] <= j:
                    continue
                colors = old_color(a, b), old_color(a, c), old_color(b, c)
                assert not (colors[0] == colors[1] == colors[2])
                triangles += 1
                one_red += sum(colors) == 1
                two_red += sum(colors) == 2
    assert (len(vertices), sum(edge_counts.values())) == (165, 4620)
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


def forcing_path(pair: Pair, path: Sequence[Triple], initial: bool) -> dict[str, object]:
    assert path[0] == path[-1]
    current = initial
    steps = []
    for source, target in zip(path, path[1:]):
        assert set(source).isdisjoint(pair)
        assert set(target).isdisjoint(pair)
        assert set(source).isdisjoint(target)
        gamma = old_color(source, target)
        assert gamma == current
        forced = not current
        steps.append({
            "source": list(source),
            "target": list(target),
            "old_edge_color": "red" if gamma else "blue",
            "assumed_source_new_edge": "red" if current else "blue",
            "forced_target_new_edge": "red" if forced else "blue",
        })
        current = forced
    assert current == (not initial)
    return {
        "initial_new_edge_color": "red" if initial else "blue",
        "final_forced_color_on_same_edge": "red" if current else "blue",
        "path_length": len(path) - 1,
        "steps": steps,
    }


def bicycle_certificates() -> dict[str, object]:
    aa_pair = (5, 6)
    aa_base = (0, 1, 7)
    aa_red = (aa_base, (2, 8, 9), (3, 4, 10), aa_base)
    aa_blue = (
        aa_base, (3, 8, 9), (0, 1, 2), (4, 7, 8),
        (3, 9, 10), aa_base,
    )

    da_pair = (0, 5)
    da_base = (1, 6, 7)
    da_red = (
        da_base, (2, 8, 9), (3, 4, 6), (1, 2, 7),
        (8, 9, 10), da_base,
    )
    da_blue = (da_base, (2, 3, 8), (4, 9, 10), da_base)

    result = {
        "anonymous-anonymous": {
            "representative_pair": list(aa_pair),
            "base_triple": list(aa_base),
            "if_red": forcing_path(aa_pair, aa_red, True),
            "if_blue": forcing_path(aa_pair, aa_blue, False),
        },
        "distinguished-anonymous": {
            "representative_pair": list(da_pair),
            "base_triple": list(da_base),
            "if_red": forcing_path(da_pair, da_red, True),
            "if_blue": forcing_path(da_pair, da_blue, False),
        },
    }
    assert not solve_pair(aa_pair)["satisfiable"]
    assert not solve_pair(da_pair)["satisfiable"]
    return result


def permute(triple: Triple, permutation: Sequence[int]) -> Triple:
    image = tuple(sorted(permutation[x] for x in triple))
    assert len(image) == 3
    return image  # type: ignore[return-value]


def verify_symmetry() -> dict[str, object]:
    generators = {
        "five_cycle_rotation": tuple((x + 1) % 5 if x < 5 else x for x in range(11)),
        "five_cycle_reflection": tuple((-x) % 5 if x < 5 else x for x in range(11)),
        "anonymous_transposition": (0, 1, 2, 3, 4, 6, 5, 7, 8, 9, 10),
        "anonymous_six_cycle": (0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 5),
    }
    vertices = tuple(itertools.combinations(range(11), 3))
    checked = 0
    for permutation in generators.values():
        assert sorted(permutation) == list(range(11))
        for i, a in enumerate(vertices):
            a_set = set(a)
            for b in vertices[i + 1:]:
                if not a_set.isdisjoint(b):
                    continue
                assert old_color(a, b) == old_color(
                    permute(a, permutation), permute(b, permutation)
                )
                checked += 1
    assert checked == 4 * 4620
    return {
        "generators": list(generators),
        "generated_group": "D5 x S6",
        "edge_images_checked": checked,
        "color_invariant": True,
    }


def main() -> None:
    rows = [solve_pair(pair) for pair in itertools.combinations(range(11), 2)]
    counts = Counter((row["pair_class"], row["satisfiable"]) for row in rows)
    assert dict(counts) == {
        ("distinguished-distinguished", True): 10,
        ("distinguished-anonymous", False): 30,
        ("anonymous-anonymous", False): 15,
    }

    result = {
        "theorem": (
            "The explicit five-point coloring of KG(11,3) is one-point saturated: "
            "it cannot be extended to a good coloring of KG(12,3) while preserving old edges."
        ),
        "old_coloring": verify_old_coloring(),
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
        "status_table_sha256": hashlib.sha256(
            json.dumps(rows, separators=(",", ":"), sort_keys=True).encode()
        ).hexdigest(),
        "explicit_signed_odd_bicycles": bicycle_certificates(),
        "symmetry": verify_symmetry(),
        "global_one_point_extension_exists": False,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
