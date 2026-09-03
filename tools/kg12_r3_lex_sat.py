#!/usr/bin/env python3
"""Generate exact KG(12,3) SAT branches with rigorous lex symmetry breaking.

After fixing one four-block partition to either the matching/C4 or P4/P4
canonical coloring, a large stabilizer remains:

* arbitrary S3 permutations inside each of the four triples;
* block automorphisms preserving the chosen canonical edge coloring.

For every listed stabilizer generator g, this encoder imposes

    x <=_lex g(x)

on a deterministic prefix of the 9,240 edge-color vector. These constraints
are satisfiability-preserving: in every orbit of the generated stabilizer,
choose an assignment whose projected prefix is lexicographically least; it
satisfies all of the inequalities simultaneously.

The exact triangle clauses and the logically redundant K4-star clauses are
both retained. SAT is checked against the original unrestricted instance.
Checked UNSAT for both canonical branches proves the exact value 12.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path

N = 12
R = 3
BLOCKS = ((0, 1, 2), (3, 4, 5), (6, 7, 8), (9, 10, 11))


class CNF:
    def __init__(self, first_aux: int):
        self.next_var = first_aux
        self.clauses: list[tuple[int, ...]] = []

    def aux(self) -> int:
        value = self.next_var
        self.next_var += 1
        return value

    def add(self, *literals: int) -> None:
        values = set(literals)
        if any(-literal in values for literal in values):
            return
        self.clauses.append(tuple(literals))


def stable_hash(value: object) -> str:
    payload = json.dumps(value, separators=(",", ":"), sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_graph():
    vertices = list(itertools.combinations(range(N), R))
    masks = [sum(1 << x for x in vertex) for vertex in vertices]
    vertex_id = {vertex: i for i, vertex in enumerate(vertices)}
    mask_to_vertex = {mask: i for i, mask in enumerate(masks)}

    edges: list[tuple[int, int]] = []
    edge_id: dict[tuple[int, int], int] = {}
    for i, a in enumerate(masks):
        for j in range(i + 1, len(vertices)):
            if a & masks[j] == 0:
                edge_id[(i, j)] = len(edges)
                edges.append((i, j))

    triangles: list[tuple[int, int, int]] = []
    four_blocks: list[tuple[int, int, int, int]] = []
    full_mask = (1 << N) - 1
    for i in range(len(vertices)):
        for j in range(i + 1, len(vertices)):
            if masks[i] & masks[j]:
                continue
            for k in range(j + 1, len(vertices)):
                if (masks[i] | masks[j]) & masks[k]:
                    continue
                triangles.append((edge_id[(i, j)], edge_id[(i, k)], edge_id[(j, k)]))
                remaining = full_mask ^ (masks[i] | masks[j] | masks[k])
                l = mask_to_vertex[remaining]
                if l > k:
                    four_blocks.append((i, j, k, l))

    stars: list[tuple[int, int, int]] = []
    for block in four_blocks:
        for center in block:
            row = []
            for other in block:
                if other == center:
                    continue
                row.append(edge_id[tuple(sorted((center, other)))])
            stars.append(tuple(sorted(row)))

    assert (len(vertices), len(edges), len(triangles), len(four_blocks), len(stars)) == (
        220, 9240, 61600, 15400, 61600
    )
    assert len(set(stars)) == len(stars)
    return vertices, masks, vertex_id, mask_to_vertex, edges, edge_id, triangles, stars


def permutation_from_block_map(block_map: tuple[int, int, int, int]) -> tuple[int, ...]:
    permutation = list(range(N))
    for source_block, target_block in enumerate(block_map):
        for offset in range(3):
            permutation[BLOCKS[source_block][offset]] = BLOCKS[target_block][offset]
    return tuple(permutation)


def internal_generators() -> list[tuple[str, tuple[int, ...]]]:
    generators: list[tuple[str, tuple[int, ...]]] = []
    for block_index, block in enumerate(BLOCKS):
        a, b, c = block
        transposition = list(range(N))
        transposition[a], transposition[b] = b, a
        generators.append((f"block_{block_index}_swap01", tuple(transposition)))

        cycle = list(range(N))
        cycle[a], cycle[b], cycle[c] = b, c, a
        generators.append((f"block_{block_index}_cycle012", tuple(cycle)))
    return generators


def stabilizer_generators(branch: str) -> list[tuple[str, tuple[int, ...]]]:
    generators = internal_generators()
    if branch == "matching":
        generators.extend(
            [
                ("swap_A_B", permutation_from_block_map((1, 0, 2, 3))),
                ("swap_C_D", permutation_from_block_map((0, 1, 3, 2))),
                ("swap_red_pairs", permutation_from_block_map((2, 3, 0, 1))),
            ]
        )
    elif branch == "path":
        # Reverse the red path A-B-D-C.
        generators.append(("reverse_red_path", permutation_from_block_map((2, 3, 0, 1))))
    else:
        raise ValueError(branch)
    for name, permutation in generators:
        if sorted(permutation) != list(range(N)):
            raise AssertionError((name, permutation))
    return generators


def canonical_units(branch: str, vertex_id, edge_id) -> list[int]:
    block_vertices = [vertex_id[tuple(block)] for block in BLOCKS]
    names = ("AB", "AC", "AD", "BC", "BD", "CD")
    pairs = ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))
    named = {
        name: edge_id[tuple(sorted((block_vertices[i], block_vertices[j])))] + 1
        for name, (i, j) in zip(names, pairs)
    }
    if branch == "matching":
        red = {"AB", "CD"}
    elif branch == "path":
        red = {"AB", "BD", "CD"}
    else:
        raise ValueError(branch)
    return [variable if name in red else -variable for name, variable in named.items()]


def edge_action(
    permutation: tuple[int, ...],
    vertices,
    mask_to_vertex,
    edges,
    edge_id,
) -> list[int]:
    vertex_image = []
    for vertex in vertices:
        image_mask = sum(1 << permutation[x] for x in vertex)
        vertex_image.append(mask_to_vertex[image_mask])
    action = []
    for i, j in edges:
        a, b = sorted((vertex_image[i], vertex_image[j]))
        action.append(edge_id[(a, b)])
    assert sorted(action) == list(range(len(edges)))
    return action


def add_equivalence(cnf: CNF, q: int, a: int, b: int) -> None:
    # q <-> (a == b).
    cnf.add(a, b, q)
    cnf.add(-a, -b, q)
    cnf.add(a, -b, -q)
    cnf.add(-a, b, -q)


def add_prefix_equivalence(cnf: CNF, q: int, previous: int, a: int, b: int) -> None:
    # q <-> previous AND (a == b).
    cnf.add(-q, previous)
    cnf.add(-q, -a, b)
    cnf.add(-q, a, -b)
    cnf.add(-previous, a, b, q)
    cnf.add(-previous, -a, -b, q)


def add_lex_leader(cnf: CNF, action: list[int], prefix_length: int) -> dict[str, int]:
    differing = [i for i in range(min(prefix_length, len(action))) if action[i] != i]
    if not differing:
        return {"differing_positions": 0, "aux_variables": 0, "clauses": 0}
    before_clauses = len(cnf.clauses)
    before_aux = cnf.next_var
    previous: int | None = None
    for position in differing:
        a = position + 1
        b = action[position] + 1
        if previous is None:
            # At the first differing coordinate, forbid a=1,b=0.
            cnf.add(-a, b)
            q = cnf.aux()
            add_equivalence(cnf, q, a, b)
        else:
            # If every previous differing coordinate agrees, forbid 1>0 here.
            cnf.add(-previous, -a, b)
            q = cnf.aux()
            add_prefix_equivalence(cnf, q, previous, a, b)
        previous = q
    return {
        "differing_positions": len(differing),
        "aux_variables": cnf.next_var - before_aux,
        "clauses": len(cnf.clauses) - before_clauses,
    }


def generate(branch: str, prefix_length: int, cnf_path: Path, metadata_path: Path) -> None:
    vertices, _masks, vertex_id, mask_to_vertex, edges, edge_id, triangles, stars = build_graph()
    cnf = CNF(first_aux=len(edges) + 1)

    for family in (triangles, stars):
        for x, y, z in family:
            a, b, c = x + 1, y + 1, z + 1
            cnf.add(a, b, c)
            cnf.add(-a, -b, -c)
    units = canonical_units(branch, vertex_id, edge_id)
    for literal in units:
        cnf.add(literal)

    generator_records = []
    for name, permutation in stabilizer_generators(branch):
        action = edge_action(permutation, vertices, mask_to_vertex, edges, edge_id)
        stats = add_lex_leader(cnf, action, prefix_length)
        generator_records.append(
            {
                "name": name,
                "point_permutation": list(permutation),
                "edge_action_sha256": stable_hash(action),
                **stats,
            }
        )

    variable_count = cnf.next_var - 1
    with cnf_path.open("w", encoding="ascii", newline="\n") as out:
        out.write(f"c Exact KG(12,3) branch={branch} with stabilizer lex leaders\n")
        out.write(f"p cnf {variable_count} {len(cnf.clauses)}\n")
        for clause in cnf.clauses:
            out.write(" ".join(map(str, clause)) + " 0\n")

    record = {
        "scope": "exact satisfiability-preserving symmetry reduction",
        "branch": branch,
        "original_edge_variables": len(edges),
        "total_cnf_variables": variable_count,
        "total_cnf_clauses": len(cnf.clauses),
        "triangle_constraints": len(triangles),
        "redundant_star_constraints": len(stars),
        "lex_prefix_length": prefix_length,
        "stabilizer_generators": generator_records,
        "canonical_unit_literals": units,
        "edge_order_sha256": stable_hash(edges),
        "triangle_order_sha256": stable_hash(triangles),
        "star_order_sha256": stable_hash(stars),
        "cnf_sha256": file_hash(cnf_path),
        "soundness": (
            "Every solution orbit under the generated branch stabilizer has a "
            "lexicographically least projected prefix; that representative "
            "satisfies every imposed generator inequality."
        ),
        "joint_UNSAT_consequence": (
            "Checked UNSAT for matching and path branches proves R_3^KG(3,3)=12."
        ),
        "SAT_consequence": (
            "A model, after checking the first 9240 variables on the unrestricted "
            "triangle instance, proves R_3^KG(3,3)=13."
        ),
    }
    metadata_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(json.dumps(record, indent=2, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", choices=("matching", "path"), required=True)
    parser.add_argument("--prefix-length", type=int, default=2400)
    parser.add_argument("--cnf", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    args = parser.parse_args()
    if args.prefix_length < 1:
        raise SystemExit("prefix length must be positive")
    generate(args.branch, args.prefix_length, args.cnf, args.metadata)


if __name__ == "__main__":
    main()
