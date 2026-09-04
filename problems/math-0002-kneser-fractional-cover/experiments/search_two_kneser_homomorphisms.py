#!/usr/bin/env python3
"""Exact SAT search for a two-coordinate Kneser coloring of KG(8,2).

A satisfying assignment gives two maps

    f_0, f_1 : V(KG(8,2)) -> V(KG(p,q))

such that every edge of KG(8,2) is mapped to an edge in at least one
coordinate.  Equivalently, the Kneser edges are covered by two graphs that
both admit a p/q-coloring.

This is a sufficient certificate for a two-graph fractional-coloring cover.
An UNSAT result for one pair (p,q) is not, by itself, an obstruction to every
p/q-fractional cover: a graph of fractional chromatic number p/q may require a
homomorphism to KG(cp,cq) for c > 1.
"""
from __future__ import annotations

import argparse
import json
from itertools import combinations
from pathlib import Path
from typing import Iterable

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Cadical195


GROUND = list(combinations(range(8), 2))
VERTEX_ID = {pair: i for i, pair in enumerate(GROUND)}
KNESER_EDGES = [
    (u, v)
    for u, v in combinations(range(len(GROUND)), 2)
    if set(GROUND[u]).isdisjoint(GROUND[v])
]
EDGE_ID = {edge: i for i, edge in enumerate(KNESER_EDGES)}


def fixed_set_clauses(lits: list[int], chosen: Iterable[int]) -> list[list[int]]:
    chosen_set = set(chosen)
    return [[lit if i in chosen_set else -lit] for i, lit in enumerate(lits)]


def build_cnf(p: int, q: int, intersection: int) -> tuple[CNF, IDPool]:
    if not (2 * q <= p):
        raise ValueError("KG(p,q) must have p >= 2q")
    if not (0 <= intersection <= q and q - intersection <= p - q):
        raise ValueError("invalid canonical intersection size")

    pool = IDPool()
    cnf = CNF()

    def member(coord: int, vertex: int, color: int) -> int:
        return pool.id(("member", coord, vertex, color))

    def assigned_coord(edge: int) -> int:
        # True means coordinate 0 covers the edge; false means coordinate 1.
        return pool.id(("edge-coordinate", edge))

    # Every vertex receives exactly q colors in each coordinate.
    for coord in range(2):
        for vertex in range(28):
            lits = [member(coord, vertex, color) for color in range(p)]
            cnf.extend(
                CardEnc.equals(
                    lits=lits,
                    bound=q,
                    vpool=pool,
                    encoding=EncType.seqcounter,
                ).clauses
            )

    # If an edge is assigned to a coordinate, the two q-sets in that
    # coordinate must be disjoint.
    for edge, (u, v) in enumerate(KNESER_EDGES):
        x = assigned_coord(edge)
        for color in range(p):
            # x -> not(member(0,u,color) and member(0,v,color))
            cnf.append([-x, -member(0, u, color), -member(0, v, color)])
            # not x -> not(member(1,u,color) and member(1,v,color))
            cnf.append([x, -member(1, u, color), -member(1, v, color)])

    # Symmetry breaking.  Independent permutations of the p colors make the
    # first vertex's two q-sets canonical.
    first = VERTEX_ID[(0, 1)]
    first_set = range(q)
    for coord in range(2):
        cnf.extend(
            fixed_set_clauses(
                [member(coord, first, color) for color in range(p)], first_set
            )
        )

    # The stabilizer of {0,1} in S_8 is transitive on its 15 disjoint
    # neighbors.  Coordinate exchange lets us assign the edge to coordinate
    # 0.  Color permutations then make the neighbor's coordinate-0 set
    # canonical.  Its coordinate-1 set is canonical once its intersection
    # size with the first q-set is fixed.
    neighbor = VERTEX_ID[(2, 3)]
    edge = EDGE_ID[tuple(sorted((first, neighbor)))]
    cnf.append([assigned_coord(edge)])

    red_neighbor = range(q, 2 * q)
    cnf.extend(
        fixed_set_clauses(
            [member(0, neighbor, color) for color in range(p)], red_neighbor
        )
    )
    blue_neighbor = list(range(intersection)) + list(
        range(q, q + (q - intersection))
    )
    cnf.extend(
        fixed_set_clauses(
            [member(1, neighbor, color) for color in range(p)], blue_neighbor
        )
    )

    return cnf, pool


def decode_and_validate(model: list[int], p: int, q: int, pool: IDPool) -> dict:
    true_vars = {lit for lit in model if lit > 0}

    def member(coord: int, vertex: int, color: int) -> int:
        return pool.id(("member", coord, vertex, color))

    sets = [
        [
            [color for color in range(p) if member(coord, vertex, color) in true_vars]
            for vertex in range(28)
        ]
        for coord in range(2)
    ]

    assert all(len(s) == q for coord in sets for s in coord)
    uncovered = []
    for u, v in KNESER_EDGES:
        covered = any(set(sets[c][u]).isdisjoint(sets[c][v]) for c in range(2))
        if not covered:
            uncovered.append((u, v))
    assert not uncovered

    return {
        "p": p,
        "q": q,
        "ratio": p / q,
        "ground_pairs": GROUND,
        "sets": sets,
        "kneser_edges": len(KNESER_EDGES),
        "validated_uncovered_edges": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--p", type=int, required=True)
    parser.add_argument("--q", type=int, required=True)
    parser.add_argument("--intersection", type=int, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    cnf, pool = build_cnf(args.p, args.q, args.intersection)
    print(
        json.dumps(
            {
                "p": args.p,
                "q": args.q,
                "ratio": args.p / args.q,
                "canonical_intersection": args.intersection,
                "variables": pool.top,
                "clauses": len(cnf.clauses),
            },
            sort_keys=True,
        ),
        flush=True,
    )

    with Cadical195(bootstrap_with=cnf.clauses) as solver:
        satisfiable = solver.solve()
        print("SAT" if satisfiable else "UNSAT", flush=True)
        if not satisfiable:
            return 20
        certificate = decode_and_validate(solver.get_model(), args.p, args.q, pool)

    output = args.output or Path(
        f"two_kg_{args.p}_{args.q}_intersection_{args.intersection}.json"
    )
    output.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    print(f"validated certificate: {output}")
    return 10


if __name__ == "__main__":
    raise SystemExit(main())
