#!/usr/bin/env python3
"""Solve the no-monochromatic-triangle problem in one cyclic symmetry class.

The ground-set permutation is specified by its cycle lengths.  Kneser-edge
variables are quotiented by the cyclic subgroup it generates before the SAT
instance is built.  Triangle generation uses complements rather than a cubic
scan, so cases such as KG(15,4) remain practical.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import time
from pathlib import Path

from pysat.solvers import Cadical195


def parse_cycle_type(text: str, n: int) -> tuple[int, ...]:
    parts = tuple(int(x) for x in text.split(",") if x)
    if not parts or any(x <= 0 for x in parts) or sum(parts) != n:
        raise ValueError(f"cycle type must be positive and sum to n={n}: {text}")
    return parts


def representative_permutation(cycle_type: tuple[int, ...]) -> tuple[int, ...]:
    perm: list[int] = []
    offset = 0
    for length in cycle_type:
        for j in range(length):
            perm.append(offset + ((j + 1) % length))
        offset += length
    return tuple(perm)


def permute_set(a: tuple[int, ...], perm: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(sorted(perm[x] for x in a))


def complement_tuple(n: int, used) -> tuple[int, ...]:
    taken = set(used)
    return tuple(x for x in range(n) if x not in taken)


def build_vertices_edges(n: int, k: int):
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
    return vertices, vertex_id, edges, edge_id


def build_edge_orbits(vertices, vertex_id, edges, edge_id, perm):
    image: list[int] = []
    for i, j in edges:
        pi = vertex_id[permute_set(vertices[i], perm)]
        pj = vertex_id[permute_set(vertices[j], perm)]
        if pi > pj:
            pi, pj = pj, pi
        image.append(edge_id[(pi, pj)])

    orbit = [-1] * len(edges)
    representatives: list[int] = []
    for start in range(len(edges)):
        if orbit[start] >= 0:
            continue
        oid = len(representatives)
        representatives.append(start)
        cur = start
        while orbit[cur] < 0:
            orbit[cur] = oid
            cur = image[cur]
    return orbit, representatives


def triangle_indices(n, k, vertices, vertex_id, edge_id):
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
                yield edge_id[(i, j)], edge_id[(i, h)], edge_id[(j, h)]


def solve(n: int, k: int, cycle_type: tuple[int, ...], out: Path) -> None:
    started = time.time()
    vertices, vertex_id, edges, edge_id = build_vertices_edges(n, k)
    perm = representative_permutation(cycle_type)
    orbit, representatives = build_edge_orbits(
        vertices, vertex_id, edges, edge_id, perm
    )
    built_orbits = time.time()

    clauses: set[tuple[int, ...]] = set()
    triangle_count = 0
    immediate_unsat = False
    for a, b, c in triangle_indices(n, k, vertices, vertex_id, edge_id):
        triangle_count += 1
        x, y, z = orbit[a] + 1, orbit[b] + 1, orbit[c] + 1
        if x == y == z:
            immediate_unsat = True
        clauses.add(tuple(sorted((x, y, z))))
        clauses.add(tuple(sorted((-x, -y, -z))))
    built_cnf = time.time()

    if immediate_unsat:
        sat = False
        model = None
    else:
        cnf = [list(c) for c in clauses]
        if representatives:
            cnf.append([1])
        with Cadical195(bootstrap_with=cnf) as solver:
            sat = solver.solve()
            model = solver.get_model() if sat else None
    solved = time.time()

    result = {
        "n": n,
        "k": k,
        "cycle_type": list(cycle_type),
        "group_order": math.lcm(*cycle_type),
        "vertices": len(vertices),
        "edges": len(edges),
        "edge_orbits": len(representatives),
        "triangles": triangle_count,
        "unique_triangle_clauses": len(clauses),
        "immediate_unsat": immediate_unsat,
        "satisfiable": bool(sat),
        "orbit_build_seconds": built_orbits - started,
        "cnf_build_seconds": built_cnf - built_orbits,
        "solve_seconds": solved - built_cnf,
        "elapsed_seconds": solved - started,
    }

    if sat and model is not None:
        assignment = {
            abs(lit): lit > 0
            for lit in model
            if abs(lit) <= len(representatives)
        }
        raw = bytearray((len(representatives) + 7) // 8)
        for i in range(1, len(representatives) + 1):
            if assignment.get(i, False):
                raw[(i - 1) // 8] |= 1 << ((i - 1) % 8)
        result["orbit_assignment_hex"] = raw.hex()
        result["orbit_assignment_sha256"] = hashlib.sha256(raw).hexdigest()
        result["red_orbit_representatives"] = [
            [list(vertices[edges[e][0]]), list(vertices[edges[e][1]])]
            for oid, e in enumerate(representatives)
            if assignment.get(oid + 1, False)
        ]
        for a, b, c in triangle_indices(n, k, vertices, vertex_id, edge_id):
            vals = (
                assignment[orbit[a] + 1],
                assignment[orbit[b] + 1],
                assignment[orbit[c] + 1],
            )
            assert not (vals[0] == vals[1] == vals[2])
        result["validated_all_triangles"] = True

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in {
        "orbit_assignment_hex", "red_orbit_representatives"
    }}, indent=2, sort_keys=True), flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument("--k", type=int, required=True)
    parser.add_argument("--cycle-type", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    solve(args.n, args.k, parse_cycle_type(args.cycle_type, args.n), args.out)


if __name__ == "__main__":
    main()
