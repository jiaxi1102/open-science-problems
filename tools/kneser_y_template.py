#!/usr/bin/env python3
"""Search weight-and-Y-trace colorings of KG(3r+2,r).

Let [3r+2]=X union Y with |X|=2r and |Y|=r+2.  A template vertex is
(w,S), where w=|A cap X| and S=A cap Y, so |S|=r-w.  The color of a
disjointness edge is required to depend only on the two template vertices.

All noncentral edges are fixed by the low/high rule around
c=floor(2r/3).  Edges touching the central layer are SAT variables.  Every
actual Kneser triangle is represented exactly by three disjoint Y-traces and
0, 1, or 2 unused Y-points; X-realizability follows because the corresponding
weights sum to at most 2r.

A satisfying assignment therefore lifts immediately to a full coloring of
KG(3r+2,r), with no dependence on individual X-coordinates.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import time
from pathlib import Path

from pysat.solvers import Cadical195

State = tuple[int, tuple[int, ...]]


def state_key(state: State):
    return state[0], state[1]


def edge_template_key(a: State, b: State, central: int):
    wa, sa = a
    wb, sb = b
    if wa == central and wb == central:
        x, y = (sa, sb) if sa <= sb else (sb, sa)
        return ("cc", x, y)
    if wa == central:
        return ("mixed", wb, sa, sb)
    if wb == central:
        return ("mixed", wa, sb, sa)
    raise ValueError("edge does not touch central layer")


def solve(r: int, out: Path) -> None:
    ny = r + 2
    central = (2 * r) // 3
    central_y_size = r - central
    started = time.time()

    variable: dict[tuple, int] = {}

    def term(a: State, b: State):
        wa, _ = a
        wb, _ = b
        if wa != central and wb != central:
            return (wa < central) == (wb < central)
        key = edge_template_key(a, b, central)
        if key not in variable:
            variable[key] = len(variable) + 1
        return variable[key]

    clauses: set[tuple[int, ...]] = set()
    immediate_unsat = False
    automatic = 0
    generated_assignments = 0
    type_triangles: set[tuple[State, State, State]] = set()

    def add_not_all(terms, forbidden: bool) -> None:
        nonlocal immediate_unsat, automatic
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

    Y = tuple(range(ny))
    for unused_size in range(3):
        for unused in itertools.combinations(Y, unused_size):
            unused_set = set(unused)
            remaining = tuple(y for y in Y if y not in unused_set)
            for labels in itertools.product(range(3), repeat=len(remaining)):
                generated_assignments += 1
                bins = [[], [], []]
                for y, label in zip(remaining, labels):
                    bins[label].append(y)
                if any(len(s) > r for s in bins):
                    continue
                states = tuple(sorted(
                    ((r - len(s), tuple(s)) for s in bins), key=state_key
                ))
                # A type triangle may contain two vertices with the same state,
                # e.g. two complementary X-only r-sets.  This is intentional.
                type_triangles.add(states)

    generated = time.time()

    for a, b, c in sorted(type_triangles):
        terms = (term(a, b), term(a, c), term(b, c))
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
        "n": 3 * r + 2,
        "x_size": 2 * r,
        "y_size": ny,
        "central_weight": central,
        "central_y_size": central_y_size,
        "raw_y_label_assignments": generated_assignments,
        "distinct_type_triangles": len(type_triangles),
        "template_variables": len(variable),
        "unique_clauses": len(clauses),
        "automatically_satisfied_half_constraints": automatic,
        "immediate_unsat": immediate_unsat,
        "satisfiable": bool(sat),
        "type_generation_seconds": generated - started,
        "cnf_build_seconds": cnf_built - generated,
        "solve_seconds": solved - cnf_built,
        "elapsed_seconds": solved - started,
    }

    if sat and model is not None:
        assignment = {abs(x): x > 0 for x in model if abs(x) <= len(variable)}
        ordered_keys = [None] * len(variable)
        for key, var in variable.items():
            ordered_keys[var - 1] = key
        raw = bytearray((len(variable) + 7) // 8)
        for i in range(1, len(variable) + 1):
            if assignment.get(i, False):
                raw[(i - 1) // 8] |= 1 << ((i - 1) % 8)
        result["assignment_hex"] = raw.hex()
        result["assignment_sha256"] = hashlib.sha256(raw).hexdigest()
        result["red_template_keys"] = [
            list(key) for key, var in variable.items() if assignment[var]
        ]
        result["variable_keys_in_order"] = [list(key) for key in ordered_keys]

        def value(t):
            return t if isinstance(t, bool) else assignment[t]

        for a, b, c in type_triangles:
            vals = value(term(a, b)), value(term(a, c)), value(term(b, c))
            assert not (vals[0] == vals[1] == vals[2]), (a, b, c, vals)
        result["validated_all_type_triangles"] = True

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    hidden = {"assignment_hex", "red_template_keys", "variable_keys_in_order"}
    print(json.dumps({k: v for k, v in result.items() if k not in hidden},
                     indent=2, sort_keys=True), flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--r", type=int, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    solve(args.r, args.out)


if __name__ == "__main__":
    main()
