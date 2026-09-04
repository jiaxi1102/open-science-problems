#!/usr/bin/env python3
"""Search union-based colorings of KG(12,3).

For disjoint triples A,B let U=A union B. Two ansatzes are supported:

* union: color(A,B) = h(U);
* switched-union: color(A,B) = h(U) XOR s(A) XOR s(B).

The second is the full switching closure of the first. A SAT model is expanded
to all 9,240 edges and independently checked on all 61,600 Kneser triangles.
UNSAT excludes only the chosen ansatz.
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
    vertex_masks = [sum(1 << x for x in vertex) for vertex in vertices]
    vertex_id = {vertex: i for i, vertex in enumerate(vertices)}
    unions = list(itertools.combinations(range(N), 2 * R))
    union_id = {sum(1 << x for x in union): i for i, union in enumerate(unions)}

    edges: list[tuple[int, int]] = []
    edge_union: list[int] = []
    edge_id: dict[tuple[int, int], int] = {}
    for i, a_mask in enumerate(vertex_masks):
        for j in range(i + 1, len(vertices)):
            if a_mask & vertex_masks[j] == 0:
                edge_id[(i, j)] = len(edges)
                edges.append((i, j))
                edge_union.append(union_id[a_mask | vertex_masks[j]])

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
    assert (len(vertices), len(unions), len(edges), len(triangles)) == (220, 924, 9240, 61600)
    return vertices, unions, edges, edge_union, edge_id, triangles


def add_xor3(cnf: CNF, out: int, a: int, b: int, c: int) -> None:
    # out = a XOR b XOR c, encoded by excluding the eight inconsistent rows.
    for av, bv, cv in itertools.product((0, 1), repeat=3):
        expected = av ^ bv ^ cv
        literals = [
            -a if av else a,
            -b if bv else b,
            -c if cv else c,
            out if expected else -out,
        ]
        cnf.add(*literals)


def canonical_units(
    branch: str,
    vertex_id: dict[tuple[int, ...], int],
    edge_vars: list[int],
    edge_id: dict[tuple[int, int], int],
) -> list[int]:
    blocks = [
        vertex_id[(0, 1, 2)],
        vertex_id[(3, 4, 5)],
        vertex_id[(6, 7, 8)],
        vertex_id[(9, 10, 11)],
    ]
    names = ("AB", "AC", "AD", "BC", "BD", "CD")
    pairs = ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))
    named = {
        name: edge_vars[edge_id[tuple(sorted((blocks[i], blocks[j])))]]
        for name, (i, j) in zip(names, pairs)
    }
    if branch == "matching":
        red = {"AB", "CD"}
    elif branch == "path":
        red = {"AB", "BD", "CD"}
    else:
        raise ValueError(branch)
    return [variable if name in red else -variable for name, variable in named.items()]


def build(mode: str, branch: str):
    vertices, unions, edges, edge_union, edge_id, triangles = base_graph()
    vertex_id = {vertex: i for i, vertex in enumerate(vertices)}
    cnf = CNF()
    union_vars = [cnf.var() for _ in unions]
    switch_vars = [cnf.var() for _ in vertices] if mode == "switched-union" else []
    edge_vars = [cnf.var() for _ in edges]

    for e, (u, v) in enumerate(edges):
        h = union_vars[edge_union[e]]
        x = edge_vars[e]
        if mode == "union":
            cnf.add(-x, h)
            cnf.add(x, -h)
        elif mode == "switched-union":
            add_xor3(cnf, x, h, switch_vars[u], switch_vars[v])
        else:
            raise ValueError(mode)

    for a, b, c in triangles:
        cnf.add(edge_vars[a], edge_vars[b], edge_vars[c])
        cnf.add(-edge_vars[a], -edge_vars[b], -edge_vars[c])

    for literal in canonical_units(branch, vertex_id, edge_vars, edge_id):
        cnf.add(literal)

    extraction = {
        "union_vars": union_vars,
        "switch_vars": switch_vars,
        "edge_vars": edge_vars,
    }
    metadata = {
        "mode": mode,
        "branch": branch,
        "scope": "SAT is decisive after full checking; UNSAT is ansatz-only",
        "vertices": len(vertices),
        "six_point_unions": len(unions),
        "full_edges": len(edges),
        "full_triangles": len(triangles),
        "cnf_variables": cnf.next_var - 1,
        "cnf_clauses": len(cnf.clauses),
        "edge_order_sha256": stable_hash(edges),
        "edge_union_map_sha256": stable_hash(edge_union),
        "triangle_order_sha256": stable_hash(triangles),
    }
    return cnf, metadata, extraction, vertices, unions, edges, edge_union, triangles


def generate(mode: str, branch: str, cnf_path: Path, metadata_path: Path, map_path: Path) -> None:
    cnf, metadata, extraction, *_ = build(mode, branch)
    with cnf_path.open("w", encoding="ascii", newline="\n") as out:
        out.write(f"c KG(12,3) {mode} branch {branch}\n")
        out.write(f"p cnf {cnf.next_var - 1} {len(cnf.clauses)}\n")
        for clause in cnf.clauses:
            out.write(" ".join(map(str, clause)) + " 0\n")
    metadata["cnf_sha256"] = file_hash(cnf_path)
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    map_path.write_text(json.dumps(extraction, separators=(",", ":")) + "\n")
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
    cnf, metadata, _extraction, vertices, unions, edges, edge_union, triangles = build(mode, branch)
    values = parse_model(solver_output, cnf.next_var - 1)
    mapping = json.loads(map_path.read_text())
    union_values = [values[var - 1] for var in mapping["union_vars"]]
    switch_values = [values[var - 1] for var in mapping["switch_vars"]]
    edge_values = [values[var - 1] for var in mapping["edge_vars"]]

    for e, (u, v) in enumerate(edges):
        predicted = union_values[edge_union[e]]
        if mode == "switched-union":
            predicted ^= switch_values[u] ^ switch_values[v]
        if predicted != edge_values[e]:
            raise AssertionError((e, u, v, predicted, edge_values[e]))

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
    record = {
        "result": "SAT_FULL_KG12_MODEL_VERIFIED",
        "mode": mode,
        "branch": branch,
        "six_point_union_labels_checked": len(unions),
        "vertex_switches_checked": len(switch_values),
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
        "ramsey_consequence": (
            "R_3^KG(3,3)=13, conditional only on the published upper bound <=13"
        ),
    }
    certificate_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(json.dumps(record, indent=2, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("union", "switched-union"), required=True)
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
