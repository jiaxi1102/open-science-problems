#!/usr/bin/env python3
"""Search finite trace gadgets for Kneser triangle lower bounds.

A gadget on m distinguished points colors every unordered pair of disjoint
traces (including the empty-empty pair). It is valid at coverage threshold t
when every three pairwise-disjoint traces whose union has at least t points
induce both colors.

Such a gadget lifts to a coloring of KG(3r+d,r), where d=m-t, provided all
traces that can occur (sizes at most r) are included. Therefore a SAT result
gives R_r^KG(3,3) >= 3r+d+1.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import time
from pathlib import Path

from pysat.solvers import Cadical195


def pair_key(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a <= b else (b, a)


def solve(m: int, threshold: int, max_trace_size: int, out: Path) -> None:
    if not 0 <= threshold <= m:
        raise ValueError("threshold must lie in [0,m]")
    max_trace_size = min(max_trace_size, m)
    started = time.time()

    states = [s for s in range(1 << m) if s.bit_count() <= max_trace_size]
    state_set = set(states)
    pair_var: dict[tuple[int, int], int] = {}
    for i, a in enumerate(states):
        for b in states[i:]:
            if a & b:
                continue
            if a == b and a != 0:
                continue
            pair_var[(a, b)] = len(pair_var) + 1
    variables_built = time.time()

    type_triangles: set[tuple[int, int, int]] = set()
    raw_assignments = 0
    for labels in itertools.product(range(4), repeat=m):
        raw_assignments += 1
        bins = [0, 0, 0, 0]
        for point, label in enumerate(labels):
            bins[label] |= 1 << point
        a, b, c, unused = bins
        if a not in state_set or b not in state_set or c not in state_set:
            continue
        if (a | b | c).bit_count() < threshold:
            continue
        type_triangles.add(tuple(sorted((a, b, c))))
    triangles_built = time.time()

    clauses: set[tuple[int, ...]] = set()
    for a, b, c in type_triangles:
        x = pair_var[pair_key(a, b)]
        y = pair_var[pair_key(a, c)]
        z = pair_var[pair_key(b, c)]
        clauses.add(tuple(sorted(set((x, y, z)))))
        clauses.add(tuple(sorted(set((-x, -y, -z)))))
    cnf = [list(clause) for clause in clauses]
    if pair_var:
        cnf.append([1])
    cnf_built = time.time()

    with Cadical195(bootstrap_with=cnf) as solver:
        sat = solver.solve()
        model = solver.get_model() if sat else None
    solved = time.time()

    result = {
        "distinguished_points": m,
        "coverage_threshold": threshold,
        "unused_tolerance": m - threshold,
        "max_trace_size": max_trace_size,
        "lifted_lower_bound": f"R_r^KG(3,3) >= 3r+{m-threshold+1} for r >= {max_trace_size}",
        "trace_states": len(states),
        "disjoint_trace_pair_variables": len(pair_var),
        "raw_four_label_assignments": raw_assignments,
        "distinct_type_triangles": len(type_triangles),
        "unique_nae_clauses": len(clauses),
        "satisfiable": bool(sat),
        "variable_build_seconds": variables_built - started,
        "triangle_build_seconds": triangles_built - variables_built,
        "cnf_build_seconds": cnf_built - triangles_built,
        "solve_seconds": solved - cnf_built,
        "elapsed_seconds": solved - started,
    }

    if sat and model is not None:
        assignment = {abs(x): x > 0 for x in model if abs(x) <= len(pair_var)}
        ordered_pairs = [None] * len(pair_var)
        for key, var in pair_var.items():
            ordered_pairs[var - 1] = key
        raw = bytearray((len(pair_var) + 7) // 8)
        for i in range(1, len(pair_var) + 1):
            if assignment.get(i, False):
                raw[(i - 1) // 8] |= 1 << ((i - 1) % 8)
        result["assignment_hex"] = raw.hex()
        result["assignment_sha256"] = hashlib.sha256(raw).hexdigest()
        result["trace_pairs_in_variable_order"] = [list(x) for x in ordered_pairs]

        for a, b, c in type_triangles:
            vals = (
                assignment[pair_var[pair_key(a, b)]],
                assignment[pair_var[pair_key(a, c)]],
                assignment[pair_var[pair_key(b, c)]],
            )
            assert not (vals[0] == vals[1] == vals[2]), (a, b, c, vals)
        result["validated_all_type_triangles"] = True

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    hidden = {"assignment_hex", "trace_pairs_in_variable_order"}
    print(json.dumps({k: v for k, v in result.items() if k not in hidden},
                     indent=2, sort_keys=True), flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--m", type=int, required=True)
    parser.add_argument("--threshold", type=int, required=True)
    parser.add_argument("--max-trace-size", type=int, default=1000000)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    solve(args.m, args.threshold, args.max_trace_size, args.out)


if __name__ == "__main__":
    main()
