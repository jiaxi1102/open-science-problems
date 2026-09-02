#!/usr/bin/env python3
"""Analyze the nine-point local star forced by a hypothetical KG(12,3) coloring.

Fix a triple A in KG(12,3).  The 84 neighbors of A are the triples in the
nine-point complement.  Their incident edge colors form a two-coloring of
C([9],3), and every partition of [9] into three triples must use both colors.

This program tests structural statements about such colorings.  In particular,
`avoid-both-covers --cover-size 2` asks whether *both* color classes can have
transversal number greater than two.  UNSAT proves that every local star has a
two-point transversal in at least one color.

The program uses python-sat only as a decision engine.  Any SAT model is checked
directly against the combinatorial definitions, and full families are emitted
for independent inspection.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import time
from pathlib import Path
from typing import Iterable, Sequence

from pysat.solvers import Cadical195, Glucose4


Triple = tuple[int, int, int]


def triples_on(n: int = 9) -> tuple[Triple, ...]:
    return tuple(itertools.combinations(range(n), 3))


def perfect_matchings(n: int = 9) -> tuple[tuple[Triple, Triple, Triple], ...]:
    """All unordered partitions of [n] into three triples; n must be nine."""
    if n != 9:
        raise ValueError("this local-star analyzer is specialized to n=9")
    points = tuple(range(n))
    out: set[tuple[Triple, Triple, Triple]] = set()
    for first in itertools.combinations(points, 3):
        remaining1 = tuple(x for x in points if x not in first)
        for second in itertools.combinations(remaining1, 3):
            third = tuple(x for x in remaining1 if x not in second)
            blocks = tuple(sorted((tuple(first), tuple(second), tuple(third))))
            out.add(blocks)
    return tuple(sorted(out))


def base_clauses(
    triples: Sequence[Triple],
    matchings: Sequence[tuple[Triple, Triple, Triple]],
) -> tuple[list[list[int]], dict[Triple, int]]:
    var_of = {triple: idx + 1 for idx, triple in enumerate(triples)}
    clauses: list[list[int]] = []
    for matching in matchings:
        variables = [var_of[block] for block in matching]
        # True = red.  Forbid all-blue and all-red perfect matchings.
        clauses.append(variables)
        clauses.append([-x for x in variables])
    # Remove global color-swap symmetry.
    clauses.append([1])
    return clauses, var_of


def disjoint_variables(
    triples: Sequence[Triple],
    cover: Iterable[int],
    var_of: dict[Triple, int],
) -> list[int]:
    chosen = set(cover)
    return [var_of[triple] for triple in triples if chosen.isdisjoint(triple)]


def add_avoid_both_cover_constraints(
    clauses: list[list[int]],
    triples: Sequence[Triple],
    var_of: dict[Triple, int],
    cover_size: int,
) -> int:
    """Require tau(red)>d and tau(blue)>d.

    It suffices to test all d-subsets: any smaller transversal can be extended
    to a d-subset, which remains a transversal.
    """
    added = 0
    for cover in itertools.combinations(range(9), cover_size):
        variables = disjoint_variables(triples, cover, var_of)
        if not variables:
            raise ValueError("cover size leaves no disjoint triple")
        clauses.append(variables)                # some red triple avoids cover
        clauses.append([-x for x in variables])  # some blue triple avoids cover
        added += 2
    return added


def add_both_covered_constraints(
    clauses: list[list[int]],
    triples: Sequence[Triple],
    var_of: dict[Triple, int],
    cover_size: int,
) -> tuple[int, list[tuple[tuple[int, ...], int]], list[tuple[tuple[int, ...], int]]]:
    """Require each color to admit some transversal of size cover_size."""
    next_var = len(triples) + 1
    red_selectors: list[tuple[tuple[int, ...], int]] = []
    blue_selectors: list[tuple[tuple[int, ...], int]] = []

    covers = [tuple(c) for c in itertools.combinations(range(9), cover_size)]
    for cover in covers:
        red_selectors.append((cover, next_var))
        next_var += 1
    for cover in covers:
        blue_selectors.append((cover, next_var))
        next_var += 1

    clauses.append([selector for _, selector in red_selectors])
    clauses.append([selector for _, selector in blue_selectors])

    added = 2
    for cover, selector in red_selectors:
        for variable in disjoint_variables(triples, cover, var_of):
            # If selected as a red transversal, every triple avoiding it is blue.
            clauses.append([-selector, -variable])
            added += 1
    for cover, selector in blue_selectors:
        for variable in disjoint_variables(triples, cover, var_of):
            # If selected as a blue transversal, every triple avoiding it is red.
            clauses.append([-selector, variable])
            added += 1
    return added, red_selectors, blue_selectors


def solver_class(name: str):
    if name == "cadical195":
        return Cadical195
    if name == "glucose4":
        return Glucose4
    raise ValueError(name)


def minimum_transversal(family: Sequence[Triple]) -> tuple[int, tuple[int, ...]]:
    family_sets = [set(edge) for edge in family]
    if not family_sets:
        return 0, ()
    for size in range(1, 10):
        for cover in itertools.combinations(range(9), size):
            chosen = set(cover)
            if all(chosen.intersection(edge) for edge in family_sets):
                return size, tuple(cover)
    raise AssertionError("the full point set must be a transversal")


def validate_coloring(
    assignment: dict[int, bool],
    triples: Sequence[Triple],
    matchings: Sequence[tuple[Triple, Triple, Triple]],
    var_of: dict[Triple, int],
) -> tuple[list[Triple], list[Triple]]:
    red = [triple for triple in triples if assignment[var_of[triple]]]
    blue = [triple for triple in triples if not assignment[var_of[triple]]]
    for matching in matchings:
        colors = [assignment[var_of[block]] for block in matching]
        if colors[0] == colors[1] == colors[2]:
            raise AssertionError(f"monochromatic perfect matching: {matching}")
    return red, blue


def family_digest(family: Sequence[Triple]) -> str:
    payload = ";".join(",".join(map(str, edge)) for edge in sorted(family))
    return hashlib.sha256(payload.encode()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=("plain", "avoid-both-covers", "both-covered"),
        required=True,
    )
    parser.add_argument("--cover-size", type=int, default=2)
    parser.add_argument(
        "--solver", choices=("cadical195", "glucose4"), default="cadical195"
    )
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    if not 1 <= args.cover_size <= 6:
        raise SystemExit("--cover-size must lie between 1 and 6")

    triples = triples_on()
    matchings = perfect_matchings()
    clauses, var_of = base_clauses(triples, matchings)
    red_selectors: list[tuple[tuple[int, ...], int]] = []
    blue_selectors: list[tuple[tuple[int, ...], int]] = []

    structural_clauses = 0
    if args.mode == "avoid-both-covers":
        structural_clauses = add_avoid_both_cover_constraints(
            clauses, triples, var_of, args.cover_size
        )
    elif args.mode == "both-covered":
        structural_clauses, red_selectors, blue_selectors = (
            add_both_covered_constraints(
                clauses, triples, var_of, args.cover_size
            )
        )

    variable_count = max(abs(lit) for clause in clauses for lit in clause)
    started = time.time()
    Solver = solver_class(args.solver)
    with Solver(bootstrap_with=clauses) as solver:
        satisfiable = bool(solver.solve())
        model = solver.get_model() if satisfiable else None
    elapsed = time.time() - started

    result: dict[str, object] = {
        "mode": args.mode,
        "cover_size": args.cover_size,
        "solver": args.solver,
        "points": 9,
        "triple_variables": len(triples),
        "perfect_matchings": len(matchings),
        "base_nae_clauses": 2 * len(matchings),
        "structural_clauses": structural_clauses,
        "total_variables": variable_count,
        "total_clauses": len(clauses),
        "satisfiable": satisfiable,
        "elapsed_seconds": elapsed,
    }

    if satisfiable:
        assert model is not None
        assignment = {abs(lit): lit > 0 for lit in model}
        missing = [idx for idx in range(1, len(triples) + 1) if idx not in assignment]
        if missing:
            raise AssertionError(f"model omits triple variables: {missing[:10]}")
        red, blue = validate_coloring(assignment, triples, matchings, var_of)
        red_tau, red_cover = minimum_transversal(red)
        blue_tau, blue_cover = minimum_transversal(blue)
        result.update(
            {
                "validated_all_perfect_matchings": True,
                "red_size": len(red),
                "blue_size": len(blue),
                "red_transversal_number": red_tau,
                "red_minimum_transversal": list(red_cover),
                "blue_transversal_number": blue_tau,
                "blue_minimum_transversal": list(blue_cover),
                "red_family_sha256": family_digest(red),
                "blue_family_sha256": family_digest(blue),
                "red_family": [list(edge) for edge in red],
                "blue_family": [list(edge) for edge in blue],
            }
        )
        if red_selectors:
            selected = [
                list(cover)
                for cover, selector in red_selectors
                if assignment.get(selector, False)
            ]
            result["selected_red_covers"] = selected
        if blue_selectors:
            selected = [
                list(cover)
                for cover, selector in blue_selectors
                if assignment.get(selector, False)
            ]
            result["selected_blue_covers"] = selected

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
