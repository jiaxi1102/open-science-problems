#!/usr/bin/env python3
"""Search for an eight-point trace coloring that lifts to KG(12,3).

The ambient ground set has eight distinguished and four anonymous points.
A 3-set is represented by its trace S on the distinguished points. Two
traces can occur on adjacent Kneser vertices exactly when they are disjoint
and |S|+|T| >= 2. Three traces can occur on a Kneser triangle exactly when
they are pairwise disjoint and their union has size at least 5.

A satisfying NAE coloring of this 1,610-variable trace instance gives a
compact, independently checkable coloring of all 9,240 edges of KG(12,3).
UNSAT only rules out this trace ansatz; it does not settle the full problem.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Iterable

M = 8
N = 12
R = 3
OUTSIDE = N - M


def subsets_upto_r() -> list[int]:
    return [mask for mask in range(1 << M) if mask.bit_count() <= R]


def build_trace_instance():
    traces = subsets_upto_r()
    trace_id = {mask: i for i, mask in enumerate(traces)}

    edges: list[tuple[int, int]] = []
    edge_id: dict[tuple[int, int], int] = {}
    for i, a in enumerate(traces):
        for j in range(i, len(traces)):
            b = traces[j]
            if a & b:
                continue
            if a.bit_count() + b.bit_count() < 2 * R - OUTSIDE:
                continue
            edge_id[(i, j)] = len(edges) + 1
            edges.append((i, j))

    triangles: set[tuple[int, int, int]] = set()
    for labels in itertools.product(range(4), repeat=M):
        bins = [0, 0, 0, 0]
        for point, label in enumerate(labels):
            bins[label] |= 1 << point
        a, b, c, _unused = bins
        if any(mask.bit_count() > R for mask in (a, b, c)):
            continue
        if (a | b | c).bit_count() < 3 * R - OUTSIDE:
            continue
        ids = [trace_id[a], trace_id[b], trace_id[c]]
        vars_: list[int] = []
        for x, y in ((ids[0], ids[1]), (ids[0], ids[2]), (ids[1], ids[2])):
            if x > y:
                x, y = y, x
            vars_.append(edge_id[(x, y)])
        triangles.add(tuple(sorted(vars_)))

    ordered_triangles = sorted(triangles)
    assert len(traces) == 93
    assert len(edges) == 1610
    assert len(ordered_triangles) == 6020
    assert all(len(set(row)) == 3 for row in ordered_triangles)
    return traces, edges, ordered_triangles, trace_id, edge_id


def stable_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, separators=(",", ":"), sort_keys=True).encode()
    ).hexdigest()


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def generate(cnf: Path, metadata: Path) -> None:
    traces, edges, triangles, _trace_id, _edge_id = build_trace_instance()
    clauses = 2 * len(triangles) + 1
    with cnf.open("w", encoding="ascii", newline="\n") as out:
        out.write("c Eight-point trace ansatz for KG(12,3)\n")
        out.write("c true=red false=blue; variable 1 fixed blue by global swap\n")
        out.write(f"p cnf {len(edges)} {clauses}\n")
        for x, y, z in triangles:
            out.write(f"{x} {y} {z} 0\n")
            out.write(f"-{x} -{y} -{z} 0\n")
        out.write("-1 0\n")

    record = {
        "scope": "eight-point trace ansatz, not the full KG(12,3) search",
        "distinguished_points": M,
        "anonymous_points": OUTSIDE,
        "admissible_traces": len(traces),
        "trace_edge_variables": len(edges),
        "realisable_trace_triangles": len(triangles),
        "cnf_clauses": clauses,
        "trace_order_sha256": stable_hash(traces),
        "trace_edge_order_sha256": stable_hash(edges),
        "trace_triangle_order_sha256": stable_hash(triangles),
        "cnf_sha256": file_hash(cnf),
        "SAT_consequence": (
            "The model lifts to a coloring of KG(12,3), hence "
            "R_3^KG(3,3)=13 using the published upper bound."
        ),
        "UNSAT_consequence": (
            "No coloring depending only on eight-point traces exists; "
            "the full exact-value problem remains open."
        ),
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
            literals.extend(int(x) for x in line[2:].split() if int(x) != 0)
    if status != "SATISFIABLE":
        raise ValueError(f"expected SATISFIABLE, got {status!r}")
    values: list[bool | None] = [None] * (variables + 1)
    for lit in literals:
        var = abs(lit)
        if not 1 <= var <= variables:
            raise ValueError(f"bad variable {var}")
        val = lit > 0
        if values[var] is not None and values[var] != val:
            raise ValueError(f"contradictory variable {var}")
        values[var] = val
    missing = [i for i in range(1, variables + 1) if values[i] is None]
    if missing:
        raise ValueError(f"partial model: {len(missing)} variables missing")
    return [bool(x) for x in values[1:]]


def pack_hex(values: Iterable[bool]) -> str:
    bits = list(values)
    data = bytearray((len(bits) + 7) // 8)
    for i, value in enumerate(bits):
        if value:
            data[i // 8] |= 1 << (i % 8)
    return data.hex()


def verify_model(solver_output: Path, certificate: Path) -> None:
    traces, edges, triangles, trace_id, edge_id = build_trace_instance()
    values = parse_model(solver_output, len(edges))

    for row in triangles:
        count = sum(values[var - 1] for var in row)
        if count not in (1, 2):
            raise AssertionError(f"bad trace triangle {row}")

    vertices = list(itertools.combinations(range(N), R))
    vertex_id = {v: i for i, v in enumerate(vertices)}
    vertex_trace = [
        sum(1 << x for x in vertex if x < M)
        for vertex in vertices
    ]

    def trace_edge_color(i: int, j: int) -> bool:
        a = trace_id[vertex_trace[i]]
        b = trace_id[vertex_trace[j]]
        if a > b:
            a, b = b, a
        return values[edge_id[(a, b)] - 1]

    full_edges: list[tuple[int, int]] = []
    full_colors: list[bool] = []
    full_edge_id: dict[tuple[int, int], int] = {}
    for i, a in enumerate(vertices):
        a_set = set(a)
        for j in range(i + 1, len(vertices)):
            if a_set.isdisjoint(vertices[j]):
                full_edge_id[(i, j)] = len(full_edges)
                full_edges.append((i, j))
                full_colors.append(trace_edge_color(i, j))

    checked = one_red = two_red = 0
    for i, a in enumerate(vertices):
        remaining_a = tuple(x for x in range(N) if x not in a)
        for b in itertools.combinations(remaining_a, R):
            j = vertex_id[b]
            if j <= i:
                continue
            remaining_ab = tuple(x for x in range(N) if x not in set(a) | set(b))
            for c in itertools.combinations(remaining_ab, R):
                k = vertex_id[c]
                if k <= j:
                    continue
                colors = (
                    full_colors[full_edge_id[(i, j)]],
                    full_colors[full_edge_id[(i, k)]],
                    full_colors[full_edge_id[(j, k)]],
                )
                count = sum(colors)
                if count == 1:
                    one_red += 1
                elif count == 2:
                    two_red += 1
                else:
                    raise AssertionError((a, b, c, colors))
                checked += 1

    assert len(full_edges) == 9240
    assert checked == 61600
    trace_hex = pack_hex(values)
    full_hex = pack_hex(full_colors)
    record = {
        "result": "SAT",
        "ansatz": "eight-point trace coloring",
        "trace_variables_checked": len(values),
        "trace_triangles_checked": len(triangles),
        "full_edges_checked": len(full_edges),
        "full_triangles_checked": checked,
        "monochromatic_full_triangles": 0,
        "full_triangles_with_one_red_edge": one_red,
        "full_triangles_with_two_red_edges": two_red,
        "full_red_edges": sum(full_colors),
        "full_blue_edges": len(full_colors) - sum(full_colors),
        "trace_model_hex": trace_hex,
        "trace_model_hex_sha256": hashlib.sha256(trace_hex.encode()).hexdigest(),
        "full_model_hex": full_hex,
        "full_model_hex_sha256": hashlib.sha256(full_hex.encode()).hexdigest(),
        "full_edge_order_sha256": stable_hash(full_edges),
        "ramsey_consequence": (
            "R_3^KG(3,3)=13, conditional only on the published upper bound <=13"
        ),
    }
    certificate.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(json.dumps(record, indent=2, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    gen = sub.add_parser("generate")
    gen.add_argument("--cnf", type=Path, required=True)
    gen.add_argument("--metadata", type=Path, required=True)
    verify = sub.add_parser("verify-model")
    verify.add_argument("--solver-output", type=Path, required=True)
    verify.add_argument("--certificate", type=Path, required=True)
    args = parser.parse_args()
    if args.cmd == "generate":
        generate(args.cnf, args.metadata)
    else:
        verify_model(args.solver_output, args.certificate)


if __name__ == "__main__":
    main()
