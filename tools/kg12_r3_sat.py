#!/usr/bin/env python3
"""Generate and independently check the exact KG(12,3) Ramsey SAT instance.

Variables are the edges of KG(12,3): one Boolean per unordered pair of
disjoint 3-subsets of [12]. True is red and False is blue. For every
Kneser triangle, two NAE clauses forbid all-blue and all-red.

A canonical triangle is symmetry-fixed to one red and two blue edges.
This is without loss of generality: any nonmonochromatic triangle can be
mapped to the canonical partition by a permutation of [12], and a global
color swap makes its unique minority color red.
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

Vertex = tuple[int, int, int]
Edge = tuple[int, int]
Triangle = tuple[int, int, int]


def build_instance() -> tuple[list[Vertex], list[Edge], list[Triangle], tuple[int, int, int]]:
    vertices: list[Vertex] = list(itertools.combinations(range(N), R))
    vertex_id = {v: i for i, v in enumerate(vertices)}

    edges: list[Edge] = []
    edge_id: dict[Edge, int] = {}
    for i, a in enumerate(vertices):
        a_set = set(a)
        for j in range(i + 1, len(vertices)):
            if a_set.isdisjoint(vertices[j]):
                edge_id[(i, j)] = len(edges) + 1
                edges.append((i, j))

    triangles: list[Triangle] = []
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
                    (
                        edge_id[(i, j)],
                        edge_id[(i, k)],
                        edge_id[(j, k)],
                    )
                )

    a = vertex_id[(0, 1, 2)]
    b = vertex_id[(3, 4, 5)]
    c = vertex_id[(6, 7, 8)]
    symmetry = (
        edge_id[tuple(sorted((a, b)))],
        edge_id[tuple(sorted((a, c)))],
        edge_id[tuple(sorted((b, c)))],
    )

    assert len(vertices) == 220
    assert len(edges) == 9240
    assert len(triangles) == 61600
    assert len(set(triangles)) == len(triangles)
    return vertices, edges, triangles, symmetry


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_json_hash(value: object) -> str:
    payload = json.dumps(value, separators=(",", ":"), sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()


def generate(cnf_path: Path, metadata_path: Path) -> None:
    vertices, edges, triangles, symmetry = build_instance()
    clauses = 2 * len(triangles) + 3

    with cnf_path.open("w", encoding="ascii", newline="\n") as out:
        out.write("c Exact triangle-Ramsey instance for KG(12,3)\n")
        out.write("c variable true=red false=blue\n")
        out.write("c symmetry: AB red, AC blue, BC blue for canonical disjoint triples\n")
        out.write(f"p cnf {len(edges)} {clauses}\n")
        for x, y, z in triangles:
            out.write(f"{x} {y} {z} 0\n")
            out.write(f"-{x} -{y} -{z} 0\n")
        ab, ac, bc = symmetry
        out.write(f"{ab} 0\n")
        out.write(f"-{ac} 0\n")
        out.write(f"-{bc} 0\n")

    metadata = {
        "problem": "Does KG(12,3) admit a red/blue edge coloring without a monochromatic triangle?",
        "ramsey_consequence": {
            "SAT": "R_3^KG(3,3)=13, using the published upper bound 13",
            "UNSAT": "R_3^KG(3,3)=12, using the five-point lower bound 12",
        },
        "n": N,
        "r": R,
        "vertices": len(vertices),
        "edges_or_boolean_variables": len(edges),
        "kneser_triangles": len(triangles),
        "cnf_clauses": clauses,
        "encoding": "two NAE clauses per Kneser triangle",
        "symmetry_breaking": {
            "canonical_vertices": [[0, 1, 2], [3, 4, 5], [6, 7, 8]],
            "canonical_edge_variables_ab_ac_bc": list(symmetry),
            "forced_colors_ab_ac_bc": ["red", "blue", "blue"],
            "justification": (
                "Every valid coloring makes this triangle nonmonochromatic. "
                "A global color swap makes the minority color red, and a "
                "ground-set permutation maps the unique red edge to AB."
            ),
        },
        "vertex_order_sha256": stable_json_hash(vertices),
        "edge_order_sha256": stable_json_hash(edges),
        "triangle_order_sha256": stable_json_hash(triangles),
        "cnf_sha256": sha256_file(cnf_path),
    }
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    print(json.dumps(metadata, indent=2, sort_keys=True))


def parse_kissat_model(path: Path, num_vars: int) -> list[bool]:
    status: str | None = None
    literals: list[int] = []
    for raw in path.read_text(errors="replace").splitlines():
        line = raw.strip()
        if line.startswith("s "):
            status = line[2:].strip()
        elif line.startswith("v "):
            for token in line[2:].split():
                lit = int(token)
                if lit:
                    literals.append(lit)
    if status != "SATISFIABLE":
        raise ValueError(f"expected SATISFIABLE output, observed {status!r}")
    values: list[bool | None] = [None] * (num_vars + 1)
    for lit in literals:
        var = abs(lit)
        if not 1 <= var <= num_vars:
            raise ValueError(f"model literal {lit} outside 1..{num_vars}")
        value = lit > 0
        if values[var] is not None and values[var] != value:
            raise ValueError(f"contradictory assignments for variable {var}")
        values[var] = value
    missing = [i for i in range(1, num_vars + 1) if values[i] is None]
    if missing:
        raise ValueError(f"model is partial; missing {len(missing)} variables")
    return [bool(x) for x in values[1:]]


def pack_model_hex(values: Iterable[bool]) -> str:
    bits = list(values)
    packed = bytearray((len(bits) + 7) // 8)
    for i, value in enumerate(bits):
        if value:
            packed[i // 8] |= 1 << (i % 8)
    return packed.hex()


def verify_model(solver_output: Path, certificate_path: Path) -> None:
    vertices, edges, triangles, symmetry = build_instance()
    values = parse_kissat_model(solver_output, len(edges))

    bad: list[tuple[int, Triangle]] = []
    one_red = 0
    two_red = 0
    for index, triangle in enumerate(triangles):
        count = sum(values[var - 1] for var in triangle)
        if count == 1:
            one_red += 1
        elif count == 2:
            two_red += 1
        else:
            bad.append((index, triangle))
            if len(bad) >= 10:
                break
    if bad:
        raise AssertionError(f"monochromatic triangles found: {bad}")

    ab, ac, bc = symmetry
    observed = (values[ab - 1], values[ac - 1], values[bc - 1])
    if observed != (True, False, False):
        raise AssertionError(f"symmetry units violated: {observed}")

    model_hex = pack_model_hex(values)
    certificate = {
        "result": "SAT",
        "interpretation": "KG(12,3) has a red/blue edge coloring with no monochromatic triangle",
        "ramsey_consequence": "R_3^KG(3,3)=13, conditional only on the published upper bound R_3^KG(3,3)<=13",
        "vertices": len(vertices),
        "edges_checked": len(edges),
        "triangles_checked": len(triangles),
        "monochromatic_triangles": 0,
        "triangles_with_one_red_edge": one_red,
        "triangles_with_two_red_edges": two_red,
        "red_edges": sum(values),
        "blue_edges": len(values) - sum(values),
        "edge_order_sha256": stable_json_hash(edges),
        "model_bit_order": "edge variables 1..9240, least-significant bit first within each byte",
        "model_hex": model_hex,
        "model_hex_sha256": hashlib.sha256(model_hex.encode()).hexdigest(),
        "solver_output_sha256": sha256_file(solver_output),
        "canonical_edge_variables_ab_ac_bc": list(symmetry),
        "canonical_colors_ab_ac_bc": ["red", "blue", "blue"],
    }
    certificate_path.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    print(json.dumps(certificate, indent=2, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("generate")
    gen.add_argument("--cnf", type=Path, required=True)
    gen.add_argument("--metadata", type=Path, required=True)

    verify = sub.add_parser("verify-model")
    verify.add_argument("--solver-output", type=Path, required=True)
    verify.add_argument("--certificate", type=Path, required=True)

    args = parser.parse_args()
    if args.command == "generate":
        generate(args.cnf, args.metadata)
    elif args.command == "verify-model":
        verify_model(args.solver_output, args.certificate)


if __name__ == "__main__":
    main()
