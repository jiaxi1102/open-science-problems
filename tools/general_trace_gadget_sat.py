#!/usr/bin/env python3
"""Search finite trace gadgets for diagonal triangle Kneser Ramsey bounds.

Fix `m` distinguished points and slack `c`, targeting KG(3r+c,r). For r>=m,
every trace is an arbitrary subset of [m]. Three r-sets forming a Kneser
triangle have pairwise-disjoint traces whose union has size at least m-c.

A two-coloring of every realizable unordered pair of disjoint traces that is
NAE on all such trace triples therefore lifts to every r>=m and proves

    R_r^KG(3,3) >= 3r+c+1.

The quotient includes the repeated empty trace: distinct Kneser vertices can
both avoid all distinguished points. SAT models are independently checked on
every trace triple. UNSAT is a complete negative result for the specified
pure-trace quotient, not for arbitrary Kneser colorings.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Iterable


def stable_hash(value: object) -> str:
    payload = json.dumps(value, separators=(",", ":"), sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_instance(m: int, slack: int):
    if m < 1 or slack < 0 or slack >= m:
        raise ValueError("require m>=1 and 0<=slack<m")
    traces = list(range(1 << m))
    edge_types: list[tuple[int, int]] = []
    edge_id: dict[tuple[int, int], int] = {}
    for a in traces:
        for b in range(a, 1 << m):
            if a & b:
                continue
            # Equal disjoint traces occur only for the empty trace.
            edge_id[(a, b)] = len(edge_types) + 1
            edge_types.append((a, b))

    minimum_union = m - slack
    trace_triangles: set[tuple[int, int, int]] = set()
    witness_patterns: dict[tuple[int, int, int], tuple[int, int, int]] = {}
    for labels in itertools.product(range(4), repeat=m):
        masks = [0, 0, 0, 0]
        for point, label in enumerate(labels):
            masks[label] |= 1 << point
        a, b, c, _unused = masks
        if (a | b | c).bit_count() < minimum_union:
            continue
        variables = []
        for x, y in ((a, b), (a, c), (b, c)):
            if x > y:
                x, y = y, x
            variables.append(edge_id[(x, y)])
        row = tuple(sorted(variables))
        trace_triangles.add(row)
        witness_patterns.setdefault(row, (a, b, c))

    triangles = sorted(trace_triangles)
    return traces, edge_types, triangles, witness_patterns


def simplify_nae(row: tuple[int, int, int]):
    # If all three edge types coincide, no quotient coloring can satisfy NAE.
    if row[0] == row[2]:
        return [()]
    clauses = []
    for signs in (1, -1):
        literals = tuple(signs * variable for variable in row)
        clauses.append(tuple(sorted(set(literals), key=abs)))
    return clauses


def generate(m: int, slack: int, cnf: Path, metadata: Path, map_path: Path) -> None:
    traces, edge_types, triangles, witnesses = build_instance(m, slack)
    clause_set: set[tuple[int, ...]] = set()
    for row in triangles:
        clause_set.update(simplify_nae(row))
    if () not in clause_set:
        clause_set.add((-1,))  # global color symmetry
    clauses = sorted(clause_set, key=lambda row: (len(row), tuple(abs(x) for x in row), row))

    with cnf.open("w", encoding="ascii", newline="\n") as out:
        out.write(f"c Pure trace gadget m={m} slack={slack}\n")
        out.write(f"p cnf {len(edge_types)} {len(clauses)}\n")
        for clause in clauses:
            out.write(" ".join(map(str, clause)) + " 0\n")

    record = {
        "distinguished_points": m,
        "slack": slack,
        "target_graph": f"KG(3r+{slack},r)",
        "valid_for": f"all r >= {m}",
        "ramsey_lower_bound_if_SAT": f"R_r^KG(3,3) >= 3r+{slack+1}",
        "all_traces": len(traces),
        "disjoint_unordered_trace_pair_types": len(edge_types),
        "realisable_trace_triangle_types": len(triangles),
        "distinct_cnf_clauses": len(clauses),
        "minimum_trace_union": m - slack,
        "contains_immediate_empty_clause": () in clause_set,
        "trace_pair_order_sha256": stable_hash(edge_types),
        "trace_triangle_order_sha256": stable_hash(triangles),
        "cnf_sha256": file_hash(cnf),
        "SAT_scope": "uniform construction for all r>=m",
        "UNSAT_scope": "complete impossibility only for this pure trace quotient",
    }
    metadata.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    map_path.write_text(json.dumps({
        "edge_types": edge_types,
        "triangle_witnesses": {",".join(map(str, key)): value for key, value in witnesses.items()},
    }, separators=(",", ":")) + "\n")
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


def verify(m: int, slack: int, solver_output: Path, certificate: Path) -> None:
    _traces, edge_types, triangles, witnesses = build_instance(m, slack)
    values = parse_model(solver_output, len(edge_types))
    one_red = two_red = 0
    for row in triangles:
        red_count = sum(values[variable - 1] for variable in row)
        if red_count == 1:
            one_red += 1
        elif red_count == 2:
            two_red += 1
        else:
            raise AssertionError({"edge_variables": row, "trace_witness": witnesses[row], "red_count": red_count})
    model_hex = pack_hex(values)
    record = {
        "result": "SAT_UNIFORM_TRACE_GADGET_VERIFIED",
        "distinguished_points": m,
        "slack": slack,
        "edge_types_checked": len(edge_types),
        "trace_triangle_types_checked": len(triangles),
        "monochromatic_trace_triangles": 0,
        "trace_triangles_with_one_red_edge": one_red,
        "trace_triangles_with_two_red_edges": two_red,
        "trace_pair_order_sha256": stable_hash(edge_types),
        "model_hex": model_hex,
        "model_hex_sha256": hashlib.sha256(model_hex.encode()).hexdigest(),
        "theorem_consequence": f"For every r>={m}, R_r^KG(3,3) >= 3r+{slack+1}.",
    }
    certificate.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(json.dumps(record, indent=2, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--m", type=int, required=True)
    parser.add_argument("--slack", type=int, required=True)
    sub = parser.add_subparsers(dest="command", required=True)
    gen = sub.add_parser("generate")
    gen.add_argument("--cnf", type=Path, required=True)
    gen.add_argument("--metadata", type=Path, required=True)
    gen.add_argument("--map", type=Path, required=True)
    verify_parser = sub.add_parser("verify-model")
    verify_parser.add_argument("--solver-output", type=Path, required=True)
    verify_parser.add_argument("--certificate", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "generate":
        generate(args.m, args.slack, args.cnf, args.metadata, args.map)
    else:
        verify(args.m, args.slack, args.solver_output, args.certificate)


if __name__ == "__main__":
    main()
