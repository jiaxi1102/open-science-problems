#!/usr/bin/env python3
"""Search symmetry-restricted colorings of KG(12,3).

A group generator is a permutation of the twelve ground points together with
an optional color flip. Edge variables in the same signed orbit are identified.
SAT produces a full coloring of KG(12,3), independently verified against every
one of its 61,600 triangles. UNSAT only excludes the selected symmetry ansatz.
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


class ParityDSU:
    """Union-find with relations value[a] XOR value[b] = parity."""

    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.to_parent = [0] * n
        self.consistent = True

    def find(self, x: int) -> tuple[int, int]:
        if self.parent[x] != x:
            root, parity = self.find(self.parent[x])
            self.to_parent[x] ^= parity
            self.parent[x] = root
        return self.parent[x], self.to_parent[x]

    def union(self, a: int, b: int, parity: int) -> None:
        ra, xa = self.find(a)
        rb, xb = self.find(b)
        if ra == rb:
            if (xa ^ xb) != parity:
                self.consistent = False
            return
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
            xa, xb = xb, xa
        self.parent[rb] = ra
        self.to_parent[rb] = xa ^ xb ^ parity
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1


def stable_hash(value: object) -> str:
    payload = json.dumps(value, separators=(",", ":"), sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def shift(step: int) -> tuple[int, ...]:
    return tuple((x + step) % N for x in range(N))


def reflect(offset: int = 0) -> tuple[int, ...]:
    return tuple((offset - x) % N for x in range(N))


def cases() -> dict[str, list[tuple[tuple[int, ...], int]]]:
    result: dict[str, list[tuple[tuple[int, ...], int]]] = {}
    for step, label in ((1, "12"), (2, "6"), (3, "4"), (4, "3"), (6, "2")):
        result[f"c{label}"] = [(shift(step), 0)]
    for step, label in ((1, "12"), (2, "6"), (3, "4"), (6, "2")):
        result[f"c{label}-signed"] = [(shift(step), 1)]
    for step, label in ((1, "12"), (2, "6"), (3, "4"), (4, "3"), (6, "2")):
        result[f"d{label}"] = [(shift(step), 0), (reflect(), 0)]
    for step, label in ((1, "12"), (2, "6"), (3, "4"), (6, "2")):
        for reflection_flip in (0, 1):
            result[f"d{label}-signed-r{reflection_flip}"] = [
                (shift(step), 1),
                (reflect(), reflection_flip),
            ]
    return result


def base_graph():
    vertices = list(itertools.combinations(range(N), R))
    vertex_id = {vertex: i for i, vertex in enumerate(vertices)}
    edges: list[tuple[int, int]] = []
    edge_id: dict[tuple[int, int], int] = {}
    for i, a in enumerate(vertices):
        a_set = set(a)
        for j in range(i + 1, len(vertices)):
            if a_set.isdisjoint(vertices[j]):
                edge_id[(i, j)] = len(edges)
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
    assert (len(vertices), len(edges), len(triangles)) == (220, 9240, 61600)
    return vertices, vertex_id, edges, edge_id, triangles


def permute_vertex(vertex: tuple[int, ...], permutation: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(sorted(permutation[x] for x in vertex))


def build_orbits(case: str):
    all_cases = cases()
    if case not in all_cases:
        raise ValueError(f"unknown case {case!r}; choose from {sorted(all_cases)}")
    generators = all_cases[case]
    vertices, vertex_id, edges, edge_id, triangles = base_graph()
    dsu = ParityDSU(len(edges))

    for permutation, flip in generators:
        image_vertex = [vertex_id[permute_vertex(v, permutation)] for v in vertices]
        for e, (i, j) in enumerate(edges):
            x, y = image_vertex[i], image_vertex[j]
            if x > y:
                x, y = y, x
            dsu.union(e, edge_id[(x, y)], flip)
        if not dsu.consistent:
            break

    if not dsu.consistent:
        return vertices, edges, triangles, generators, None

    root_id: dict[int, int] = {}
    edge_map: list[tuple[int, int]] = []
    for edge in range(len(edges)):
        root, parity = dsu.find(edge)
        if root not in root_id:
            root_id[root] = len(root_id) + 1
        edge_map.append((root_id[root], parity))
    return vertices, edges, triangles, generators, edge_map


def simplify_clause(literals: Iterable[int]) -> tuple[int, ...] | None:
    values = set(literals)
    if any(-literal in values for literal in values):
        return None
    return tuple(sorted(values, key=lambda literal: (abs(literal), literal < 0)))


def generate(case: str, cnf: Path, metadata: Path) -> None:
    vertices, edges, triangles, generators, edge_map = build_orbits(case)
    if edge_map is None:
        cnf.write_text("p cnf 0 1\n0\n")
        metadata.write_text(json.dumps({
            "case": case,
            "signed_orbit_relations_consistent": False,
            "result_without_solver": "UNSAT",
        }, indent=2, sort_keys=True) + "\n")
        return

    clauses: set[tuple[int, ...]] = set()
    for triangle in triangles:
        red_literals: list[int] = []
        for edge in triangle:
            variable, parity = edge_map[edge]
            red_literals.append(variable if parity == 0 else -variable)
        for raw in (red_literals, [-literal for literal in red_literals]):
            clause = simplify_clause(raw)
            if clause is not None:
                clauses.add(clause)
    clauses.add((-1,))
    ordered_clauses = sorted(clauses, key=lambda c: (len(c), tuple(abs(x) for x in c), c))
    variables = max(variable for variable, _ in edge_map)

    with cnf.open("w", encoding="ascii", newline="\n") as out:
        out.write(f"c Orbit-symmetry ansatz {case} for KG(12,3)\n")
        out.write("c orbit variable true=red at parity zero; variable 1 fixed blue\n")
        out.write(f"p cnf {variables} {len(ordered_clauses)}\n")
        for clause in ordered_clauses:
            out.write(" ".join(map(str, clause)) + " 0\n")

    generator_record = [
        {"permutation": list(permutation), "color_flip": bool(flip)}
        for permutation, flip in generators
    ]
    parity_counts = {"zero": 0, "one": 0}
    for _, parity in edge_map:
        parity_counts["one" if parity else "zero"] += 1
    record = {
        "case": case,
        "scope": "symmetry ansatz; SAT is decisive, UNSAT is ansatz-only",
        "full_vertices": len(vertices),
        "full_edges": len(edges),
        "full_triangles": len(triangles),
        "generators": generator_record,
        "signed_orbit_relations_consistent": True,
        "orbit_variables": variables,
        "distinct_simplified_cnf_clauses": len(ordered_clauses),
        "full_edge_parity_counts": parity_counts,
        "edge_orbit_map_sha256": stable_hash(edge_map),
        "clause_set_sha256": stable_hash(ordered_clauses),
        "cnf_sha256": file_hash(cnf),
        "SAT_consequence": (
            "The expanded model colors KG(12,3) without a monochromatic triangle, "
            "so R_3^KG(3,3)=13 using the published upper bound."
        ),
        "UNSAT_consequence": f"No coloring with symmetry ansatz {case} exists.",
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
            raise ValueError(f"variable {variable} outside 1..{variables}")
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


def verify_model(case: str, solver_output: Path, certificate: Path) -> None:
    _vertices, edges, triangles, generators, edge_map = build_orbits(case)
    if edge_map is None:
        raise ValueError("inconsistent signed action cannot have a SAT model")
    variables = max(variable for variable, _ in edge_map)
    orbit_values = parse_model(solver_output, variables)
    full_values = [orbit_values[variable - 1] ^ bool(parity) for variable, parity in edge_map]

    one_red = two_red = 0
    for triangle in triangles:
        red_count = sum(full_values[edge] for edge in triangle)
        if red_count == 1:
            one_red += 1
        elif red_count == 2:
            two_red += 1
        else:
            raise AssertionError(f"monochromatic full triangle {triangle}")

    # Independently re-check every generator relation on all 9,240 edges.
    vertices, vertex_id, _, edge_id, _ = base_graph()
    relation_checks = 0
    for permutation, flip in generators:
        image_vertex = [vertex_id[permute_vertex(v, permutation)] for v in vertices]
        for edge, (i, j) in enumerate(edges):
            x, y = image_vertex[i], image_vertex[j]
            if x > y:
                x, y = y, x
            image_edge = edge_id[(x, y)]
            if full_values[image_edge] != (full_values[edge] ^ bool(flip)):
                raise AssertionError((edge, image_edge, flip))
            relation_checks += 1

    orbit_hex = pack_hex(orbit_values)
    full_hex = pack_hex(full_values)
    record = {
        "result": "SAT",
        "case": case,
        "orbit_variables": variables,
        "full_edges_checked": len(edges),
        "full_triangles_checked": len(triangles),
        "monochromatic_full_triangles": 0,
        "triangles_with_one_red_edge": one_red,
        "triangles_with_two_red_edges": two_red,
        "full_red_edges": sum(full_values),
        "full_blue_edges": len(full_values) - sum(full_values),
        "generator_relations_checked": relation_checks,
        "orbit_model_hex": orbit_hex,
        "orbit_model_hex_sha256": hashlib.sha256(orbit_hex.encode()).hexdigest(),
        "full_model_hex": full_hex,
        "full_model_hex_sha256": hashlib.sha256(full_hex.encode()).hexdigest(),
        "full_edge_order_sha256": stable_hash(edges),
        "ramsey_consequence": (
            "R_3^KG(3,3)=13, conditional only on the published upper bound <=13"
        ),
    }
    certificate.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(json.dumps(record, indent=2, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", required=True, choices=sorted(cases()))
    sub = parser.add_subparsers(dest="command", required=True)
    gen = sub.add_parser("generate")
    gen.add_argument("--cnf", type=Path, required=True)
    gen.add_argument("--metadata", type=Path, required=True)
    verify = sub.add_parser("verify-model")
    verify.add_argument("--solver-output", type=Path, required=True)
    verify.add_argument("--certificate", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "generate":
        generate(args.case, args.cnf, args.metadata)
    else:
        verify_model(args.case, args.solver_output, args.certificate)


if __name__ == "__main__":
    main()
