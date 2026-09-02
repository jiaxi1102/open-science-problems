#!/usr/bin/env python3
"""Create exhaustive two-K4 decision cubes for the exact KG(12,3) search.

The first K4 is the canonical partition into consecutive triples and is already
fixed by `tools/kneser_exact_cnf.py --seed`. The second K4 is the transversal
partition whose four blocks have intersection matrix J-I with the first one.
Under the residual automorphism group of the first colored K4, its 18 good
colorings have 7 orbits in the matching branch and 14 in the path branch.
"""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

from kneser_exact_cnf import K4_EDGE_PAIRS, build_instance


TRANSVERSAL_BLOCKS = (
    (3, 6, 9),
    (0, 7, 10),
    (1, 4, 11),
    (2, 5, 8),
)

EXPECTED_REPRESENTATIVES = {
    "matching": (
        "001100",
        "001101",
        "001110",
        "011110",
        "100001",
        "100011",
        "101101",
    ),
    "path": (
        "001100",
        "001101",
        "001110",
        "010010",
        "010011",
        "010110",
        "011010",
        "011110",
        "100001",
        "100011",
        "100101",
        "101001",
        "101101",
        "110011",
    ),
}


def permute_state(state: str, permutation: tuple[int, ...]) -> str:
    edge_id = {edge: index for index, edge in enumerate(K4_EDGE_PAIRS)}
    result = ["?"] * 6
    for edge, index in edge_id.items():
        image = tuple(sorted((permutation[edge[0]], permutation[edge[1]])))
        result[edge_id[image]] = state[index]
    return "".join(result)


def good_k4_states() -> tuple[str, ...]:
    edge_id = {edge: index for index, edge in enumerate(K4_EDGE_PAIRS)}
    triangle_indices = tuple(
        tuple(edge_id[tuple(sorted(pair))] for pair in itertools.combinations(triangle, 2))
        for triangle in itertools.combinations(range(4), 3)
    )
    states = []
    for bits in itertools.product("01", repeat=6):
        state = "".join(bits)
        if all(len({state[index] for index in triangle}) == 2 for triangle in triangle_indices):
            states.append(state)
    assert len(states) == 18
    return tuple(states)


def canonical_seed_state(seed: str) -> str:
    if seed == "matching":
        red = {(0, 1), (2, 3)}
    elif seed == "path":
        red = {(0, 1), (1, 2), (2, 3)}
    else:
        raise ValueError(seed)
    return "".join("1" if edge in red else "0" for edge in K4_EDGE_PAIRS)


def seed_automorphisms(seed: str) -> tuple[tuple[int, ...], ...]:
    state = canonical_seed_state(seed)
    group = tuple(
        permutation
        for permutation in itertools.permutations(range(4))
        if permute_state(state, permutation) == state
    )
    expected = 8 if seed == "matching" else 2
    assert len(group) == expected
    return group


def state_orbits(seed: str) -> tuple[tuple[str, ...], ...]:
    group = seed_automorphisms(seed)
    remaining = set(good_k4_states())
    orbits = []
    while remaining:
        state = min(remaining)
        orbit = tuple(sorted({permute_state(state, permutation) for permutation in group}))
        orbits.append(orbit)
        remaining.difference_update(orbit)
    result = tuple(orbits)
    representatives = tuple(orbit[0] for orbit in result)
    assert representatives == EXPECTED_REPRESENTATIVES[seed]
    assert sum(len(orbit) for orbit in result) == 18
    return result


def cube_units(seed: str, state: str) -> tuple[int, ...]:
    if state not in EXPECTED_REPRESENTATIVES[seed]:
        raise ValueError(f"{state!r} is not a canonical {seed} cube representative")
    instance = build_instance(12, 3, seed)
    vertex_id = {vertex: index for index, vertex in enumerate(instance.vertices)}
    edge_id = {edge: index + 1 for index, edge in enumerate(instance.edges)}
    block_ids = [vertex_id[block] for block in TRANSVERSAL_BLOCKS]
    variables = tuple(
        edge_id[tuple(sorted((block_ids[a], block_ids[b])))]
        for a, b in K4_EDGE_PAIRS
    )
    return tuple(variable if bit == "1" else -variable for variable, bit in zip(variables, state))


def append_cube(input_path: Path, output_path: Path, units: tuple[int, ...]) -> tuple[int, int]:
    lines = input_path.read_text().splitlines()
    if not lines or not lines[0].startswith("p cnf "):
        raise ValueError("input is not a DIMACS CNF with a first-line header")
    _, _, variables_text, clauses_text = lines[0].split()
    variables = int(variables_text)
    clauses = int(clauses_text)
    output_lines = [f"p cnf {variables} {clauses + len(units)}"]
    output_lines.extend(lines[1:])
    output_lines.extend(f"{unit} 0" for unit in units)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(output_lines) + "\n")
    return variables, clauses + len(units)


def command_list(_: argparse.Namespace) -> None:
    payload = {}
    for seed in ("matching", "path"):
        orbits = state_orbits(seed)
        payload[seed] = {
            "seed_automorphism_group_order": len(seed_automorphisms(seed)),
            "good_labeled_states": 18,
            "orbit_count": len(orbits),
            "orbits": [
                {"representative": orbit[0], "orbit_size": len(orbit), "states": list(orbit)}
                for orbit in orbits
            ],
        }
    print(json.dumps(payload, indent=2, sort_keys=True))


def command_apply(args: argparse.Namespace) -> None:
    state_orbits(args.seed)
    units = cube_units(args.seed, args.state)
    variables, clauses = append_cube(args.input, args.output, units)
    payload = {
        "seed_type": args.seed,
        "transversal_state": args.state,
        "transversal_blocks": [list(block) for block in TRANSVERSAL_BLOCKS],
        "cube_units": list(units),
        "variables": variables,
        "clauses_after_cube": clauses,
        "representative_is_canonical": True,
        "representatives_cover_all_18_good_second_k4_states": True,
    }
    args.metadata.parent.mkdir(parents=True, exist_ok=True)
    args.metadata.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list")
    list_parser.set_defaults(func=command_list)

    apply_parser = subparsers.add_parser("apply")
    apply_parser.add_argument("--seed", choices=("matching", "path"), required=True)
    apply_parser.add_argument("--state", required=True)
    apply_parser.add_argument("--input", type=Path, required=True)
    apply_parser.add_argument("--output", type=Path, required=True)
    apply_parser.add_argument("--metadata", type=Path, required=True)
    apply_parser.set_defaults(func=command_apply)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
