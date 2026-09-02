#!/usr/bin/env python3
"""Search cyclic/dihedral weight-and-Y-trace templates for KG(3r+2,r)."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import time
from pathlib import Path

from pysat.solvers import Cadical195

State = tuple[int, tuple[int, ...]]


def rotate_subset(s: tuple[int, ...], n: int, shift: int,
                  reflect: bool = False) -> tuple[int, ...]:
    if reflect:
        return tuple(sorted((shift - x) % n for x in s))
    return tuple(sorted((x + shift) % n for x in s))


def raw_key(a: State, b: State, central: int):
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


def transform_key(key: tuple, ny: int, shift: int, reflect: bool):
    if key[0] == "cc":
        x = rotate_subset(key[1], ny, shift, reflect)
        y = rotate_subset(key[2], ny, shift, reflect)
        if x > y:
            x, y = y, x
        return ("cc", x, y)
    return (
        "mixed", key[1],
        rotate_subset(key[2], ny, shift, reflect),
        rotate_subset(key[3], ny, shift, reflect),
    )


def canonical_key(key: tuple, ny: int, symmetry: str):
    candidates = [transform_key(key, ny, shift, False)
                  for shift in range(ny)]
    if symmetry == "dihedral":
        candidates.extend(transform_key(key, ny, shift, True)
                          for shift in range(ny))
    elif symmetry != "cyclic":
        raise ValueError(symmetry)
    return min(candidates)


def solve(r: int, symmetry: str, out: Path) -> None:
    ny = r + 2
    central = (2 * r) // 3
    started = time.time()
    variable: dict[tuple, int] = {}

    def term(a: State, b: State):
        wa, _ = a
        wb, _ = b
        if wa != central and wb != central:
            return (wa < central) == (wb < central)
        key = canonical_key(raw_key(a, b, central), ny, symmetry)
        if key not in variable:
            variable[key] = len(variable) + 1
        return variable[key]

    Y = tuple(range(ny))
    type_triangles: set[tuple[State, State, State]] = set()
    raw_assignments = 0
    for unused_size in range(3):
        for unused in itertools.combinations(Y, unused_size):
            unused_set = set(unused)
            remaining = tuple(y for y in Y if y not in unused_set)
            for labels in itertools.product(range(3), repeat=len(remaining)):
                raw_assignments += 1
                bins = [[], [], []]
                for y, label in zip(remaining, labels):
                    bins[label].append(y)
                if any(len(s) > r for s in bins):
                    continue
                states = tuple(sorted(
                    ((r - len(s), tuple(s)) for s in bins)
                ))
                type_triangles.add(states)
    generated = time.time()

    clauses: set[tuple[int, ...]] = set()
    immediate_unsat = False
    automatic = 0

    def add_not_all(terms, forbidden: bool):
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

    for a, b, c in sorted(type_triangles):
        terms = term(a, b), term(a, c), term(b, c)
        add_not_all(terms, True)
        add_not_all(terms, False)
    built = time.time()

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
        "y_size": ny,
        "central_weight": central,
        "central_y_size": r - central,
        "symmetry": symmetry,
        "raw_y_label_assignments": raw_assignments,
        "distinct_type_triangles": len(type_triangles),
        "template_orbit_variables": len(variable),
        "unique_clauses": len(clauses),
        "automatically_satisfied_half_constraints": automatic,
        "immediate_unsat": immediate_unsat,
        "satisfiable": bool(sat),
        "type_generation_seconds": generated - started,
        "cnf_build_seconds": built - generated,
        "solve_seconds": solved - built,
        "elapsed_seconds": solved - started,
    }

    if sat and model is not None:
        assignment = {abs(x): x > 0 for x in model if abs(x) <= len(variable)}
        keys = [None] * len(variable)
        for key, var in variable.items():
            keys[var - 1] = key
        raw = bytearray((len(variable) + 7) // 8)
        for i in range(1, len(variable) + 1):
            if assignment.get(i, False):
                raw[(i - 1) // 8] |= 1 << ((i - 1) % 8)
        result["assignment_hex"] = raw.hex()
        result["assignment_sha256"] = hashlib.sha256(raw).hexdigest()
        result["variable_orbit_keys_in_order"] = [list(k) for k in keys]

        def value(t):
            return t if isinstance(t, bool) else assignment[t]

        for a, b, c in type_triangles:
            vals = value(term(a, b)), value(term(a, c)), value(term(b, c))
            assert not (vals[0] == vals[1] == vals[2])
        result["validated_all_type_triangles"] = True

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    hidden = {"assignment_hex", "variable_orbit_keys_in_order"}
    print(json.dumps({k: v for k, v in result.items() if k not in hidden},
                     indent=2, sort_keys=True), flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--r", type=int, required=True)
    parser.add_argument("--symmetry", choices=["cyclic", "dihedral"], required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    solve(args.r, args.symmetry, args.out)


if __name__ == "__main__":
    main()
