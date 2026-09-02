#!/usr/bin/env python3
"""Test closed-form central-layer cores inside the boundary-layer construction.

Currently implements the r=4 star-leftover coloring of KG(6,2).  For two
disjoint Y-pairs P,Q, let L be the remaining Y-pair.  The central-central
edge color is determined by whether a distinguished point belongs to L.
Every perfect matching of K6 has exactly one pair containing that point, so
this coloring has no monochromatic Kneser triangle by inspection.
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
    used = set(used)
    return tuple(x for x in range(n) if x not in used)


def central_color(yp: tuple[int, ...], yq: tuple[int, ...], ny: int,
                  distinguished: int, swap: bool) -> bool:
    leftover = set(range(ny)) - set(yp) - set(yq)
    red = distinguished in leftover
    return not red if swap else red


def solve(r: int, distinguished: int, swap: bool, out: Path) -> None:
    if r != 4:
        raise ValueError("the current closed-form core is defined for r=4")
    n, nx, ny = 3 * r + 2, 2 * r, r + 2
    central = (2 * r) // 3
    started = time.time()

    vertices = list(itertools.combinations(range(n), r))
    vid = {a: i for i, a in enumerate(vertices)}
    weights = [sum(x < nx for x in a) for a in vertices]
    yparts = [tuple(x - nx for x in a if x >= nx) for a in vertices]

    edges: list[tuple[int, int]] = []
    eid: dict[tuple[int, int], int] = {}
    for i, a in enumerate(vertices):
        for b in itertools.combinations(complement_tuple(n, a), r):
            j = vid[b]
            if j <= i:
                continue
            eid[(i, j)] = len(edges)
            edges.append((i, j))
    graph_built = time.time()

    fixed: dict[int, bool] = {}
    variable: dict[int, int] = {}
    for e, (i, j) in enumerate(edges):
        wi, wj = weights[i], weights[j]
        if wi != central and wj != central:
            fixed[e] = (wi < central) == (wj < central)
        elif wi == central and wj == central:
            fixed[e] = central_color(
                yparts[i], yparts[j], ny, distinguished, swap
            )
        else:
            variable[e] = len(variable) + 1

    def term(e: int):
        return fixed[e] if e in fixed else variable[e]

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
            j = vid[b]
            if j <= i:
                continue
            rem_ab = complement_tuple(n, a + b)
            for c in itertools.combinations(rem_ab, r):
                h = vid[c]
                if h <= j:
                    continue
                triangles += 1
                terms = (
                    term(eid[(i, j)]), term(eid[(i, h)]), term(eid[(j, h)])
                )
                add_not_all(terms, True)
                add_not_all(terms, False)
    cnf_built = time.time()

    if immediate_unsat:
        sat, model = False, None
    else:
        with Cadical195(bootstrap_with=[list(c) for c in clauses]) as solver:
            sat = solver.solve()
            model = solver.get_model() if sat else None
    solved = time.time()

    result = {
        "r": r,
        "n": n,
        "central_rule": "star-leftover",
        "distinguished_y_point": distinguished,
        "central_color_swapped": swap,
        "vertices": len(vertices),
        "edges": len(edges),
        "triangles": triangles,
        "fixed_edges": len(fixed),
        "mixed_variables": len(variable),
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
        assignment = {abs(x): x > 0 for x in model if abs(x) <= len(variable)}
        raw = bytearray((len(variable) + 7) // 8)
        for i in range(1, len(variable) + 1):
            if assignment.get(i, False):
                raw[(i - 1) // 8] |= 1 << ((i - 1) % 8)
        result["mixed_assignment_hex"] = raw.hex()
        result["mixed_assignment_sha256"] = hashlib.sha256(raw).hexdigest()

        def colour(e: int) -> bool:
            return fixed[e] if e in fixed else assignment[variable[e]]

        for i, a in enumerate(vertices):
            rem_a = complement_tuple(n, a)
            for b in itertools.combinations(rem_a, r):
                j = vid[b]
                if j <= i:
                    continue
                rem_ab = complement_tuple(n, a + b)
                for c in itertools.combinations(rem_ab, r):
                    h = vid[c]
                    if h <= j:
                        continue
                    vals = (
                        colour(eid[(i, j)]), colour(eid[(i, h)]),
                        colour(eid[(j, h)])
                    )
                    assert not (vals[0] == vals[1] == vals[2])
        result["validated_all_triangles"] = True

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in result.items()
                      if k != "mixed_assignment_hex"}, indent=2,
                     sort_keys=True), flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--r", type=int, default=4)
    parser.add_argument("--distinguished", type=int, default=0)
    parser.add_argument("--swap", action="store_true")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    solve(args.r, args.distinguished, args.swap, args.out)


if __name__ == "__main__":
    main()
