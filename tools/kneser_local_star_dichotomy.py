#!/usr/bin/env python3
"""Generate and audit the nine-point local-star dichotomy.

Let the 84 variables color the triples of a nine-point set red/blue. The base
constraints say that every partition into three triples uses both colors.

The negation of the dichotomy adds:
1. for every point and every color, a triple of that color avoiding the point;
2. for every 4+5 split, neither side has opposite monochromatic triple cores.

Unsatisfiability proves that every base coloring has one of two structures:

* point type: one color has a common point (and hence, by a one-line matching
  argument, the coloring is exactly point-star versus its complement);
* barrier type: some four-set has all four internal triples in one color while
  its five-point complement has all ten internal triples in the other color.

The generator has no third-party dependencies. SAT solvers and proof checkers
consume its DIMACS output in CI.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Sequence


POINTS = tuple(range(9))
TRIPLES = tuple(itertools.combinations(POINTS, 3))
TRIPLE_ID = {triple: index + 1 for index, triple in enumerate(TRIPLES)}


def perfect_matchings() -> tuple[tuple[int, int, int], ...]:
    result: list[tuple[int, int, int]] = []
    for first_index, first in enumerate(TRIPLES):
        remaining = tuple(point for point in POINTS if point not in first)
        for second in itertools.combinations(remaining, 3):
            second_index = TRIPLE_ID[second] - 1
            if second_index <= first_index:
                continue
            third = tuple(point for point in remaining if point not in second)
            third_index = TRIPLE_ID[third] - 1
            if third_index <= second_index:
                continue
            result.append(
                (
                    first_index + 1,
                    second_index + 1,
                    third_index + 1,
                )
            )
    assert len(result) == 280
    return tuple(result)


PERFECT_MATCHINGS = perfect_matchings()


def build_clauses() -> tuple[tuple[tuple[int, ...], ...], tuple[dict[str, object], ...]]:
    clauses: list[tuple[int, ...]] = []
    labels: list[dict[str, object]] = []

    for index, matching in enumerate(PERFECT_MATCHINGS):
        clauses.append(matching)
        labels.append(
            {
                "kind": "perfect_matching_not_all_blue",
                "matching_index": index,
                "variables": list(matching),
            }
        )
        clauses.append(tuple(-variable for variable in matching))
        labels.append(
            {
                "kind": "perfect_matching_not_all_red",
                "matching_index": index,
                "variables": list(matching),
            }
        )

    for point in POINTS:
        avoiding = tuple(
            TRIPLE_ID[triple]
            for triple in TRIPLES
            if point not in triple
        )
        assert len(avoiding) == 56
        clauses.append(avoiding)
        labels.append(
            {
                "kind": "red_has_triple_avoiding_point",
                "point": point,
                "variables": list(avoiding),
            }
        )
        clauses.append(tuple(-variable for variable in avoiding))
        labels.append(
            {
                "kind": "blue_has_triple_avoiding_point",
                "point": point,
                "variables": list(avoiding),
            }
        )

    for four_set in itertools.combinations(POINTS, 4):
        four = set(four_set)
        five_set = tuple(point for point in POINTS if point not in four)
        inside_four = tuple(
            TRIPLE_ID[triple]
            for triple in TRIPLES
            if set(triple).issubset(four)
        )
        inside_five = tuple(
            TRIPLE_ID[triple]
            for triple in TRIPLES
            if set(triple).issubset(five_set)
        )
        assert len(inside_four) == 4
        assert len(inside_five) == 10

        # Forbid: all four-side triples red and all five-side triples blue.
        clauses.append(
            tuple(-variable for variable in inside_four) + inside_five
        )
        labels.append(
            {
                "kind": "forbid_red4_blue5_core",
                "four_set": list(four_set),
                "five_set": list(five_set),
                "inside_four": list(inside_four),
                "inside_five": list(inside_five),
            }
        )

        # Forbid the color-swapped core.
        clauses.append(
            inside_four + tuple(-variable for variable in inside_five)
        )
        labels.append(
            {
                "kind": "forbid_blue4_red5_core",
                "four_set": list(four_set),
                "five_set": list(five_set),
                "inside_four": list(inside_four),
                "inside_five": list(inside_five),
            }
        )

    assert len(clauses) == 830
    assert len(labels) == len(clauses)
    return tuple(clauses), tuple(labels)


CLAUSES, CLAUSE_LABELS = build_clauses()


def write_dimacs(path: Path, clauses: Sequence[Sequence[int]]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    with path.open("wb") as handle:
        header = f"p cnf {len(TRIPLES)} {len(clauses)}\n".encode()
        handle.write(header)
        digest.update(header)
        for clause in clauses:
            line = (" ".join(map(str, clause)) + " 0\n").encode()
            handle.write(line)
            digest.update(line)
    return digest.hexdigest()


def is_base_coloring(assignment: Sequence[bool]) -> bool:
    return all(
        not (
            assignment[a - 1]
            == assignment[b - 1]
            == assignment[c - 1]
        )
        for a, b, c in PERFECT_MATCHINGS
    )


def common_point_types(
    assignment: Sequence[bool],
) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    for color in (False, True):
        color_triples = [
            triple
            for triple, value in zip(TRIPLES, assignment)
            if value == color
        ]
        for point in POINTS:
            if color_triples and all(point in triple for triple in color_triples):
                result.append(
                    {
                        "color": "red" if color else "blue",
                        "point": point,
                    }
                )
    return result


def barrier_cores(
    assignment: Sequence[bool],
) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    for four_set in itertools.combinations(POINTS, 4):
        four = set(four_set)
        five_set = tuple(point for point in POINTS if point not in four)
        four_colors = {
            assignment[TRIPLE_ID[triple] - 1]
            for triple in TRIPLES
            if set(triple).issubset(four)
        }
        five_colors = {
            assignment[TRIPLE_ID[triple] - 1]
            for triple in TRIPLES
            if set(triple).issubset(five_set)
        }
        if (
            len(four_colors) == 1
            and len(five_colors) == 1
            and next(iter(four_colors)) != next(iter(five_colors))
        ):
            result.append(
                {
                    "four_set": list(four_set),
                    "five_set": list(five_set),
                    "four_color": (
                        "red" if next(iter(four_colors)) else "blue"
                    ),
                    "five_color": (
                        "red" if next(iter(five_colors)) else "blue"
                    ),
                }
            )
    return result


def verify_exact_point_star(
    assignment: Sequence[bool],
    color: bool,
    point: int,
) -> bool:
    return all(
        value == (point in triple)
        if color
        else value == (point not in triple)
        for triple, value in zip(TRIPLES, assignment)
    )


def assignment_digest(assignment: Sequence[bool]) -> str:
    bits = "".join("1" if value else "0" for value in assignment)
    return hashlib.sha256(bits.encode()).hexdigest()


def check_sharpness_witnesses() -> dict[str, object]:
    point = 0
    point_assignment = tuple(point in triple for triple in TRIPLES)
    assert is_base_coloring(point_assignment)
    point_types = common_point_types(point_assignment)
    assert {"color": "red", "point": point} in point_types
    assert verify_exact_point_star(point_assignment, True, point)

    four_set = {0, 1, 2, 3}
    barrier_assignment = tuple(
        len(set(triple) & four_set) >= 2
        for triple in TRIPLES
    )
    assert is_base_coloring(barrier_assignment)
    cores = barrier_cores(barrier_assignment)
    assert any(core["four_set"] == sorted(four_set) for core in cores)

    return {
        "point_star": {
            "point": point,
            "red_triples": sum(point_assignment),
            "blue_triples": len(TRIPLES) - sum(point_assignment),
            "assignment_sha256": assignment_digest(point_assignment),
            "base_constraints_valid": True,
            "common_point_types": point_types,
        },
        "four_five_barrier": {
            "four_set": sorted(four_set),
            "red_triples": sum(barrier_assignment),
            "blue_triples": len(TRIPLES) - sum(barrier_assignment),
            "assignment_sha256": assignment_digest(barrier_assignment),
            "base_constraints_valid": True,
            "barrier_cores": cores,
        },
    }


def command_generate(args: argparse.Namespace) -> None:
    digest = write_dimacs(args.cnf, CLAUSES)
    witnesses = check_sharpness_witnesses()
    metadata = {
        "theorem": (
            "Every red-blue coloring of the triples of a 9-set with no "
            "monochromatic perfect matching is point type or has an "
            "opposite monochromatic 4+5 core."
        ),
        "variables": len(TRIPLES),
        "perfect_matchings": len(PERFECT_MATCHINGS),
        "base_nae_clauses": 2 * len(PERFECT_MATCHINGS),
        "no_common_point_clauses": 2 * len(POINTS),
        "no_barrier_core_clauses": 2 * len(tuple(itertools.combinations(POINTS, 4))),
        "total_clauses": len(CLAUSES),
        "dimacs_sha256": digest,
        "sharpness_witnesses": witnesses,
    }
    args.metadata.parent.mkdir(parents=True, exist_ok=True)
    args.metadata.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    args.clause_map.parent.mkdir(parents=True, exist_ok=True)
    args.clause_map.write_text(
        json.dumps(
            {
                "variables": {
                    str(index + 1): list(triple)
                    for index, triple in enumerate(TRIPLES)
                },
                "clauses": {
                    str(index + 1): label
                    for index, label in enumerate(CLAUSE_LABELS)
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    print(json.dumps(metadata, indent=2, sort_keys=True))


def command_check_witnesses(_: argparse.Namespace) -> None:
    print(json.dumps(check_sharpness_witnesses(), indent=2, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate = subparsers.add_parser("generate")
    generate.add_argument("--cnf", type=Path, required=True)
    generate.add_argument("--metadata", type=Path, required=True)
    generate.add_argument("--clause-map", type=Path, required=True)
    generate.set_defaults(func=command_generate)

    check = subparsers.add_parser("check-witnesses")
    check.set_defaults(func=command_check_witnesses)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
