#!/usr/bin/env python3
"""Extract an irreducible unsatisfiable core for a finite trace gadget.

Each type-triangle contributes the two clauses forbidding all-red and all-blue.
A selector activates the pair.  CaDiCaL first returns an assumption core; a
deletion pass then makes it irreducible at the type-triangle level.
"""
from __future__ import annotations

import argparse
import itertools
import json
import time
from pathlib import Path

from pysat.solvers import Cadical195


def pair_key(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a <= b else (b, a)


def subset_text(mask: int, m: int) -> str:
    return "{" + ",".join(str(i) for i in range(m) if mask & (1 << i)) + "}"


def build(m: int, threshold: int):
    states = list(range(1 << m))
    pair_var: dict[tuple[int, int], int] = {}
    for i, a in enumerate(states):
        for b in states[i:]:
            if a & b:
                continue
            if a == b and a != 0:
                continue
            pair_var[(a, b)] = len(pair_var) + 1

    triangles: set[tuple[int, int, int]] = set()
    for labels in itertools.product(range(4), repeat=m):
        bins = [0, 0, 0, 0]
        for point, label in enumerate(labels):
            bins[label] |= 1 << point
        a, b, c, _unused = bins
        if (a | b | c).bit_count() >= threshold:
            triangles.add(tuple(sorted((a, b, c))))
    return pair_var, sorted(triangles)


def solve(m: int, threshold: int, out: Path) -> None:
    started = time.time()
    pair_var, triangles = build(m, threshold)
    first_selector = len(pair_var) + 1
    selectors = [first_selector + i for i in range(len(triangles))]

    with Cadical195() as solver:
        for selector, (a, b, c) in zip(selectors, triangles):
            x = pair_var[pair_key(a, b)]
            y = pair_var[pair_key(a, c)]
            z = pair_var[pair_key(b, c)]
            solver.add_clause([x, y, z, -selector])
            solver.add_clause([-x, -y, -z, -selector])

        assert not solver.solve(assumptions=selectors)
        core = solver.get_core()
        if not core:
            core = selectors[:]
        core = sorted(set(abs(x) for x in core))
        initial_core_size = len(core)

        # Deletion-based irreducibility. Start with the solver's native core.
        i = 0
        checks = 0
        while i < len(core):
            candidate = core[:i] + core[i + 1:]
            checks += 1
            if not solver.solve(assumptions=candidate):
                core = candidate
            else:
                i += 1

        assert not solver.solve(assumptions=core)
        for i in range(len(core)):
            assert solver.solve(assumptions=core[:i] + core[i + 1:])

    index = {selector: i for i, selector in enumerate(selectors)}
    core_triangles = [triangles[index[s]] for s in core]
    used_pairs: set[tuple[int, int]] = set()
    for a, b, c in core_triangles:
        used_pairs.update((pair_key(a, b), pair_key(a, c), pair_key(b, c)))

    result = {
        "distinguished_points": m,
        "coverage_threshold": threshold,
        "unused_tolerance": m - threshold,
        "all_type_triangles": len(triangles),
        "all_pair_variables": len(pair_var),
        "initial_solver_core_size": initial_core_size,
        "irreducible_core_size": len(core_triangles),
        "core_pair_variables": len(used_pairs),
        "deletion_checks": checks,
        "elapsed_seconds": time.time() - started,
        "core": [
            {
                "masks": [a, b, c],
                "sets": [subset_text(a, m), subset_text(b, m), subset_text(c, m)],
                "sizes": [a.bit_count(), b.bit_count(), c.bit_count()],
                "union_size": (a | b | c).bit_count(),
            }
            for a, b, c in core_triangles
        ],
    }

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True), flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--m", type=int, required=True)
    parser.add_argument("--threshold", type=int, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    solve(args.m, args.threshold, args.out)


if __name__ == "__main__":
    main()
