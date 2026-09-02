#!/usr/bin/env python3
"""Test whether the critical central layer factors through its Y-coordinate.

For KG(3r+2,r), split the ground set into X of size 2r and Y of size r+2,
put c=floor(2r/3), and fix every noncentral edge by the low/high rule.  Edges
with two central endpoints are required to depend only on the unordered pair
of their Y-parts.  Mixed central/noncentral edges remain completely free.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import time
from pathlib import Path

from pysat.solvers import Cadical195


def complement_tuple(n: int, used) -> tuple[int, ...]:
    taken = set(used)
    return tuple(x for x in range(n) if x not in taken)


def pair_key(a: tuple[int, ...], b: tuple[int, ...]):
    return (a, b) if a <= b else (b, a)


def solve(r: int, out: Path) -> None:
    n = 3 * r + 2
    nx = 2 * r
    central = (2 * r) // 3
    started = time.time()

    vertices = list(itertools.combinations(range(n), r))
    vertex_id = {a: i for i, a in enumerate(vertices)}
    weights = [sum(x < nx for x in a) for a in vertices]
    yparts = [tuple(x - nx for x in a if x >= nx) for a in vertices]

    edges: list[tuple[int, int]] = []
    edge_id: dict[tuple[int, int], int] = {}
    for i, a in enumerate(vertices):
        for b in itertools.combinations(complement_tuple(n, a), r):
            j = vertex_id[b]
            if j <= i:
                continue
            edge_id[(i, j)] = len(edges)
            edges.append((i, j))
    graph_built = time.time()

    fixed: dict[int, bool] = {}
    key_to_var: dict[tuple, int] = {}
    edge_var: dict[int, int] = {}
    cc_keys: set[tuple] = set()
    mixed_count = 0

    for e, (i, j) in enumerate(edges):
        wi, wj = weights[i], weights[j]
        if wi != central and wj != central:
            fixed[e] = (wi < central) == (wj < central)
            continue
        if wi == central and wj == central:
            key = ("cc",) + pair_key(yparts[i], yparts[j])
            cc_keys.add(key)
        else:
            key = ("mixed", e)
            mixed_count += 1
        if key not in key_to_var:
            key_to_var[key] = len(key_to_var) + 1
        edge_var[e] = key_to_var[key]

    def term(e: int):
        if e in fixed:
            return fixed[e]
        return edge_var[e]

    clauses: set[tuple[int, ...]] = set()
    triangles = 0
    automatic = 0
    immediate_unsat = False

    def add_not_all(terms, forbidden: bool) -> None:
        nonlocal automatic, immediate_unsat
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

    for i, a in enumerate(vertices):
        rem_a = complement_tuple(n, a)
        for b in itertools.combinations(rem_a, r):
            j = vertex_id[b]
            if j <= i:
                continue
            rem_ab = complement_tuple(n, a + b)
            for cset in itertools.combinations(rem_ab, r):
                h = vertex_id[cset]
                if h <= j:
                    continue
                triangles += 1
                terms = (
                    term(edge_id[(i, j)]),
                    term(edge_id[(i, h)]),
                    term(edge_id[(j, h)]),
                )
                add_not_all(terms, True)
                add_not_all(terms, False)
    cnf_built = time.time()

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
        "central_weight": central,
        "vertices": len(vertices),
        "edges": len(edges),
        "triangles": triangles,
        "fixed_noncentral_edges": len(fixed),
        "central_central_y_pair_variables": len(cc_keys),
        "mixed_edge_variables": mixed_count,
        "total_variables": len(key_to_var),
        "unique_clauses": len(clauses),
        "automatically_satisfied_half_constraints": automatic,
        "immediate_unsat": immediate_unsat,
        "satisfiable": bool(sat),
        "graph_build_seconds": graph_built - started,
        "cnf_build_seconds": cnf_built - graph_built,
        "solve_seconds": solved - cnf_built,
        "elapsed_seconds": solved - started,
    }

    if sat and model is not None:
        assignment = {
            abs(x): x > 0 for x in model if abs(x) <= len(key_to_var)
        }
        raw = bytearray((len(key_to_var) + 7) // 8)
        for i in range(1, len(key_to_var) + 1):
            if assignment.get(i, False):
                raw[(i - 1) // 8] |= 1 << ((i - 1) % 8)
        result["assignment_hex"] = raw.hex()
        result["assignment_sha256"] = hashlib.sha256(raw).hexdigest()
        result["red_central_y_pairs"] = [
            [list(key[1]), list(key[2])]
            for key, var in key_to_var.items()
            if key[0] == "cc" and assignment[var]
        ]

        def colour(e: int) -> bool:
            if e in fixed:
                return fixed[e]
            return assignment[edge_var[e]]

        for i, a in enumerate(vertices):
            rem_a = complement_tuple(n, a)
            for b in itertools.combinations(rem_a, r):
                j = vertex_id[b]
                if j <= i:
                    continue
                rem_ab = complement_tuple(n, a + b)
                for cset in itertools.combinations(rem_ab, r):
                    h = vertex_id[cset]
                    if h <= j:
                        continue
                    vals = (
                        colour(edge_id[(i, j)]),
                        colour(edge_id[(i, h)]),
                        colour(edge_id[(j, h)]),
                    )
                    assert not (vals[0] == vals[1] == vals[2])
        result["validated_all_triangles"] = True

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in {
        "assignment_hex", "red_central_y_pairs"
    }}, indent=2, sort_keys=True), flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--r", type=int, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    solve(args.r, args.out)


if __name__ == "__main__":
    main()
