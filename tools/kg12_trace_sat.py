#!/usr/bin/env python3
"""Generate and verify trace-quotient SAT instances for KG(12,3).

Choose M distinguished points and treat the other 12-M points anonymously.
Every Kneser vertex is represented by its trace on the distinguished points.
A satisfying trace-edge coloring lifts mechanically to all of KG(12,3).

For M=11 the trace map is injective and the instance is equivalent to the
full problem. Smaller M are progressively stronger quotient ansatzes: SAT is
decisive for the full problem, while UNSAT only rules out that quotient.
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


def stable_hash(value: object) -> str:
    payload = json.dumps(value, separators=(",", ":"), sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_instance(m: int):
    if not 5 <= m <= 11:
        raise ValueError("distinguished-point count must lie in 5..11")
    outside = N - m
    traces = [mask for mask in range(1 << m) if mask.bit_count() <= R]
    trace_id = {mask: i for i, mask in enumerate(traces)}

    # Two disjoint traces S,T can be completed to disjoint 3-sets using the
    # anonymous points iff the anonymous deficits fit in the outside set.
    pair_union_minimum = 2 * R - outside
    edges: list[tuple[int, int]] = []
    edge_id: dict[tuple[int, int], int] = {}
    for i, a in enumerate(traces):
        for j in range(i, len(traces)):
            b = traces[j]
            if a & b:
                continue
            if a.bit_count() + b.bit_count() < pair_union_minimum:
                continue
            edge_id[(i, j)] = len(edges) + 1
            edges.append((i, j))

    # Three pairwise-disjoint traces are jointly realizable on a Kneser
    # triangle iff their total anonymous deficit is at most `outside`, i.e.
    # their distinguished union has size at least 3R-outside.
    triangle_union_minimum = 3 * R - outside
    triangles: set[tuple[int, int, int]] = set()
    for labels in itertools.product(range(4), repeat=m):
        bins = [0, 0, 0, 0]
        for point, label in enumerate(labels):
            bins[label] |= 1 << point
        a, b, c, _unused = bins
        if any(mask.bit_count() > R for mask in (a, b, c)):
            continue
        if (a | b | c).bit_count() < triangle_union_minimum:
            continue
        ids = [trace_id[a], trace_id[b], trace_id[c]]
        variables: list[int] = []
        for x, y in ((ids[0], ids[1]), (ids[0], ids[2]), (ids[1], ids[2])):
            if x > y:
                x, y = y, x
            variables.append(edge_id[(x, y)])
        if len(set(variables)) != 3:
            raise AssertionError((m, a, b, c, variables))
        triangles.add(tuple(sorted(variables)))

    ordered_triangles = sorted(triangles)
    symmetry: tuple[int, int, int] | None = None
    if m >= 9:
        masks = (
            sum(1 << x for x in (0, 1, 2)),
            sum(1 << x for x in (3, 4, 5)),
            sum(1 << x for x in (6, 7, 8)),
        )
        ids = [trace_id[mask] for mask in masks]
        vars_: list[int] = []
        for x, y in ((ids[0], ids[1]), (ids[0], ids[2]), (ids[1], ids[2])):
            if x > y:
                x, y = y, x
            vars_.append(edge_id[(x, y)])
        symmetry = tuple(vars_)
        assert len(set(symmetry)) == 3

    expected = {
        8: (93, 1610, 6020),
        9: (130, 3318, 16240),
        10: (176, 6090, 36400),
        11: (232, 9240, 61600),
    }
    if m in expected:
        assert (len(traces), len(edges), len(ordered_triangles)) == expected[m]
    return traces, edges, ordered_triangles, trace_id, edge_id, symmetry


def generate(m: int, cnf: Path, metadata: Path) -> None:
    traces, edges, triangles, _trace_id, _edge_id, symmetry = build_instance(m)
    unit_count = 3 if symmetry is not None else 1
    clauses = 2 * len(triangles) + unit_count
    with cnf.open("w", encoding="ascii", newline="\n") as out:
        out.write(f"c {m}-point trace quotient for KG(12,3)\n")
        out.write("c true=red false=blue\n")
        out.write(f"p cnf {len(edges)} {clauses}\n")
        for x, y, z in triangles:
            out.write(f"{x} {y} {z} 0\n")
            out.write(f"-{x} -{y} -{z} 0\n")
        if symmetry is None:
            out.write("-1 0\n")
        else:
            ab, ac, bc = symmetry
            out.write(f"{ab} 0\n")
            out.write(f"-{ac} 0\n")
            out.write(f"-{bc} 0\n")

    outside = N - m
    record = {
        "scope": (
            "full KG(12,3) instance" if m == 11 else
            f"{m}-point trace quotient; UNSAT is ansatz-only"
        ),
        "distinguished_points": m,
        "anonymous_points": outside,
        "pair_trace_union_minimum": 2 * R - outside,
        "triangle_trace_union_minimum": 3 * R - outside,
        "admissible_traces": len(traces),
        "trace_edge_variables": len(edges),
        "realisable_trace_triangles": len(triangles),
        "cnf_clauses": clauses,
        "trace_order_sha256": stable_hash(traces),
        "trace_edge_order_sha256": stable_hash(edges),
        "trace_triangle_order_sha256": stable_hash(triangles),
        "cnf_sha256": file_hash(cnf),
        "symmetry_variables_ab_ac_bc": list(symmetry) if symmetry else None,
        "SAT_consequence": (
            "The model lifts to KG(12,3), hence R_3^KG(3,3)=13 using "
            "the published upper bound."
        ),
        "UNSAT_consequence": (
            "R_3^KG(3,3)=12" if m == 11 else
            f"No {m}-point trace coloring exists; the full problem remains open."
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
            for token in line[2:].split():
                lit = int(token)
                if lit:
                    literals.append(lit)
    if status != "SATISFIABLE":
        raise ValueError(f"expected SATISFIABLE, observed {status!r}")
    values: list[bool | None] = [None] * (variables + 1)
    for lit in literals:
        var = abs(lit)
        if not 1 <= var <= variables:
            raise ValueError(f"model variable {var} outside 1..{variables}")
        value = lit > 0
        if values[var] is not None and values[var] != value:
            raise ValueError(f"contradictory assignment for variable {var}")
        values[var] = value
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


def verify_model(m: int, solver_output: Path, certificate: Path) -> None:
    traces, edges, triangles, trace_id, edge_id, symmetry = build_instance(m)
    values = parse_model(solver_output, len(edges))
    for row in triangles:
        red_count = sum(values[var - 1] for var in row)
        if red_count not in (1, 2):
            raise AssertionError(f"monochromatic trace triangle {row}")

    vertices = list(itertools.combinations(range(N), R))
    vertex_id = {vertex: i for i, vertex in enumerate(vertices)}
    vertex_trace = [sum(1 << x for x in vertex if x < m) for vertex in vertices]

    def lifted_color(i: int, j: int) -> bool:
        x = trace_id[vertex_trace[i]]
        y = trace_id[vertex_trace[j]]
        if x > y:
            x, y = y, x
        return values[edge_id[(x, y)] - 1]

    full_edges: list[tuple[int, int]] = []
    full_colors: list[bool] = []
    full_edge_id: dict[tuple[int, int], int] = {}
    for i, a in enumerate(vertices):
        a_set = set(a)
        for j in range(i + 1, len(vertices)):
            if a_set.isdisjoint(vertices[j]):
                full_edge_id[(i, j)] = len(full_edges)
                full_edges.append((i, j))
                full_colors.append(lifted_color(i, j))

    checked = one_red = two_red = 0
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
                colors = (
                    full_colors[full_edge_id[(i, j)]],
                    full_colors[full_edge_id[(i, k)]],
                    full_colors[full_edge_id[(j, k)]],
                )
                red_count = sum(colors)
                if red_count == 1:
                    one_red += 1
                elif red_count == 2:
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
        "distinguished_points": m,
        "anonymous_points": N - m,
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
        "symmetry_variables_ab_ac_bc": list(symmetry) if symmetry else None,
        "ramsey_consequence": (
            "R_3^KG(3,3)=13, conditional only on the published upper bound <=13"
        ),
    }
    certificate.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(json.dumps(record, indent=2, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--distinguished", type=int, required=True)
    sub = parser.add_subparsers(dest="command", required=True)
    gen = sub.add_parser("generate")
    gen.add_argument("--cnf", type=Path, required=True)
    gen.add_argument("--metadata", type=Path, required=True)
    verify = sub.add_parser("verify-model")
    verify.add_argument("--solver-output", type=Path, required=True)
    verify.add_argument("--certificate", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "generate":
        generate(args.distinguished, args.cnf, args.metadata)
    else:
        verify_model(args.distinguished, args.solver_output, args.certificate)


if __name__ == "__main__":
    main()
