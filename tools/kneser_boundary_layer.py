#!/usr/bin/env python3
"""Boundary-layer reduction for triangle-free 2-colourings of KG(3r+2,r).

Split the ground set as X union Y with |X|=2r and |Y|=r+2, and put
c=floor(2r/3).  For an r-set A write w(A)=|A cap X|.

When neither endpoint has weight c, fix an edge AB red exactly when w(A)
and w(B) lie on the same side of c.  Every Kneser triangle avoiding the
central layer w=c is then automatically non-monochromatic: its total X-weight
lies in {2r-2,2r-1,2r}, so it cannot consist entirely of low or entirely of
high vertices.

Only edge orbits touching the central layer remain as SAT variables.  Optional
cyclic symmetry can be imposed diagonally or independently on X and Y.
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


def complement_tuple(n: int, used) -> tuple[int, ...]:
    taken = set(used)
    return tuple(x for x in range(n) if x not in taken)


def rotate_perm(nx: int, ny: int, rotate_x: bool, rotate_y: bool) -> tuple[int, ...]:
    n = nx + ny
    p = list(range(n))
    if rotate_x:
        for i in range(nx):
            p[i] = (i + 1) % nx
    if rotate_y:
        for j in range(ny):
            p[nx + j] = nx + ((j + 1) % ny)
    return tuple(p)


def permute_set(a: tuple[int, ...], p: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(sorted(p[x] for x in a))


class DSU:
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: int, b: int) -> None:
        a, b = self.find(a), self.find(b)
        if a == b:
            return
        if self.rank[a] < self.rank[b]:
            a, b = b, a
        self.parent[b] = a
        if self.rank[a] == self.rank[b]:
            self.rank[a] += 1


def build_instance(r: int):
    n = 3 * r + 2
    vertices = list(itertools.combinations(range(n), r))
    vertex_id = {a: i for i, a in enumerate(vertices)}
    edges: list[tuple[int, int]] = []
    edge_id: dict[tuple[int, int], int] = {}
    for i, a in enumerate(vertices):
        for b in itertools.combinations(complement_tuple(n, a), r):
            j = vertex_id[b]
            if j <= i:
                continue
            edge_id[(i, j)] = len(edges)
            edges.append((i, j))
    return n, vertices, vertex_id, edges, edge_id


def triangle_indices(n, r, vertices, vertex_id, edge_id):
    for i, a in enumerate(vertices):
        rem_a = complement_tuple(n, a)
        for b in itertools.combinations(rem_a, r):
            j = vertex_id[b]
            if j <= i:
                continue
            rem_ab = complement_tuple(n, a + b)
            for c in itertools.combinations(rem_ab, r):
                h = vertex_id[c]
                if h <= j:
                    continue
                yield edge_id[(i, j)], edge_id[(i, h)], edge_id[(j, h)]


def edge_orbits(r, vertices, vertex_id, edges, edge_id, symmetry):
    nx, ny = 2 * r, r + 2
    generators: list[tuple[int, ...]] = []
    if symmetry == "diagonal":
        generators.append(rotate_perm(nx, ny, True, True))
    elif symmetry == "product":
        generators.extend([
            rotate_perm(nx, ny, True, False),
            rotate_perm(nx, ny, False, True),
        ])
    elif symmetry != "none":
        raise ValueError(symmetry)

    dsu = DSU(len(edges))
    for p in generators:
        for e, (i, j) in enumerate(edges):
            pi = vertex_id[permute_set(vertices[i], p)]
            pj = vertex_id[permute_set(vertices[j], p)]
            if pi > pj:
                pi, pj = pj, pi
            dsu.union(e, edge_id[(pi, pj)])

    root_to_oid: dict[int, int] = {}
    orbit = [0] * len(edges)
    representatives: list[int] = []
    for e in range(len(edges)):
        root = dsu.find(e)
        if root not in root_to_oid:
            root_to_oid[root] = len(representatives)
            representatives.append(e)
        orbit[e] = root_to_oid[root]
    return orbit, representatives


def solve(r: int, symmetry: str, out: Path) -> None:
    started = time.time()
    n, vertices, vertex_id, edges, edge_id = build_instance(r)
    central_weight = (2 * r) // 3
    nx = 2 * r
    weight = [sum(x < nx for x in a) for a in vertices]
    built_graph = time.time()

    orbit, representatives = edge_orbits(
        r, vertices, vertex_id, edges, edge_id, symmetry
    )
    built_orbits = time.time()

    # Each orbit is either analytically fixed or represented by one SAT variable.
    fixed: dict[int, bool] = {}
    variable: dict[int, int] = {}
    for oid, e in enumerate(representatives):
        i, j = edges[e]
        wi, wj = weight[i], weight[j]
        if wi != central_weight and wj != central_weight:
            fixed[oid] = (wi < central_weight) == (wj < central_weight)
        else:
            variable[oid] = len(variable) + 1

    def term(edge_index: int):
        oid = orbit[edge_index]
        if oid in fixed:
            return fixed[oid]
        return variable[oid]

    clauses: set[tuple[int, ...]] = set()
    triangle_count = 0
    automatic = 0
    immediate_unsat = False

    def add_not_all(terms, forbidden: bool):
        nonlocal automatic, immediate_unsat
        # Clause says at least one term differs from forbidden.
        lits: list[int] = []
        for t in terms:
            if isinstance(t, bool):
                if t != forbidden:
                    automatic += 1
                    return
            else:
                lits.append(-t if forbidden else t)
        lits = sorted(set(lits))
        if not lits:
            immediate_unsat = True
        else:
            clauses.add(tuple(lits))

    for a, b, c in triangle_indices(n, r, vertices, vertex_id, edge_id):
        triangle_count += 1
        terms = (term(a), term(b), term(c))
        add_not_all(terms, True)
        add_not_all(terms, False)
    built_cnf = time.time()

    if immediate_unsat:
        sat = False
        model = None
    else:
        with Cadical195(bootstrap_with=[list(c) for c in clauses]) as solver:
            sat = solver.solve()
            model = solver.get_model() if sat else None
    solved = time.time()

    result = {
        "r": r,
        "n": n,
        "symmetry": symmetry,
        "central_weight": central_weight,
        "vertices": len(vertices),
        "edges": len(edges),
        "edge_orbits": len(representatives),
        "fixed_edge_orbits": len(fixed),
        "boundary_variable_orbits": len(variable),
        "triangles": triangle_count,
        "unique_clauses": len(clauses),
        "automatically_satisfied_half_constraints": automatic,
        "immediate_unsat": immediate_unsat,
        "satisfiable": bool(sat),
        "graph_build_seconds": built_graph - started,
        "orbit_build_seconds": built_orbits - built_graph,
        "cnf_build_seconds": built_cnf - built_orbits,
        "solve_seconds": solved - built_cnf,
        "elapsed_seconds": solved - started,
    }

    if sat and model is not None:
        assignment = {abs(x): x > 0 for x in model if abs(x) <= len(variable)}

        def colour(edge_index: int) -> bool:
            oid = orbit[edge_index]
            if oid in fixed:
                return fixed[oid]
            return assignment[variable[oid]]

        raw = bytearray((len(variable) + 7) // 8)
        for i in range(1, len(variable) + 1):
            if assignment.get(i, False):
                raw[(i - 1) // 8] |= 1 << ((i - 1) % 8)
        result["boundary_assignment_hex"] = raw.hex()
        result["boundary_assignment_sha256"] = hashlib.sha256(raw).hexdigest()
        result["red_boundary_orbit_representatives"] = [
            [list(vertices[edges[e][0]]), list(vertices[edges[e][1]])]
            for oid, e in enumerate(representatives)
            if oid in variable and assignment[variable[oid]]
        ]

        for a, b, c in triangle_indices(n, r, vertices, vertex_id, edge_id):
            vals = colour(a), colour(b), colour(c)
            assert not (vals[0] == vals[1] == vals[2])
        result["validated_all_triangles"] = True

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    hidden = {"boundary_assignment_hex", "red_boundary_orbit_representatives"}
    print(json.dumps({k: v for k, v in result.items() if k not in hidden},
                     indent=2, sort_keys=True), flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--r", type=int, required=True)
    parser.add_argument("--symmetry", choices=["none", "diagonal", "product"], required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    solve(args.r, args.symmetry, args.out)


if __name__ == "__main__":
    main()
