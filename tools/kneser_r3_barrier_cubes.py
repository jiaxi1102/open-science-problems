#!/usr/bin/env python3
"""Second-level canonical cubes inside the KG(12,3) barrier case.

Fix A = {0,1,2}, S = {3,4,5,6}, and T = {7,8,9,10,11}.  The first local
barrier has all A--B edges red for B in C(S,3), and all A--B edges blue for
B in C(T,3).  Choose D = {3,4,5}; then c(A,D) is red.

The stabilizer of the first configuration and D acts as S_3 on A, fixes 6,
and acts as S_5 on T.  Applying the certified nine-point dichotomy at D gives
three point-type orbits and twelve barrier-type orbits, for fifteen complete
canonical cubes in total.
"""

from __future__ import annotations

import argparse
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
from kneser_r3_point_cubes import (
    SECOND_ANCHOR,
    barrier_units,
    merge_units,
    point_units,
)


A_POINTS = (0, 1, 2)
FIXED_S_POINT = 6
T_POINTS = (7, 8, 9, 10, 11)


@dataclass(frozen=True)
class CubeSpec:
    name: str
    kind: str
    pivot: int | None = None
    pivot_color: str | None = None
    four_set: tuple[int, ...] | None = None
    four_color: str | None = None
    a_count: int | None = None
    contains_fixed_s_point: bool | None = None


def cube_specs() -> tuple[CubeSpec, ...]:
    return (
        CubeSpec(
            name="point-red-A",
            kind="point",
            pivot=0,
            pivot_color="red",
        ),
        CubeSpec(
            name="point-blue-s",
            kind="point",
            pivot=FIXED_S_POINT,
            pivot_color="blue",
        ),
        CubeSpec(
            name="point-blue-T",
            kind="point",
            pivot=7,
            pivot_color="blue",
        ),
        CubeSpec(
            name="barrier-a0-b0",
            kind="barrier",
            four_set=(7, 8, 9, 10),
            four_color="blue",
            a_count=0,
            contains_fixed_s_point=False,
        ),
        CubeSpec(
            name="barrier-a0-b1",
            kind="barrier",
            four_set=(6, 7, 8, 9),
            four_color="blue",
            a_count=0,
            contains_fixed_s_point=True,
        ),
        CubeSpec(
            name="barrier-a1-b0-red",
            kind="barrier",
            four_set=(0, 7, 8, 9),
            four_color="red",
            a_count=1,
            contains_fixed_s_point=False,
        ),
        CubeSpec(
            name="barrier-a1-b0-blue",
            kind="barrier",
            four_set=(0, 7, 8, 9),
            four_color="blue",
            a_count=1,
            contains_fixed_s_point=False,
        ),
        CubeSpec(
            name="barrier-a1-b1-red",
            kind="barrier",
            four_set=(0, 6, 7, 8),
            four_color="red",
            a_count=1,
            contains_fixed_s_point=True,
        ),
        CubeSpec(
            name="barrier-a1-b1-blue",
            kind="barrier",
            four_set=(0, 6, 7, 8),
            four_color="blue",
            a_count=1,
            contains_fixed_s_point=True,
        ),
        CubeSpec(
            name="barrier-a2-b0-red",
            kind="barrier",
            four_set=(0, 1, 7, 8),
            four_color="red",
            a_count=2,
            contains_fixed_s_point=False,
        ),
        CubeSpec(
            name="barrier-a2-b0-blue",
            kind="barrier",
            four_set=(0, 1, 7, 8),
            four_color="blue",
            a_count=2,
            contains_fixed_s_point=False,
        ),
        CubeSpec(
            name="barrier-a2-b1-red",
            kind="barrier",
            four_set=(0, 1, 6, 7),
            four_color="red",
            a_count=2,
            contains_fixed_s_point=True,
        ),
        CubeSpec(
            name="barrier-a2-b1-blue",
            kind="barrier",
            four_set=(0, 1, 6, 7),
            four_color="blue",
            a_count=2,
            contains_fixed_s_point=True,
        ),
        CubeSpec(
            name="barrier-a3-b0",
            kind="barrier",
            four_set=(0, 1, 2, 7),
            four_color="red",
            a_count=3,
            contains_fixed_s_point=False,
        ),
        CubeSpec(
            name="barrier-a3-b1",
            kind="barrier",
            four_set=(0, 1, 2, 6),
            four_color="red",
            a_count=3,
            contains_fixed_s_point=True,
        ),
    )


CUBE_SPECS = {spec.name: spec for spec in cube_specs()}


def _audit_specs() -> None:
    specs = cube_specs()
    assert len(specs) == 15
    assert len(CUBE_SPECS) == len(specs)

    point_specs = [spec for spec in specs if spec.kind == "point"]
    barrier_specs = [spec for spec in specs if spec.kind == "barrier"]
    assert len(point_specs) == 3
    assert len(barrier_specs) == 12

    for spec in barrier_specs:
        assert spec.four_set is not None
        assert spec.four_color in {"red", "blue"}
        four = set(spec.four_set)
        assert len(four) == 4
        assert four.isdisjoint(SECOND_ANCHOR)
        assert len(four & set(A_POINTS)) == spec.a_count
        assert ((FIXED_S_POINT in four) == spec.contains_fixed_s_point)
        if spec.a_count == 0:
            assert spec.four_color == "blue"
        if spec.a_count == 3:
            assert spec.four_color == "red"


_audit_specs()


def build_cube(name: str) -> tuple[KneserInstance, CubeSpec]:
    spec = CUBE_SPECS[name]
    base = build_case("barrier")
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
            "first_level_case": "barrier",
            "first_anchor": list(ANCHOR),
            "first_barrier_four": [3, 4, 5, 6],
            "first_barrier_five": list(T_POINTS),
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
            "first_level_case": "barrier",
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
