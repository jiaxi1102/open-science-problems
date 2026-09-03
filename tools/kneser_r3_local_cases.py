#!/usr/bin/env python3
"""Generate the two local-star canonical cases for exact KG(12,3).

The nine-point local-star dichotomy shows that any hypothetical triangle-free
red/blue edge-coloring of KG(12,3), after relabeling and global color swap,
falls into exactly one of the following cases at A0 = {0,1,2}:

* `point`: c(A0,B) is red exactly when B contains point 3;
* `barrier`: all B inside {3,4,5,6} are red and all B inside
  {7,8,9,10,11} are blue.

This script adds those canonical units to the exact CNF and independently
validates any SAT model against the original Kneser graph.
"""

from __future__ import annotations

import argparse
import itertools
import json
from dataclasses import replace
from pathlib import Path

from kneser_exact_cnf import (
    KneserInstance,
    build_instance,
    parse_solver_model,
    validate_model,
    write_dimacs,
)


N = 12
K = 3
ANCHOR = (0, 1, 2)
POINT_PIVOT = 3
BARRIER_FOUR = (3, 4, 5, 6)
BARRIER_FIVE = (7, 8, 9, 10, 11)


def _edge_variable(
    vertex_id: dict[tuple[int, ...], int],
    edge_id: dict[tuple[int, int], int],
    first: tuple[int, ...],
    second: tuple[int, ...],
) -> int:
    i, j = sorted((vertex_id[first], vertex_id[second]))
    return edge_id[(i, j)]


def canonical_units(instance: KneserInstance, case: str) -> tuple[int, ...]:
    if instance.n != N or instance.k != K:
        raise ValueError("local-star canonical cases are specific to KG(12,3)")

    vertex_id = {
        vertex: index
        for index, vertex in enumerate(instance.vertices)
    }
    edge_id = {
        edge: index + 1
        for index, edge in enumerate(instance.edges)
    }
    complement = tuple(point for point in range(N) if point not in ANCHOR)

    units: list[int] = []
    if case == "point":
        for neighbor in itertools.combinations(complement, K):
            variable = _edge_variable(
                vertex_id,
                edge_id,
                ANCHOR,
                neighbor,
            )
            units.append(variable if POINT_PIVOT in neighbor else -variable)
        assert len(units) == 84
    elif case == "barrier":
        for neighbor in itertools.combinations(BARRIER_FOUR, K):
            units.append(
                _edge_variable(
                    vertex_id,
                    edge_id,
                    ANCHOR,
                    neighbor,
                )
            )
        for neighbor in itertools.combinations(BARRIER_FIVE, K):
            units.append(
                -_edge_variable(
                    vertex_id,
                    edge_id,
                    ANCHOR,
                    neighbor,
                )
            )
        assert len(units) == 14
    else:
        raise ValueError(f"unknown canonical case: {case}")

    assert len({abs(unit) for unit in units}) == len(units)
    return tuple(units)


def build_case(case: str) -> KneserInstance:
    base = build_instance(N, K, None)
    return replace(base, seed_units=canonical_units(base, case))


def command_generate(args: argparse.Namespace) -> None:
    instance = build_case(args.case)
    metadata = write_dimacs(instance, args.cnf, args.closure)
    metadata.update(
        {
            "canonical_case": args.case,
            "anchor": list(ANCHOR),
            "point_pivot": POINT_PIVOT if args.case == "point" else None,
            "barrier_four": (
                list(BARRIER_FOUR) if args.case == "barrier" else None
            ),
            "barrier_five": (
                list(BARRIER_FIVE) if args.case == "barrier" else None
            ),
            "case_complete_given_local_dichotomy": True,
        }
    )
    args.metadata.parent.mkdir(parents=True, exist_ok=True)
    args.metadata.write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(metadata, indent=2, sort_keys=True))


def command_check(args: argparse.Namespace) -> None:
    status, assignment = parse_solver_model(args.model)
    if status != "SATISFIABLE":
        raise SystemExit(
            f"solver output is not SATISFIABLE (status={status!r})"
        )
    instance = build_case(args.case)
    result = validate_model(instance, assignment)
    result.update(
        {
            "canonical_case": args.case,
            "solver_status": status,
            "case_units_checked": len(instance.seed_units),
        }
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate = subparsers.add_parser("generate")
    generate.add_argument("--case", choices=("point", "barrier"), required=True)
    generate.add_argument(
        "--closure",
        choices=("none", "star", "prime"),
        default="prime",
    )
    generate.add_argument("--cnf", type=Path, required=True)
    generate.add_argument("--metadata", type=Path, required=True)
    generate.set_defaults(func=command_generate)

    check = subparsers.add_parser("check")
    check.add_argument("--case", choices=("point", "barrier"), required=True)
    check.add_argument("--model", type=Path, required=True)
    check.add_argument("--out", type=Path, required=True)
    check.set_defaults(func=command_check)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
