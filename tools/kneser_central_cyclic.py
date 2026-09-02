#!/usr/bin/env python3
"""Cyclic Kneser-Ramsey search with a recursively projected central layer.

For KG(3r+2,r), split the ground set into cycles X and Y of lengths 2r and
r+2.  The diagonal rotation acts on all Kneser edges.  For the critical
weight c=floor(2r/3), central vertices have Y-parts of size d=r-c.  This
solver additionally requires every central-central edge color to depend only
on the corresponding edge of KG(r+2,d), not on either X-part.

Triangle constraints are generated from representatives of the rotation
orbits of the two unused ground points.  This covers every Kneser triangle
while avoiding a scan through all triangle orbits of KG(17,5).
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
    used = set(used)
    return tuple(x for x in range(n) if x not in used)


def pair_key(i: int, j: int, size: int) -> int:
    if i > j:
        i, j = j, i
    return i * size + j


def rotate_permutation(nx: int, ny: int) -> tuple[int, ...]:
    return tuple(
        [((i + 1) % nx) for i in range(nx)]
        + [nx + ((j + 1) % ny) for j in range(ny)]
    )


def permute_set(a: tuple[int, ...], p: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(sorted(p[x] for x in a))


def orbit_representatives_of_pairs(n: int, p: tuple[int, ...]):
    seen: set[tuple[int, int]] = set()
    reps: list[tuple[int, int]] = []
    for a in range(n):
        for b in range(a + 1, n):
            start = (a, b)
            if start in seen:
                continue
            reps.append(start)
            cur = start
            while cur not in seen:
                seen.add(cur)
                x, y = p[cur[0]], p[cur[1]]
                cur = (x, y) if x < y else (y, x)
    return reps


def build_orbit_map(starts, image, key_fn, first_var: int):
    """Map every key in cyclic orbits meeting starts to consecutive variables."""
    mapping: dict[int, int] = {}
    next_var = first_var
    for start in starts:
        key = key_fn(*start)
        if key in mapping:
            continue
        orbit_keys: list[int] = []
        i, j = start
        while True:
            q = key_fn(i, j)
            if q in orbit_keys:
                break
            orbit_keys.append(q)
            i, j = image[i], image[j]
            if i > j:
                i, j = j, i
        existing = {mapping[q] for q in orbit_keys if q in mapping}
        if len(existing) > 1:
            raise AssertionError("inconsistent orbit map")
        if existing:
            var = existing.pop()
        else:
            var = next_var
            next_var += 1
        for q in orbit_keys:
            mapping[q] = var
    return mapping, next_var


def solve(r: int, out: Path, full_validate: bool = False) -> None:
    n, nx, ny = 3 * r + 2, 2 * r, r + 2
    central_weight = (2 * r) // 3
    central_y_size = r - central_weight
    group_order = math.lcm(nx, ny)
    started = time.time()

    vertices = list(itertools.combinations(range(n), r))
    vertex_id = {a: i for i, a in enumerate(vertices)}
    vcount = len(vertices)
    weight = [sum(x < nx for x in a) for a in vertices]
    ypart = [tuple(x - nx for x in a if x >= nx) for a in vertices]
    p = rotate_permutation(nx, ny)
    vertex_image = [vertex_id[permute_set(a, p)] for a in vertices]
    graph_setup = time.time()

    # Recursive central quotient KG(ny, central_y_size), modulo Y rotation.
    yvertices = list(itertools.combinations(range(ny), central_y_size))
    yid = {a: i for i, a in enumerate(yvertices)}
    ycount = len(yvertices)
    yimage = [yid[tuple(sorted(((x + 1) % ny for x in a)))] for a in yvertices]
    yedge_starts: list[tuple[int, int]] = []
    for i, a in enumerate(yvertices):
        A = set(a)
        for j in range(i + 1, ycount):
            if A.isdisjoint(yvertices[j]):
                yedge_starts.append((i, j))
    yedge_var, next_var = build_orbit_map(
        yedge_starts, yimage, lambda i, j: pair_key(i, j, ycount), 1
    )
    central_vars = next_var - 1

    # Every non-central-central edge receives a variable for its diagonal
    # rotation orbit.  We keep a compact integer key rather than tuple objects.
    edge_var: dict[int, int] = {}
    edge_starts = 0
    for i, a in enumerate(vertices):
        rem = complement_tuple(n, a)
        for b in itertools.combinations(rem, r):
            j = vertex_id[b]
            if j <= i:
                continue
            if weight[i] == central_weight and weight[j] == central_weight:
                continue
            q = pair_key(i, j, vcount)
            if q in edge_var:
                continue
            edge_starts += 1
            orbit_keys: list[int] = []
            x, y = i, j
            while True:
                key = pair_key(x, y, vcount)
                if key in orbit_keys:
                    break
                orbit_keys.append(key)
                x, y = vertex_image[x], vertex_image[y]
                if x > y:
                    x, y = y, x
            existing = {edge_var[key] for key in orbit_keys if key in edge_var}
            if len(existing) > 1:
                raise AssertionError("inconsistent edge orbit")
            if existing:
                var = existing.pop()
            else:
                var = next_var
                next_var += 1
            for key in orbit_keys:
                edge_var[key] = var
    ordinary_vars = next_var - 1 - central_vars
    orbits_built = time.time()

    def term(i: int, j: int) -> int:
        if i > j:
            i, j = j, i
        if weight[i] == central_weight and weight[j] == central_weight:
            yi, yj = yid[ypart[i]], yid[ypart[j]]
            return yedge_var[pair_key(yi, yj, ycount)]
        return edge_var[pair_key(i, j, vcount)]

    leftover_reps = orbit_representatives_of_pairs(n, p)
    clauses: set[tuple[int, ...]] = set()
    scanned = 0
    degenerate = 0

    def add_nae(x: int, y: int, z: int) -> None:
        nonlocal degenerate
        positive = tuple(sorted(set((x, y, z))))
        negative = tuple(sorted(set((-x, -y, -z))))
        if len(positive) < 3:
            degenerate += 1
        clauses.add(positive)
        clauses.add(negative)

    for u, v in leftover_reps:
        remaining = tuple(x for x in range(n) if x not in {u, v})
        for a in itertools.combinations(remaining, r):
            rem_a = tuple(x for x in remaining if x not in set(a))
            i = vertex_id[a]
            for b in itertools.combinations(rem_a, r):
                rem_b = tuple(x for x in rem_a if x not in set(b))
                c = rem_b  # exactly r points remain
                j, h = vertex_id[b], vertex_id[c]
                if not (i < j < h):
                    continue
                scanned += 1
                add_nae(term(i, j), term(i, h), term(j, h))
    clauses_built = time.time()

    cnf = [list(c) for c in clauses]
    if next_var > 1:
        cnf.append([1])  # global color-swap symmetry
    with Cadical195(bootstrap_with=cnf) as solver:
        sat = solver.solve()
        model = solver.get_model() if sat else None
    solved = time.time()

    result = {
        "r": r,
        "n": n,
        "x_size": nx,
        "y_size": ny,
        "central_weight": central_weight,
        "central_y_size": central_y_size,
        "group_order": group_order,
        "vertices": vcount,
        "central_y_vertices": ycount,
        "central_y_edge_orbit_variables": central_vars,
        "ordinary_edge_orbit_variables": ordinary_vars,
        "total_variables": next_var - 1,
        "actual_noncentral_central_edges_mapped": len(edge_var),
        "leftover_pair_orbit_representatives": len(leftover_reps),
        "partition_representatives_scanned": scanned,
        "unique_nae_clauses": len(clauses),
        "degenerate_orbit_constraints": degenerate,
        "satisfiable": bool(sat),
        "graph_setup_seconds": graph_setup - started,
        "orbit_build_seconds": orbits_built - graph_setup,
        "clause_build_seconds": clauses_built - orbits_built,
        "solve_seconds": solved - clauses_built,
        "elapsed_seconds": solved - started,
    }

    if sat and model is not None:
        assignment = {abs(x): x > 0 for x in model if abs(x) < next_var}
        raw = bytearray((next_var - 1 + 7) // 8)
        for i in range(1, next_var):
            if assignment.get(i, False):
                raw[(i - 1) // 8] |= 1 << ((i - 1) % 8)
        result["assignment_hex"] = raw.hex()
        result["assignment_sha256"] = hashlib.sha256(raw).hexdigest()
        result["red_central_y_orbits"] = [
            [list(yvertices[key // ycount]), list(yvertices[key % ycount])]
            for key, var in sorted(yedge_var.items())
            if assignment[var]
        ]

        # Recheck the complete representative cover independently of the CNF
        # set.  Invariance then transfers the check to every actual triangle.
        checked = 0
        for u, v in leftover_reps:
            remaining = tuple(x for x in range(n) if x not in {u, v})
            for a in itertools.combinations(remaining, r):
                aset = set(a)
                rem_a = tuple(x for x in remaining if x not in aset)
                i = vertex_id[a]
                for b in itertools.combinations(rem_a, r):
                    bset = set(b)
                    c = tuple(x for x in rem_a if x not in bset)
                    j, h = vertex_id[b], vertex_id[c]
                    if not (i < j < h):
                        continue
                    vals = (
                        assignment[term(i, j)],
                        assignment[term(i, h)],
                        assignment[term(j, h)],
                    )
                    assert not (vals[0] == vals[1] == vals[2])
                    checked += 1
        assert checked == scanned
        result["validated_representative_cover"] = True

        if full_validate:
            total = 0
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
                        vals = (
                            assignment[term(i, j)],
                            assignment[term(i, h)],
                            assignment[term(j, h)],
                        )
                        assert not (vals[0] == vals[1] == vals[2])
                        total += 1
            result["validated_all_triangles"] = total

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    hidden = {"assignment_hex", "red_central_y_orbits"}
    print(json.dumps({k: v for k, v in result.items() if k not in hidden},
                     indent=2, sort_keys=True), flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--r", type=int, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--full-validate", action="store_true")
    args = parser.parse_args()
    solve(args.r, args.out, args.full_validate)


if __name__ == "__main__":
    main()
