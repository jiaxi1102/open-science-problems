#!/usr/bin/env python3
"""Exact SAT encoding for monochromatic-triangle-free colorings of KG(12,3).

Variables encode colors of Kneser edges. For every Kneser triangle, the two
3-literal clauses enforce not-all-equal. A canonical triangle is fixed to the
pattern 0,0,1 using ground-set and global-color symmetry.

Usage:
  python search_kneser_r3_exact.py generate output.cnf [metadata.json]
  python search_kneser_r3_exact.py verify solver-output.txt [metadata.json]
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


def build_instance():
    vertices = list(itertools.combinations(range(N), R))
    vertex_id = {v: i for i, v in enumerate(vertices)}

    edges: list[tuple[int, int]] = []
    edge_id: dict[tuple[int, int], int] = {}
    for i, a in enumerate(vertices):
        sa = set(a)
        for j in range(i + 1, len(vertices)):
            if sa.isdisjoint(vertices[j]):
                edge_id[(i, j)] = len(edges) + 1  # DIMACS variables are 1-based.
                edges.append((i, j))

    triangles: list[tuple[int, int, int]] = []
    universe = set(range(N))
    for i, a in enumerate(vertices):
        rem_a = universe.difference(a)
        for b in itertools.combinations(sorted(rem_a), R):
            j = vertex_id[b]
            if j <= i:
                continue
            rem_ab = rem_a.difference(b)
            for c in itertools.combinations(sorted(rem_ab), R):
                k = vertex_id[c]
                if k <= j:
                    continue
                triangles.append((
                    edge_id[(i, j)],
                    edge_id[(i, k)],
                    edge_id[(j, k)],
                ))

    assert len(vertices) == 220
    assert len(edges) == 9240
    assert len(triangles) == 61600
    assert len(set(triangles)) == len(triangles)

    # Every satisfying coloring can be carried by a permutation of [12] and,
    # if needed, global color complementation to this canonical pattern.
    a = vertex_id[(0, 1, 2)]
    b = vertex_id[(3, 4, 5)]
    c = vertex_id[(6, 7, 8)]
    canonical = (
        edge_id[tuple(sorted((a, b)))],
        edge_id[tuple(sorted((a, c)))],
        edge_id[tuple(sorted((b, c)))],
    )
    return vertices, edges, triangles, canonical


def clauses_for(triangles, canonical) -> Iterable[tuple[int, ...]]:
    for a, b, c in triangles:
        yield (a, b, c)
        yield (-a, -b, -c)
    # Fixed canonical NAE pattern: 0, 0, 1.
    yield (-canonical[0],)
    yield (-canonical[1],)
    yield (canonical[2],)


def generate(cnf_path: Path, metadata_path: Path | None) -> None:
    vertices, edges, triangles, canonical = build_instance()
    num_vars = len(edges)
    num_clauses = 2 * len(triangles) + 3

    digest = hashlib.sha256()
    with cnf_path.open("w", encoding="ascii", newline="\n") as f:
        header = f"p cnf {num_vars} {num_clauses}\n"
        f.write(header)
        digest.update(header.encode("ascii"))
        for clause in clauses_for(triangles, canonical):
            line = " ".join(map(str, clause)) + " 0\n"
            f.write(line)
            digest.update(line.encode("ascii"))

    metadata = {
        "problem": (
            "Does KG(12,3) admit a red/blue edge-coloring with no "
            "monochromatic triangle?"
        ),
        "n": N,
        "r": R,
        "vertices": len(vertices),
        "edges": len(edges),
        "triangles": len(triangles),
        "variables": num_vars,
        "clauses": num_clauses,
        "canonical_triangle_variables": canonical,
        "canonical_pattern": [0, 0, 1],
        "cnf_sha256": digest.hexdigest(),
        "edge_order": (
            "lexicographic vertex IDs; vertices are lexicographic 3-subsets "
            "of range(12)"
        ),
    }
    if metadata_path:
        metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    print(json.dumps(metadata, indent=2, sort_keys=True))


def parse_model(text: str) -> tuple[str, dict[int, bool]]:
    status = "UNKNOWN"
    assignment: dict[int, bool] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("s "):
            if "UNSATISFIABLE" in line:
                status = "UNSAT"
            elif "SATISFIABLE" in line:
                status = "SAT"
        elif line.startswith("v "):
            for token in line[2:].split():
                lit = int(token)
                if lit == 0:
                    continue
                assignment[abs(lit)] = lit > 0
    return status, assignment


def verify(output_path: Path, metadata_path: Path | None) -> None:
    _, edges, triangles, canonical = build_instance()
    status, assignment = parse_model(output_path.read_text(errors="replace"))
    if status == "UNSAT":
        print(json.dumps({
            "status": "UNSAT",
            "warning": (
                "Solver status only; an independently checked proof certificate "
                "is still required."
            ),
        }, indent=2))
        return
    if status != "SAT":
        raise SystemExit("solver output has no SAT/UNSAT status")
    if len(assignment) < len(edges):
        missing = [i for i in range(1, len(edges) + 1) if i not in assignment]
        raise SystemExit(f"incomplete model: {len(missing)} variables missing")

    assert not assignment[canonical[0]]
    assert not assignment[canonical[1]]
    assert assignment[canonical[2]]

    mono = []
    one_true = 0
    two_true = 0
    for tri in triangles:
        colors = tuple(assignment[x] for x in tri)
        if colors[0] == colors[1] == colors[2]:
            mono.append(tri)
        elif sum(colors) == 1:
            one_true += 1
        else:
            two_true += 1
    if mono:
        raise SystemExit(f"invalid model: {len(mono)} monochromatic triangles")

    bits = "".join("1" if assignment[i] else "0" for i in range(1, len(edges) + 1))
    result = {
        "status": "SAT",
        "variables_assigned": len(assignment),
        "monochromatic_triangles": 0,
        "triangles_with_one_true_edge": one_true,
        "triangles_with_two_true_edges": two_true,
        "model_bits_sha256": hashlib.sha256(bits.encode("ascii")).hexdigest(),
    }
    if metadata_path and metadata_path.exists():
        result["metadata"] = json.loads(metadata_path.read_text())
    print(json.dumps(result, indent=2, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_gen = sub.add_parser("generate")
    p_gen.add_argument("cnf", type=Path)
    p_gen.add_argument("metadata", type=Path, nargs="?")
    p_ver = sub.add_parser("verify")
    p_ver.add_argument("solver_output", type=Path)
    p_ver.add_argument("metadata", type=Path, nargs="?")
    args = parser.parse_args()
    if args.cmd == "generate":
        generate(args.cnf, args.metadata)
    else:
        verify(args.solver_output, args.metadata)


if __name__ == "__main__":
    main()
