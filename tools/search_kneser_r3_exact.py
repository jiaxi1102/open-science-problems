#!/usr/bin/env python3
"""Generate and independently verify the exact r=3 Kneser-Ramsey SAT instance.

The Boolean variable for a Kneser edge is true for red and false for blue.
For each triangle with edge variables x,y,z, the two clauses

    x or y or z
    not x or not y or not z

forbid monochromatic triangles.  Three unit clauses impose a valid symmetry
break: a fixed triangle has exactly one specified red edge.  Any non-
monochromatic coloring can be moved to this normalization by a ground-set
permutation and, if necessary, swapping red with blue.

Commands:

    python tools/search_kneser_r3_exact.py generate OUTDIR
    python tools/search_kneser_r3_exact.py verify OUTDIR/solver.out OUTDIR
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Iterable

N = 12
R = 3


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_data() -> tuple[
    list[tuple[int, ...]],
    list[tuple[int, int]],
    list[tuple[int, int, int]],
]:
    vertices = list(itertools.combinations(range(N), R))
    vertex_id = {vertex: index for index, vertex in enumerate(vertices)}

    edges: list[tuple[int, int]] = []
    edge_id: dict[tuple[int, int], int] = {}
    for left, a in enumerate(vertices):
        a_set = set(a)
        for right in range(left + 1, len(vertices)):
            if a_set.isdisjoint(vertices[right]):
                edge_id[(left, right)] = len(edges)
                edges.append((left, right))

    triangles: list[tuple[int, int, int]] = []
    for first, a in enumerate(vertices):
        remaining_a = tuple(x for x in range(N) if x not in a)
        for b in itertools.combinations(remaining_a, R):
            second = vertex_id[b]
            if second <= first:
                continue
            used = set(a) | set(b)
            remaining_ab = tuple(x for x in range(N) if x not in used)
            for c in itertools.combinations(remaining_ab, R):
                third = vertex_id[c]
                if third <= second:
                    continue
                triangles.append(
                    (
                        edge_id[(first, second)],
                        edge_id[(first, third)],
                        edge_id[(second, third)],
                    )
                )

    assert len(vertices) == 220
    assert len(edges) == 9240
    assert len(triangles) == 61600
    assert len(set(triangles)) == len(triangles)
    return vertices, edges, triangles


def symmetry_units(
    vertices: list[tuple[int, ...]], edges: list[tuple[int, int]]
) -> list[tuple[int, bool]]:
    vertex_id = {vertex: index for index, vertex in enumerate(vertices)}
    edge_id = {edge: index for index, edge in enumerate(edges)}
    a = vertex_id[(0, 1, 2)]
    b = vertex_id[(3, 4, 5)]
    c = vertex_id[(6, 7, 8)]

    def edge(left: int, right: int) -> int:
        return edge_id[tuple(sorted((left, right)))]

    # Exactly one red edge on the canonical triangle.
    return [(edge(a, b), True), (edge(a, c), False), (edge(b, c), False)]


def stable_json(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def generate(outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    vertices, edges, triangles = canonical_data()
    units = symmetry_units(vertices, edges)

    clause_count = 2 * len(triangles) + len(units)
    cnf_path = outdir / "kg12_3_no_mono_triangle.cnf"
    with cnf_path.open("w", encoding="ascii", newline="\n") as handle:
        handle.write(
            "c KG(12,3) red-blue edge coloring with no monochromatic triangle\n"
        )
        handle.write("c true variables are red; false variables are blue\n")
        handle.write("c three final unit clauses are a sound symmetry break\n")
        handle.write(f"p cnf {len(edges)} {clause_count}\n")
        for x, y, z in triangles:
            # DIMACS variables are one-based.
            handle.write(f"{x + 1} {y + 1} {z + 1} 0\n")
            handle.write(f"-{x + 1} -{y + 1} -{z + 1} 0\n")
        for variable, value in units:
            literal = variable + 1 if value else -(variable + 1)
            handle.write(f"{literal} 0\n")

    cnf_bytes = cnf_path.read_bytes()
    metadata = {
        "problem": "Does KG(12,3) admit a red-blue edge coloring with no monochromatic triangle?",
        "interpretation": {
            "SAT": "R_3^KG(3,3) = 13, using the published upper bound 13",
            "UNSAT": "R_3^KG(3,3) = 12, using the five-point coloring of KG(11,3)",
        },
        "ground_set_size": N,
        "uniformity": R,
        "vertices": len(vertices),
        "edges_boolean_variables": len(edges),
        "kneser_triangles": len(triangles),
        "cnf_clauses": clause_count,
        "symmetry_units_zero_based": [
            {"edge_id": variable, "red": value} for variable, value in units
        ],
        "vertex_order_sha256": sha256_bytes(stable_json(vertices)),
        "edge_order_sha256": sha256_bytes(stable_json(edges)),
        "triangle_order_sha256": sha256_bytes(stable_json(triangles)),
        "cnf_sha256": sha256_bytes(cnf_bytes),
    }
    (outdir / "instance-metadata.json").write_bytes(stable_json(metadata))
    print(json.dumps(metadata, indent=2, sort_keys=True))


def parse_kissat_model(path: Path, variable_count: int) -> tuple[str, list[bool] | None]:
    status: str | None = None
    assignments: dict[int, bool] = {}
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if line.startswith("s "):
            if "UNSATISFIABLE" in line:
                status = "UNSAT"
            elif "SATISFIABLE" in line:
                status = "SAT"
        elif line.startswith("v "):
            for token in line[2:].split():
                literal = int(token)
                if literal == 0:
                    continue
                variable = abs(literal)
                if not 1 <= variable <= variable_count:
                    raise ValueError(f"model variable outside range: {literal}")
                value = literal > 0
                previous = assignments.setdefault(variable, value)
                if previous != value:
                    raise ValueError(f"contradictory assignment for variable {variable}")

    if status is None:
        raise ValueError("solver output has no SATISFIABLE/UNSATISFIABLE status line")
    if status == "UNSAT":
        return status, None
    missing = sorted(set(range(1, variable_count + 1)) - assignments.keys())
    if missing:
        raise ValueError(f"SAT model is incomplete; {len(missing)} variables missing")
    return status, [assignments[index] for index in range(1, variable_count + 1)]


def verify(model_path: Path, outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    vertices, edges, triangles = canonical_data()
    units = symmetry_units(vertices, edges)
    status, colors = parse_kissat_model(model_path, len(edges))

    if status == "UNSAT":
        record = {
            "solver_status": "UNSAT",
            "verification": "A solver status alone is not a proof. Check the emitted proof trace independently before making a mathematical claim.",
        }
        (outdir / "solver-status.json").write_bytes(stable_json(record))
        print(json.dumps(record, indent=2, sort_keys=True))
        return

    assert colors is not None
    for variable, value in units:
        assert colors[variable] is value

    red_count = sum(colors)
    one_red = 0
    two_red = 0
    for x, y, z in triangles:
        count = int(colors[x]) + int(colors[y]) + int(colors[z])
        if count == 1:
            one_red += 1
        elif count == 2:
            two_red += 1
        else:
            raise AssertionError(
                f"monochromatic triangle at edge variables {(x, y, z)}"
            )

    bitstring = "".join("1" if value else "0" for value in colors)
    certificate = {
        "solver_status": "SAT",
        "independent_verification": "PASS",
        "vertices": len(vertices),
        "edges": len(edges),
        "triangles_checked": len(triangles),
        "monochromatic_triangles": 0,
        "triangles_with_one_red_edge": one_red,
        "triangles_with_two_red_edges": two_red,
        "red_edges": red_count,
        "blue_edges": len(edges) - red_count,
        "edge_color_bitstring_sha256": sha256_bytes(bitstring.encode()),
        "red_edge_ids_zero_based": [
            index for index, value in enumerate(colors) if value
        ],
        "ordering": {
            "vertices": "lexicographic 3-subsets of range(12)",
            "edges": "lexicographic pairs of vertex IDs whose triples are disjoint",
        },
    }
    (outdir / "sat-certificate.json").write_bytes(stable_json(certificate))
    (outdir / "edge-colors.bits").write_text(bitstring + "\n", encoding="ascii")
    print(json.dumps({key: value for key, value in certificate.items()
                      if key != "red_edge_ids_zero_based"}, indent=2, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    generate_parser = subparsers.add_parser("generate")
    generate_parser.add_argument("outdir", type=Path)
    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("model", type=Path)
    verify_parser.add_argument("outdir", type=Path)
    args = parser.parse_args()
    if args.command == "generate":
        generate(args.outdir)
    else:
        verify(args.model, args.outdir)


if __name__ == "__main__":
    main()
