#!/usr/bin/env python3
"""Search bilinear parity colorings of KG(12,3).

Choose a simple graph H on the twelve ground points. For disjoint triples A,B,
define the base color as the parity of H-edges crossing from A to B. Two modes:

* bilinear: x(A,B) = sum_{a in A,b in B} H_ab mod 2;
* switched-bilinear: x(A,B) = base XOR s(A) XOR s(B).

SAT gives a compact algebraic construction and is independently checked on all
61,600 Kneser triangles. UNSAT excludes only the selected algebraic class.
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


class CNF:
    def __init__(self):
        self.next_var = 1
        self.clauses: list[tuple[int, ...]] = []

    def var(self) -> int:
        value = self.next_var
        self.next_var += 1
        return value

    def add(self, *literals: int) -> None:
        self.clauses.append(tuple(literals))


def add_xor2(cnf: CNF, out: int, a: int, b: int) -> None:
    # out = a XOR b
    cnf.add(-a, -b, -out)
    cnf.add(a, b, -out)
    cnf.add(a, -b, out)
    cnf.add(-a, b, out)


def add_equal(cnf: CNF, a: int, b: int) -> None:
    cnf.add(-a, b)
    cnf.add(a, -b)


def stable_hash(value: object) -> str:
    payload = json.dumps(value, separators=(",", ":"), sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def base_graph():
    vertices = list(itertools.combinations(range(N), R))
    vertex_id = {vertex: i for i, vertex in enumerate(vertices)}
    point_pairs = list(itertools.combinations(range(N), 2))
    pair_id = {pair: i for i, pair in enumerate(point_pairs)}
    edges: list[tuple[int, int]] = []
    cross_pairs: list[list[int]] = []
    edge_id: dict[tuple[int, int], int] = {}
    for i, a in enumerate(vertices):
        a_set = set(a)
        for j in range(i + 1, len(vertices)):
            b = vertices[j]
            if not a_set.isdisjoint(b):
                continue
            edge_id[(i, j)] = len(edges)
            edges.append((i, j))
            cross_pairs.append(sorted(pair_id[tuple(sorted((x, y)))] for x in a for y in b))

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
                triangles.append((edge_id[(i, j)], edge_id[(i, k)], edge_id[(j, k)]))
    assert (len(vertices), len(point_pairs), len(edges), len(triangles)) == (220, 66, 9240, 61600)
    assert all(len(row) == 9 and len(set(row)) == 9 for row in cross_pairs)
    return vertices, vertex_id, point_pairs, edges, cross_pairs, edge_id, triangles


def canonical_units(branch: str, vertex_id, edge_vars, edge_id):
    blocks = [vertex_id[(0, 1, 2)], vertex_id[(3, 4, 5)], vertex_id[(6, 7, 8)], vertex_id[(9, 10, 11)]]
    names = ("AB", "AC", "AD", "BC", "BD", "CD")
    pairs = ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))
    named = {name: edge_vars[edge_id[tuple(sorted((blocks[i], blocks[j])))]] for name, (i, j) in zip(names, pairs)}
    if branch == "matching":
        red = {"AB", "CD"}
    elif branch == "path":
        red = {"AB", "BD", "CD"}
    else:
        raise ValueError(branch)
    return [variable if name in red else -variable for name, variable in named.items()]


def parity_chain(cnf: CNF, inputs: list[int]) -> int:
    assert inputs
    if len(inputs) == 1:
        return inputs[0]
    current = cnf.var()
    add_xor2(cnf, current, inputs[0], inputs[1])
    for value in inputs[2:]:
        nxt = cnf.var()
        add_xor2(cnf, nxt, current, value)
        current = nxt
    return current


def build(mode: str, branch: str):
    vertices, vertex_id, point_pairs, edges, cross_pairs, edge_id, triangles = base_graph()
    cnf = CNF()
    graph_vars = [cnf.var() for _ in point_pairs]
    switch_vars = [cnf.var() for _ in vertices] if mode == "switched-bilinear" else []
    edge_vars = [cnf.var() for _ in edges]

    for e, (u, v) in enumerate(edges):
        base = parity_chain(cnf, [graph_vars[pair] for pair in cross_pairs[e]])
        if mode == "bilinear":
            add_equal(cnf, edge_vars[e], base)
        elif mode == "switched-bilinear":
            partial = cnf.var()
            add_xor2(cnf, partial, base, switch_vars[u])
            final = cnf.var()
            add_xor2(cnf, final, partial, switch_vars[v])
            add_equal(cnf, edge_vars[e], final)
        else:
            raise ValueError(mode)

    for x, y, z in triangles:
        cnf.add(edge_vars[x], edge_vars[y], edge_vars[z])
        cnf.add(-edge_vars[x], -edge_vars[y], -edge_vars[z])
    for literal in canonical_units(branch, vertex_id, edge_vars, edge_id):
        cnf.add(literal)

    metadata = {
        "mode": mode,
        "branch": branch,
        "scope": "SAT is decisive after full checking; UNSAT is algebraic-ansatz-only",
        "ground_graph_bits": len(point_pairs),
        "vertex_switch_bits": len(switch_vars),
        "full_edges": len(edges),
        "full_triangles": len(triangles),
        "cnf_variables": cnf.next_var - 1,
        "cnf_clauses": len(cnf.clauses),
        "point_pair_order_sha256": stable_hash(point_pairs),
        "edge_order_sha256": stable_hash(edges),
        "cross_pair_map_sha256": stable_hash(cross_pairs),
        "triangle_order_sha256": stable_hash(triangles),
    }
    mapping = {"graph_vars": graph_vars, "switch_vars": switch_vars, "edge_vars": edge_vars}
    return cnf, metadata, mapping, vertices, point_pairs, edges, cross_pairs, triangles


def generate(mode: str, branch: str, cnf_path: Path, metadata_path: Path, map_path: Path) -> None:
    cnf, metadata, mapping, *_ = build(mode, branch)
    with cnf_path.open("w", encoding="ascii", newline="\n") as out:
        out.write(f"c KG(12,3) {mode} branch {branch}\n")
        out.write(f"p cnf {cnf.next_var - 1} {len(cnf.clauses)}\n")
        for clause in cnf.clauses:
            out.write(" ".join(map(str, clause)) + " 0\n")
    metadata["cnf_sha256"] = file_hash(cnf_path)
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    map_path.write_text(json.dumps(mapping, separators=(",", ":")) + "\n")
    print(json.dumps(metadata, indent=2, sort_keys=True))


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
            raise ValueError(variable)
        value = literal > 0
        if values[variable] is not None and values[variable] != value:
            raise ValueError(f"contradictory variable {variable}")
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


def verify(mode: str, branch: str, solver_output: Path, map_path: Path, certificate_path: Path) -> None:
    cnf, metadata, _mapping, vertices, point_pairs, edges, cross_pairs, triangles = build(mode, branch)
    values = parse_model(solver_output, cnf.next_var - 1)
    mapping = json.loads(map_path.read_text())
    graph_values = [values[var - 1] for var in mapping["graph_vars"]]
    switch_values = [values[var - 1] for var in mapping["switch_vars"]]
    edge_values = [values[var - 1] for var in mapping["edge_vars"]]

    for e, (u, v) in enumerate(edges):
        predicted = bool(sum(graph_values[pair] for pair in cross_pairs[e]) % 2)
        if mode == "switched-bilinear":
            predicted ^= switch_values[u] ^ switch_values[v]
        if predicted != edge_values[e]:
            raise AssertionError((e, predicted, edge_values[e]))

    one_red = two_red = 0
    for triangle in triangles:
        count = sum(edge_values[e] for e in triangle)
        if count == 1:
            one_red += 1
        elif count == 2:
            two_red += 1
        else:
            raise AssertionError(triangle)

    model_hex = pack_hex(edge_values)
    ground_edges = [list(pair) for pair, value in zip(point_pairs, graph_values) if value]
    record = {
        "result": "SAT_FULL_KG12_MODEL_VERIFIED",
        "mode": mode,
        "branch": branch,
        "ground_graph_edges": ground_edges,
        "ground_graph_edge_count": len(ground_edges),
        "vertex_switches": [i for i, value in enumerate(switch_values) if value],
        "full_edges_checked": len(edges),
        "full_triangles_checked": len(triangles),
        "monochromatic_triangles": 0,
        "triangles_with_one_red_edge": one_red,
        "triangles_with_two_red_edges": two_red,
        "red_edges": sum(edge_values),
        "blue_edges": len(edge_values) - sum(edge_values),
        "edge_order_sha256": metadata["edge_order_sha256"],
        "edge_model_hex": model_hex,
        "edge_model_hex_sha256": hashlib.sha256(model_hex.encode()).hexdigest(),
        "ramsey_consequence": "R_3^KG(3,3)=13, conditional only on the published upper bound <=13",
    }
    certificate_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(json.dumps(record, indent=2, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("bilinear", "switched-bilinear"), required=True)
    parser.add_argument("--branch", choices=("matching", "path"), required=True)
    sub = parser.add_subparsers(dest="command", required=True)
    gen = sub.add_parser("generate")
    gen.add_argument("--cnf", type=Path, required=True)
    gen.add_argument("--metadata", type=Path, required=True)
    gen.add_argument("--map", type=Path, required=True)
    verify = sub.add_parser("verify-model")
    verify.add_argument("--solver-output", type=Path, required=True)
    verify.add_argument("--map", type=Path, required=True)
    verify.add_argument("--certificate", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "generate":
        generate(args.mode, args.branch, args.cnf, args.metadata, args.map)
    else:
        verify(args.mode, args.branch, args.solver_output, args.map, args.certificate)


if __name__ == "__main__":
    main()
