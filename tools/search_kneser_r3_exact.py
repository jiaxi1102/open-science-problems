#!/usr/bin/env python3
"""Exact SAT encoding for triangle-free two-colorings of ``KG(12,3)``.

One Boolean variable is assigned to every Kneser edge.  Every Kneser triangle
contributes the two clauses that forbid its three edge colors from being all
zero or all one.

The base encoding fixes one canonical Kneser triangle to ``0,0,1``.  Optional
``--k4-case`` values split all solutions into the two possible color-isomorphism
types on the unique fourth triple completing that triangle to a Kneser K4.
All DIMACS identifiers are obtained by symbolic lookup and asserted against a
known manifest; no hand-copied variable numbers are used.
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
BLOCKS = (
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (9, 10, 11),
)


def build_instance():
    vertices = list(itertools.combinations(range(N), R))
    vertex_id = {v: i for i, v in enumerate(vertices)}

    edges: list[tuple[int, int]] = []
    edge_id: dict[tuple[int, int], int] = {}
    for i, a in enumerate(vertices):
        sa = set(a)
        for j in range(i + 1, len(vertices)):
            if sa.isdisjoint(vertices[j]):
                edge_id[(i, j)] = len(edges) + 1
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

    block_ids = [vertex_id[block] for block in BLOCKS]

    def block_edge(i: int, j: int) -> int:
        x, y = sorted((block_ids[i], block_ids[j]))
        return edge_id[(x, y)]

    k4 = {
        "AB": block_edge(0, 1),
        "AC": block_edge(0, 2),
        "BC": block_edge(1, 2),
        "AD": block_edge(0, 3),
        "BD": block_edge(1, 3),
        "CD": block_edge(2, 3),
    }
    expected = {
        "AB": 1,
        "AC": 65,
        "BC": 8401,
        "AD": 84,
        "BD": 8420,
        "CD": 9231,
    }

    assert len(vertices) == 220
    assert len(edges) == 9240
    assert len(triangles) == 61600
    assert len(set(triangles)) == len(triangles)
    assert k4 == expected, (k4, expected)
    return vertices, edges, triangles, k4


def branch_units(k4: dict[str, int], case: str) -> list[int]:
    if case == "none":
        return []

    # The base units are AB=0, AC=0, BC=1.  The three triangles involving D
    # imply AD=1 and not(BD=1 and CD=1).  Swapping B and C preserves the base
    # pattern, so every solution has an isomorphic representative with BD=0.
    # CD then distinguishes the only two K4 color-isomorphism types.
    common = [k4["AD"], -k4["BD"]]
    if case == "cycle-matching":
        return common + [-k4["CD"]]
    if case == "path-path":
        return common + [k4["CD"]]
    raise ValueError(f"unknown K4 case: {case}")


def clauses_for(
    triangles: Iterable[tuple[int, int, int]],
    k4: dict[str, int],
    case: str,
) -> Iterable[tuple[int, ...]]:
    for a, b, c in triangles:
        yield (a, b, c)
        yield (-a, -b, -c)

    # A canonical nonmonochromatic triangle, without loss of generality under
    # S_12 and global color complementation.
    yield (-k4["AB"],)
    yield (-k4["AC"],)
    yield (k4["BC"],)

    for literal in branch_units(k4, case):
        yield (literal,)


def generate(cnf_path: Path, metadata_path: Path | None, case: str) -> None:
    vertices, edges, triangles, k4 = build_instance()
    clauses = list(clauses_for(triangles, k4, case))

    digest = hashlib.sha256()
    with cnf_path.open("w", encoding="ascii", newline="\n") as handle:
        header = f"p cnf {len(edges)} {len(clauses)}\n"
        handle.write(header)
        digest.update(header.encode("ascii"))
        for clause in clauses:
            line = " ".join(map(str, clause)) + " 0\n"
            handle.write(line)
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
        "variables": len(edges),
        "clauses": len(clauses),
        "canonical_blocks": BLOCKS,
        "canonical_k4_variables": k4,
        "canonical_triangle_pattern": {"AB": 0, "AC": 0, "BC": 1},
        "k4_case": case,
        "branch_unit_literals": branch_units(k4, case),
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
                literal = int(token)
                if literal:
                    assignment[abs(literal)] = literal > 0
    return status, assignment


def verify(output_path: Path, metadata_path: Path | None) -> None:
    _, edges, triangles, k4 = build_instance()
    metadata = json.loads(metadata_path.read_text()) if metadata_path else {}
    status, assignment = parse_model(output_path.read_text(errors="replace"))
    if status == "UNSAT":
        print(json.dumps({
            "status": "UNSAT",
            "warning": (
                "Solver status only; an independently checked proof trace is "
                "required before this is mathematical evidence."
            ),
        }, indent=2))
        return
    if status != "SAT":
        raise SystemExit("solver output has no SAT/UNSAT status")
    missing = [i for i in range(1, len(edges) + 1) if i not in assignment]
    if missing:
        raise SystemExit(f"incomplete model: {len(missing)} variables missing")

    assert not assignment[k4["AB"]]
    assert not assignment[k4["AC"]]
    assert assignment[k4["BC"]]
    for literal in metadata.get("branch_unit_literals", []):
        assert assignment[abs(literal)] == (literal > 0)

    mono = []
    one_true = 0
    two_true = 0
    for triangle in triangles:
        colors = tuple(assignment[x] for x in triangle)
        if colors[0] == colors[1] == colors[2]:
            mono.append(triangle)
        elif sum(colors) == 1:
            one_true += 1
        else:
            two_true += 1
    if mono:
        raise SystemExit(f"invalid model: {len(mono)} monochromatic triangles")

    bits = "".join("1" if assignment[i] else "0" for i in range(1, len(edges) + 1))
    print(json.dumps({
        "status": "SAT",
        "variables_assigned": len(assignment),
        "monochromatic_triangles": 0,
        "triangles_with_one_true_edge": one_true,
        "triangles_with_two_true_edges": two_true,
        "model_bits_sha256": hashlib.sha256(bits.encode("ascii")).hexdigest(),
        "metadata": metadata,
    }, indent=2, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_gen = sub.add_parser("generate")
    p_gen.add_argument("cnf", type=Path)
    p_gen.add_argument("metadata", type=Path, nargs="?")
    p_gen.add_argument(
        "--k4-case",
        choices=("none", "cycle-matching", "path-path"),
        default="none",
    )
    p_ver = sub.add_parser("verify")
    p_ver.add_argument("solver_output", type=Path)
    p_ver.add_argument("metadata", type=Path, nargs="?")
    args = parser.parse_args()
    if args.cmd == "generate":
        generate(args.cnf, args.metadata, args.k4_case)
    else:
        verify(args.solver_output, args.metadata)


if __name__ == "__main__":
    main()
