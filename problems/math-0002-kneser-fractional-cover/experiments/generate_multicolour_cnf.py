#!/usr/bin/env python3
"""Generate a symmetry-broken SAT instance for a two-coordinate (p,q)-cover.

Each of the 28 vertices of KG(8,2) receives a q-subset of [p] in each of two
coordinates. Every Kneser edge is assigned to one coordinate, where its two
q-subsets must be disjoint. Thus a satisfying assignment gives two covering
subgraphs, each admitting a homomorphism to KG(p,q), and hence fractional
chromatic number at most p/q.
"""
from __future__ import annotations

import argparse
from itertools import combinations
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--p", type=int, default=14)
    parser.add_argument("--q", type=int, default=5)
    parser.add_argument("--intersection", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    p, q, intersection = args.p, args.q, args.intersection
    if not (0 < q and 2 * q <= p):
        raise SystemExit("require 0 < q and 2q <= p")
    if not (0 <= intersection <= q and q - intersection <= p - q):
        raise SystemExit("invalid canonical intersection case")

    vertices = list(combinations(range(8), 2))
    edges = [
        (u, v)
        for u, v in combinations(range(28), 2)
        if set(vertices[u]).isdisjoint(vertices[v])
    ]
    edge_id = {edge: i for i, edge in enumerate(edges)}
    if len(vertices) != 28 or len(edges) != 210:
        raise AssertionError("unexpected KG(8,2) dimensions")

    membership_variables = 2 * 28 * p
    variable_count = membership_variables + len(edges)

    def member(coordinate: int, vertex: int, colour: int) -> int:
        return 1 + (coordinate * 28 + vertex) * p + colour

    def assigned_edge(edge: int) -> int:
        return 1 + membership_variables + edge

    clauses: list[tuple[int, ...]] = []

    # Exactly q colours at each vertex and coordinate. The small fixed values
    # p=14, q=5 make the direct subset encoding compact and transparent.
    for coordinate in range(2):
        for vertex in range(28):
            group = [member(coordinate, vertex, colour) for colour in range(p)]
            # At most q true variables.
            for subset in combinations(group, q + 1):
                clauses.append(tuple(-literal for literal in subset))
            # At least q true variables: at most p-q variables may be false.
            for subset in combinations(group, p - q + 1):
                clauses.append(tuple(subset))

    # Partition each Kneser edge between the two coordinates. x_e=true means
    # coordinate 0 covers it, so the coordinate-0 sets must be disjoint;
    # x_e=false means coordinate 1 covers it.
    for edge, (u, v) in enumerate(edges):
        x = assigned_edge(edge)
        for colour in range(p):
            clauses.append((-x, -member(0, u, colour), -member(0, v, colour)))
            clauses.append((x, -member(1, u, colour), -member(1, v, colour)))

    def fix_set(coordinate: int, vertex: int, chosen: set[int]) -> None:
        if len(chosen) != q:
            raise AssertionError("fixed set has wrong cardinality")
        for colour in range(p):
            literal = member(coordinate, vertex, colour)
            clauses.append((literal if colour in chosen else -literal,))

    # Palette permutations let us fix both sets on vertex {0,1}.
    canonical = set(range(q))
    fix_set(0, 0, canonical)
    fix_set(1, 0, canonical)

    # The fixed disjoint neighbour {2,3} must be covered in at least one
    # coordinate. Swapping the two coordinates makes coordinate 0 cover it.
    neighbour = vertices.index((2, 3))
    fixed_edge = edge_id[tuple(sorted((0, neighbour)))]
    clauses.append((assigned_edge(fixed_edge),))

    # The stabilizer of the first coordinate's canonical set makes the
    # neighbour's disjoint q-set canonical as well.
    fix_set(0, neighbour, set(range(q, 2 * q)))

    # In the second coordinate only the intersection size with the canonical
    # q-set is invariant. Branching over this value gives q+1 exhaustive cases.
    second_neighbour = set(range(intersection)) | set(
        range(q, q + (q - intersection))
    )
    fix_set(1, neighbour, second_neighbour)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="ascii") as handle:
        handle.write(
            f"c KG(8,2) two-coordinate ({p},{q}) cover\n"
            f"c canonical second-coordinate intersection {intersection}\n"
            f"p cnf {variable_count} {len(clauses)}\n"
        )
        for clause in clauses:
            handle.write(" ".join(map(str, clause)) + " 0\n")

    print(
        f"generated={args.output} p={p} q={q} ratio={p/q:.12g} "
        f"intersection={intersection} variables={variable_count} "
        f"clauses={len(clauses)}"
    )


if __name__ == "__main__":
    main()
