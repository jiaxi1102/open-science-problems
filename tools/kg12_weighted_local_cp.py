#!/usr/bin/env python3
"""Search zero-sum local-weight colorings of KG(12,3) with CP-SAT.

For every Kneser vertex A, assign integer weights to the nine points outside A,
with total zero. The edge A--B is red exactly when the three weights on B have
positive sum. This automatically gives a valid two-coloring of the perfect
matchings in the nine-point neighborhood of A. Shared edge colors enforce
agreement between the local representations at A and B, while the original
61,600 triangle NAE constraints enforce the global Ramsey condition.

A SAT model is independently expanded and checked against all edges and
triangles, so it is decisive for the unrestricted problem. An INFEASIBLE
result only excludes the chosen bounded-weight ansatz.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Iterable

from ortools.sat.python import cp_model

N = 12
R = 3


def stable_hash(value: object) -> str:
    payload = json.dumps(value, separators=(",", ":"), sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()


def base_graph():
    vertices = list(itertools.combinations(range(N), R))
    vertex_id = {vertex: i for i, vertex in enumerate(vertices)}
    edges: list[tuple[int, int]] = []
    edge_id: dict[tuple[int, int], int] = {}
    for i, a in enumerate(vertices):
        a_set = set(a)
        for j in range(i + 1, len(vertices)):
            if a_set.isdisjoint(vertices[j]):
                edge_id[(i, j)] = len(edges)
                edges.append((i, j))

    triangles: list[tuple[int, int, int]] = []
    for i, a in enumerate(vertices):
        remaining_a = tuple(x for x in range(N) if x not in a)
        for b in itertools.combinations(remaining_a, R):
            j = vertex_id[b]
            if j <= i:
                continue
            used_ab = set(a) | set(b)
            remaining_ab = tuple(x for x in range(N) if x not in used_ab)
            for c in itertools.combinations(remaining_ab, R):
                k = vertex_id[c]
                if k <= j:
                    continue
                triangles.append(
                    (edge_id[(i, j)], edge_id[(i, k)], edge_id[(j, k)])
                )
    assert (len(vertices), len(edges), len(triangles)) == (220, 9240, 61600)
    return vertices, vertex_id, edges, edge_id, triangles


def canonical_colors(
    branch: str,
    vertex_id: dict[tuple[int, ...], int],
    edge_id: dict[tuple[int, int], int],
) -> dict[int, bool]:
    blocks = [
        vertex_id[(0, 1, 2)],
        vertex_id[(3, 4, 5)],
        vertex_id[(6, 7, 8)],
        vertex_id[(9, 10, 11)],
    ]
    names = ("AB", "AC", "AD", "BC", "BD", "CD")
    pairs = ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))
    named_edges = {
        name: edge_id[tuple(sorted((blocks[i], blocks[j])))]
        for name, (i, j) in zip(names, pairs)
    }
    if branch == "matching":
        red = {"AB", "CD"}
    elif branch == "path":
        red = {"AB", "BD", "CD"}
    elif branch == "triangle":
        named_edges = {name: named_edges[name] for name in ("AB", "AC", "BC")}
        red = {"AB"}
    else:
        raise ValueError(branch)
    return {edge: name in red for name, edge in named_edges.items()}


def pack_hex(values: Iterable[bool]) -> str:
    bits = list(values)
    packed = bytearray((len(bits) + 7) // 8)
    for i, value in enumerate(bits):
        if value:
            packed[i // 8] |= 1 << (i % 8)
    return packed.hex()


def solve(
    bound: int,
    branch: str,
    time_limit: float,
    workers: int,
    seed: int,
    output: Path,
) -> int:
    vertices, vertex_id, edges, edge_id, triangles = base_graph()
    model = cp_model.CpModel()

    weights: list[dict[int, cp_model.IntVar]] = []
    for owner, vertex in enumerate(vertices):
        row = {
            point: model.new_int_var(-bound, bound, f"w_{owner}_{point}")
            for point in range(N)
            if point not in vertex
        }
        model.add(sum(row.values()) == 0)
        weights.append(row)

    edge_colors = [model.new_bool_var(f"edge_{i}") for i in range(len(edges))]
    local_sign_constraints = 0
    for edge_index, (u, v) in enumerate(edges):
        color = edge_colors[edge_index]
        for owner, neighbor in ((u, v), (v, u)):
            triple_sum = sum(weights[owner][point] for point in vertices[neighbor])
            model.add(triple_sum >= 1).only_enforce_if(color)
            model.add(triple_sum <= -1).only_enforce_if(color.negated())
            local_sign_constraints += 1

    for x, y, z in triangles:
        model.add_bool_or([edge_colors[x], edge_colors[y], edge_colors[z]])
        model.add_bool_or(
            [edge_colors[x].negated(), edge_colors[y].negated(), edge_colors[z].negated()]
        )

    fixed = canonical_colors(branch, vertex_id, edge_id)
    for edge, value in fixed.items():
        model.add(edge_colors[edge] == value)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = seed
    solver.parameters.log_search_progress = True
    solver.parameters.cp_model_presolve = True
    solver.parameters.symmetry_level = 2
    status = solver.solve(model)
    status_name = solver.status_name(status)

    record: dict[str, object] = {
        "scope": "bounded zero-sum local-weight ansatz",
        "bound": bound,
        "branch": branch,
        "seed": seed,
        "solver_status": status_name,
        "wall_time_seconds": solver.wall_time,
        "conflicts": solver.num_conflicts,
        "branches": solver.num_branches,
        "vertices": len(vertices),
        "edges": len(edges),
        "triangles": len(triangles),
        "local_sign_constraints": local_sign_constraints,
        "edge_order_sha256": stable_hash(edges),
        "triangle_order_sha256": stable_hash(triangles),
    }

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        edge_values = [bool(solver.value(color)) for color in edge_colors]
        weight_values = [
            {str(point): solver.value(variable) for point, variable in row.items()}
            for row in weights
        ]

        for owner, row in enumerate(weight_values):
            if sum(row.values()) != 0:
                raise AssertionError((owner, row))
        directed_checks = 0
        for edge_index, (u, v) in enumerate(edges):
            observed = edge_values[edge_index]
            for owner, neighbor in ((u, v), (v, u)):
                triple_sum = sum(
                    weight_values[owner][str(point)] for point in vertices[neighbor]
                )
                predicted = triple_sum > 0
                if triple_sum == 0 or predicted != observed:
                    raise AssertionError((owner, neighbor, triple_sum, observed))
                directed_checks += 1

        one_red = two_red = 0
        for triangle in triangles:
            red_count = sum(edge_values[edge] for edge in triangle)
            if red_count == 1:
                one_red += 1
            elif red_count == 2:
                two_red += 1
            else:
                raise AssertionError((triangle, red_count))

        for edge, value in fixed.items():
            if edge_values[edge] != value:
                raise AssertionError((edge, value, edge_values[edge]))

        model_hex = pack_hex(edge_values)
        record.update(
            {
                "result": "SAT_FULL_KG12_MODEL_VERIFIED",
                "directed_local_predictions_checked": directed_checks,
                "full_triangles_checked": len(triangles),
                "monochromatic_triangles": 0,
                "triangles_with_one_red_edge": one_red,
                "triangles_with_two_red_edges": two_red,
                "red_edges": sum(edge_values),
                "blue_edges": len(edge_values) - sum(edge_values),
                "edge_model_hex": model_hex,
                "edge_model_hex_sha256": hashlib.sha256(model_hex.encode()).hexdigest(),
                "weights": weight_values,
                "ramsey_consequence": (
                    "R_3^KG(3,3)=13, conditional only on the published upper bound <=13"
                ),
            }
        )
        output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
        print(json.dumps(record, indent=2, sort_keys=True))
        return 0

    if status == cp_model.INFEASIBLE:
        record["result"] = "UNSAT_BOUNDED_WEIGHT_ANSATZ_ONLY"
        output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
        print(json.dumps(record, indent=2, sort_keys=True))
        return 0

    record["result"] = "INCONCLUSIVE"
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(json.dumps(record, indent=2, sort_keys=True))
    return 2


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bound", type=int, required=True)
    parser.add_argument("--branch", choices=("triangle", "matching", "path"), required=True)
    parser.add_argument("--time-limit", type=float, default=900)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.bound < 1:
        raise SystemExit("bound must be positive")
    raise SystemExit(
        solve(args.bound, args.branch, args.time_limit, args.workers, args.seed, args.output)
    )


if __name__ == "__main__":
    main()
