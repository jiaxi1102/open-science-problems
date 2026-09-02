#!/usr/bin/env python3
"""Generate and validate the exact one-apex reduction for KG(12,3).

A good coloring of KG(12,3), restricted to the triples avoiding point 11 and
to the single vertex {0,1,11}, would color the graph consisting of KG(11,3)
plus one apex adjacent to the 84 triples of {2,...,10}. Conversely, a coloring
of that one-apex graph is precisely a good KG(11,3) coloring admitting that
one new vertex. Thus UNSAT of this much smaller graph proves
R_3^KG(3,3) = 12.

The two seed cases are exhaustive up to permutations of the nine complement
points and a global color swap: on one fixed K4 containing the apex, the red
edges are either a matching or a path with the apex as an endpoint.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import re
from pathlib import Path
from typing import Iterator, Sequence

from kneser_exact_cnf import (
    K4_EDGE_PAIRS,
    K4_PRIME_FOUR_TEMPLATES,
    K4_STAR_INDEX_TRIPLES,
)

Triple = tuple[int, int, int]
Clause = tuple[int, ...]

OLD_N = 11
K = 3
FIXED_PAIR = (0, 1)
COMPLEMENT = tuple(range(2, 11))
SEED_BLOCKS = ((2, 3, 4), (5, 6, 7), (8, 9, 10))


def partitions_into_triples(items: tuple[int, ...]) -> Iterator[tuple[Triple, Triple, Triple]]:
    assert len(items) == 9
    first_point = items[0]
    for first_tail in itertools.combinations(items[1:], 2):
        first = tuple(sorted((first_point,) + first_tail))
        remaining1 = tuple(point for point in items if point not in first)
        second_point = remaining1[0]
        for second_tail in itertools.combinations(remaining1[1:], 2):
            second = tuple(sorted((second_point,) + second_tail))
            third = tuple(point for point in remaining1 if point not in second)
            yield first, second, third  # type: ignore[misc]


def build_graph() -> dict[str, object]:
    vertices = tuple(itertools.combinations(range(OLD_N), K))
    vertex_id = {vertex: index for index, vertex in enumerate(vertices)}

    old_edges: list[tuple[int, int]] = []
    old_edge_id: dict[tuple[int, int], int] = {}
    for i, left in enumerate(vertices):
        left_set = set(left)
        for j in range(i + 1, len(vertices)):
            if left_set.isdisjoint(vertices[j]):
                old_edge_id[(i, j)] = len(old_edges) + 1
                old_edges.append((i, j))
    assert len(old_edges) == 4620

    neighbors = tuple(itertools.combinations(COMPLEMENT, K))
    apex_edge_id: dict[Triple, int] = {
        triple: len(old_edges) + index + 1
        for index, triple in enumerate(neighbors)
    }
    assert len(neighbors) == 84

    old_triangles: list[tuple[int, int, int]] = []
    for i, a in enumerate(vertices):
        a_set = set(a)
        for j in range(i + 1, len(vertices)):
            b = vertices[j]
            if not a_set.isdisjoint(b):
                continue
            remaining = tuple(point for point in range(OLD_N) if point not in a_set | set(b))
            for c in itertools.combinations(remaining, K):
                h = vertex_id[c]
                if h <= j:
                    continue
                old_triangles.append((
                    old_edge_id[(i, j)],
                    old_edge_id[tuple(sorted((i, h)))],
                    old_edge_id[tuple(sorted((j, h)))],
                ))
    assert len(old_triangles) == 15400

    apex_triangles: list[tuple[int, int, int]] = []
    for i, left in enumerate(neighbors):
        left_set = set(left)
        for right in neighbors[i + 1:]:
            if not left_set.isdisjoint(right):
                continue
            u, v = sorted((vertex_id[left], vertex_id[right]))
            apex_triangles.append((
                apex_edge_id[left],
                apex_edge_id[right],
                old_edge_id[(u, v)],
            ))
    assert len(apex_triangles) == 840

    return {
        "vertices": vertices,
        "vertex_id": vertex_id,
        "old_edges": tuple(old_edges),
        "old_edge_id": old_edge_id,
        "neighbors": neighbors,
        "apex_edge_id": apex_edge_id,
        "old_triangles": tuple(old_triangles),
        "apex_triangles": tuple(apex_triangles),
    }


def k4_variables(
    graph: dict[str, object],
    blocks: Sequence[Triple],
) -> tuple[int, ...]:
    vertex_id = graph["vertex_id"]
    old_edge_id = graph["old_edge_id"]
    apex_edge_id = graph["apex_edge_id"]
    assert isinstance(vertex_id, dict)
    assert isinstance(old_edge_id, dict)
    assert isinstance(apex_edge_id, dict)
    block_ids = [vertex_id[block] for block in blocks]

    # K4 vertices are numbered apex=0, block0=1, block1=2, block2=3.
    variables = []
    for left, right in K4_EDGE_PAIRS:
        if left == 0:
            variables.append(apex_edge_id[blocks[right - 1]])
        else:
            u, v = sorted((block_ids[left - 1], block_ids[right - 1]))
            variables.append(old_edge_id[(u, v)])
    return tuple(variables)


def seed_units(graph: dict[str, object], seed: str) -> tuple[int, ...]:
    variables = k4_variables(graph, SEED_BLOCKS)
    if seed == "matching":
        red_pairs = {(0, 1), (2, 3)}
    elif seed == "path":
        red_pairs = {(0, 1), (1, 2), (2, 3)}
    else:
        raise ValueError(seed)
    return tuple(
        variable if pair in red_pairs else -variable
        for pair, variable in zip(K4_EDGE_PAIRS, variables)
    )


def exclude_pattern(variables: Sequence[int], values: Sequence[int]) -> Clause:
    return tuple(variable if value == 0 else -variable for variable, value in zip(variables, values))


def iter_clauses(graph: dict[str, object], seed: str, closure: str) -> Iterator[Clause]:
    old_triangles = graph["old_triangles"]
    apex_triangles = graph["apex_triangles"]
    assert isinstance(old_triangles, tuple)
    assert isinstance(apex_triangles, tuple)

    for triangle in old_triangles + apex_triangles:
        yield triangle
        yield tuple(-literal for literal in triangle)

    if closure == "prime":
        for blocks in partitions_into_triples(COMPLEMENT):
            variables = k4_variables(graph, blocks)
            for indices in K4_STAR_INDEX_TRIPLES:
                selected = tuple(variables[index] for index in indices)
                yield selected
                yield tuple(-variable for variable in selected)
            for indices, values in K4_PRIME_FOUR_TEMPLATES:
                selected = tuple(variables[index] for index in indices)
                yield exclude_pattern(selected, values)
    elif closure != "none":
        raise ValueError(closure)

    yield from ((unit,) for unit in seed_units(graph, seed))


def write_cnf(path: Path, metadata_path: Path, seed: str, closure: str) -> None:
    graph = build_graph()
    clauses = tuple(iter_clauses(graph, seed, closure))
    variable_count = len(graph["old_edges"]) + len(graph["neighbors"])
    digest = hashlib.sha256()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as handle:
        header = f"p cnf {variable_count} {len(clauses)}\n".encode()
        handle.write(header)
        digest.update(header)
        for clause in clauses:
            line = (" ".join(map(str, clause)) + " 0\n").encode()
            handle.write(line)
            digest.update(line)

    metadata = {
        "mathematical_graph": "KG(11,3) plus the vertex {0,1,11}",
        "seed_type": seed,
        "closure": closure,
        "old_vertices": len(graph["vertices"]),
        "old_edge_variables": len(graph["old_edges"]),
        "apex_edge_variables": len(graph["neighbors"]),
        "total_variables": variable_count,
        "old_triangles": len(graph["old_triangles"]),
        "apex_triangles": len(graph["apex_triangles"]),
        "core_nae_clauses": 2 * (len(graph["old_triangles"]) + len(graph["apex_triangles"])),
        "apex_k4_partitions": 280 if closure == "prime" else 0,
        "derived_prime_clauses": 20 * 280 if closure == "prime" else 0,
        "seed_units": list(seed_units(graph, seed)),
        "total_clauses": len(clauses),
        "dimacs_sha256": digest.hexdigest(),
    }
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    print(json.dumps(metadata, indent=2, sort_keys=True))


def parse_model(path: Path) -> tuple[str | None, dict[int, bool]]:
    status = None
    assignment: dict[int, bool] = {}
    for raw_line in path.read_text(errors="replace").splitlines():
        line = raw_line.strip()
        upper = line.upper()
        if "UNSATISFIABLE" in upper:
            status = "UNSATISFIABLE"
        elif "SATISFIABLE" in upper:
            status = "SATISFIABLE"
        if not line or not re.match(r"^[vV]\s+|^-?\d", line):
            continue
        if line[0] in "vV":
            line = line[1:].strip()
        for token in line.split():
            try:
                literal = int(token)
            except ValueError:
                continue
            if literal:
                assignment[abs(literal)] = literal > 0
    return status, assignment


def validate_model(model_path: Path, out_path: Path, seed: str) -> None:
    graph = build_graph()
    status, assignment = parse_model(model_path)
    variable_count = len(graph["old_edges"]) + len(graph["neighbors"])
    if status != "SATISFIABLE":
        raise ValueError(f"model status is {status!r}")
    missing = [variable for variable in range(1, variable_count + 1) if variable not in assignment]
    if missing:
        raise ValueError(f"missing original variables: {missing[:20]}")

    for unit in seed_units(graph, seed):
        assert assignment[abs(unit)] == (unit > 0)

    checked = 0
    for triangle in graph["old_triangles"] + graph["apex_triangles"]:
        colors = tuple(assignment[variable] for variable in triangle)
        if colors[0] == colors[1] == colors[2]:
            raise ValueError(f"monochromatic triangle {triangle}")
        checked += 1
    assert checked == 16240

    bits = "".join("1" if assignment[index] else "0" for index in range(1, variable_count + 1))
    result = {
        "solver_status": status,
        "seed_type": seed,
        "variables_checked": variable_count,
        "triangles_checked": checked,
        "red_edges": bits.count("1"),
        "blue_edges": bits.count("0"),
        "model_bits_sha256": hashlib.sha256(bits.encode()).hexdigest(),
        "valid_good_one_apex_coloring": True,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate = subparsers.add_parser("generate")
    generate.add_argument("--seed", choices=("matching", "path"), required=True)
    generate.add_argument("--closure", choices=("none", "prime"), default="prime")
    generate.add_argument("--cnf", type=Path, required=True)
    generate.add_argument("--metadata", type=Path, required=True)

    check = subparsers.add_parser("check")
    check.add_argument("--seed", choices=("matching", "path"), required=True)
    check.add_argument("--model", type=Path, required=True)
    check.add_argument("--out", type=Path, required=True)

    args = parser.parse_args()
    if args.command == "generate":
        write_cnf(args.cnf, args.metadata, args.seed, args.closure)
    else:
        validate_model(args.model, args.out, args.seed)


if __name__ == "__main__":
    main()
