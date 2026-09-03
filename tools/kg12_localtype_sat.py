#!/usr/bin/env python3
"""Strengthened SAT search for a triangle-free edge coloring of KG(12,3).

In any valid coloring, fix a vertex A. The colors of the 84 incident edges
2-color the triples of the nine-point complement of A with no monochromatic
partition into three triples. The independently exhaustive local classifier
shows that every such coloring has the form

  polarity XOR [|B intersect S_A| >= ceil(|S_A|/3)]

for a subset S_A of size 1, 2, or 4.

This encoder imposes those local threshold types at all 220 vertices in
addition to the original 61,600 triangle NAE constraints. A SAT model is a
fully valid coloring regardless of the classification theorem and is checked
independently. UNSAT becomes decisive only after the local classification is
accepted/formally certified.
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
        self.names: dict[str, int] = {}

    def var(self, name: str) -> int:
        if name in self.names:
            return self.names[name]
        value = self.next_var
        self.next_var += 1
        self.names[name] = value
        return value

    def add(self, *literals: int) -> None:
        if not literals:
            self.clauses.append(())
            return
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


def add_exactly_one(cnf: CNF, variables: list[int]) -> None:
    cnf.add(*variables)
    for i, a in enumerate(variables):
        for b in variables[i + 1:]:
            cnf.add(-a, -b)


def add_conditional_exact_cardinality(
    cnf: CNF, gate: int, variables: list[int], cardinality: int
) -> None:
    # gate -> at most cardinality
    for subset in itertools.combinations(variables, cardinality + 1):
        cnf.add(-gate, *(-x for x in subset))
    # gate -> at least cardinality
    for subset in itertools.combinations(variables, len(variables) - cardinality + 1):
        cnf.add(-gate, *subset)


def add_or3(cnf: CNF, out: int, a: int, b: int, c: int) -> None:
    cnf.add(-a, out)
    cnf.add(-b, out)
    cnf.add(-c, out)
    cnf.add(a, b, c, -out)


def add_majority3(cnf: CNF, out: int, a: int, b: int, c: int) -> None:
    # Any two true force out true.
    cnf.add(-a, -b, out)
    cnf.add(-a, -c, out)
    cnf.add(-b, -c, out)
    # Out true requires at least two true.
    cnf.add(a, b, -out)
    cnf.add(a, c, -out)
    cnf.add(b, c, -out)


def add_gate_equality(cnf: CNF, gate: int, a: int, b: int) -> None:
    cnf.add(-gate, -a, b)
    cnf.add(-gate, a, -b)


def add_xor(cnf: CNF, out: int, a: int, b: int) -> None:
    # out = a XOR b
    cnf.add(-a, -b, -out)
    cnf.add(a, b, -out)
    cnf.add(a, -b, out)
    cnf.add(-a, b, out)


def canonical_units(
    branch: str, vertex_id: dict[tuple[int, ...], int], edge_vars: list[int],
    edge_id: dict[tuple[int, int], int]
) -> list[int]:
    blocks = [
        vertex_id[(0, 1, 2)],
        vertex_id[(3, 4, 5)],
        vertex_id[(6, 7, 8)],
        vertex_id[(9, 10, 11)],
    ]
    names = ("AB", "AC", "AD", "BC", "BD", "CD")
    pairs = ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))
    variables = {
        name: edge_vars[edge_id[tuple(sorted((blocks[i], blocks[j])))]]
        for name, (i, j) in zip(names, pairs)
    }
    if branch == "matching":
        red = {"AB", "CD"}
    elif branch == "path":
        red = {"AB", "BD", "CD"}
    elif branch == "triangle":
        red = {"AB"}
        variables = {name: variables[name] for name in ("AB", "AC", "BC")}
    else:
        raise ValueError(branch)
    return [variable if name in red else -variable for name, variable in variables.items()]


def build_cnf(branch: str):
    vertices, vertex_id, edges, edge_id, triangles = base_graph()
    cnf = CNF()

    edge_vars = [cnf.var(f"edge:{i}") for i in range(len(edges))]
    local_bits: list[dict[int, int]] = []
    polarities: list[int] = []
    modes: list[tuple[int, int, int]] = []

    for v, vertex in enumerate(vertices):
        complement = [point for point in range(N) if point not in vertex]
        bits = {point: cnf.var(f"S:{v}:{point}") for point in complement}
        polarity = cnf.var(f"polarity:{v}")
        mode1 = cnf.var(f"mode1:{v}")
        mode2 = cnf.var(f"mode2:{v}")
        mode4 = cnf.var(f"mode4:{v}")
        add_exactly_one(cnf, [mode1, mode2, mode4])
        bit_values = [bits[point] for point in complement]
        add_conditional_exact_cardinality(cnf, mode1, bit_values, 1)
        add_conditional_exact_cardinality(cnf, mode2, bit_values, 2)
        add_conditional_exact_cardinality(cnf, mode4, bit_values, 4)
        local_bits.append(bits)
        polarities.append(polarity)
        modes.append((mode1, mode2, mode4))

    # Directed local predictions are equated to each shared undirected edge.
    prediction_checks = 0
    for edge_index, (u, v) in enumerate(edges):
        for owner, neighbor in ((u, v), (v, u)):
            points = vertices[neighbor]
            selected = [local_bits[owner][point] for point in points]
            h1 = cnf.var(f"hit1:{owner}:{neighbor}")
            h2 = cnf.var(f"hit2:{owner}:{neighbor}")
            threshold = cnf.var(f"threshold:{owner}:{neighbor}")
            predicted = cnf.var(f"predicted:{owner}:{neighbor}")
            add_or3(cnf, h1, *selected)
            add_majority3(cnf, h2, *selected)
            mode1, mode2, mode4 = modes[owner]
            add_gate_equality(cnf, mode1, threshold, h1)
            add_gate_equality(cnf, mode2, threshold, h1)
            add_gate_equality(cnf, mode4, threshold, h2)
            add_xor(cnf, predicted, threshold, polarities[owner])
            # predicted = shared edge color
            cnf.add(-predicted, edge_vars[edge_index])
            cnf.add(predicted, -edge_vars[edge_index])
            prediction_checks += 1

    for x, y, z in triangles:
        a, b, c = edge_vars[x], edge_vars[y], edge_vars[z]
        cnf.add(a, b, c)
        cnf.add(-a, -b, -c)

    units = canonical_units(branch, vertex_id, edge_vars, edge_id)
    for literal in units:
        cnf.add(literal)

    metadata = {
        "branch": branch,
        "scope": (
            "SAT is independently decisive; UNSAT relies on the exhaustive "
            "local-neighborhood classification."
        ),
        "full_vertices": len(vertices),
        "full_edges": len(edges),
        "full_triangles": len(triangles),
        "cnf_variables": cnf.next_var - 1,
        "cnf_clauses": len(cnf.clauses),
        "directed_local_predictions": prediction_checks,
        "local_types_per_vertex": 342,
        "canonical_unit_literals": units,
        "edge_variable_range": [edge_vars[0], edge_vars[-1]],
        "edge_order_sha256": stable_hash(edges),
        "triangle_order_sha256": stable_hash(triangles),
    }
    extraction = {
        "edge_vars": edge_vars,
        "local_bits": [{str(k): value for k, value in row.items()} for row in local_bits],
        "polarities": polarities,
        "modes": [list(row) for row in modes],
    }
    return cnf, metadata, extraction, vertices, edges, triangles


def write_instance(branch: str, cnf_path: Path, metadata_path: Path, map_path: Path) -> None:
    cnf, metadata, extraction, _vertices, _edges, _triangles = build_cnf(branch)
    with cnf_path.open("w", encoding="ascii", newline="\n") as out:
        out.write(f"c Local-threshold strengthened KG(12,3) branch {branch}\n")
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


def verify_model(
    branch: str, solver_output: Path, map_path: Path, certificate_path: Path
) -> None:
    cnf, metadata, _generated, vertices, edges, triangles = build_cnf(branch)
    values = parse_model(solver_output, cnf.next_var - 1)
    mapping = json.loads(map_path.read_text())
    edge_values = [values[variable - 1] for variable in mapping["edge_vars"]]

    one_red = two_red = 0
    for triangle in triangles:
        count = sum(edge_values[edge] for edge in triangle)
        if count == 1:
            one_red += 1
        elif count == 2:
            two_red += 1
        else:
            raise AssertionError(f"monochromatic triangle {triangle}")

    local_checks = 0
    type_counts: dict[str, int] = {}
    edge_id = {edge: i for i, edge in enumerate(edges)}
    for owner, vertex in enumerate(vertices):
        bits = {
            int(point): values[variable - 1]
            for point, variable in mapping["local_bits"][owner].items()
        }
        selected_set = {point for point, selected in bits.items() if selected}
        mode_values = [values[variable - 1] for variable in mapping["modes"][owner]]
        if sum(mode_values) != 1:
            raise AssertionError((owner, mode_values))
        expected_size = (1, 2, 4)[mode_values.index(True)]
        if len(selected_set) != expected_size:
            raise AssertionError((owner, selected_set, expected_size))
        polarity = values[mapping["polarities"][owner] - 1]
        threshold = 2 if expected_size == 4 else 1
        key = f"size_{expected_size}_polarity_{int(polarity)}"
        type_counts[key] = type_counts.get(key, 0) + 1

        for neighbor, neighbor_vertex in enumerate(vertices):
            if owner == neighbor or not set(vertex).isdisjoint(neighbor_vertex):
                continue
            pair = tuple(sorted((owner, neighbor)))
            predicted = polarity ^ (len(selected_set.intersection(neighbor_vertex)) >= threshold)
            if predicted != edge_values[edge_id[pair]]:
                raise AssertionError((owner, neighbor, selected_set, polarity))
            local_checks += 1

    model_hex = pack_hex(edge_values)
    record = {
        "result": "SAT",
        "branch": branch,
        "full_edges_checked": len(edges),
        "full_triangles_checked": len(triangles),
        "monochromatic_triangles": 0,
        "triangles_with_one_red_edge": one_red,
        "triangles_with_two_red_edges": two_red,
        "red_edges": sum(edge_values),
        "blue_edges": len(edge_values) - sum(edge_values),
        "directed_local_predictions_checked": local_checks,
        "local_type_counts": dict(sorted(type_counts.items())),
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
    parser.add_argument("--branch", choices=("triangle", "matching", "path"), required=True)
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
        write_instance(args.branch, args.cnf, args.metadata, args.map)
    else:
        verify_model(args.branch, args.solver_output, args.map, args.certificate)


if __name__ == "__main__":
    main()
