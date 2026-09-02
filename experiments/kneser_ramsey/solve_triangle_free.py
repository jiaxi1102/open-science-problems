#!/usr/bin/env python3
import argparse, itertools, json, time
from pathlib import Path
from pysat.solvers import Cadical195


def kneser_instance(n: int, k: int):
    vertices = list(itertools.combinations(range(n), k))
    edges = []
    edge_id = {}
    for i, a in enumerate(vertices):
        A = set(a)
        for j in range(i + 1, len(vertices)):
            b = vertices[j]
            if A.isdisjoint(b):
                edge_id[(i, j)] = len(edges) + 1
                edges.append((i, j))

    triangles = []
    # A triangle in KG(n,k) is exactly three pairwise-disjoint k-sets.
    for i, a in enumerate(vertices):
        A = set(a)
        for j in range(i + 1, len(vertices)):
            b = vertices[j]
            if not A.isdisjoint(b):
                continue
            AB = A | set(b)
            for h in range(j + 1, len(vertices)):
                c = vertices[h]
                if AB.isdisjoint(c):
                    triangles.append((edge_id[(i, j)], edge_id[(i, h)], edge_id[(j, h)]))
    return vertices, edges, triangles


def solve(n: int, k: int, out: Path):
    vertices, edges, triangles = kneser_instance(n, k)
    clauses = []
    for x, y, z in triangles:
        # Not all red and not all blue. True=red, False=blue.
        clauses.append([x, y, z])
        clauses.append([-x, -y, -z])
    # Global color-swap symmetry: make the first edge red.
    if edges:
        clauses.append([1])

    started = time.time()
    with Cadical195(bootstrap_with=clauses) as solver:
        sat = solver.solve()
        model = solver.get_model() if sat else None
    elapsed = time.time() - started

    result = {
        "n": n,
        "k": k,
        "vertices": len(vertices),
        "edges": len(edges),
        "triangles": len(triangles),
        "clauses": len(clauses),
        "satisfiable": bool(sat),
        "elapsed_seconds": elapsed,
    }
    if sat:
        assignment = {abs(x): x > 0 for x in model if abs(x) <= len(edges)}
        red = []
        blue = []
        for eid, (i, j) in enumerate(edges, 1):
            pair = [list(vertices[i]), list(vertices[j])]
            (red if assignment.get(eid, False) else blue).append(pair)
        result["red_edges"] = red
        result["blue_edges"] = blue

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in ["n","k","vertices","edges","triangles","clauses","satisfiable","elapsed_seconds"]}, indent=2))
    return sat


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--k", type=int, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    solve(args.n, args.k, args.out)
