#!/usr/bin/env python3
"""Verify a SAT model for a two-coordinate (p,q)-cover of KG(8,2)."""
from __future__ import annotations

import argparse
import json
from itertools import combinations
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--p", type=int, default=14)
    parser.add_argument("--q", type=int, default=5)
    parser.add_argument("--solver-output", type=Path, required=True)
    parser.add_argument("--json-output", type=Path, required=True)
    args = parser.parse_args()

    p, q = args.p, args.q
    vertices = list(combinations(range(8), 2))
    edges = [
        (u, v)
        for u, v in combinations(range(28), 2)
        if set(vertices[u]).isdisjoint(vertices[v])
    ]
    membership_variables = 2 * 28 * p

    def member(coordinate: int, vertex: int, colour: int) -> int:
        return 1 + (coordinate * 28 + vertex) * p + colour

    def assigned_edge(edge: int) -> int:
        return 1 + membership_variables + edge

    text = args.solver_output.read_text(errors="replace")
    if "s SATISFIABLE" not in text:
        raise SystemExit("solver output does not report SATISFIABLE")

    assignment: dict[int, bool] = {}
    for line in text.splitlines():
        if not line.startswith("v "):
            continue
        for token in line.split()[1:]:
            literal = int(token)
            if literal == 0:
                continue
            assignment[abs(literal)] = literal > 0

    variable_count = membership_variables + len(edges)
    missing = [v for v in range(1, variable_count + 1) if v not in assignment]
    if missing:
        raise SystemExit(f"model omits {len(missing)} variables")

    sets: list[list[list[int]]] = [[], []]
    for coordinate in range(2):
        for vertex in range(28):
            chosen = [
                colour
                for colour in range(p)
                if assignment[member(coordinate, vertex, colour)]
            ]
            if len(chosen) != q:
                raise AssertionError(
                    f"coordinate {coordinate}, vertex {vertex}: {len(chosen)} colours"
                )
            sets[coordinate].append(chosen)

    partition: list[int] = []
    for edge, (u, v) in enumerate(edges):
        coordinate = 0 if assignment[assigned_edge(edge)] else 1
        if set(sets[coordinate][u]) & set(sets[coordinate][v]):
            raise AssertionError(
                f"edge {edge} ({u},{v}) is not disjoint in coordinate {coordinate}"
            )
        partition.append(coordinate)

    payload = {
        "p": p,
        "q": q,
        "ratio": p / q,
        "vertices": vertices,
        "sets": sets,
        "edge_partition": partition,
    }
    args.json_output.write_text(json.dumps(payload, indent=2) + "\n")
    print(
        f"PASS p={p} q={q} vertices={len(vertices)} edges={len(edges)} "
        f"coordinate0_edges={partition.count(0)} "
        f"coordinate1_edges={partition.count(1)} "
        f"json={args.json_output}"
    )


if __name__ == "__main__":
    main()
