#!/usr/bin/env python3
"""Generate and independently validate exact Kneser-Ramsey SAT instances.

Variables are colors of edges of KG(n,k): positive means red and negative means
blue. Every triangle contributes the two NAE clauses forbidding all-red and
all-blue. For n = 4k, `matching` and `path` are the two canonical colorings of
a fixed K4 up to relabeling and global color swap.

For n = 4k, optional K4 closure clauses add logically redundant consequences
of the four triangle constraints on every partition into four k-sets. `star`
adds the four star-NAE relations; `prime` additionally adds all twelve
four-literal prime implicates of the 18-state good-K4 relation. These clauses
preserve the exact model set while greatly strengthening unit propagation.

This file deliberately has no third-party dependencies. External SAT and
symmetry tools consume the generated DIMACS file, while this program validates
any returned model against the original mathematical instance.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Sequence


K4_EDGE_PAIRS = ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))
K4_STAR_INDEX_TRIPLES = ((0, 1, 2), (0, 3, 4), (1, 3, 5), (2, 4, 5))
K4_PRIME_FOUR_TEMPLATES = (
    ((0, 1, 4, 5), (0, 0, 1, 1)),
    ((0, 1, 4, 5), (0, 1, 0, 1)),
    ((0, 1, 4, 5), (1, 0, 1, 0)),
    ((0, 1, 4, 5), (1, 1, 0, 0)),
    ((0, 2, 3, 5), (0, 0, 1, 1)),
    ((0, 2, 3, 5), (0, 1, 0, 1)),
    ((0, 2, 3, 5), (1, 0, 1, 0)),
    ((0, 2, 3, 5), (1, 1, 0, 0)),
    ((1, 2, 3, 4), (0, 0, 1, 1)),
    ((1, 2, 3, 4), (0, 1, 0, 1)),
    ((1, 2, 3, 4), (1, 0, 1, 0)),
    ((1, 2, 3, 4), (1, 1, 0, 0)),
)


@dataclass(frozen=True)
class KneserInstance:
    n: int
    k: int
    vertices: tuple[tuple[int, ...], ...]
    edges: tuple[tuple[int, int], ...]
    triangles: tuple[tuple[int, int, int], ...]
    seed_units: tuple[int, ...]


def _canonical_seed_units(
    n: int,
    k: int,
    vertices: Sequence[tuple[int, ...]],
    edge_id: dict[tuple[int, int], int],
    seed: str | None,
) -> tuple[int, ...]:
    if seed is None:
        return (1,) if edge_id else ()
    if n != 4 * k:
        raise ValueError("canonical K4 seeding requires n = 4k")

    blocks = [tuple(range(t * k, (t + 1) * k)) for t in range(4)]
    vertex_id = {vertex: idx for idx, vertex in enumerate(vertices)}
    block_ids = [vertex_id[block] for block in blocks]

    def eid(a: int, b: int) -> int:
        i, j = sorted((block_ids[a], block_ids[b]))
        return edge_id[(i, j)]

    if seed == "matching":
        red = {(0, 1), (2, 3)}
    elif seed == "path":
        red = {(0, 1), (1, 2), (2, 3)}
    else:
        raise ValueError(f"unknown seed type: {seed}")

    units: list[int] = []
    for a, b in K4_EDGE_PAIRS:
        variable = eid(a, b)
        units.append(variable if (a, b) in red else -variable)
    return tuple(units)


def build_instance(n: int, k: int, seed: str | None) -> KneserInstance:
    if n < 3 * k:
        raise ValueError("KG(n,k) has no triangles when n < 3k")
    vertices = tuple(itertools.combinations(range(n), k))
    vertex_id = {vertex: idx for idx, vertex in enumerate(vertices)}

    edges: list[tuple[int, int]] = []
    edge_id: dict[tuple[int, int], int] = {}
    for i, a in enumerate(vertices):
        a_set = set(a)
        for j in range(i + 1, len(vertices)):
            if a_set.isdisjoint(vertices[j]):
                edge_id[(i, j)] = len(edges) + 1
                edges.append((i, j))

    triangles: list[tuple[int, int, int]] = []
    for i, a in enumerate(vertices):
        a_set = set(a)
        for j in range(i + 1, len(vertices)):
            b = vertices[j]
            if not a_set.isdisjoint(b):
                continue
            used = a_set | set(b)
            remaining = [point for point in range(n) if point not in used]
            for c in itertools.combinations(remaining, k):
                h = vertex_id[c]
                if h <= j:
                    continue
                triangles.append(
                    (
                        edge_id[(i, j)],
                        edge_id[tuple(sorted((i, h)))],
                        edge_id[tuple(sorted((j, h)))],
                    )
                )

    seed_units = _canonical_seed_units(n, k, vertices, edge_id, seed)
    return KneserInstance(
        n=n,
        k=k,
        vertices=vertices,
        edges=tuple(edges),
        triangles=tuple(triangles),
        seed_units=seed_units,
    )


def _set_partitions_into_four_blocks(n: int, k: int) -> Iterator[tuple[tuple[int, ...], ...]]:
    if n != 4 * k:
        raise ValueError("four-block closure requires n = 4k")
    points = tuple(range(n))
    for first_tail in itertools.combinations(points[1:], k - 1):
        first = (0,) + first_tail
        remaining1 = tuple(x for x in points if x not in first)
        anchor2 = remaining1[0]
        for second_tail in itertools.combinations(remaining1[1:], k - 1):
            second = (anchor2,) + second_tail
            remaining2 = tuple(x for x in remaining1 if x not in second)
            anchor3 = remaining2[0]
            for third_tail in itertools.combinations(remaining2[1:], k - 1):
                third = (anchor3,) + third_tail
                fourth = tuple(x for x in remaining2 if x not in third)
                yield (tuple(first), tuple(second), tuple(third), tuple(fourth))


def _k4_edge_variables(instance: KneserInstance) -> Iterator[tuple[int, ...]]:
    vertex_id = {vertex: idx for idx, vertex in enumerate(instance.vertices)}
    edge_id = {edge: idx + 1 for idx, edge in enumerate(instance.edges)}
    for blocks in _set_partitions_into_four_blocks(instance.n, instance.k):
        block_ids = [vertex_id[block] for block in blocks]
        variables = []
        for a, b in K4_EDGE_PAIRS:
            variables.append(edge_id[tuple(sorted((block_ids[a], block_ids[b])))])
        yield tuple(variables)


def _clause_excluding(variables: Sequence[int], values: Sequence[int]) -> tuple[int, ...]:
    return tuple(variable if value == 0 else -variable for variable, value in zip(variables, values))


def _verify_k4_templates() -> None:
    edge_id = {edge: index for index, edge in enumerate(K4_EDGE_PAIRS)}
    triangle_indices = tuple(
        tuple(edge_id[tuple(sorted(pair))] for pair in itertools.combinations(triangle, 2))
        for triangle in itertools.combinations(range(4), 3)
    )
    good = []
    for bits in itertools.product((0, 1), repeat=6):
        if all(len({bits[index] for index in tri}) == 2 for tri in triangle_indices):
            good.append(bits)
    assert len(good) == 18
    for bits in good:
        for indices in K4_STAR_INDEX_TRIPLES:
            assert len({bits[index] for index in indices}) == 2
        for indices, values in K4_PRIME_FOUR_TEMPLATES:
            assert any(bits[index] != value for index, value in zip(indices, values))


def iter_clauses(
    instance: KneserInstance,
    closure: str,
) -> Iterator[tuple[int, ...]]:
    for x, y, z in instance.triangles:
        yield (x, y, z)
        yield (-x, -y, -z)

    if closure != "none":
        if instance.n != 4 * instance.k:
            raise ValueError("K4 closure clauses require n = 4k")
        _verify_k4_templates()
        for variables in _k4_edge_variables(instance):
            for indices in K4_STAR_INDEX_TRIPLES:
                selected = tuple(variables[index] for index in indices)
                yield selected
                yield tuple(-variable for variable in selected)
            if closure == "prime":
                for indices, values in K4_PRIME_FOUR_TEMPLATES:
                    selected = tuple(variables[index] for index in indices)
                    yield _clause_excluding(selected, values)

    for unit in instance.seed_units:
        yield (unit,)


def _factorial(value: int) -> int:
    result = 1
    for number in range(2, value + 1):
        result *= number
    return result


def write_dimacs(
    instance: KneserInstance,
    path: Path,
    closure: str,
) -> dict[str, object]:
    clauses = tuple(iter_clauses(instance, closure))
    path.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    with path.open("wb") as handle:
        header = f"p cnf {len(instance.edges)} {len(clauses)}\n".encode()
        handle.write(header)
        digest.update(header)
        for clause in clauses:
            line = (" ".join(map(str, clause)) + " 0\n").encode()
            handle.write(line)
            digest.update(line)

    four_partitions = 0
    derived_star = 0
    derived_prime = 0
    if closure != "none":
        four_partitions = _factorial(instance.n) // (
            _factorial(instance.k) ** 4 * _factorial(4)
        )
        derived_star = 8 * four_partitions
        if closure == "prime":
            derived_prime = 12 * four_partitions

    return {
        "n": instance.n,
        "k": instance.k,
        "vertices": len(instance.vertices),
        "edge_variables": len(instance.edges),
        "triangles": len(instance.triangles),
        "nae_clauses": 2 * len(instance.triangles),
        "closure": closure,
        "four_block_partitions": four_partitions,
        "derived_star_nae_clauses": derived_star,
        "derived_prime_four_clauses": derived_prime,
        "seed_units": list(instance.seed_units),
        "total_clauses": len(clauses),
        "dimacs_sha256": digest.hexdigest(),
    }


def parse_solver_model(path: Path) -> tuple[str | None, dict[int, bool]]:
    status: str | None = None
    assignment: dict[int, bool] = {}
    integer_line = re.compile(r"^[vV]\s+|^-?\d")
    for raw_line in path.read_text(errors="replace").splitlines():
        line = raw_line.strip()
        upper = line.upper()
        if "UNSATISFIABLE" in upper:
            status = "UNSATISFIABLE"
        elif "SATISFIABLE" in upper:
            status = "SATISFIABLE"
        if not line or not integer_line.search(line):
            continue
        if line[0] in "vV":
            line = line[1:].strip()
        for token in line.split():
            try:
                literal = int(token)
            except ValueError:
                continue
            if literal:
                assignment[abs(literal)] = literal > 0
    return status, assignment


def _edge_bit_digest(assignment: dict[int, bool], count: int) -> tuple[str, str]:
    bits = "".join("1" if assignment[idx] else "0" for idx in range(1, count + 1))
    padding = (-len(bits)) % 4
    encoded = f"{int(bits + ('0' * padding), 2):0{(len(bits) + padding) // 4}x}"
    return encoded, hashlib.sha256(bits.encode()).hexdigest()


def validate_model(
    instance: KneserInstance,
    assignment: dict[int, bool],
) -> dict[str, object]:
    missing = [idx for idx in range(1, len(instance.edges) + 1) if idx not in assignment]
    if missing:
        raise ValueError(
            f"model does not assign all original variables; first missing IDs: {missing[:20]}"
        )

    for unit in instance.seed_units:
        if assignment[abs(unit)] != (unit > 0):
            raise ValueError(f"model violates seed unit {unit}")

    for index, (x, y, z) in enumerate(instance.triangles):
        values = (assignment[x], assignment[y], assignment[z])
        if values[0] == values[1] == values[2]:
            raise ValueError(
                f"monochromatic triangle {index}: variables {(x, y, z)}, value {values[0]}"
            )

    red_count = sum(assignment[idx] for idx in range(1, len(instance.edges) + 1))
    encoded, bit_digest = _edge_bit_digest(assignment, len(instance.edges))
    return {
        "n": instance.n,
        "k": instance.k,
        "edge_variables": len(instance.edges),
        "triangles_checked": len(instance.triangles),
        "red_edges": red_count,
        "blue_edges": len(instance.edges) - red_count,
        "edge_bits_hex": encoded,
        "edge_bits_sha256": bit_digest,
        "validated_all_triangles": True,
        "validated_seed_units": True,
    }


def command_generate(args: argparse.Namespace) -> None:
    instance = build_instance(args.n, args.k, args.seed)
    metadata = write_dimacs(instance, args.cnf, args.closure)
    metadata["seed_type"] = args.seed
    args.metadata.parent.mkdir(parents=True, exist_ok=True)
    args.metadata.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    print(json.dumps(metadata, indent=2, sort_keys=True))


def command_check(args: argparse.Namespace) -> None:
    status, assignment = parse_solver_model(args.model)
    if status != "SATISFIABLE":
        raise SystemExit(f"solver output is not SATISFIABLE (status={status!r})")
    instance = build_instance(args.n, args.k, args.seed)
    result = validate_model(instance, assignment)
    result["seed_type"] = args.seed
    result["solver_status"] = status
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate = subparsers.add_parser("generate")
    generate.add_argument("--n", type=int, required=True)
    generate.add_argument("--k", type=int, required=True)
    generate.add_argument("--seed", choices=("matching", "path"))
    generate.add_argument("--closure", choices=("none", "star", "prime"), default="none")
    generate.add_argument("--cnf", type=Path, required=True)
    generate.add_argument("--metadata", type=Path, required=True)
    generate.set_defaults(func=command_generate)

    check = subparsers.add_parser("check")
    check.add_argument("--n", type=int, required=True)
    check.add_argument("--k", type=int, required=True)
    check.add_argument("--seed", choices=("matching", "path"))
    check.add_argument("--model", type=Path, required=True)
    check.add_argument("--out", type=Path, required=True)
    check.set_defaults(func=command_check)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
