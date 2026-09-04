#!/usr/bin/env python3
"""Generate a propagation-strengthened exact SAT instance for KG(12,3).

The base formula forbids monochromatic edge-triangles. For every partition of
the twelve points into four triples, the induced K4 also has no monochromatic
three-edge star: if a star were red, its opposite triangle would be forced
blue, and conversely. These star NAE clauses are logically redundant but
substantially improve propagation.

The matching/C4 and P4/P4 canonical branches are exhaustive under S4 and a
global color swap. SAT models are checked by the independent base verifier;
checked UNSAT proofs for both branches decide the exact value 12.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path

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


def build():
    vertices = list(itertools.combinations(range(N), R))
    masks = [sum(1 << x for x in vertex) for vertex in vertices]
    vertex_id = {vertex: i for i, vertex in enumerate(vertices)}
    edges: list[tuple[int, int]] = []
    edge_id: dict[tuple[int, int], int] = {}
    for i, a in enumerate(masks):
        for j in range(i + 1, len(vertices)):
            if a & masks[j] == 0:
                edge_id[(i, j)] = len(edges) + 1
                edges.append((i, j))

    triangles: list[tuple[int, int, int]] = []
    four_blocks: list[tuple[int, int, int, int]] = []
    for i in range(len(vertices)):
        for j in range(i + 1, len(vertices)):
            if masks[i] & masks[j]:
                continue
            for k in range(j + 1, len(vertices)):
                if (masks[i] | masks[j]) & masks[k]:
                    continue
                triangles.append((edge_id[(i, j)], edge_id[(i, k)], edge_id[(j, k)]))
                used = masks[i] | masks[j] | masks[k]
                remaining = ((1 << N) - 1) ^ used
                if remaining.bit_count() == R:
                    l = next(index for index, mask in enumerate(masks) if mask == remaining)
                    if l > k:
                        four_blocks.append((i, j, k, l))

    stars: list[tuple[int, int, int]] = []
    for block in four_blocks:
        for center_pos in range(4):
            center = block[center_pos]
            others = [block[pos] for pos in range(4) if pos != center_pos]
            row = []
            for other in others:
                a, b = sorted((center, other))
                row.append(edge_id[(a, b)])
            stars.append(tuple(sorted(row)))

    assert (len(vertices), len(edges), len(triangles), len(four_blocks), len(stars)) == (220, 9240, 61600, 15400, 61600)
    assert len(set(stars)) == len(stars)
    return vertices, vertex_id, edges, edge_id, triangles, four_blocks, stars


def canonical_units(branch: str, vertex_id, edge_id):
    blocks = [vertex_id[(0, 1, 2)], vertex_id[(3, 4, 5)], vertex_id[(6, 7, 8)], vertex_id[(9, 10, 11)]]
    names = ("AB", "AC", "AD", "BC", "BD", "CD")
    pairs = ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))
    named = {name: edge_id[tuple(sorted((blocks[i], blocks[j])))] for name, (i, j) in zip(names, pairs)}
    if branch == "matching":
        red = {"AB", "CD"}
    elif branch == "path":
        red = {"AB", "BD", "CD"}
    else:
        raise ValueError(branch)
    return [variable if name in red else -variable for name, variable in named.items()]


def generate(branch: str, cnf: Path, metadata: Path) -> None:
    vertices, vertex_id, edges, edge_id, triangles, four_blocks, stars = build()
    units = canonical_units(branch, vertex_id, edge_id)
    clause_count = 2 * (len(triangles) + len(stars)) + len(units)
    with cnf.open("w", encoding="ascii", newline="\n") as out:
        out.write(f"c Exact KG(12,3), canonical K4 {branch}, with redundant K4-star NAE clauses\n")
        out.write(f"p cnf {len(edges)} {clause_count}\n")
        for family in (triangles, stars):
            for x, y, z in family:
                out.write(f"{x} {y} {z} 0\n")
                out.write(f"-{x} -{y} -{z} 0\n")
        for literal in units:
            out.write(f"{literal} 0\n")

    record = {
        "scope": "exact exhaustive canonical-K4 branch",
        "branch": branch,
        "vertices": len(vertices),
        "edge_variables": len(edges),
        "kneser_triangles": len(triangles),
        "four_block_partitions": len(four_blocks),
        "redundant_k4_star_constraints": len(stars),
        "cnf_clauses": clause_count,
        "canonical_unit_literals": units,
        "edge_order_sha256": stable_hash(edges),
        "triangle_order_sha256": stable_hash(triangles),
        "four_block_order_sha256": stable_hash(four_blocks),
        "star_order_sha256": stable_hash(stars),
        "cnf_sha256": file_hash(cnf),
        "star_redundancy_proof": (
            "A monochromatic star in a K4 forces the opposite triangle to the other color by the three incident triangle constraints."
        ),
        "joint_UNSAT_consequence": (
            "Checked UNSAT for matching and path branches proves R_3^KG(3,3)=12 using the verified lower bound."
        ),
        "SAT_consequence": "A checked model proves R_3^KG(3,3)=13 using the published upper bound.",
    }
    metadata.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(json.dumps(record, indent=2, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", choices=("matching", "path"), required=True)
    parser.add_argument("--cnf", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    args = parser.parse_args()
    generate(args.branch, args.cnf, args.metadata)


if __name__ == "__main__":
    main()
