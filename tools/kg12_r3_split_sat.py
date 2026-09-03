#!/usr/bin/env python3
"""Exact KG(12,3) Ramsey SAT search split by canonical K4 type.

Every red/blue coloring of K4 without a monochromatic triangle is, up to a
vertex permutation and global color swap, one of two types:

1. MATCHING: two red opposite edges and a blue four-cycle;
2. PATH: a red P4 and its blue-complement P4.

The canonical four Kneser vertices are the disjoint triples
A=012, B=345, C=678, D=9ab. Fixing either representative therefore gives two
exhaustive symmetry branches for the full KG(12,3) problem.
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


def stable_hash(value: object) -> str:
    payload = json.dumps(value, separators=(",", ":"), sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_instance():
    vertices = list(itertools.combinations(range(N), R))
    vertex_id = {vertex: i for i, vertex in enumerate(vertices)}
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
        remaining_a = tuple(x for x in range(N) if x not in a)
        for b in itertools.combinations(remaining_a, R):
            j = vertex_id[b]
            if j <= i:
                continue
            used_ab = set(a) | set(b)
            remaining_ab = tuple(x for x in range(N) if x not in used_ab)
            for c in itertools.combinations(remaining_ab, R):
                k = vertex_id[c]
                if k <= j:
                    continue
                triangles.append(
                    (edge_id[(i, j)], edge_id[(i, k)], edge_id[(j, k)])
                )

    blocks = [
        vertex_id[(0, 1, 2)],
        vertex_id[(3, 4, 5)],
        vertex_id[(6, 7, 8)],
        vertex_id[(9, 10, 11)],
    ]
    names = ("AB", "AC", "AD", "BC", "BD", "CD")
    pairs = ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))
    canonical = {
        name: edge_id[tuple(sorted((blocks[i], blocks[j])))]
        for name, (i, j) in zip(names, pairs)
    }
    assert (len(vertices), len(edges), len(triangles)) == (220, 9240, 61600)
    return vertices, edges, triangles, canonical


def units_for(branch: str, canonical: dict[str, int]) -> list[int]:
    if branch == "matching":
        # Red perfect matching AB,CD; blue complementary four-cycle.
        red = {"AB", "CD"}
    elif branch == "path":
        # Red path A-B-D-C: AB,BD,CD; blue complement AC,AD,BC.
        red = {"AB", "BD", "CD"}
    else:
        raise ValueError(branch)
    return [variable if name in red else -variable for name, variable in canonical.items()]


def generate(branch: str, cnf: Path, metadata: Path) -> None:
    vertices, edges, triangles, canonical = build_instance()
    units = units_for(branch, canonical)
    clauses = 2 * len(triangles) + len(units)
    with cnf.open("w", encoding="ascii", newline="\n") as out:
        out.write(f"c Exact KG(12,3) branch: canonical K4 {branch}\n")
        out.write("c true=red false=blue\n")
        out.write(f"p cnf {len(edges)} {clauses}\n")
        for x, y, z in triangles:
            out.write(f"{x} {y} {z} 0\n")
            out.write(f"-{x} -{y} -{z} 0\n")
        for literal in units:
            out.write(f"{literal} 0\n")

    record = {
        "scope": "one of two exhaustive canonical-K4 symmetry branches",
        "branch": branch,
        "vertices": len(vertices),
        "edge_color_variables": len(edges),
        "kneser_triangles": len(triangles),
        "cnf_clauses": clauses,
        "canonical_edge_variables": canonical,
        "canonical_unit_literals": units,
        "edge_order_sha256": stable_hash(edges),
        "triangle_order_sha256": stable_hash(triangles),
        "cnf_sha256": file_hash(cnf),
        "exhaustiveness": (
            "Every nonmonochromatic red/blue K4 is, under S4 and global "
            "color swap, either a matching/C4 coloring or a P4/P4 coloring."
        ),
        "SAT_consequence": (
            "A model is a full KG(12,3) coloring, proving R_3^KG(3,3)=13 "
            "using the published upper bound."
        ),
        "joint_UNSAT_consequence": (
            "If both canonical branches have checked UNSAT proofs, then "
            "R_3^KG(3,3)=12 using the five-point lower bound."
        ),
    }
    metadata.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(json.dumps(record, indent=2, sort_keys=True))


def parse_model(path: Path, variables: int) -> list[bool]:
    status = None
    literals: list[int] = []
    for raw in path.read_text(errors="replace").splitlines():
        line = raw.strip()
        if line.startswith("s "):
            status = line[2:].strip()
        elif line.startswith("v "):
            for token in line[2:].split():
                literal = int(token)
                if literal:
                    literals.append(literal)
    if status != "SATISFIABLE":
        raise ValueError(f"expected SATISFIABLE, observed {status!r}")
    values: list[bool | None] = [None] * (variables + 1)
    for literal in literals:
        variable = abs(literal)
        if not 1 <= variable <= variables:
            raise ValueError(f"model variable {variable} outside 1..{variables}")
        value = literal > 0
        if values[variable] is not None and values[variable] != value:
            raise ValueError(f"contradictory assignment for variable {variable}")
        values[variable] = value
    missing = [i for i in range(1, variables + 1) if values[i] is None]
    if missing:
        raise ValueError(f"partial model: {len(missing)} variables missing")
    return [bool(value) for value in values[1:]]


def pack_hex(values: Iterable[bool]) -> str:
    bits = list(values)
    packed = bytearray((len(bits) + 7) // 8)
    for i, value in enumerate(bits):
        if value:
            packed[i // 8] |= 1 << (i % 8)
    return packed.hex()


def verify_model(branch: str, solver_output: Path, certificate: Path) -> None:
    _vertices, edges, triangles, canonical = build_instance()
    values = parse_model(solver_output, len(edges))
    for literal in units_for(branch, canonical):
        observed = values[abs(literal) - 1]
        if observed != (literal > 0):
            raise AssertionError((literal, observed))

    one_red = two_red = 0
    for triangle in triangles:
        count = sum(values[variable - 1] for variable in triangle)
        if count == 1:
            one_red += 1
        elif count == 2:
            two_red += 1
        else:
            raise AssertionError(f"monochromatic triangle {triangle}")

    model_hex = pack_hex(values)
    record = {
        "result": "SAT",
        "branch": branch,
        "edges_checked": len(edges),
        "triangles_checked": len(triangles),
        "monochromatic_triangles": 0,
        "triangles_with_one_red_edge": one_red,
        "triangles_with_two_red_edges": two_red,
        "red_edges": sum(values),
        "blue_edges": len(values) - sum(values),
        "edge_order_sha256": stable_hash(edges),
        "model_hex": model_hex,
        "model_hex_sha256": hashlib.sha256(model_hex.encode()).hexdigest(),
        "ramsey_consequence": (
            "R_3^KG(3,3)=13, conditional only on the published upper bound <=13"
        ),
    }
    certificate.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(json.dumps(record, indent=2, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", choices=("matching", "path"), required=True)
    sub = parser.add_subparsers(dest="command", required=True)
    gen = sub.add_parser("generate")
    gen.add_argument("--cnf", type=Path, required=True)
    gen.add_argument("--metadata", type=Path, required=True)
    verify = sub.add_parser("verify-model")
    verify.add_argument("--solver-output", type=Path, required=True)
    verify.add_argument("--certificate", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "generate":
        generate(args.branch, args.cnf, args.metadata)
    else:
        verify_model(args.branch, args.solver_output, args.certificate)


if __name__ == "__main__":
    main()
