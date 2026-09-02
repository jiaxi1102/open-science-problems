#!/usr/bin/env python3
"""Scan cyclic subgroups of S_n for symmetric good colorings of KG(n,k).

For each conjugacy class (cycle type) of a nonidentity ground-set
permutation, quotient the Kneser-edge variables by the cyclic group it
generates, then solve the exact no-monochromatic-triangle CNF.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import time
from pathlib import Path

from pysat.solvers import Cadical195


def integer_partitions(n: int, maximum: int | None = None):
    if n == 0:
        yield ()
        return
    if maximum is None or maximum > n:
        maximum = n
    for first in range(maximum, 0, -1):
        for tail in integer_partitions(n - first, first):
            yield (first,) + tail


def representative_permutation(cycle_type: tuple[int, ...]) -> tuple[int, ...]:
    perm: list[int] = []
    offset = 0
    for length in cycle_type:
        cycle = list(range(offset, offset + length))
        if length == 1:
            perm.append(offset)
        else:
            for j in range(length):
                perm.append(cycle[(j + 1) % length])
        offset += length
    return tuple(perm)


def permute_set(a: tuple[int, ...], perm: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(sorted(perm[x] for x in a))


def build_instance(n: int, k: int):
    vertices = list(itertools.combinations(range(n), k))
    vertex_id = {a: i for i, a in enumerate(vertices)}
    edges: list[tuple[int, int]] = []
    edge_id: dict[tuple[int, int], int] = {}
    for i, a in enumerate(vertices):
        aa = set(a)
        for j in range(i + 1, len(vertices)):
            if aa.isdisjoint(vertices[j]):
                edge_id[(i, j)] = len(edges)
                edges.append((i, j))

    triangles: list[tuple[int, int, int]] = []
    for i, a in enumerate(vertices):
        aa = set(a)
        for j in range(i + 1, len(vertices)):
            b = vertices[j]
            if not aa.isdisjoint(b):
                continue
            used = aa | set(b)
            for h in range(j + 1, len(vertices)):
                if used.isdisjoint(vertices[h]):
                    triangles.append(
                        (edge_id[(i, j)], edge_id[(i, h)], edge_id[(j, h)])
                    )
    return vertices, vertex_id, edges, edge_id, triangles


def edge_orbits(
    vertices,
    vertex_id,
    edges,
    edge_id,
    perm: tuple[int, ...],
):
    edge_map: list[int] = []
    for i, j in edges:
        pi = vertex_id[permute_set(vertices[i], perm)]
        pj = vertex_id[permute_set(vertices[j], perm)]
        if pi > pj:
            pi, pj = pj, pi
        edge_map.append(edge_id[(pi, pj)])

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
            cur = edge_map[cur]
    return orbit, representatives


def solve_cycle_type(instance, cycle_type: tuple[int, ...]):
    vertices, vertex_id, edges, edge_id, triangles = instance
    perm = representative_permutation(cycle_type)
    orbit, representatives = edge_orbits(vertices, vertex_id, edges, edge_id, perm)

    clauses: set[tuple[int, ...]] = set()
    immediate_unsat = False
    for a, b, c in triangles:
        x, y, z = orbit[a] + 1, orbit[b] + 1, orbit[c] + 1
        pos = tuple(sorted((x, y, z)))
        neg = tuple(sorted((-x, -y, -z)))
        clauses.add(pos)
        clauses.add(neg)
        if x == y == z:
            immediate_unsat = True

    order = math.lcm(*cycle_type)
    started = time.time()
    if immediate_unsat:
        sat = False
        model = None
    else:
        cnf = [list(c) for c in clauses]
        if representatives:
            cnf.append([1])  # quotient by global color swap
        with Cadical195(bootstrap_with=cnf) as solver:
            sat = solver.solve()
            model = solver.get_model() if sat else None
    elapsed = time.time() - started

    result = {
        "cycle_type": list(cycle_type),
        "group_order": order,
        "edge_orbits": len(representatives),
        "unique_triangle_clauses": len(clauses),
        "immediate_unsat": immediate_unsat,
        "satisfiable": bool(sat),
        "elapsed_seconds": elapsed,
    }
    if sat and model is not None:
        assignment = {
            abs(lit): lit > 0
            for lit in model
            if abs(lit) <= len(representatives)
        }
        result["red_orbit_representatives"] = [
            [list(vertices[edges[e][0]]), list(vertices[edges[e][1]])]
            for oid, e in enumerate(representatives)
            if assignment.get(oid + 1, False)
        ]
        # Independent validation on every actual Kneser triangle.
        for a, b, c in triangles:
            colors = (
                assignment[orbit[a] + 1],
                assignment[orbit[b] + 1],
                assignment[orbit[c] + 1],
            )
            assert not (colors[0] == colors[1] == colors[2])
        result["validated_all_triangles"] = True
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument("--k", type=int, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    instance = build_instance(args.n, args.k)
    vertices, _, edges, _, triangles = instance
    types = [p for p in integer_partitions(args.n) if p != (1,) * args.n]
    types.sort(key=lambda p: (-math.lcm(*p), len(p), p), reverse=False)

    results = []
    for cycle_type in types:
        row = solve_cycle_type(instance, cycle_type)
        results.append(row)
        print(
            json.dumps(
                {k: v for k, v in row.items() if k != "red_orbit_representatives"},
                sort_keys=True,
            ),
            flush=True,
        )

    sat_rows = [r for r in results if r["satisfiable"]]
    summary = {
        "n": args.n,
        "k": args.k,
        "vertices": len(vertices),
        "edges": len(edges),
        "triangles": len(triangles),
        "cycle_types_tested": len(results),
        "satisfiable_cycle_types": len(sat_rows),
        "maximum_symmetric_group_order": max(
            (r["group_order"] for r in sat_rows), default=1
        ),
        "results": results,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {k: v for k, v in summary.items() if k != "results"}, indent=2
        )
    )


if __name__ == "__main__":
    main()
