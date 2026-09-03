#!/usr/bin/env python3
"""Second-level canonical cubes inside the KG(12,3) point case.

Fix A = {0,1,2} and the exact point-star local coloring at A with pivot 3.
Choose the red neighbor D = {3,4,5}.  The stabilizer of the first local
configuration acts as S_3 on A and S_6 on {6,...,11}.  Applying the certified
nine-point dichotomy at D leaves only eight canonical local structures:

* two exact point-star orientations;
* six 4+5 barrier cores, indexed by |S cap A| and the core color.

The eight cubes can overlap, but their union contains every global solution in
the first-level point case.
"""

from __future__ import annotations

import argparse
import itertools
import json
from dataclasses import dataclass, replace
from pathlib import Path

from kneser_exact_cnf import (
    KneserInstance,
    parse_solver_model,
    validate_model,
    write_dimacs,
)
from kneser_r3_local_cases import ANCHOR, build_case


SECOND_ANCHOR = (3, 4, 5)
A_POINTS = (0, 1, 2)
Q_POINTS = (6, 7, 8, 9, 10, 11)


@dataclass(frozen=True)
class CubeSpec:
    name: str
    kind: str
    pivot: int | None = None
    pivot_color: str | None = None
    four_set: tuple[int, ...] | None = None
    four_color: str | None = None


def cube_specs() -> tuple[CubeSpec, ...]:
    return (
        CubeSpec(
            name="point-red-A",
            kind="point",
            pivot=0,
            pivot_color="red",
        ),
        CubeSpec(
            name="point-blue-Q",
            kind="point",
            pivot=6,
            pivot_color="blue",
        ),
        CubeSpec(
            name="barrier-a0",
            kind="barrier",
            four_set=(6, 7, 8, 9),
            four_color="blue",
        ),
        CubeSpec(
            name="barrier-a1-red",
            kind="barrier",
            four_set=(0, 6, 7, 8),
            four_color="red",
        ),
        CubeSpec(
            name="barrier-a1-blue",
            kind="barrier",
            four_set=(0, 6, 7, 8),
            four_color="blue",
        ),
        CubeSpec(
            name="barrier-a2-red",
            kind="barrier",
            four_set=(0, 1, 6, 7),
            four_color="red",
        ),
        CubeSpec(
            name="barrier-a2-blue",
            kind="barrier",
            four_set=(0, 1, 6, 7),
            four_color="blue",
        ),
        CubeSpec(
            name="barrier-a3",
            kind="barrier",
            four_set=(0, 1, 2, 6),
            four_color="red",
        ),
    )


CUBE_SPECS = {spec.name: spec for spec in cube_specs()}


def edge_variable(
    instance: KneserInstance,
    first: tuple[int, ...],
    second: tuple[int, ...],
) -> int:
    vertex_id = {
        vertex: index
        for index, vertex in enumerate(instance.vertices)
    }
    edge_id = {
        edge: index + 1
        for index, edge in enumerate(instance.edges)
    }
    i, j = sorted((vertex_id[first], vertex_id[second]))
    return edge_id[(i, j)]


def point_units(
    instance: KneserInstance,
    pivot: int,
    pivot_color: str,
) -> tuple[int, ...]:
    complement = tuple(
        point
        for point in range(instance.n)
        if point not in SECOND_ANCHOR
    )
    units: list[int] = []
    for neighbor in itertools.combinations(complement, instance.k):
        variable = edge_variable(instance, SECOND_ANCHOR, neighbor)
        contains = pivot in neighbor
        red = contains if pivot_color == "red" else not contains
        units.append(variable if red else -variable)
    assert len(units) == 84
    return tuple(units)


def barrier_units(
    instance: KneserInstance,
    four_set: tuple[int, ...],
    four_color: str,
) -> tuple[int, ...]:
    complement = set(range(instance.n)) - set(SECOND_ANCHOR)
    four = set(four_set)
    if not four.issubset(complement) or len(four) != 4:
        raise ValueError(f"invalid four-set: {four_set}")
    five = tuple(sorted(complement - four))
    four_is_red = four_color == "red"
    units: list[int] = []
    for neighbor in itertools.combinations(sorted(four), instance.k):
        variable = edge_variable(instance, SECOND_ANCHOR, neighbor)
        units.append(variable if four_is_red else -variable)
    for neighbor in itertools.combinations(five, instance.k):
        variable = edge_variable(instance, SECOND_ANCHOR, neighbor)
        units.append(-variable if four_is_red else variable)
    assert len(units) == 14
    return tuple(units)


def merge_units(*families: tuple[int, ...]) -> tuple[int, ...]:
    values: dict[int, bool] = {}
    for family in families:
        for literal in family:
            variable = abs(literal)
            value = literal > 0
            if variable in values and values[variable] != value:
                raise ValueError(f"conflicting unit for variable {variable}")
            values[variable] = value
    return tuple(
        variable if value else -variable
        for variable, value in sorted(values.items())
    )


def build_cube(name: str) -> tuple[KneserInstance, CubeSpec]:
    spec = CUBE_SPECS[name]
    base = build_case("point")
    if spec.kind == "point":
        assert spec.pivot is not None and spec.pivot_color is not None
        extra = point_units(base, spec.pivot, spec.pivot_color)
    else:
        assert spec.four_set is not None and spec.four_color is not None
        extra = barrier_units(base, spec.four_set, spec.four_color)
    units = merge_units(base.seed_units, extra)
    return replace(base, seed_units=units), spec


def command_list(_: argparse.Namespace) -> None:
    print(
        json.dumps(
            [spec.__dict__ for spec in cube_specs()],
            indent=2,
            sort_keys=True,
        )
    )


def command_generate(args: argparse.Namespace) -> None:
    instance, spec = build_cube(args.cube)
    metadata = write_dimacs(instance, args.cnf, args.closure)
    metadata.update(
        {
            "first_level_case": "point",
            "first_anchor": list(ANCHOR),
            "second_anchor": list(SECOND_ANCHOR),
            "cube": spec.__dict__,
            "second_level_cases_complete_given_dichotomy": True,
            "case_units_after_deduplication": len(instance.seed_units),
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
    instance, spec = build_cube(args.cube)
    result = validate_model(instance, assignment)
    result.update(
        {
            "solver_status": status,
            "first_level_case": "point",
            "cube": spec.__dict__,
            "case_units_checked": len(instance.seed_units),
        }
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    listing = subparsers.add_parser("list")
    listing.set_defaults(func=command_list)

    generate = subparsers.add_parser("generate")
    generate.add_argument("--cube", choices=tuple(CUBE_SPECS), required=True)
    generate.add_argument(
        "--closure",
        choices=("none", "star", "prime"),
        default="prime",
    )
    generate.add_argument("--cnf", type=Path, required=True)
    generate.add_argument("--metadata", type=Path, required=True)
    generate.set_defaults(func=command_generate)

    check = subparsers.add_parser("check")
    check.add_argument("--cube", choices=tuple(CUBE_SPECS), required=True)
    check.add_argument("--model", type=Path, required=True)
    check.add_argument("--out", type=Path, required=True)
    check.set_defaults(func=command_check)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
